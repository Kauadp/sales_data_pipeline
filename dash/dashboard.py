import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import unicodedata
import sys
import os

from exagerado_theme import (
    inject_theme,
    sidebar_logo,
    section_header,
    kpi_card,
    chart_card,
    resumo_estrategico
)


from data_loader import (
    load_data_atual,
    load_data_historico
)

st.set_page_config(
    page_title='Dashboard de Expositores',
    layout='wide',
    initial_sidebar_state='expanded',
)

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app_path = os.path.join(root_path, 'app')

sys.path.append(root_path)
sys.path.append(app_path)

from app.pipeline import run_pipeline

inject_theme()

# SideBar

with st.sidebar:
    st.image('img/favicon.ico', width=50)
    sidebar_logo()

    st.markdown('###')

    atualizar_dados = st.button('🔄 Atualizar dados', type = "primary")
    if atualizar_dados:
        with st.spinner('Executando ETL...'):
            try:
                run_pipeline()
                st.cache_data.clear()
                st.success("✅ Dados atualizados!")

                st.rerun()  # força refresh do app

            except Exception as exc:
                st.error(f'❌ Falha ao atualizar dados: {exc}')

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('### Seção do Dashboard')

    secao = st.radio(
        'Seção',
        ['Comercial', 'Receita', 'Descontos', 'Espaço', 'Comissionado', 'Previsão'],
        index=0,
        label_visibility='collapsed',
    )

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)

    st.markdown('### Filtros')

    evento = st.selectbox(
        'Evento',
        ['Todos eventos', 'Espírito Santo', 'Rio de Janeiro', 'São Paulo']
    )

    periodo = st.selectbox(
        'Data',
        ['Hoje', 'Semana', 'Mês', 'Total']
    )

    tipo_stand = st.selectbox(
        'Tipo',
        ['STAND', 'FOOD']
    )


### APLICA FILTROS ###

try:
    if periodo == "Total":
        df = load_data_atual()
    else: 
        df = load_data_historico()
        hoje = pd.Timestamp.now(tz="UTC").normalize()
        
        if periodo == "Hoje":
            df["snapshot"] = pd.to_datetime(df["snapshot"], utc=True)
            df = df[df["snapshot"].dt.normalize() == hoje]
        elif periodo == "Semana":
            df["snapshot"] = pd.to_datetime(df["snapshot"], utc=True)
            df = df[df["snapshot"] >= hoje - pd.Timedelta(days=6)]
        elif periodo == "Mês":
            df["snapshot"] = pd.to_datetime(df["snapshot"], utc=True)
            df = df[df["snapshot"] >= hoje - pd.Timedelta(days=29)]

        df = df.sort_values("snapshot").groupby("id_expositor").last().reset_index()
except Exception as exc:
    st.error(f'❌ Falha ao carregar dados do banco: {exc}')
    st.stop()

pipeline_map = {
    'Espírito Santo': 'ES_MAIO_26',
    'Rio de Janeiro': 'RJ_26',
    'São Paulo': 'SP_26',
}

meta_es_stand = 2500000
meta_es_food = 300000
meta_rj_stand = 1500000

meta_sp_stand = 0 # A definir

meta_map = {
    'Espírito Santo': {'STAND': meta_es_stand, 'FOOD': meta_es_food},
    'Rio de Janeiro': {'STAND': meta_rj_stand, 'FOOD': 0},
    'São Paulo': {'STAND': meta_sp_stand, 'FOOD': 0},
}

if evento == 'Todos eventos':
    meta = sum(event_meta.get(tipo_stand, 0) for event_meta in meta_map.values())
else:
    meta = meta_map.get(evento, {}).get(tipo_stand, 0)
    df = df[df["pipeline"] == pipeline_map.get(evento)]

df = df[df["tipo"] == tipo_stand]

# CALCULA KPIS

# Gráfico temporal

from kpis import render_temporal_card

# Import para primeira seção

from kpis import (
    kpis_first_section,
    pie_chart_novos_recorrentes,
    bar_chart_enviados_assinados
)

first_section = kpis_first_section(df)

# Import para secunda seção

from kpis import (
    kpis_second_section,
    top3_chart,
    chart_receita_prevista_realizada
)

second_section = kpis_second_section(df, meta)

# Import para terceira seção

from kpis import (
    kpi_third_section
)

third_section = kpi_third_section(df)

# Import para quarta seção

from kpis import (
    kpi_fourth_section,
    chart_area_disp_ocup,
    chart_receita_area
)

fourth_section = kpi_fourth_section(df)

# Importa para quinta seção

from kpis import (
    kpi_fifth_section
)

fifth_section = kpi_fifth_section(df)

# Import para sexta seção

from kpis import (
    kpi_sixth_section
)

sixth_section = kpi_sixth_section(df, meta)

# INÍCIO DO DASH

st.title('Dashboard de Expositores')

