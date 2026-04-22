import functools
import numpy as np
import pandas as pd
import torch
from neuralprophet import load as np_load

# carrega o modelo uma vez só na inicialização do módulo
# (não a cada request do dash)
torch.load = functools.partial(torch.load, weights_only=False)

try:
    MODEL_OTIMO = np_load("models/model_otimo.np")
    print("[MODEL] model_otimo.np carregado com sucesso")
except Exception as e:
    MODEL_OTIMO = None
    print(f"[MODEL] Aviso: não foi possível carregar model_otimo.np — {e}")


def croston(series: np.ndarray, alpha: float = 0.2) -> float:
    """
    Método de Croston para séries intermitentes.
    Retorna a previsão de um passo à frente.
    """
    demand = np.array(series)
    nonzero = demand[demand > 0]

    if len(nonzero) == 0:
        return 0.0

    indices = np.where(demand > 0)[0]
    p = np.diff(indices)

    a = nonzero[0]
    q = p[0] if len(p) > 0 else 1.0

    for i in range(1, len(nonzero)):
        a = alpha * nonzero[i] + (1 - alpha) * a
        if i - 1 < len(p):
            q = alpha * p[i - 1] + (1 - alpha) * q

    return a / q if q > 0 else 0.0


def _preparar_df(df_trends: pd.DataFrame, id_expositor: str) -> pd.DataFrame:
    """
    Prepara o DataFrame para o NeuralProphet:
    renomeia colunas, garante frequência semanal, log1p no target.
    Inclui o ID do expositor, como o modelo foi treinado.
    """
    df = df_trends.rename(columns={"data": "ds", "trends": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    df["ID"] = id_expositor                        
    df = df.sort_values("ds").drop_duplicates("ds")
    df = df.set_index("ds").asfreq("W-SUN")
    df["y"] = df["y"].ffill().fillna(0)
    df["y"] = np.log1p(df["y"])
    return df.reset_index()



def predict_neural(
    df_trends: pd.DataFrame,
    id_expositor: str,          
    data_alvo: str,
) -> float:
    if MODEL_OTIMO is None:
        raise RuntimeError("model_otimo.np não foi carregado.")

    df = _preparar_df(df_trends, id_expositor)
    data_alvo_dt = pd.to_datetime(data_alvo)
    ultima_data = df["ds"].max()
    semanas = max(1, (data_alvo_dt - ultima_data).days // 7)

    if semanas <= 0:
        forecast = MODEL_OTIMO.predict(df)
        col_target = "yhat1"
    else:
        future = MODEL_OTIMO.make_future_dataframe(df, periods=semanas)
        forecast = MODEL_OTIMO.predict(future)
        col_target = f"yhat{min(semanas, 26)}"

    pred = forecast[forecast["ds"] == data_alvo_dt].copy()
    
    if pred.empty or col_target not in pred.columns:
        raise ValueError(f"Não foi possível gerar previsão para {data_alvo_dt}")
    
    yhat_log = pred[col_target].values[0]
    
    if pd.isna(yhat_log):
        raise ValueError(f"Previsão retornou NaN para {data_alvo_dt}")

    return float(np.expm1(yhat_log))


def predict_croston_serie(df_trends: pd.DataFrame) -> float:
    """
    Roda Croston para séries intermitentes.
    Retorna yhat na escala original (revertendo log1p).
    """
    y = np.log1p(df_trends["trends"].values)
    yhat_log = croston(y, alpha=0.2)
    return float(np.expm1(yhat_log))


def predict(
    df_trends: pd.DataFrame,
    tipo_serie: str,
    data_alvo: str,
    id_expositor: str = "",
) -> tuple[float, str]:
    if df_trends.empty:
        return 0.0, "SEM DADOS TRENDS"
    if tipo_serie == "sem_sinal":
        return 0.0, "SEM DADOS TRENDS"
    if tipo_serie == "otima":
        try:
            yhat = predict_neural(df_trends, id_expositor, data_alvo)
            if pd.isna(yhat) or yhat < 0:
                print(f"[MODEL] Previsão inválida para {id_expositor}: {yhat}")
                return 0.0, "NENHUM"
            return yhat, "NEURAL_PROPHET"
        except Exception as e:
            print(f"[MODEL] NeuralProphet falhou para {id_expositor} — {e}")
            return 0.0, "NENHUM"
    elif tipo_serie == "intermitente":
        yhat = predict_croston_serie(df_trends)
        return yhat, "CROSTON"
    else:
        return 0.0, "SEM DADOS TRENDS"