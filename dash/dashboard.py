import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import unicodedata
import sys
import os

# Configurar paths ANTES de importações relativas
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app_path = os.path.join(root_path, 'app')
img_path = os.path.join(root_path, 'img')
sys.path.insert(0, root_path)
sys.path.insert(0, app_path)
sys.path.insert(0, os.path.dirname(__file__))

from exagerado_theme import (
    inject_theme,
    sidebar_logo,
    section_header,
    kpi_card,
    chart_card,
    resumo_estrategico,
    table_card,
    priority_header,
    simulacao_card
)


from data_loader import (
    load_data_atual,
    load_data_historico,
    load_forecast_trends,
)

from forecast import rodar_etl_otimizacao
from app.pipeline import run_pipeline

st.set_page_config(
    page_title='Dashboard de Expositores',
    layout='wide',
    initial_sidebar_state='expanded',
)

inject_theme()

# SideBar

with st.sidebar:
    favicon_path = os.path.join(img_path, 'favicon.ico')
    st.image(favicon_path, width=50)
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
        ['Comercial', 'Receita', 'Descontos', 'Espaço', 'Comissionado', 'Previsão', 'Forecasting'],
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
        df_historico = df.copy()
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

        df_historico = df.copy()

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

# Import para seção forecasting

df_forecast = load_forecast_trends()

from kpis import (
    kpi_forecast_section,
    scatter_prob_ganho,
    bar_ranking_expositores,
    waterfall_piso_upside,
    get_filter_options,
    aplicar_filtros_forecast,
    get_tabela_forecast,
    get_tabela_riscos,
    get_tabela_oportunidades
    )