if secao == 'Comercial':
    st.title('Comercial')
    section_header('Expositores, vacâncias, contratos e conversão', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        kpi_card(
            'Expositores',
            f'{first_section['qtde_expositores']:,}',
            'Total de expositores',
            'neutral',
            'purple'
        )
    with col2:
        kpi_card(
            'Vacâncias',
            f'{first_section['vacancias']:,}',
            'Espaços livres',
            'negative'
        )
    with col3:
        kpi_card(
            'To Dentro',
            f'{first_section['to_dentro']:,}',
            'Confirmados',
            'positive',
            'green'
        )
    with col4:
        kpi_card(
            'Contratos Enviados',
            f'{first_section['contratos_enviados']:,}',
            'Pipeline ativo',
            'neutral'
        )
    with col5:
        kpi_card(
            'Contratos Assinados',
            f'{first_section['contratos_assinados']:,}',
            'Fechamento Contratado',
            'positive',
            'green'
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col6, col7 = st.columns([2,1])

    with col6:
        fig_pie = pie_chart_novos_recorrentes(df)
        chart_card('Clientes Recorrentes vs Novos', fig_pie)

    with col7:
        fig_bar = bar_chart_enviados_assinados(df)
        chart_card('Contratos Enviados vs Assinados', fig_bar)

    render_temporal_card(df, secao, meta, periodo)
    
elif secao == 'Receita':
    st.title('Receita')
    section_header('Receita realizada, gap para meta e principais expositores', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card(
            'Receita Realizada',
            f'R$ {second_section['receita_realizada']:,.0f}',
            'Valor realizado',
            'positive',
            'purple'
        )
    with col2:
        kpi_card(
            'Meta',
            f'R$ {meta:,.0f}',
            'Meta geral',
            'neutral'
        )
    with col3:
        kpi_card(
            'Receita Faltante',
            f'R$ {second_section['receita_faltante']:,.0f}',
            'Gap para meta',
            'negative',
            'red'
        )
    with col4:
        kpi_card(
            '% Faltante',
            f'{second_section['percentual_faltante']:.2f}%',
            'Do total',
            'negative',
            'red'
        )

    st.markdown('<br>', unsafe_allow_html=True)

    col5, col6 = st.columns([2, 1])

    with col5:
        fig_top3 = top3_chart(df)
        chart_card('Top 3 Expositores por Receita Realizada', fig_top3)

    with col6:
        fig_receita = chart_receita_prevista_realizada(df)
        chart_card('Receita Prevista vs Realizada', fig_receita)

    render_temporal_card(df, secao, meta, periodo)

elif secao == 'Descontos':
    st.title('Descontos')
    section_header('Descontos concedidos, média e impacto', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card(
            'Descontos Dados', 
            f'R$ {third_section['descontos']:,.0f}',
            'Total concedido',
            'negative',
            'purple'
        )
    with col2:
        kpi_card(
            'Desconto Médio',
            f'R$ {third_section['media_desconto_por_expositor']:,.0f}',
            'Por exepositor',
            'neutral'
        )
    with col3:
        kpi_card(
            '% Desconto Médio',
            f'{third_section['prop_desconto_medio']*100:.2f}%',
            'Média geral',
            'negative',
            'red'
        )

    render_temporal_card(df, secao, meta, periodo)

elif secao == 'Espaço':
    st.title('Espaço')
    section_header('Área ocupada, disponível e receita por metro quadrado', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card(
            'Área Total',
            f'{fourth_section['area_total']:,.0f} m²',
            'Capacidade total',
            'neutral',
            'purple'
        )
    with col2:
        kpi_card(
            'Área Preenchida',
            f'{fourth_section['area_preenchida']:,.0f} m²',
            'Soma m² onde há receita realizada',
            'positive',
            'green',
        )
    with col3:
        kpi_card(
            'Taxa Ocupação',
            f'{fourth_section['prop_area_preenchida']:.2f}%',
            'Ocupação atual',
            'positive' if fourth_section['prop_area_preenchida'] >= 70 else 'neagtive'
        )
        
    with col4:
        kpi_card(
            'Receita por m²',
            f'R$ {fourth_section['receita_por_metro_quadrado']:,.0f}',
            'Ticket médio',
            'neutral'
        )

    col5, col6 = st.columns(2)
    with col5:
        kpi_card(
            'Área Disponível',
            f'{fourth_section['area_disponivel']:,.0f} m²',
            'Espaço livre',
            'negative', 
            'red'
            )
    with col6:
        kpi_card(
            'Receita Potencial Vaga',
            f'R$ {fourth_section['receita_potencial_vaga']:,.0f}',
            'Potencial adicional',
            'neutral',
            'amber')

    st.markdown('###')

    col7, col8 = st.columns(2)

    with col7:
        fig_area = chart_area_disp_ocup(df)
        chart_card('Área Ocupada vs Disponível', fig_area)

    with col8:
        fig_scatter = chart_receita_area(df)
        chart_card('Receita vs Área', fig_scatter)

    render_temporal_card(df, secao, meta, periodo)

elif secao == 'Comissionado':
    st.title('Comissionado')
    section_header('Expositores com comissão ativa e performance', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card(
            'Expositores Comissionados',
            f'{fifth_section['qtde_expositores_comissionados']:,}',
            'Quantidade de expositores comissionados',
            'neutral',
            'purple',
        )
    with col2:
        kpi_card(
            'Área Total Comissionada',
            f'{fifth_section['area_total_comissionados']:,.0f} m²',
            'Soma de m² dos comissionados',
            'neutral',
            'green',
        )
    with col3:
        kpi_card(
            'Média m² por Comissionado',
            f'{fifth_section['media_area_por_expositor_comissionado']:,.2f} m²',
            'Área média por expositor comissionado',
            'neutral',
        )

    col4, col5, col6 = st.columns(3)
    with col4:
        kpi_card(
            'Receita Realizada Mínima Garantida Pelos Expositores Comissionados',
            f'R$ {fifth_section['receita_realizada_comissionados']:,.0f}',
            'Total De Receita Realizada Como Mínimo Garantido Pelos Expositores Comissionados',
            'positive',
            'purple',
        )
    with col5:
        kpi_card(
            'Média Receita Mínima Garantida Por Expositor Comissionado',
            f'R$ {fifth_section['media_receita_por_expositor_comissionado']:,.0f}',
            'Receita Mínima Garantida Média por Expositor Comissionado',
            'neutral',
        )
    with col6:
        kpi_card(
            'Média % Comissão',
            f'{fifth_section['media_percentual_comissao']:.2f}%',
            'Média do percentual de comissão',
            'neutral',
            'amber',
        )

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('###')
    st.markdown('---')

    section_header('Resumo Estratégico')
    summary_items = [
        {
            'type': 'ok',
            'label': 'Percentual de expositores comissionados',
            'value': f'{fifth_section['pct_clientes_comissionados'] * 100:.2f}%',
            'delta': 'Expositores comissionados sobre o total de expositores ativos.',
        },
        {
            'type': 'ok',
            'label': 'Percentual de área comissionada',
            'value': f'{fifth_section['pct_area_comissionada_sobre_preenchida'] * 100:.2f}%',
            'delta': 'Área dos comissionados sobre a área total preenchida.',
        },
        {
            'type': 'ok',
            'label': 'Percentual de receita realizada comissionada',
            'value': f'{fifth_section['pct_receita_comissionada_sobre_total'] * 100:.2f}%',
            'delta': 'Receita dos comissionados sobre a receita total realizada.',
        },
        {
            'type': 'ok',
            'label': 'Média de receita dos comissionados vs geral',
            'value': f'{fifth_section['pct_media_receita_comissionado_vs_geral'] * 100:.2f}%',
            'delta': 'Média de receita por comissionado comparada à média geral por expositor ativo.',
        }
    ]

    if summary_items:
        resumo_estrategico(summary_items)

elif secao == 'Previsão':
    st.title('Previsão')
    section_header('Projeções de receita e metas', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card(
            'Receita Projetada',
            f'R$ {sixth_section['receita_projetada']:,.0f}',
            'Cenário atual',
            'neutral',
            'purple')
    with col2:
        kpi_card(
            'Preço Necessário por m²',
            f'R$ {sixth_section['preco_necessario_m2']:,.0f}',
            'Valor necessário',
            'negative' if sixth_section['preco_necessario_m2'] > fourth_section['receita_por_metro_quadrado'] else 'positive')
    with col3:
        kpi_card(
            'Meta',
            'Atinge' if sixth_section['bate_meta'] else 'Não Atinge', 'Projeção', 'positive' if sixth_section['bate_meta'] else 'negative',
            'green' if sixth_section['bate_meta'] else 'red')

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('###')
    st.markdown('---')

    render_temporal_card(df, secao, meta, periodo)

    section_header('Resumo Estratégico')

    summary_items = []
    if fourth_section['receita_por_metro_quadrado'] < sixth_section['preco_necessario_m2']:
        summary_items.append({
            'type': 'warn',
            'label': 'Preço médio por m² abaixo do necessário',
            'value': f'R$ {fourth_section['receita_por_metro_quadrado']:,.0f}',
            'delta': 'Será necessário vender os espaços restantes por um valor maior.',
        })
    if third_section['prop_desconto_medio'] > 0.15:
        summary_items.append({
            'type': 'warn',
            'label': 'Desconto médio elevado',
            'value': f'{third_section['prop_desconto_medio']*100:.2f}%',
            'delta': 'O desconto pode estar reduzindo a receita total.',
        })
    if fourth_section['prop_area_preenchida'] < 70:
        summary_items.append({
            'type': 'ok',
            'label': 'Área disponível ainda positiva',
            'value': f'{fourth_section['prop_area_preenchida']:.2f}%',
            'delta': 'Focar em ocupação pode aumentar a receita.',
        })
    if first_section['contratos_assinados'] / first_section['contratos_enviados'] < 0.5:
        summary_items.append({
            'type': 'alert',
            'label': 'Assinatura de contratos baixa',
            'value': f'{(first_section['contratos_assinados'] / first_section['contratos_enviados'] * 100) if first_section['contratos_enviados'] else 0:.0f}%',
            'delta': 'Pode ser necessário follow-up comercial.',
        })

    if summary_items:
        resumo_estrategico(summary_items)