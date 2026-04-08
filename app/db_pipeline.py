import hashlib
from typing import Dict, List, Optional

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert


HASH_COLUMNS = [
    "STAND",
    "NOME FANTASIA",
    "EVENTO",
    "TIPO",
    "PIPELINE",
    "AREA",
    "RECEITA REALIZADA",
    "RECEITA PREVISTA",
    "DESCONTO",
    "TO DENTRO",
    "RECORRENTE",
    "CONTRATO ASSINADO",
    "CONTRATO ENVIADO",
    "CIDADE",
    "CATEGORIA",
]

EVENTO_PIPELINE_MAP = {
    "ES": "ESPÍRITO SANTO",
    "RJ": "RIO DE JANEIRO",
    "SP": "SÃO PAULO",
    "SAO": "SÃO PAULO",
}

TABLE_ATUAL = "expositores_atual"
TABLE_HISTORICO = "expositores_historico"


def create_postgres_tables(conn_or_engine) -> None:
    """Cria as tabelas no PostgreSQL, se ainda não existirem."""
    # Divide os statements em múltiplas chamadas
    statements = [
        """CREATE TABLE IF NOT EXISTS expositores_atual (
    id_expositor VARCHAR(255) PRIMARY KEY,
    nome_fantasia TEXT NOT NULL,
    evento VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    pipeline VARCHAR(80),
    area NUMERIC(12,2) NOT NULL DEFAULT 0,
    receita_realizada NUMERIC(18,2) NOT NULL DEFAULT 0,
    receita_prevista NUMERIC(18,2) NOT NULL DEFAULT 0,
    desconto NUMERIC(18,2) NOT NULL DEFAULT 0,
    to_dentro BOOLEAN NOT NULL DEFAULT FALSE,
    recorrente BOOLEAN NOT NULL DEFAULT FALSE,
    contrato_assinado BOOLEAN NOT NULL DEFAULT FALSE,
    contrato_enviado BOOLEAN NOT NULL DEFAULT FALSE,
    cidade VARCHAR(100),
    categoria VARCHAR(100),
    hash CHAR(64) NOT NULL,
    snapshot TIMESTAMPTZ NOT NULL DEFAULT NOW()
)""",
        """CREATE INDEX IF NOT EXISTS idx_expositores_atual_snapshot ON expositores_atual(snapshot)""",
        """CREATE TABLE IF NOT EXISTS expositores_historico (
    historico_id BIGSERIAL PRIMARY KEY,
    id_expositor VARCHAR(255) NOT NULL,
    nome_fantasia TEXT NOT NULL,
    evento VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    pipeline VARCHAR(80),
    area NUMERIC(12,2) NOT NULL DEFAULT 0,
    receita_realizada NUMERIC(18,2) NOT NULL DEFAULT 0,
    receita_prevista NUMERIC(18,2) NOT NULL DEFAULT 0,
    desconto NUMERIC(18,2) NOT NULL DEFAULT 0,
    to_dentro BOOLEAN NOT NULL DEFAULT FALSE,
    recorrente BOOLEAN NOT NULL DEFAULT FALSE,
    contrato_assinado BOOLEAN NOT NULL DEFAULT FALSE,
    contrato_enviado BOOLEAN NOT NULL DEFAULT FALSE,
    cidade VARCHAR(100),
    categoria VARCHAR(100),
    hash CHAR(64) NOT NULL,
    snapshot TIMESTAMPTZ NOT NULL DEFAULT NOW()
)""",
        """CREATE INDEX IF NOT EXISTS idx_expositores_historico_expositor_snapshot ON expositores_historico(id_expositor, snapshot DESC)""",
        """CREATE INDEX IF NOT EXISTS idx_expositores_historico_snapshot ON expositores_historico(snapshot DESC)""",
    ]

    # Diferencia Engine de Connection para evitar nested transactions
    try:
        from sqlalchemy.engine import Engine, Connection
    except Exception:
        Engine = None  # type: ignore
        Connection = None  # type: ignore

    if Engine is not None and isinstance(conn_or_engine, Engine):
        # É uma Engine: abrir transação própria
        with conn_or_engine.begin() as conn:
            for stmt in statements:
                conn.execute(sa.text(stmt))
    elif Connection is not None and isinstance(conn_or_engine, Connection):
        # É uma Connection ativa: executar diretamente
        for stmt in statements:
            conn_or_engine.execute(sa.text(stmt))
    else:
        # Pode ser uma URL ou outro tipo; criar um engine temporário
        engine = sa.create_engine(conn_or_engine, pool_pre_ping=True)
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(sa.text(stmt))


