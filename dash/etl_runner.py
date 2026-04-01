from typing import Dict, Tuple

import pandas as pd

from app.db_pipeline import sync_expositores
from app.main import run_etl as run_etl_pipeline


def run_etl() -> pd.DataFrame:
    """Executa o ETL e retorna o DataFrame final."""
    return run_etl_pipeline()


def sync_database(df: pd.DataFrame, db_url: str) -> Dict[str, int]:
    """Sincroniza o DataFrame gerado pelo ETL com o banco de dados."""
    return sync_expositores(df, db_url=db_url)


def run_etl_and_sync(db_url: str) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Executa o ETL e atualiza as tabelas PostgreSQL."""
    df = run_etl()
    result = sync_database(df, db_url)
    return df, result
