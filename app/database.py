import os
from pathlib import Path
from typing import Mapping, Optional, Union
import time

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.engine import Engine, Connection
from db_pipeline import create_postgres_tables

DB_ENV_VAR = "DATABASE_URL"
SECRET_SECTION = "postgres"
SECRET_KEY = "url"
CONFIG_FILE_NAME = "config.toml"

try:
    import tomllib as toml
except ModuleNotFoundError:
    import toml  # type: ignore


def load_config_toml(config_path: Optional[Union[str, Path]] = None) -> Mapping:
    config_path = Path(config_path) if config_path else Path(__file__).resolve().parent / CONFIG_FILE_NAME
    if not config_path.exists():
        return {}

    try:
        with config_path.open("rb") as file_handle:
            return toml.load(file_handle)
    except Exception:
        return {}


def load_toml_file(file_path: Union[str, Path]) -> Mapping:
    file_path = Path(file_path)
    if not file_path.exists():
        return {}

    try:
        with file_path.open("rb") as file_handle:
            return toml.load(file_handle)
    except Exception:
        return {}


def get_database_url(streamlit_secrets: Optional[Mapping] = None, config_path: Optional[Union[str, Path]] = None) -> str:
    """Retorna a URL do banco de dados a partir de ambiente, st.secrets, config.toml ou secrets.toml."""
    db_url = os.getenv(DB_ENV_VAR, "").strip()
    if db_url:
        return db_url

    # Lê arquivos TOML locais primeiro, especialmente quando a URI está em secrets.toml.
    # Além da pasta `app/`, também verifica a raiz do projeto e `dash/config.toml`.
    project_root = Path(__file__).resolve().parents[1]
    local_secret_paths = [
        Path(__file__).resolve().parent / "secrets.toml",
        Path(__file__).resolve().parent / ".streamlit" / "secrets.toml",
        project_root / "secrets.toml",
        project_root / ".streamlit" / "secrets.toml",
        project_root / "dash" / "config.toml",
        project_root / "config.toml",
    ]
    for secret_path in local_secret_paths:
        secret_config = load_toml_file(secret_path)
        if isinstance(secret_config, Mapping):
            postgres_section = secret_config.get(SECRET_SECTION)
            if isinstance(postgres_section, Mapping) and postgres_section.get(SECRET_KEY):
                return str(postgres_section.get(SECRET_KEY)).strip()

            if secret_config.get(DB_ENV_VAR):
                return str(secret_config.get(DB_ENV_VAR)).strip()

    if streamlit_secrets is not None:
        try:
            secret_url = streamlit_secrets.get(SECRET_SECTION, {}).get(SECRET_KEY, "")
            if secret_url:
                return str(secret_url).strip()
        except Exception:
            pass

    config = load_config_toml(config_path)
    if not config:
        return ""

    if isinstance(config, Mapping) and config.get(DB_ENV_VAR):
        return str(config.get(DB_ENV_VAR)).strip()

    if isinstance(config, Mapping):
        database_section = config.get("database")
        if isinstance(database_section, Mapping) and database_section.get("url"):
            return str(database_section.get("url")).strip()

        postgres_section = config.get(SECRET_SECTION)
        if isinstance(postgres_section, Mapping) and postgres_section.get(SECRET_KEY):
            return str(postgres_section.get(SECRET_KEY)).strip()

    return ""


def get_engine(db_url: str) -> Engine:
    """Cria um engine SQLAlchemy para PostgreSQL, normalizando a URL com psycopg2."""
    if not db_url:
        raise ValueError("DATABASE_URL não informado. Use variável de ambiente ou st.secrets.")
    
    # Normaliza a URL para usar psycopg2 explicitamente se ainda não usar um driver
    normalized_url = db_url.strip()
    if normalized_url.startswith("postgresql://") and "+psycopg2" not in normalized_url:
        normalized_url = normalized_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    return sa.create_engine(normalized_url, pool_pre_ping=True)


def get_connection(engine: Engine) -> Connection:
    """Retorna uma conexão ativa para uso com contexto."""
    return engine.connect()


def load_data_from_db(db_url: str, table_name: str = "expositores_atual") -> pd.DataFrame:
    """Carrega dados do banco e normaliza os nomes das colunas para o padrão do dashboard."""
    # Mapeamento de colunas do banco (snake_case) para o padrão do dashboard (MAIÚSCULAS COM ESPAÇOS)
    column_mapping = {
        "stand": "STAND",
        "id_expositor": "ID_EXPOSITOR",
        "nome_fantasia": "NOME FANTASIA",
        "evento": "EVENTO",
        "tipo": "TIPO",
        "pipeline": "PIPELINE",
        "area": "AREA",
        "receita_realizada": "RECEITA REALIZADA",
        "receita_prevista": "RECEITA PREVISTA",
        "desconto": "DESCONTO",
        "to_dentro": "TO DENTRO",
        "recorrente": "RECORRENTE",
        "contrato_assinado": "CONTRATO ASSINADO",
        "contrato_enviado": "CONTRATO ENVIADO",
        "cidade": "CIDADE",
        "categoria": "CATEGORIA",
        "hash": "HASH",
        "snapshot": "SNAPSHOT",
    }
    
    engine = get_engine(db_url)
    max_retries = 3
    last_exc: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            with get_connection(engine) as conn:
                # garante que as tabelas existem antes de ler
                create_postgres_tables(conn)
                df = pd.read_sql(sa.text(f"SELECT * FROM {table_name}"), conn)

            # Renomeia as colunas usando o mapeamento
            df.columns = [column_mapping.get(col.lower(), col.upper()) if isinstance(col, str) else col for col in df.columns]
            return df
        except Exception as e:
            last_exc = e
            # log minimal
            print(f"Tentativa {attempt}/{max_retries} falhou ao carregar dados: {e}")
            if attempt < max_retries:
                time.sleep(2)
            else:
                # após tentativas, re-levanta com mensagem clara
                raise RuntimeError(f"Falha ao carregar dados do banco após {max_retries} tentativas: {e}") from e