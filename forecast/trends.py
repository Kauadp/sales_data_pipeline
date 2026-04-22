import time
import pandas as pd
from pytrends.request import TrendReq
from sqlalchemy import text
import random
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def _buscar_trends(nome_fantasia: str, geo: str = "BR-RJ", max_retries: int = 5) -> pd.DataFrame:
    logger.info(f"[TRENDS] Iniciando busca para {nome_fantasia} (geo={geo})")
    pytrends = TrendReq(hl="pt-BR", tz=360)
    
    for attempt in range(max_retries):
        try:
            pytrends.build_payload(
                [nome_fantasia],
                cat=0,
                timeframe="today 5-y",
                geo=geo,
            )
            data = pytrends.interest_over_time()

            logger.info(f"[TRENDS] Sucesso para {nome_fantasia}, {len(data)} linhas retornadas")
            if data.empty:
                logger.warning(f"[TRENDS] Dados vazios para {nome_fantasia}")
                return pd.DataFrame()
            if "isPartial" in data.columns:
                data = data.drop(columns=["isPartial"])

            data = data.reset_index().rename(
                columns={"date": "data", nome_fantasia: "trends"}
            )
            
            # sleep DEPOIS do sucesso também, protege a próxima chamada
            time.sleep(random.uniform(4, 8))
            return data[["data", "trends"]]

        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                wait = (2 ** attempt) + random.uniform(0, 3)
                logger.warning(f"[TRENDS] 429 em {nome_fantasia} — aguardando {wait:.1f}s (tentativa {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                logger.error(f"[TRENDS] Erro em {nome_fantasia}: {e}")
                return None

    logger.error(f"[TRENDS] Desistindo de {nome_fantasia} após {max_retries} tentativas")
    return None


def classificar_serie(df_trends: pd.DataFrame) -> str:
    logger.info(f"[CLASSIFICAR] Classificando série com {len(df_trends)} linhas")
    if df_trends.empty:
        logger.warning("[CLASSIFICAR] DataFrame vazio, retornando 'sem_sinal'")
        return "sem_sinal"

    pct_zero = (df_trends["trends"] == 0).mean()
    
    if pct_zero < 0.70:
        logger.info(f"[CLASSIFICAR] Classificada como 'otima' (pct_zero={pct_zero:.2%})")
        return "otima"
    elif pct_zero < 0.95:
        logger.info(f"[CLASSIFICAR] Classificada como 'intermitente' (pct_zero={pct_zero:.2%})")
        return "intermitente"
    else:
        logger.info(f"[CLASSIFICAR] Classificada como 'sem_sinal' (pct_zero={pct_zero:.2%})")
        return "sem_sinal"