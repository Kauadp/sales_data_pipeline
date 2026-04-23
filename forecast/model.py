import functools
import os
import tempfile
import numpy as np
import pandas as pd
import torch
from neuralprophet import load as np_load
import logging
import shutil

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Define diretório temporário para produção (evita Permission denied em /home/kau)
temp_dir = tempfile.mkdtemp()
os.environ["TMPDIR"] = temp_dir
os.environ["HOME"] = temp_dir
os.environ["TEMP"] = temp_dir
os.environ["TMP"] = temp_dir

# NÃO muda o diretório de trabalho - apenas configura variáveis de ambiente
# os.chdir(temp_dir)  # REMOVIDO - causava problema de caminho

# Configura diretório de cache do PyTorch
torch_cache = os.path.join(temp_dir, "torch_cache")
os.makedirs(torch_cache, exist_ok=True)
torch.hub.set_dir(torch_cache)

# Configura diretório para NeuralProphet logs
np_cache = os.path.join(temp_dir, "np_cache")
os.makedirs(np_cache, exist_ok=True)

logger.info(f"[MODEL] Temp dir configurado: {temp_dir}")

# carrega o modelo uma vez só na inicialização do módulo
# (não a cada request do dash)
torch.load = functools.partial(torch.load, weights_only=False)

# Determina o caminho base corretamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# O modelo está em /mount/src/sales_data_pipeline/models/
MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR), "models", "model_otimo.np")

logger.info(f"[MODEL] BASE_DIR: {BASE_DIR}")
logger.info(f"[MODEL] MODEL_PATH: {MODEL_PATH}")
logger.info(f"[MODEL] Modelo existe: {os.path.exists(MODEL_PATH)}")

try:
    MODEL_OTIMO = np_load(MODEL_PATH)

    logger.info("[MODEL] model_otimo.np carregado com sucesso")

    if hasattr(MODEL_OTIMO, "trainer") and MODEL_OTIMO.trainer is not None:
        MODEL_OTIMO.trainer.logger = None
        MODEL_OTIMO.trainer.enable_checkpointing = False
        MODEL_OTIMO.trainer.default_root_dir = temp_dir
        MODEL_OTIMO.trainer.callbacks = []

    MODEL_OTIMO.config_train.logger = None
    MODEL_OTIMO.config_train.epochs = 0
    MODEL_OTIMO.fitted = True

except Exception as e:
    MODEL_OTIMO = None
    logger.error(f"[MODEL] Aviso: não foi possível carregar model_otimo.np — {e}")


def croston(series: np.ndarray, alpha: float = 0.2) -> float:
    """
    Método de Croston para séries intermitentes.
    Retorna a previsão de um passo à frente.
    """
    logger.info(f"[CROSTON] Iniciando com alpha={alpha}, series_len={len(series)}")
    demand = np.array(series)
    nonzero = demand[demand > 0]

    if len(nonzero) == 0:
        logger.warning("[CROSTON] Nenhum valor não-zero encontrado, retornando 0.0")
        return 0.0

    indices = np.where(demand > 0)[0]
    p = np.diff(indices)

    a = nonzero[0]
    q = p[0] if len(p) > 0 else 1.0

    for i in range(1, len(nonzero)):
        a = alpha * nonzero[i] + (1 - alpha) * a
        if i - 1 < len(p):
            q = alpha * p[i - 1] + (1 - alpha) * q

    result = a / q if q > 0 else 0.0
    logger.info(f"[CROSTON] Resultado: {result}")
    return result


def _preparar_df(df_trends: pd.DataFrame, id_expositor: str) -> pd.DataFrame:
    """
    Prepara o DataFrame para o NeuralProphet:
    renomeia colunas, garante frequência semanal, log1p no target.
    Inclui o ID do expositor, como o modelo foi treinado.
    """
    logger.info(f"[_PREPARAR] Preparando DataFrame para {id_expositor}, {len(df_trends)} linhas")
    df = df_trends.rename(columns={"data": "ds", "trends": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    df["ID"] = id_expositor                        
    df = df.sort_values("ds").drop_duplicates("ds")
    df = df.set_index("ds").asfreq("W-SUN")
    df["y"] = df["y"].ffill().fillna(0)
    df["y"] = np.log1p(df["y"])
    result = df.reset_index()
    logger.info(f"[_PREPARAR] DataFrame preparado, {len(result)} linhas finais")
    return result



def predict_neural(
    df_trends: pd.DataFrame,
    id_expositor: str,          
    data_alvo: str,
) -> float:
    logger.info(f"[NEURAL] Iniciando previsão para {id_expositor}, data_alvo={data_alvo}")
    if MODEL_OTIMO is None:
        logger.error("[NEURAL] MODEL_OTIMO é None")
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
        logger.error(f"[NEURAL] Previsão retornou NaN para {data_alvo_dt}")
        raise ValueError(f"Previsão retornou NaN para {data_alvo_dt}")
    
    logger.info(f"[NEURAL] Previsão final: {yhat_log} (log) -> {np.expm1(yhat_log)} (original)")

    return float(np.expm1(yhat_log))


def predict_croston_serie(df_trends: pd.DataFrame) -> float:
    """
    Roda Croston para séries intermitentes.
    Retorna yhat na escala original (revertendo log1p).
    """
    logger.info(f"[CROSTON_SERIE] Iniciando para série com {len(df_trends)} pontos")
    y = np.log1p(df_trends["trends"].values)
    yhat_log = croston(y, alpha=0.2)
    result = float(np.expm1(yhat_log))
    logger.info(f"[CROSTON_SERIE] Resultado: {result}")
    return result


def predict(
    df_trends: pd.DataFrame,
    tipo_serie: str,
    data_alvo: str,
    id_expositor: str = "",
) -> tuple[float, str]:
    logger.info(f"[PREDICT] id={id_expositor}, tipo_serie={tipo_serie}, data_alvo={data_alvo}")
    if df_trends.empty:
        logger.warning("[PREDICT] df_trends vazio, retornando 0.0, SEM DADOS TRENDS")
        return 0.0, "SEM DADOS TRENDS"
    if tipo_serie == "sem_sinal":
        logger.warning("[PREDICT] tipo_serie='sem_sinal', retornando 0.0")
        return 0.0, "SEM DADOS TRENDS"
    if tipo_serie == "otima":
        try:
            yhat = predict_neural(df_trends, id_expositor, data_alvo)
            if pd.isna(yhat) or yhat < 0:
                logger.error(f"[PREDICT] Previsão inválida para {id_expositor}: {yhat}")
                return 0.0, "NENHUM"
            logger.info(f"[PREDICT] NeuralProphet retornou {yhat}")
            return yhat, "NEURAL_PROPHET_OTIMO"
        except Exception as e:
            logger.error(f"[PREDICT] NeuralProphet falhou para {id_expositor} — {e}")
            return 0.0, "NENHUM"
    elif tipo_serie == "intermitente":
        logger.info("[PREDICT] Usando Croston para série intermitente")
        yhat = predict_croston_serie(df_trends)
        return yhat, "CROSTON"
    else:
        logger.warning(f"[PREDICT] Tipo série desconhecido: {tipo_serie}")
        return 0.0, "SEM DADOS TRENDS"