def generate_hash_from_row(values: List[Optional[str]], algorithm: str = "sha256") -> str:
    """Gera hash estável a partir de uma lista de valores normalizados."""
    normalized = "|".join(
        "" if v is None else str(v).strip().upper() for v in values
    )
    digest = hashlib.new(algorithm, normalized.encode("utf-8"))
    return digest.hexdigest()


def compute_hash_column(df: pd.DataFrame, hash_columns: Optional[List[str]] = None) -> pd.Series:
    """Adiciona um hash por linha usando as colunas relevantes."""
    hash_columns = hash_columns or HASH_COLUMNS

    missing = [col for col in hash_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Faltam colunas obrigatórias para hash: {missing}")

    def row_hash(row: pd.Series) -> str:
        values = [row[col] for col in hash_columns]
        return generate_hash_from_row(values)

    return df.apply(row_hash, axis=1)


def _infer_event_by_pipeline(pipeline: str) -> str:
    pipeline = str(pipeline or "").strip().upper()
    for key, event in EVENTO_PIPELINE_MAP.items():
        if key in pipeline:
            return event
    return ""


def normalize_dataframe_for_db(df: pd.DataFrame, id_column: str = "id_expositor") -> pd.DataFrame:
    """Prepara o DataFrame final para sincronização com as tabelas PostgreSQL."""
    df = df.copy()
    df.columns = [str(col).strip().upper() for col in df.columns]

    df["PIPELINE"] = df.get("PIPELINE", "").astype(str).str.strip().str.upper()
    if "EVENTO" not in df.columns or df["EVENTO"].astype(str).str.strip().eq("").all():
        df["EVENTO"] = df["PIPELINE"].apply(_infer_event_by_pipeline)

    if "ID_EXPOSITOR" not in df.columns:
        if "EVENTO" not in df.columns or df["EVENTO"].astype(str).str.strip().eq("").all():
            if "NOME FANTASIA" not in df.columns:
                raise ValueError(
                    "O DataFrame deve conter 'ID_EXPOSITOR' ou 'NOME FANTASIA' para construir a chave lógica."
                )
            df["EVENTO"] = df["PIPELINE"].apply(_infer_event_by_pipeline)

        if "NOME FANTASIA" not in df.columns:
            raise ValueError("O DataFrame deve conter 'NOME FANTASIA' para construir id_expositor.")

        # Construir `ID_EXPOSITOR` com tolerância a nomes fantasia repetidos.
        # Quando houver `STAND`, ele passa a compor a chave para qualquer nome fantasia
        # (incluindo VACÂNCIA), evitando colisões legítimas do mesmo nome em posições distintas.
        # Se não houver `STAND`, mantém o fallback por nome fantasia.
        def _build_id(row):
            evento = str(row.get("EVENTO", "")).strip().upper()
            nome = str(row.get("NOME FANTASIA", "")).strip().upper()
            stand = str(row.get("STAND", "")).strip().upper()
            base_nome = nome if nome else "VACANCIA"
            if stand:
                return f"{evento}|{base_nome}_{stand}"
            return f"{evento}|{base_nome}"

        df["ID_EXPOSITOR"] = df.apply(_build_id, axis=1)

    df["NOME FANTASIA"] = df["NOME FANTASIA"].astype(str).str.strip().str.upper()
    df["EVENTO"] = df.get("EVENTO", "").astype(str).str.strip().str.upper()
    df["TIPO"] = df.get("TIPO", "").astype(str).str.strip().str.upper()
    df["PIPELINE"] = df.get("PIPELINE", "").astype(str).str.strip().str.upper()
    df["CIDADE"] = df.get("CIDADE", "").astype(str).str.strip().str.upper()
    df["CATEGORIA"] = df.get("CATEGORIA", "").astype(str).str.strip().str.upper()

    for bool_col in ["TO DENTRO", "RECORRENTE", "CONTRATO ASSINADO", "CONTRATO ENVIADO"]:
        if bool_col in df.columns:
            df[bool_col] = df[bool_col].astype(bool)
        else:
            df[bool_col] = False

    for numeric_col in ["AREA", "RECEITA REALIZADA", "RECEITA PREVISTA", "DESCONTO"]:
        if numeric_col not in df.columns:
            df[numeric_col] = 0
        df[numeric_col] = pd.to_numeric(df[numeric_col], errors="coerce").fillna(0)

    if "DESCONTO" not in df.columns or df["DESCONTO"].isna().all():
        df["DESCONTO"] = df["RECEITA PREVISTA"] - df["RECEITA REALIZADA"]

    if "SNAPSHOT" not in df.columns:
        df["SNAPSHOT"] = pd.Timestamp.now()
    else:
        df["SNAPSHOT"] = pd.to_datetime(df["SNAPSHOT"], errors="coerce").fillna(pd.Timestamp.now())

    return df


from sqlalchemy.engine import Engine


def sync_expositores(
    df: pd.DataFrame,
    db_url: str = "",
    engine: Optional[Engine] = None,
    id_column: str = "id_expositor",
) -> Dict[str, int]:
    """Sincroniza o DataFrame com as tabelas atuais e de histórico do PostgreSQL."""
    if engine is None:
        if not db_url:
            raise ValueError("Forneça db_url ou engine para sync_expositores.")
        engine = sa.create_engine(db_url, pool_pre_ping=True)

    df = normalize_dataframe_for_db(df, id_column=id_column)
    df["HASH"] = compute_hash_column(df)
    df["SNAPSHOT"] = pd.to_datetime(df["SNAPSHOT"], errors="coerce").fillna(pd.Timestamp.now())

    columns = [
        "ID_EXPOSITOR",
        "NOME FANTASIA",
        "EVENTO",
        "TIPO",
        "PIPELINE",
        "AREA",
        "RECEITA REALIZADA",
        "RECEITA PREVISTA",
        "DESCONTO",
        "TO DENTRO",
        "RECORRENTE",
        "CONTRATO ASSINADO",
        "CONTRATO ENVIADO",
        "CIDADE",
        "CATEGORIA",
        "HASH",
        "SNAPSHOT",
    ]

    records = (
        df[columns]
        .rename(columns={"ID_EXPOSITOR": "id_expositor"})
        .to_dict(orient="records")
    )

    def _sanitize_key(k: str) -> str:
        # normalize header keys to snake_case database column names
        return str(k).strip().lower().replace(" ", "_")

    records = [{_sanitize_key(k): v for k, v in row.items()} for row in records]

    # Debugging: mostrar quantos registros vamos processar e um exemplo breve
    print(f"sync_expositores: registros a processar = {len(records)}")
    if records:
        sample_keys = list(records[0].keys())[:6]
        print("sync_expositores: sample keys:", sample_keys)
        print("sync_expositores: sample record:", {k: records[0][k] for k in sample_keys})

    # Strong deduplication by id_expositor: keep the record with the most recent snapshot.
    from datetime import datetime

    def _snapshot_to_dt(val):
        if val is None:
            return datetime.min
        # pandas Timestamp
        try:
            import pandas as _pd

            if isinstance(val, _pd.Timestamp):
                return val.to_pydatetime()
        except Exception:
            pass

        # python datetime
        try:
            if isinstance(val, datetime):
                return val
        except Exception:
            pass

        # fallback: try parse via pandas
        try:
            return pd.to_datetime(val)
        except Exception:
            return datetime.min

    dedup_map: Dict[str, Dict[str, object]] = {}
    for r in records:
        key = r.get("id_expositor")
        if key is None:
            continue
        prev = dedup_map.get(key)
        if prev is None:
            dedup_map[key] = r
            continue

        # choose the record with the newest snapshot
        if _snapshot_to_dt(r.get("snapshot")) >= _snapshot_to_dt(prev.get("snapshot")):
            dedup_map[key] = r

    if len(dedup_map) != len(records):
        records = list(dedup_map.values())
        print(f"sync_expositores: duplicates removed, now records = {len(records)}")

    with engine.begin() as conn:
        create_postgres_tables(conn)

        if not records:
            print("sync_expositores: nenhum registro para inserir (records vazio).")
            return {"inserted": 0, "updated": 0, "skipped": 0}

        ids = [row["id_expositor"] for row in records]
        existing_rows = conn.execute(
            sa.text(
                f"SELECT id_expositor, hash FROM {TABLE_ATUAL} WHERE id_expositor = ANY(:ids)"
            ),
            {"ids": ids},
        ).fetchall()

        existing_hash = {row[0]: row[1] for row in existing_rows}
        to_insert_hist: List[Dict[str, object]] = []
        for row in records:
            current_hash = existing_hash.get(row["id_expositor"])
            if current_hash is None or current_hash != row["hash"]:
                to_insert_hist.append(row)

        expositores_atual = sa.Table(
            TABLE_ATUAL,
            sa.MetaData(),
            sa.Column("id_expositor", sa.String(255), primary_key=True),
            sa.Column("nome_fantasia", sa.Text, nullable=False),
            sa.Column("evento", sa.String(50), nullable=False),
            sa.Column("tipo", sa.String(20), nullable=False),
            sa.Column("pipeline", sa.String(80)),
            sa.Column("area", sa.Numeric(12, 2), nullable=False, default=0),
            sa.Column("receita_realizada", sa.Numeric(18, 2), nullable=False, default=0),
            sa.Column("receita_prevista", sa.Numeric(18, 2), nullable=False, default=0),
            sa.Column("desconto", sa.Numeric(18, 2), nullable=False, default=0),
            sa.Column("to_dentro", sa.Boolean, nullable=False, default=False),
            sa.Column("recorrente", sa.Boolean, nullable=False, default=False),
            sa.Column("contrato_assinado", sa.Boolean, nullable=False, default=False),
            sa.Column("contrato_enviado", sa.Boolean, nullable=False, default=False),
            sa.Column("cidade", sa.String(100)),
            sa.Column("categoria", sa.String(100)),
            sa.Column("hash", sa.String(64), nullable=False),
            sa.Column("snapshot", sa.DateTime(timezone=True), nullable=False),
        )

        insert_stmt = insert(expositores_atual).values(records)
        update_columns = {k: insert_stmt.excluded[k] for k in records[0].keys() if k != "id_expositor"}
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["id_expositor"],
            set_=update_columns,
            where=(expositores_atual.c.hash != insert_stmt.excluded.hash),
        )
        res = conn.execute(upsert_stmt)
        print(f"sync_expositores: upsert executed, result: {res}")

        inserted = len([row for row in records if row["id_expositor"] not in existing_hash])
        updated = len([row for row in records if row["id_expositor"] in existing_hash and existing_hash[row["id_expositor"]] != row["hash"]])
        skipped = len(records) - inserted - updated

        if to_insert_hist:
            expositores_historico = sa.Table(
                TABLE_HISTORICO,
                sa.MetaData(),
                sa.Column("id_expositor", sa.String(255), nullable=False),
                sa.Column("nome_fantasia", sa.Text, nullable=False),
                sa.Column("evento", sa.String(50), nullable=False),
                sa.Column("tipo", sa.String(20), nullable=False),
                sa.Column("pipeline", sa.String(80)),
                sa.Column("area", sa.Numeric(12, 2), nullable=False, default=0),
                sa.Column("receita_realizada", sa.Numeric(18, 2), nullable=False, default=0),
                sa.Column("receita_prevista", sa.Numeric(18, 2), nullable=False, default=0),
                sa.Column("desconto", sa.Numeric(18, 2), nullable=False, default=0),
                sa.Column("to_dentro", sa.Boolean, nullable=False, default=False),
                sa.Column("recorrente", sa.Boolean, nullable=False, default=False),
                sa.Column("contrato_assinado", sa.Boolean, nullable=False, default=False),
                sa.Column("contrato_enviado", sa.Boolean, nullable=False, default=False),
                sa.Column("cidade", sa.String(100)),
                sa.Column("categoria", sa.String(100)),
                sa.Column("hash", sa.String(64), nullable=False),
                sa.Column("snapshot", sa.DateTime(timezone=True), nullable=False),
            )

            hist_res = conn.execute(expositores_historico.insert(), to_insert_hist)
            print(f"sync_expositores: historico inserido, rows: {len(to_insert_hist)}")

    return {"inserted": inserted, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    raise RuntimeError(
        "Este módulo foi feito para ser importado. Use sync_expositores(df, db_url) para rodar a carga." 
    )
