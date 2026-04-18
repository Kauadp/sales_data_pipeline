import hashlib
import pandas as pd
from sqlalchemy import text

def _hash_row(row) -> str:
    valor = "|".join(str(row[col]) for col in row.index if col != "snapshot")
    return hashlib.sha256(valor.encode()).hexdigest()

def carregar_banco(df_novo: pd.DataFrame, engine) -> None:
    df_novo = df_novo.copy()
    df_novo["hash"] = df_novo.apply(_hash_row, axis=1)

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE expositores_atual"))
        df_novo.to_sql("expositores_atual", conn, if_exists="append", index=False)

        conn.execute(text("""
            INSERT INTO expositores_historico
            SELECT * FROM expositores_atual a
            WHERE NOT EXISTS (
                SELECT 1 FROM expositores_historico h
                WHERE h.id_expositor = a.id_expositor
                AND h.hash = a.hash
            )
        """))

    print("Banco sincronizado.")