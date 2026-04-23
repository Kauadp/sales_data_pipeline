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
    melhores_parametros_otimizados
)
import os 
import logging
import json
import sys

# Adicionar o path do app para importar get_engine
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app_path = os.path.join(root_path, 'app')
sys.path.insert(0, root_path)
sys.path.insert(0, app_path)

from app.db.database import get_engine

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

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
        logger.info(f"[ETL] Processando {row['nome_fantasia']}...")

        df_trends = _buscar_trends(row["nome_fantasia"])
        if df_trends is None:
            logger.info(f"Pulando {row['nome_fantasia']} devido a erro ou falta de dados.")
            continue
        tipo_serie = classificar_serie(df_trends)
        yhat, modelo_origem = predict(df_trends, tipo_serie, DATA_ALVO, row['nome_fantasia'])
        if modelo_origem == "NENHUM":
            logger.info(f"Pulando {row['nome_fantasia']} devido a erro no modelo.")
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

    logger.info(f"[ETL] ETL Completo para {row['nome_fantasia']}...")
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
        logger.info(f"[DB] {len(df_db)} registros salvos em forecast_trends_cache")
    except Exception as e:
        logger.info(f"[DB] Erro ao salvar em forecast_trends_cache: {e}")

def rodar_etl_otimizacao(data) -> pd.DataFrame:
    """
    ETL de otimização — obtém a engine automaticamente do módulo de database.
    """
    from app.config import URL_DB
    engine = get_engine(URL_DB)
    
    logger.info(f"[OTM] Processando {data['nome_fantasia']}...")
 
    df_trends = _buscar_trends(data["nome_fantasia"])
    if df_trends is None:
        logger.info(f"Não foi possível processar {data['nome_fantasia']} devido a erro ou falta de dados.")
        return None
    tipo_serie = classificar_serie(df_trends)
    yhat, modelo_origem = predict(df_trends, tipo_serie, DATA_ALVO, data['nome_fantasia'])
    if modelo_origem == "NENHUM":
        logger.info(f"Não foi possível processar {data['nome_fantasia']} devido a erro no modelo.")
        return None
 
    def definir_porte(area):
        if area <= 20:
            return "Pequeno"
        elif area <= 35:
            return "Médio"
        else:
            return "Grande"
 
    porte = definir_porte(data["area"])
    logger.info(f"[DEBUG] Porte de {data['nome_fantasia']} é {porte}")
 
    resultado_mc = rodar_monte_carlo(
        yhat=yhat,
        porte=porte,
        ticket_medio=data["ticket_medio"],
        percentual_comissao=data["pct_comissao"],
        minimo_garantido=data["minimo_garantido"],
        volume_por_ponto=VOLUME_POR_PONTO,
    )
 
    area = data["area"]
    preco_base = 690.0
 
    def simular_desconto(porte):
        if porte == "Pequeno":
            return np.random.uniform(0.05, 0.20)
        elif porte == "Médio":
            return np.random.uniform(0.20, 0.25)
        else:
            return np.random.uniform(0.25, 0.70)
 
    desconto = simular_desconto(porte)
    receita_otimizada_nova = area * preco_base * (1 - desconto)
 
    if data["pct_comissao"] > 0:
        valor_excedente = (data["minimo_garantido"] / data["pct_comissao"]) + data["minimo_garantido"]
    else:
        valor_excedente = 0
 
    meta_total = receita_otimizada_nova + valor_excedente
 
    resultado = {
        'nome_fantasia':        data["nome_fantasia"],
        'modelo_origem':        modelo_origem,
        'porte':                porte,
        'area':                 area,
        'ticket_medio':         data["ticket_medio"],
        'minimo_garantido':     round(data["minimo_garantido"], 2),
        'receita_estimada_media': resultado_mc["receita_mediana"],
        'percentual_comissao':  data["pct_comissao"],
        'meta_total':           round(meta_total, 2),
        'receita_otimizada':    round(receita_otimizada_nova, 2),
        'ganho_real_medio':     resultado_mc["ganho_medio"],
        'prob_vale_a_pena_pct': resultado_mc["prob_vale_a_pena_pct"],
        'status_decisao':       resultado_mc["status_decisao"],
        'yhat_trends':          round(yhat, 4),
        'data_simulacao':       pd.Timestamp.now()
    }
 
    resultado_df = pd.DataFrame([resultado])
 
    # ------------------------------------------------------------------
    # Verificar se já vale a pena ANTES de otimizar
    # ------------------------------------------------------------------
    status_atual = resultado_df['status_decisao'].iloc[0]
    ja_otimo     = status_atual == "Comissão Vale A Pena"
 
    if ja_otimo:
        otm        = {}
        sem_cenario = False
    else:
        otm         = melhores_parametros_otimizados(resultado_df)
        sem_cenario = not otm or not otm.get("tem_otimizacao")
 
    # ------------------------------------------------------------------
    # Monta df_db conforme o resultado da otimização
    # ------------------------------------------------------------------
    if ja_otimo or sem_cenario:
        df_db = {
            'nome_fantasia':        resultado_df['nome_fantasia'].iloc[0],
            'status_atual':         resultado_df['status_decisao'].iloc[0],
            'prob_atual':           resultado_df['prob_vale_a_pena_pct'].iloc[0],
            'meta_teto_para_60pct': resultado_df['receita_otimizada'].iloc[0],
            'tem_otimizacao':       False,
            'ja_otimo':             ja_otimo,   # True = já vale a pena / False = sem cenário viável
            'tem_tabela':           False,
            'linhas':               [],
            'modelo_origem':        modelo_origem,
            'porte':                porte,
            'mg_atual':             resultado_df['minimo_garantido'].iloc[0],
            'yhat_trends':          round(yhat, 4),
            'data_simulacao':       pd.Timestamp.now()
        }
    else:
        df_db = {
            'nome_fantasia':        otm['nome_fantasia'],
            'status_atual':         otm['status_atual'],
            'prob_atual':           otm['prob_atual'],
            'meta_teto_para_60pct': otm['meta_teto_para_60pct'],
            'tem_otimizacao':       otm['tem_otimizacao'],
            'ja_otimo':             False,
            'tem_tabela':           otm['tem_tabela'],
            'linhas':               otm['linhas'],
            'modelo_origem':        modelo_origem,
            'porte':                porte,
            'mg_atual':             resultado_df['minimo_garantido'].iloc[0],
            'yhat_trends':          round(yhat, 4),
            'data_simulacao':       pd.Timestamp.now()
        }
 
    df_viz = {k: df_db[k] for k in [
        "nome_fantasia", "status_atual", "prob_atual",
        "meta_teto_para_60pct", "tem_otimizacao", "ja_otimo",
        "tem_tabela", "linhas"
    ]}
 
    logger.info(f"[ETL] ETL Completo para {data['nome_fantasia']}...")
 
    df_db      = pd.DataFrame([df_db])
    df_db_save = df_db.copy()
    df_db_save['linhas'] = df_db_save['linhas'].apply(json.dumps)
 
    if not df_db_save.empty:
        _salvar_forecast_otm(engine, df_db_save)
 
    return df_viz


def _salvar_forecast_otm(engine: Engine, df_db: pd.DataFrame) -> None:
    try:
        df_db.to_sql(
            "forecast_trends_otm",
            engine,
            if_exists="append",
            index=False,
        )
        logger.info(f"[DB] {len(df_db)} registros salvos em forecast_trends_otm")
    except Exception as e:
        logger.info(f"[DB] Erro ao salvar em forecast_trends_otm: {e}")