forecast_section = kpi_forecast_section(df_forecast)


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

    render_temporal_card(df_historico, secao, meta, periodo)
    
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

    render_temporal_card(df_historico, secao, meta, periodo)

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

    render_temporal_card(df_historico, secao, meta, periodo)

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

    render_temporal_card(df_historico, secao, meta, periodo)

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
            f'R$ {sixth_section["receita_projetada"]:,.0f}',
            'Cenário atual',
            'neutral',
            'purple')
    with col2:
        kpi_card(
            'Preço Necessário por m²',
            f'R$ {sixth_section["preco_necessario_m2"]:,.0f}',
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

    render_temporal_card(df_historico, secao, meta, periodo)

    section_header('Resumo Estratégico')

    summary_items = []
    if fourth_section['receita_por_metro_quadrado'] < sixth_section['preco_necessario_m2']:
        summary_items.append({
            'type': 'warn',
            'label': 'Preço médio por m² abaixo do necessário',
            'value': f'R$ {fourth_section["receita_por_metro_quadrado"]:,.0f}',
            'delta': 'Será necessário vender os espaços restantes por um valor maior.',
        })
    if third_section['prop_desconto_medio'] > 0.15:
        summary_items.append({
            'type': 'warn',
            'label': 'Desconto médio elevado',
            'value': f'{third_section["prop_desconto_medio"]*100:.2f}%',
            'delta': 'O desconto pode estar reduzindo a receita total.',
        })
    if fourth_section['prop_area_preenchida'] < 70:
        summary_items.append({
            'type': 'ok',
            'label': 'Área disponível ainda positiva',
            'value': f'{fourth_section["prop_area_preenchida"]:.2f}%',
            'delta': 'Focar em ocupação pode aumentar a receita.',
        })
    if first_section['contratos_assinados'] / first_section['contratos_enviados'] < 0.5:
        summary_items.append({
            'type': 'alert',
            'label': 'Assinatura de contratos baixa',
            'value': f'{(first_section["contratos_assinados"] / first_section["contratos_enviados"] * 100) if first_section["contratos_enviados"] else 0:.0f}%',
            'delta': 'Pode ser necessário follow-up comercial.',
        })

    if summary_items:
        resumo_estrategico(summary_items)

elif secao == 'Forecasting':
    st.title('Forecasting')
    if evento != "Rio de Janeiro":
        section_header(
            'Carteira de expositores comissionados — cenário de receita, risco e otimização de parâmetros de negociação',
            'Seção Apenas Disponível Para Funil do Rio de Janeiro.'
        )
    else:
        section_header(
            'Carteira de expositores comissionados — cenário de receita, risco e otimização de parâmetros de negociação',
            'Visão Geral'
        )
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')
 
 
    if df_forecast.empty:
        st.info("Sem simulações salvas ainda. Execute o pipeline para gerar os dados de forecasting.")
        st.stop()
 
    st.markdown('###')
    col1, col2 = st.columns([2, 1])
    with col1:
        kpi_card(
            'Total de Ganho Real da Comissão - Valor Estimado',
            f'R$ {forecast_section['ganho_real_total']:,.0f}',
            f'Receita Total Real Por Expositor Avaliado Com Média R$ {forecast_section['ganho_real_medio']:,.0f}',
            'negative' if forecast_section['ganho_real_total'] < 0 else 'positive',
            'red' if forecast_section['ganho_real_total'] <0 else 'green',
        )
    with col2:
        kpi_card(
                'Percentual Comissões Que Valeram A Pena',
                f'{forecast_section['pct_valeu_a_pena']:,.2f}%',
                f'Para {forecast_section['count_valeu_a_pena']:,.0f} Comissões que Valeram A Pena',
                'neutral'
            )
 
    st.markdown('###')
 
    # ── 2. KPIs SECUNDÁRIOS ───────────────────────────────────────────────────
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        kpi_card(
            'Expositores Avaliados',
            f'{forecast_section["total_expositores"]:,}',
            f'Base da carteira de {forecast_section['total_expositores_base']:.0f} No Banco',
            'neutral',
            'purple',
        )
    with col4:
        kpi_card(
            'Piso Garantido',
            f'R$ {forecast_section["piso_total"]:,.0f}',
            'Soma dos mínimos garantidos — já está no bolso',
            'positive',
            'green',
        )
    with col5:
        kpi_card(
            'Upside Potencial',
            f'R$ {forecast_section["upside_total"]:,.0f}',
            'Acima do piso no cenário otimizado',
            'neutral',
            'amber',
        )
    with col6:
        kpi_card(
            'Probabilidade Média',
            f'{forecast_section["prob_media"]:.1f}%',
            (
                f'Média dos {forecast_section["total_expositores"]} expositores com dados suficientes para avaliação. '
                f'{forecast_section["total_expositores_base"] - forecast_section["total_expositores"]} '
                f'expositores sem dados de Trends.'
            ),
            'positive' if forecast_section["prob_media"] >= 60 else 'negative',
        )
 
    st.markdown('###')
    st.markdown('---')

    # ── Otimização de Parâmetros ─────────────────────────────────────────────────────

    section_header('Otimização de Parâmetros e Cenários Alternativos')

    col_nome, col_area, col_ticket = st.columns([2, 1, 1])

    with col_nome:
        sim_expositor = st.text_input(
            "Nome Fantasia",
            placeholder="Digite o nome do expositor...",
            key="sim_nome"
        )

    with col_area:
        sim_area = st.number_input(
            "Área (m²)",
            value=None,
            placeholder="0",
            key="sim_area"
        )

    with col_ticket:
        sim_ticket = st.number_input(
            "Ticket Médio (R$)",
            value=None,
            placeholder="0,00",
            format="%.2f",
            key="sim_ticket"
        )

    col_comissao, col_minimo = st.columns(2)

    with col_comissao:
        sim_comissao = st.number_input(
            "Comissão (%)",
            value=None,
            placeholder="0,00",
            format="%.2f",
            key="sim_comissao"
        )

    with col_minimo:
        sim_minimo = st.number_input(
            "Mínimo Garantido (R$)",
            value=None,
            placeholder="0,00",
            format="%.2f",
            key="sim_minimo"
        )


    _, col_btn = st.columns([5, 1])

    with col_btn:
        simular = st.button("🔄 Simular", type="primary", use_container_width=True)

    if simular:
        campos = {
            "Nome Fantasia": sim_expositor,
            "Área": sim_area,
            "Ticket Médio": sim_ticket,
            "Percentual Comissão": sim_comissao,
            "Mínimo Garantido": sim_minimo
        }

        erros = []
        for nome, valor in campos.items():
            if valor is None or valor == "":
                erros.append(nome)

        if erros:
            st.error(f"🚨 **Erro de validação:** Preencha os campos: {', '.join(erros)}")
            st.stop()

        st.markdown(
            """
            <style>
            /* spinner dentro do main content (fundo claro) */
            .main div[data-testid='stSpinner'] p {
                color: #1a1a1a !important;
            }

            /* sidebar mantém o padrão claro (fundo escuro) */
            section[data-testid='stSidebar'] div[data-testid='stSpinner'] p {
                color: #ffffff !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        with st.spinner("🚀 Processando dados e otimizando parâmetros..."):
            
            # Prepara os dados
            dados_simulacao = {
                "nome_fantasia": sim_expositor,
                "area": sim_area,
                "ticket_medio": sim_ticket,
                "pct_comissao": sim_comissao / 100,
                "minimo_garantido": sim_minimo
            }

            # Roda o processamento pesado
            df_resultado = rodar_etl_otimizacao(dados_simulacao)
            
            if df_resultado:
                # Salva no estado para persistir na tela
                st.session_state["sim_resultado"] = df_resultado
                st.toast("✅ Simulação concluída com sucesso!", icon="🎉")
            else:
                st.error("⚠️ Falha ao processar os dados da simulação.")

    # Exibição dos resultados (fora do bloco 'if simular' para não sumir ao interagir)
    if "sim_resultado" in st.session_state:
        resultado_dict = st.session_state["sim_resultado"]
        
        section_header("Resultado da Simulação")
        simulacao_card(resultado_dict)
        
        # Botão opcional para limpar a simulação
        if st.button("🗑️ Limpar Simulação", help="Remove os dados calculados da tela"):
            del st.session_state["sim_resultado"]
            st.rerun()

    st.markdown('---')
 
    # ── 3. SCATTER: prob × ganho ──────────────────────────────────────────────
    section_header('Mapa de Prioridades da Carteira')
   
    fig_scatter = scatter_prob_ganho(df_forecast)
    chart_card('Probabilidade vs Ganho Real Médio', fig_scatter)
 
    st.markdown('###')
    st.markdown('---')
 
    # ── 4. WATERFALL + RANKING ────────────────────────────────────────────────
    section_header('Composição da Receita e Ranking de Expositores')
 
    col_wf, col_rank = st.columns(2)
    with col_wf:
        fig_wf = waterfall_piso_upside(forecast_section)
        chart_card('Piso Garantido → Upside → Receita Otimizada', fig_wf)
 
    with col_rank:
        fig_rank = bar_ranking_expositores(df_forecast, top_n=10)
        chart_card('Top 10 por Receita Otimizada', fig_rank)
 
    st.markdown('###')
    st.markdown('---')
 
    # ── 6. TABELA DETALHADA (drill-down) ──────────────────────────────────────
    COL_LABELS_FORECAST = {
        "nome_fantasia":          "Expositor",
        "porte":                  "Porte",
        "status_decisao":         "Status",
        "prob_vale_a_pena_pct":   "Prob. (%)",
        "ganho_real_medio":       "Ganho Médio",
        "minimo_garantido":       "Piso Garantido",
        "receita_estimada_media": "Receita Estimada",
        "receita_otimizada":      "Receita Otimizada",
        "volume_vendas":          "Volume Vendas",
    }
    
    COL_LABELS_PRIORIDADE = {
        "nome_fantasia":        "Expositor",
        "prob_vale_a_pena_pct": "Prob. (%)",
        "ganho_real_medio":     "Ganho Médio",
        "status_decisao":       "Status",
    }
    
    # ── Tabela Detalhada ──────────────────────────────────────────────────────────
    section_header('Tabela Detalhada por Expositor')
    
    opcoes = get_filter_options(df_forecast)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filtro_status = st.selectbox("Status", opcoes["status_opcoes"], key="fc_status")
    with col_f2:
        prob_min = st.slider("Prob. mínima (%)", opcoes["prob_min"], opcoes["prob_max"], opcoes["prob_min"], key="fc_prob")
    with col_f3:
        ordenar_por = st.selectbox("Ordenar por", opcoes["colunas_ordenacao"], key="fc_order")
    
    df_filtrado = aplicar_filtros_forecast(df_forecast, filtro_status, prob_min, ordenar_por)
    table_card(get_tabela_forecast(df_filtrado), col_labels=COL_LABELS_FORECAST)
    
    # ── Prioridades da Gestão ─────────────────────────────────────────────────────
    st.markdown('###')
    section_header('Prioridades da Gestão')
    
    col_risco, col_opp = st.columns(2)
    with col_risco:
        priority_header("risco")
        table_card(get_tabela_riscos(df_forecast), col_labels=COL_LABELS_PRIORIDADE)
    
    with col_opp:
        priority_header("oportunidade")
        table_card(get_tabela_oportunidades(df_forecast), col_labels=COL_LABELS_PRIORIDADE)

    st.markdown('---')
 
    # ── 5. RESUMO ESTRATÉGICO ─────────────────────────────────────────────────
    section_header('Resumo Estratégico')
    items_resumo = []
 
    # 2. Expositores críticos (alto ganho + baixa prob)
    if forecast_section["qtde_criticos"] > 0:
        items_resumo.append({
            "type": "alert",
            "label": f"{forecast_section['qtde_criticos']} expositor(es) crítico(s): alto ganho, baixa probabilidade",
            "value": f"{forecast_section['qtde_criticos']} expositor(es)",
            "delta": "Merecem atenção comercial imediata — são os que mais impactam se não converterem.",
        })
 
    # 3. Probabilidade média da carteira
    prob = forecast_section["prob_media"]
    if prob >= 70:
        items_resumo.append({
            "type": "ok",
            "label": "Probabilidade média da carteira saudável",
            "value": f"{prob:.1f}%",
            "delta": "A maioria dos expositores tem boa chance de retorno.",
        })
    elif prob >= 50:
        items_resumo.append({
            "type": "warn",
            "label": "Probabilidade média moderada",
            "value": f"{prob:.1f}%",
            "delta": "Parte da carteira ainda está em zona de incerteza.",
        })
    else:
        items_resumo.append({
            "type": "alert",
            "label": "Probabilidade média baixa na carteira",
            "value": f"{prob:.1f}%",
            "delta": "A maioria dos expositores está abaixo de 50% de chance de valer a pena.",
        })
 
    # 4. Upside vs piso
    pct_upside = (forecast_section["upside_total"] / forecast_section["piso_total"] * 100) if forecast_section["piso_total"] > 0 else 0
    items_resumo.append({
        "type": "ok" if pct_upside > 30 else "warn",
        "label": "Upside potencial sobre o piso garantido",
        "value": f"{pct_upside:.1f}%",
        "delta": f"R$ {forecast_section['upside_total']:,.0f} acima do mínimo garantido no melhor cenário.",
    })
    if items_resumo:
        resumo_estrategico(items_resumo)
 