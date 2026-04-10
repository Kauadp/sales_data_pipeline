import sys
from pathlib import Path

# Garante que o diretório do projeto (pai) e a própria pasta `dash/`
# estejam no `sys.path` para que imports como `app.database` e
# `etl_runner`/`exagerado_theme` sejam resolvidos quando o
# script for executado via `streamlit run dash/dashboard.py`.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from app.database import get_database_url, load_data_from_db
from etl_runner import run_etl_and_sync
from exagerado_theme import (
    inject_theme,
    chart_card,
    kpi_card,
    resumo_estrategico,
    section_header,
    sidebar_logo,
)

st.set_page_config(
    page_title='Dashboard de Expositores',
    layout='wide',
    initial_sidebar_state='expanded',
)
inject_theme()


def area_soma_com_receita_realizada(df: pd.DataFrame) -> float:
    """Soma AREA nas linhas com receita realizada > 0 (venda contando na receita)."""
    if df.empty or 'AREA' not in df.columns or 'RECEITA REALIZADA' not in df.columns:
        return 0.0
    rec = pd.to_numeric(df['RECEITA REALIZADA'], errors='coerce').fillna(0)
    area = pd.to_numeric(df['AREA'], errors='coerce').fillna(0)
    return float(area[rec > 0].sum())


# =========================
# CARREGAR DADOS
# =========================
@st.cache_data
def carregar_dados_do_banco(db_url: str):
    return load_data_from_db(db_url)


def formatar_db_url():
    streamlit_secrets = None
    try:
        streamlit_secrets = st.secrets
    except Exception:
        streamlit_secrets = None

    try:
        return get_database_url(streamlit_secrets)
    except Exception:
        return get_database_url(None)


db_url_from_env = formatar_db_url()

df = pd.DataFrame()

db_url_to_use = db_url_from_env

