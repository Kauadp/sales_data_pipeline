import hashlib
import pandas as pd
from sqlalchemy import text

COLUNAS_EXPOSITORES_ATUAL = [
    "id_expositor",
    "nome_fantasia",
    "evento",
    "tipo",
    "pipeline",
    "area",
    "receita_realizada",
    "receita_prevista",
    "desconto",
    "to_dentro",
    "recorrente",
    "contrato_assinado",
    "contrato_enviado",
    "cidade",
    "categoria",
    "hash",
    "snapshot",
    "percentual_comissao",
]

def _hash_row(row) -> str:
    valor = "|".join(str(row[col]) for col in row.index if col != "snapshot")
    return hashlib.sha256(valor.encode()).hexdigest()

def carregar_banco(df_novo: pd.DataFrame, engine) -> None:
    df_novo = df_novo.copy()

    # Normaliza nomes de colunas para bater com schema do Supabase.
    if "percentual_comissão" in df_novo.columns:
        df_novo = df_novo.rename(columns={"percentual_comissão": "percentual_comissao"})

    # Garante colunas numéricas para cálculo e gravação.
    for col in ["area", "receita_prevista", "receita_realizada", "percentual_comissao"]:
        if col not in df_novo.columns:
            df_novo[col] = 0
        df_novo[col] = pd.to_numeric(df_novo[col], errors="coerce").fillna(0)

    # Regra de negócio: desconto = prevista - realizada.
    df_novo["desconto"] = df_novo["receita_prevista"] - df_novo["receita_realizada"]
    df_novo["desconto"] = pd.to_numeric(df_novo["desconto"], errors="coerce").fillna(0)

    # Garante campos booleanos sem null (tabela usa NOT NULL).
    for col in ["to_dentro", "recorrente", "contrato_assinado", "contrato_enviado"]:
        if col not in df_novo.columns:
            df_novo[col] = False
        df_novo[col] = df_novo[col].fillna(False).astype(bool)

    # Garante campos textuais sem null.
    for col in ["cidade", "categoria", "nome_fantasia", "evento", "tipo", "pipeline", "id_expositor"]:
        if col not in df_novo.columns:
            df_novo[col] = ""
        df_novo[col] = df_novo[col].fillna("").astype(str)

    df_novo["hash"] = df_novo.apply(_hash_row, axis=1)

    # Monta payload final estritamente com as colunas da tabela.
    for col in COLUNAS_EXPOSITORES_ATUAL:
        if col not in df_novo.columns:
            df_novo[col] = None
    df_novo = df_novo[COLUNAS_EXPOSITORES_ATUAL]

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE expositores_atual"))
        df_novo.to_sql("expositores_atual", conn, if_exists="append", index=False)

        conn.execute(text("""
            INSERT INTO expositores_historico (
                id_expositor,
                nome_fantasia,
                evento,
                tipo,
                pipeline,
                area,
                receita_realizada,
                receita_prevista,
                desconto,
                to_dentro,
                recorrente,
                contrato_assinado,
                contrato_enviado,
                cidade,
                categoria,
                hash,
                snapshot,
                percentual_comissao
            )
            SELECT
                a.id_expositor,
                a.nome_fantasia,
                a.evento,
                a.tipo,
                a.pipeline,
                a.area,
                a.receita_realizada,
                a.receita_prevista,
                a.desconto,
                a.to_dentro,
                a.recorrente,
                a.contrato_assinado,
                a.contrato_enviado,
                a.cidade,
                a.categoria,
                a.hash,
                a.snapshot,
                a.percentual_comissao
            FROM expositores_atual a
            WHERE NOT EXISTS (
                SELECT 1 FROM expositores_historico h
                WHERE h.id_expositor = a.id_expositor
                AND h.hash = a.hash
            )
        """))

    print("Banco sincronizado.")