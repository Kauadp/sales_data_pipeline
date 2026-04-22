import pandas as pd
import numpy as np
from sqlalchemy.engine import Engine
from sqlalchemy import text
from datetime import datetime
import streamlit as st
# Importações dos seus módulos internos
from forecast.trends import _buscar_trends, classificar_serie
from forecast.model import predict
from forecast.simulation import (
    rodar_monte_carlo, 
)
import os 

DATA_ALVO = st.secrets["data_alvo"]["DATA_ALVO"]
VOLUME_POR_PONTO = 100000

def rodar_etl_oficial(
    engine: Engine,
    df_expositores: pd.DataFrame,
    pipeline_evento: str,
) -> pd.DataFrame:
    """
    ETL batch — roda para todos os expositores comissionados já na base.
    """
    resultados = []

    for _, row in df_expositores.iterrows():
        print(f"[ETL] Processando {row['nome_fantasia']}...")

        df_trends = _buscar_trends(row["nome_fantasia"])
        if df_trends is None:
            print(f"Pulando {row['nome_fantasia']} devido a erro ou falta de dados.")
            continue
        tipo_serie = classificar_serie(df_trends)
        yhat, modelo_origem = predict(df_trends, tipo_serie, DATA_ALVO, row['nome_fantasia'])
        if modelo_origem == "NENHUM":
            print(f"Pulando {row['nome_fantasia']} devido a erro no modelo.")
            continue

        resultado_mc = rodar_monte_carlo(
            yhat=yhat,
            porte=row["porte"],
            ticket_medio=row.get("ticket_medio", 200),
            percentual_comissao=row["percentual_comissao"],
            minimo_garantido=row["receita_realizada"],
            volume_por_ponto=VOLUME_POR_PONTO,
        )

        area = float(row.get("area", 0))
        preco_base = 690.0

        def simular_desconto(porte):
            if porte == "Pequeno":
                return np.random.uniform(0.05, 0.20)
            elif porte == "Médio":
                return np.random.uniform(0.20, 0.25)
            else:  # Grande
                return np.random.uniform(0.25, 0.70)
            
        desconto = simular_desconto(row['porte'])
            
        receita_otimizada_nova = area * preco_base * (1 - desconto)
        
        if row["percentual_comissao"] > 0:
            valor_excedente = (row["receita_realizada"] / row["percentual_comissao"]) + row["receita_realizada"]
        else:
            valor_excedente = 0
            
        meta_total = receita_otimizada_nova + valor_excedente

        resultado_db = {
            'id_expositor': row["id_expositor"],
            'nome_fantasia': row["nome_fantasia"],
            'modelo_origem': modelo_origem,
            'porte': row["porte"],
            'area': area,
            'minimo_garantido': round(row["receita_realizada"], 2),
            'receita_estimada_media': resultado_mc["receita_mediana"],
            'meta_total': round(meta_total, 2),
            'receita_otimizada': round(receita_otimizada_nova, 2),
            'ganho_real_medio': resultado_mc["ganho_medio"],
            'prob_vale_a_pena_pct': resultado_mc["prob_vale_a_pena_pct"],
            'status_decisao': resultado_mc["status_decisao"],
            'yhat_trends': round(yhat, 4),
            'data_simulacao': pd.Timestamp.now()
        }
        resultados.append(resultado_db)

    print(f"[ETL] ETL Completo para {row['nome_fantasia']}...")
    df_db = pd.DataFrame(resultados)
    if not df_db.empty:
        _salvar_forecast_cache(engine, df_db)

    return df_db

def _salvar_forecast_cache(engine: Engine, df_db: pd.DataFrame) -> None:
    try:
        df_db.to_sql(
            "forecast_trends_cache",
            engine,
            if_exists="append",
            index=False,
        )
        print(f"[DB] {len(df_db)} registros salvos em forecast_trends_cache")
    except Exception as e:
        print(f"[DB] Erro ao salvar em forecast_trends_cache: {e}")