# =========================
# FILTROS SIDEBAR
# =========================
with st.sidebar:
    st.image('img/favicon.ico', width=50)
    sidebar_logo()

    st.markdown('###')

    db_url_to_use = db_url_from_env

    atualizar_dados = st.button('🔄 Atualizar dados', type = "primary")
    if atualizar_dados:
        if not db_url_to_use:
            st.error('URL do banco não configurada. Verifique secrets.toml ou config.toml.')
        else:
            with st.spinner('Executando ETL e sincronizando com o PostgreSQL...'):
                try:
                    _, sync_result = run_etl_and_sync(db_url_to_use)
                    carregar_dados_do_banco.clear()
                    st.success(
                        f"✅ Dados atualizados: {sync_result['inserted']} inseridos, "
                        f"{sync_result['updated']} atualizados, {sync_result['skipped']} ignorados, "
                        f"{sync_result.get('removed', 0)} removidos do atual (nao estavam no lote)."
                    )
                except Exception as exc:
                    st.error(f'❌ Falha ao atualizar dados: {exc}')

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('### Seção do Dashboard')

    secao = st.radio(
        'Seção',
        ['Comercial', 'Receita', 'Descontos', 'Espaço', 'Previsão'],
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


if not db_url_to_use:
    st.warning('⚠️ URL do banco PostgreSQL não encontrada em secrets.toml, config.toml ou variáveis de ambiente.')
    st.stop()

try:
    df = carregar_dados_do_banco(db_url_to_use)
except Exception as exc:
    st.error(f'❌ Falha ao carregar dados do banco: {exc}')
    st.stop()

# Remove linhas sem dados úteis e normaliza as colunas de pipeline, tipo e snapshot.

valid_cols = []
if not df.empty:
    valid_cols = [c for c in ['NOME FANTASIA', 'AREA', 'RECEITA REALIZADA', 'RECEITA PREVISTA', 'STATUS'] if c in df.columns]
    if valid_cols:
        df = df.loc[df[valid_cols].notna().any(axis=1)].copy()

if 'PIPELINE' in df.columns:
    df['PIPELINE'] = df['PIPELINE'].astype(str).str.strip().str.upper()
if 'TIPO' in df.columns:
    df['TIPO'] = df['TIPO'].astype(str).str.strip().str.upper()

snapshot_col = next((c for c in df.columns if c.lower() == 'snapshot'), None)
if snapshot_col is not None:
    df[snapshot_col] = pd.to_datetime(df[snapshot_col], errors='coerce')
    # Ensure timestamps and comparison use the same timezone (UTC)
    # If series is tz-aware convert to UTC, otherwise localize to UTC.
    try:
        df[snapshot_col] = df[snapshot_col].dt.tz_convert('UTC')
    except Exception:
        try:
            df[snapshot_col] = df[snapshot_col].dt.tz_localize('UTC')
        except Exception:
            # leave as-is if neither works
            pass

if 'NOME FANTASIA' in df.columns:
    df['NOME FANTASIA'] = df['NOME FANTASIA'].astype(str).str.strip().str.upper()

if df.empty:
    df_raw = df.copy()
else:
    df_raw = df.copy()

meta_es_stand = 2500000
meta_es_food = 300000
meta_rj_stand = 1500000

meta_sp_stand = 0 # A definir

# =========================
# FILTRO DE DADOS
pipeline_map = {
    'Espírito Santo': 'ES',
    'Rio de Janeiro': 'RJ',
    'São Paulo': 'SP|SAO',
}

meta_map = {
    'Espírito Santo': {'STAND': meta_es_stand, 'FOOD': meta_es_food},
    'Rio de Janeiro': {'STAND': meta_rj_stand, 'FOOD': 0},
    'São Paulo': {'STAND': meta_sp_stand, 'FOOD': 0},
}

if evento == 'Todos eventos':
    meta = sum(event_meta.get(tipo_stand, 0) for event_meta in meta_map.values())
else:
    meta = meta_map.get(evento, {}).get(tipo_stand, 0)

if 'PIPELINE' in df.columns and evento != 'Todos eventos':
    pipeline_pattern = pipeline_map.get(evento)
    if pipeline_pattern:
        df = df[df['PIPELINE'].astype(str).str.contains(pipeline_pattern, case=False, na=False)]

if 'TIPO' in df.columns:
    df = df[df['TIPO'].astype(str).str.strip().str.upper() == tipo_stand]

if snapshot_col is not None and not df.empty:
    # use timezone-aware UTC timestamp for comparisons
    snapshot_today = pd.Timestamp.now(tz='UTC').normalize()
    if periodo == 'Hoje':
        # normalize preserves tz-aware, compare with snapshot_today (UTC)
        df = df[df[snapshot_col].dt.normalize() == snapshot_today]
    elif periodo == 'Semana':
        df = df[df[snapshot_col] >= (snapshot_today - pd.Timedelta(days=6))]
    elif periodo == 'Mês':
        df = df[df[snapshot_col] >= (snapshot_today - pd.Timedelta(days=29))]
    elif periodo == 'Total':
        pass

# =========================
# KPIs
# =========================
receita_realizada = df['RECEITA REALIZADA'].sum()
receita_prevista = df['RECEITA PREVISTA'].sum()
df_desconto = df[df["RECEITA REALIZADA"].notna()]

vendas_reais = df_desconto[
    (df_desconto['NOME FANTASIA'] != 'VACÂNCIA') & 
    (df_desconto['RECEITA REALIZADA'] > 0)
].copy()

vendas_reais['desconto'] = vendas_reais['RECEITA PREVISTA'] - vendas_reais['RECEITA REALIZADA']

vendas_com_desconto = vendas_reais[
    (vendas_reais['desconto'] > 0) & 
    (vendas_reais['desconto'] / vendas_reais['RECEITA PREVISTA'] < 1)
]

descontos_dados = vendas_com_desconto['desconto'].sum()

receita_faltante = meta - receita_realizada
percentual_faltante = (receita_faltante / meta) * 100 if meta > 0 else 0

qtde_expositores = (df['NOME FANTASIA'] != 'VACÂNCIA').sum()
vacancias = (df['NOME FANTASIA'] == 'VACÂNCIA').sum()

area_total = df['AREA'].sum()
area_preenchida = area_soma_com_receita_realizada(df)
prop_area_preenchida = (area_preenchida / area_total) * 100 if area_total > 0 else 0
area_disponivel = area_total - area_preenchida

receita_por_metro_quadrado = receita_realizada / area_preenchida if area_preenchida > 0 else 0
receita_potencial_vaga = area_disponivel * receita_por_metro_quadrado

contratos_enviados = df['CONTRATO ENVIADO'].sum()
contratos_assinados = df['CONTRATO ASSINADO'].sum()
to_dentro = df['TO DENTRO'].sum()
clientes_recorrentes = df['RECORRENTE'].sum()
clientes_novos = (df['RECORRENTE'] == False).sum()

media_receita_por_expositor = receita_realizada / qtde_expositores if qtde_expositores > 0 else 0
media_desconto_por_expositor = descontos_dados / qtde_expositores if qtde_expositores > 0 else 0

prop_desconto_medio = (
    (vendas_com_desconto['desconto'] / vendas_com_desconto['RECEITA PREVISTA'])
).mean() if len(vendas_com_desconto) > 0 else 0

preco_necessario_m2 = receita_faltante / area_disponivel if area_disponivel > 0 else 0
receita_projetada = receita_realizada + (area_disponivel * receita_por_metro_quadrado)
bate_meta = receita_projetada >= meta


def build_temporal_chart(df, secao, snapshot_col, meta):
    if snapshot_col is None or df.empty:
        return None

    df = df.copy()
    # create a timezone-naive normalized date for plotting
    tmp_ts = df[snapshot_col]
    try:
        tmp_ts = tmp_ts.dt.tz_convert('UTC')
    except Exception:
        try:
            tmp_ts = tmp_ts.dt.tz_localize('UTC')
        except Exception:
            pass
    df['snapshot_date'] = tmp_ts.dt.normalize()
    try:
        df['snapshot_date'] = df['snapshot_date'].dt.tz_localize(None)
    except Exception:
        # already naive
        pass
    df = df[df['snapshot_date'].notna()]
    if df.empty:
        return None

    if secao == 'Comercial':
        plot_df = pd.concat([
            df[df['NOME FANTASIA'] != 'VACÂNCIA'].groupby('snapshot_date').size().rename('Expositores'),
            df[df['NOME FANTASIA'] == 'VACÂNCIA'].groupby('snapshot_date').size().rename('Vacâncias'),
            df.groupby('snapshot_date')['TO DENTRO'].sum().rename('To Dentro'),
            df.groupby('snapshot_date')['CONTRATO ENVIADO'].sum().rename('Contratos Enviados'),
            df.groupby('snapshot_date')['CONTRATO ASSINADO'].sum().rename('Contratos Assinados'),
        ], axis=1).fillna(0).reset_index()
        plot_df = plot_df.melt(id_vars='snapshot_date', var_name='Métrica', value_name='Valor')

    elif secao == 'Receita':
        plot_df = (
            df.groupby('snapshot_date')[['RECEITA REALIZADA', 'RECEITA PREVISTA']]
            .sum()
            .reset_index()
            .melt(id_vars='snapshot_date', var_name='Métrica', value_name='Valor')
        )

    elif secao == 'Descontos':
        rows = []
        for date, group in df.groupby('snapshot_date'):
            total = (group['RECEITA PREVISTA'] - group['RECEITA REALIZADA']).sum()
            avg_pct = (
                ((group['RECEITA PREVISTA'] - group['RECEITA REALIZADA']) / group['RECEITA PREVISTA'])
                .replace([np.inf, -np.inf], np.nan)
                .mean()
            ) * 100
            rows.append({'snapshot_date': date, 'Desconto Total': total, 'Desconto Médio %': avg_pct})
        plot_df = pd.DataFrame(rows)
        if plot_df.empty:
            return None
        plot_df = plot_df.melt(id_vars='snapshot_date', var_name='Métrica', value_name='Valor')

    elif secao == 'Espaço':
        rows = []
        for date, group in df.groupby('snapshot_date'):
            area_total = group['AREA'].sum()
            area_preenchida = area_soma_com_receita_realizada(group)
            area_disponivel = area_total - area_preenchida
            rows.append({'snapshot_date': date, 'Área Preenchida': area_preenchida, 'Área Disponível': area_disponivel})
        plot_df = pd.DataFrame(rows)
        if plot_df.empty:
            return None
        plot_df = plot_df.melt(id_vars='snapshot_date', var_name='Métrica', value_name='Valor')

    elif secao == 'Previsão':
        rows = []
        for date, group in df.groupby('snapshot_date'):
            receita_real = group['RECEITA REALIZADA'].sum()
            area_preenchida = area_soma_com_receita_realizada(group)
            receita_por_m2 = receita_real / area_preenchida if area_preenchida > 0 else 0
            area_total = group['AREA'].sum()
            area_disponivel = area_total - area_preenchida
            receita_projetada = receita_real + (area_disponivel * receita_por_m2)
            gap = max(meta - receita_real, 0)
            rows.append({'snapshot_date': date, 'Receita Projetada': receita_projetada, 'Gap para Meta': gap})
        plot_df = pd.DataFrame(rows)
        if plot_df.empty:
            return None
        plot_df = plot_df.melt(id_vars='snapshot_date', var_name='Métrica', value_name='Valor')

    else:
        return None

    fig = px.line(
        plot_df,
        x='snapshot_date',
        y='Valor',
        color='Métrica',
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Valor',
        legend=dict(orientation='h', y=-0.2),
        margin=dict(t=40, b=40, l=40, r=40),
    )
    fig.update_xaxes(tickformat='%d/%m/%Y', ticklabelmode='period')
    fig.update_traces(mode='lines+markers')
    return fig


def render_temporal_card(df, secao, snapshot_col, meta, periodo):
    if periodo == 'Hoje':
        return
    fig_temporal = build_temporal_chart(df, secao, snapshot_col, meta)
    if fig_temporal is not None:
        chart_card('Desempenho Temporal', fig_temporal)

# =========================
# TÍTULO
# =========================

st.title('Dashboard de Expositores')

if secao == 'Comercial':
    st.title('Comercial')
    section_header('Expositores, vacâncias, contratos e conversão', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        kpi_card('Expositores', f'{qtde_expositores:,}', 'Total de expositores', 'neutral', 'purple')
    with col2:
        kpi_card('Vacâncias', f'{vacancias:,}', 'Espaços livres', 'negative')
    with col3:
        kpi_card('To Dentro', f'{to_dentro:,}', 'Confirmados', 'positive', 'green')
    with col4:
        kpi_card('Contratos Enviados', f'{contratos_enviados:,}', 'Pipeline ativo', 'neutral')
    with col5:
        kpi_card('Contratos Assinados', f'{contratos_assinados:,}', 'Fechamento contratado', 'positive', 'green')

        st.markdown("<br>", unsafe_allow_html=True)

    col_chart, col_gauge = st.columns([2, 1])

    with col_chart:
        df_recorrentes = pd.DataFrame({
            'Tipo': ['Recorrente', 'Novo'],
            'Quantidade': [clientes_recorrentes, clientes_novos]
        })

        fig_pie = px.pie(
            df_recorrentes,
            names='Tipo',
            values='Quantidade',
            hole=0.45,
        )
        fig_pie.update_traces(marker_colors=['#6B3FA0', '#9B6FCC'], textinfo='percent+label')
        fig_pie.update_layout(
            legend=dict(orientation='h', y=-0.2),
        )

        chart_card('Clientes Recorrentes vs Novos', fig_pie)

    with col_gauge:
        df_contratos = pd.DataFrame({
            'Status': ['Enviados', 'Assinados'],
            'Quantidade': [contratos_enviados, contratos_assinados]
        })

        fig_bar = px.bar(
            df_contratos,
            x='Status',
            y='Quantidade',
            text='Quantidade',
        )
        fig_bar.update_traces(marker_color='#6B3FA0')

        chart_card('Contratos Enviados vs Assinados', fig_bar)

    render_temporal_card(df, secao, snapshot_col, meta, periodo)

elif secao == 'Receita':
    st.title('Receita')
    section_header('Receita realizada, gap para meta e principais expositores', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card('Receita Realizada', f'R$ {receita_realizada:,.0f}', 'Valor realizado', 'positive', 'purple')
    with col2:
        kpi_card('Meta', f'R$ {meta:,.0f}', 'Meta geral', 'neutral')
    with col3:
        kpi_card('Receita Faltante', f'R$ {receita_faltante:,.0f}', 'Gap para meta', 'negative', 'red')
    with col4:
        kpi_card('% Faltante', f'{percentual_faltante:.2f}%', 'Do total', 'negative', 'red')

    st.markdown('<br>', unsafe_allow_html=True)

    top3 = (
        df[df['NOME FANTASIA'] != 'VACÂNCIA']
        .sort_values(by='RECEITA REALIZADA', ascending=False)
        .head(3)
    )

    col_left, col_right = st.columns([2, 1])

    with col_left:
        fig_top3 = px.bar(
            top3,
            x='NOME FANTASIA',
            y='RECEITA REALIZADA',
            text='RECEITA REALIZADA',
        )
        fig_top3.update_traces(marker_color='#6B3FA0')
        fig_top3.update_layout(
            xaxis_title='',
            yaxis_title='Receita',
        )
        chart_card('Top 3 Expositores por Receita Realizada', fig_top3)

    with col_right:
        df_receita = pd.DataFrame({
            'Tipo': ['Prevista', 'Realizada'],
            'Valor': [receita_prevista, receita_realizada]
        })
        fig_receita = px.bar(
            df_receita,
            x='Tipo',
            y='Valor',
            text='Valor',
        )
        fig_receita.update_traces(marker_color=['#6B3FA0', '#9B6FCC'])
        fig_receita.update_layout(
            xaxis_title='',
            yaxis_title='Valor',
        )
        chart_card('Receita Prevista vs Realizada', fig_receita)

    render_temporal_card(df, secao, snapshot_col, meta, periodo)

elif secao == 'Descontos':
    st.title('Descontos')
    section_header('Descontos concedidos, média e impacto', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card('Descontos Dados', f'R$ {descontos_dados:,.0f}', 'Total concedido', 'negative', 'purple')
    with col2:
        kpi_card('Desconto Médio', f'R$ {media_desconto_por_expositor:,.0f}', 'Por expositor', 'neutral')
    with col3:
        kpi_card('% Desconto Médio', f'{prop_desconto_medio*100:.2f}%', 'Média geral', 'negative', 'red')

    render_temporal_card(df, secao, snapshot_col, meta, periodo)

elif secao == 'Espaço':
    st.title('Espaço')
    section_header('Área ocupada, disponível e receita por metro quadrado', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card('Área Total', f'{area_total:,.0f} m²', 'Capacidade total', 'neutral', 'purple')
    with col2:
        kpi_card(
            'Área Preenchida',
            f'{area_preenchida:,.0f} m²',
            'Soma m² onde há receita realizada',
            'positive',
            'green',
        )
    with col3:
        kpi_card('Taxa Ocupação', f'{prop_area_preenchida:.2f}%', 'Ocupação atual', 'positive' if prop_area_preenchida >= 70 else 'negative')
    with col4:
        kpi_card('Receita por m²', f'R$ {receita_por_metro_quadrado:,.0f}', 'Ticket médio', 'neutral')

    col5, col6 = st.columns(2)
    with col5:
        kpi_card('Área Disponível', f'{area_disponivel:,.0f} m²', 'Espaço livre', 'negative', 'red')
    with col6:
        kpi_card('Receita Potencial Vaga', f'R$ {receita_potencial_vaga:,.0f}', 'Potencial adicional', 'neutral', 'amber')

    st.write('')
    st.write('')

    df_area = pd.DataFrame({
        'Tipo': ['Ocupada', 'Disponível'],
        'Área': [area_preenchida, area_disponivel]
    })

    col_left, col_right = st.columns(2)

    with col_left:
        fig_area = px.pie(
            df_area,
            names='Tipo',
            values='Área',
            hole=0.4,
        )
        fig_area.update_traces(marker_colors=['#6B3FA0', '#9B6FCC'], textinfo='percent+label')
        chart_card('Área Ocupada vs Disponível', fig_area)

    with col_right:
        df_plot = df[df['NOME FANTASIA'] != 'VACÂNCIA']
        fig_scatter = px.scatter(
            df_plot,
            x='AREA',
            y='RECEITA REALIZADA',
            hover_name='NOME FANTASIA',
        )
        fig_scatter.update_traces(marker_color='#6B3FA0')
        fig_scatter.update_layout(
            xaxis_title='Área',
            yaxis_title='Receita',
        )
        chart_card('Receita vs Área', fig_scatter)

    render_temporal_card(df, secao, snapshot_col, meta, periodo)

elif secao == 'Previsão':
    st.title('Previsão')
    section_header('Projeções de receita e metas', 'Visão Geral')
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0">', unsafe_allow_html=True)
    st.markdown('###')

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card('Receita Projetada', f'R$ {receita_projetada:,.0f}', 'Cenário atual', 'neutral', 'purple')
    with col2:
        kpi_card('Preço Necessário por m²', f'R$ {preco_necessario_m2:,.0f}', 'Valor necessário', 'negative' if preco_necessario_m2 > receita_por_metro_quadrado else 'positive')
    with col3:
        kpi_card('Meta', 'Atinge' if bate_meta else 'Não Atinge', 'Projeção', 'positive' if bate_meta else 'negative', 'green' if bate_meta else 'red')

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('###')
    st.markdown('---')

    render_temporal_card(df, secao, snapshot_col, meta, periodo)

    section_header('Resumo Estratégico')

    summary_items = []
    if receita_por_metro_quadrado < preco_necessario_m2:
        summary_items.append({
            'type': 'warn',
            'label': 'Preço médio por m² abaixo do necessário',
            'value': f'R$ {receita_por_metro_quadrado:,.0f}',
            'delta': 'Será necessário vender os espaços restantes por um valor maior.',
        })
    if prop_desconto_medio > 0.15:
        summary_items.append({
            'type': 'warn',
            'label': 'Desconto médio elevado',
            'value': f'{prop_desconto_medio*100:.2f}%',
            'delta': 'O desconto pode estar reduzindo a receita total.',
        })
    if prop_area_preenchida < 70:
        summary_items.append({
            'type': 'ok',
            'label': 'Área disponível ainda positiva',
            'value': f'{prop_area_preenchida:.2f}%',
            'delta': 'Focar em ocupação pode aumentar a receita.',
        })
    if contratos_assinados / contratos_enviados < 0.5:
        summary_items.append({
            'type': 'alert',
            'label': 'Assinatura de contratos baixa',
            'value': f'{(contratos_assinados / contratos_enviados * 100) if contratos_enviados else 0:.0f}%',
            'delta': 'Pode ser necessário follow-up comercial.',
        })

    if summary_items:
        resumo_estrategico(summary_items)
