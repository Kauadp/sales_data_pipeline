import pandas as pd
import numpy as np
import plotly.express as px
from exagerado_theme import chart_card

### GRÁFICO TEMPORAL ####

def build_temporal_chart(df, secao, meta):
    if df.empty or "snapshot" not in df.columns:
        return None

    df = df.copy()
    df["snapshot_date"] = pd.to_datetime(df["snapshot"], utc=True).dt.normalize().dt.tz_localize(None)
    df = df[df["snapshot_date"].notna()]
    if df.empty:
        return None

    configs = {
        "Comercial": lambda g: {
            "Expositores": (g["nome_fantasia"] != "VACÂNCIA").sum(),
            "Vacâncias": (g["nome_fantasia"] == "VACÂNCIA").sum(),
            "To Dentro": g["to_dentro"].sum(),
            "Contratos Enviados": g["contrato_enviado"].sum(),
            "Contratos Assinados": g["contrato_assinado"].sum(),
        },
        "Receita": lambda g: {
            "Receita Realizada": g.loc[g["contrato_assinado"], "receita_realizada"].sum(),
            "Receita Prevista": g["receita_prevista"].sum(),
        },
        "Descontos": lambda g: {
            "Desconto Total": (g["receita_prevista"] - g["receita_realizada"]).sum(),
            "Desconto Médio %": ((g["receita_prevista"] - g["receita_realizada"]) / g["receita_prevista"].replace(0, np.nan)).mean() * 100,
        },
        "Espaço": lambda g: {
            "Área Preenchida": g.loc[g["contrato_assinado"] & (g["receita_realizada"] > 0), "area"].sum(),
            "Área Disponível": g["area"].sum() - g.loc[g["contrato_assinado"] & (g["receita_realizada"] > 0), "area"].sum(),
        },
        "Previsão": lambda g: {
            "Receita Projetada": (lambda rec, a_p, a_t: rec + (a_t - a_p) * (rec / a_p if a_p > 0 else 0))(
                g.loc[g["contrato_assinado"], "receita_realizada"].sum(),
                g.loc[g["contrato_assinado"] & (g["receita_realizada"] > 0), "area"].sum(),
                g["area"].sum(),
            ),
            "Gap para Meta": max(meta - g.loc[g["contrato_assinado"], "receita_realizada"].sum(), 0),
        },
    }

    fn = configs.get(secao)
    if fn is None:
        return None

    rows = [{"snapshot_date": date, **fn(group)} for date, group in df.groupby("snapshot_date")]
    if not rows:
        return None

    plot_df = pd.DataFrame(rows).melt(id_vars="snapshot_date", var_name="Métrica", value_name="Valor")

    fig = px.line(
        plot_df,
        x="snapshot_date",
        y="Valor",
        color="Métrica",
        markers=True,
        color_discrete_sequence=["#6B3FA0", "#9B6FCC", "#C49BE8", "#E040FB", "#F48FB1"],
    )
    fig.update_layout(xaxis_title="Data", yaxis_title="Valor", legend=dict(orientation="h", y=-0.2))
    fig.update_xaxes(tickformat="%d/%m/%Y")
    return fig


def render_temporal_card(df, secao, meta, periodo):
    if periodo == "Hoje":
        return
    fig = build_temporal_chart(df, secao, meta)
    if fig:
        chart_card("Desempenho Temporal", fig)

####### KPIS E GRÁFICOS PRIMEIRA SEÇÃO ######

def kpis_first_section(df: pd.DataFrame):
    qtde_expositores = (df['nome_fantasia'] != 'VACÂNCIA').sum()
    vacancias = (df['nome_fantasia'] == 'VACÂNCIA').sum()
    to_dentro = df['to_dentro'].sum()
    contratos_enviados = df['contrato_enviado'].sum()
    contratos_assinados = df['contrato_assinado'].sum()

    return {
        'qtde_expositores': qtde_expositores,
        'vacancias': vacancias,
        'to_dentro': to_dentro,
        'contratos_enviados': contratos_enviados,
        'contratos_assinados': contratos_assinados
    }

def pie_chart_novos_recorrentes(df: pd.DataFrame):
    clientes_recorrentes = df['recorrente'].sum()
    qtde_expositores = (df['nome_fantasia'] != 'VACÂNCIA').sum()
    clientes_novos = qtde_expositores - clientes_recorrentes

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
    return fig_pie

def bar_chart_enviados_assinados(df: pd.DataFrame):
    contratos_enviados = df['contrato_enviado'].sum()
    contratos_assinados = df['contrato_assinado'].sum()

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

    return fig_bar


####### KPIS E GRÁFICOS SEGUNDA SEÇÃO ######


def kpis_second_section(df: pd.DataFrame, meta: int):
    df_assinados = df[df["contrato_assinado"] == True]

    receita_realizada = df_assinados['receita_realizada'].sum()
    receita_faltante = meta - receita_realizada
    percentual_faltante = (receita_faltante / meta) * 100 if meta > 0 else 0

    return {
        'receita_realizada': receita_realizada,
        'receita_faltante': receita_faltante,
        'percentual_faltante': percentual_faltante
    }

def top3_chart(df: pd.DataFrame):
    df_assinados = df[df["contrato_assinado"] == True]
    top3 = (
        df_assinados[df_assinados['nome_fantasia'] != 'VACÂNCIA']
        .sort_values(by='receita_realizada', ascending=False)
        .head(3)
    )
    fig_top3 = px.bar(
            top3,
            x='nome_fantasia',
            y='receita_realizada',
            text='receita_realizada',
        )
    fig_top3.update_traces(marker_color='#6B3FA0')
    fig_top3.update_layout(
        xaxis_title='',
        yaxis_title='Receita',
    )
    return fig_top3

def chart_receita_prevista_realizada(df: pd.DataFrame):
    df_assinados = df[df["contrato_assinado"] == True]
    receita_realizada = df_assinados['receita_realizada'].sum()
    receita_prevista = df['receita_prevista'].sum()

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
    return fig_receita


####### KPIS E GRÁFICOS TERCEIRA SEÇÃO ######

def kpi_third_section(df: pd.DataFrame):
    df_desconto = df[
        (df['contrato_assinado'] == True) &
        (df['receita_realizada'] > 0) &
        (df['nome_fantasia'] != 'VACÂNCIA')
    ].copy()

    df_desconto['desconto'] = df_desconto['receita_prevista'] - df_desconto['receita_realizada']
    
    df_desconto = df_desconto[
        (df_desconto['desconto'] > 0) &
        (df_desconto['desconto'] / df_desconto['receita_prevista'] < 1)
    ]

    descontos = df_desconto['desconto'].sum()
    qtde_expositores = len(df_desconto)
    media_desconto_por_expositor = descontos / qtde_expositores if qtde_expositores > 0 else 0
    prop_desconto_medio = (df_desconto['desconto'] / df_desconto['receita_prevista']).mean() if qtde_expositores > 0 else 0

    return {
        'descontos': descontos,
        'media_desconto_por_expositor': media_desconto_por_expositor,
        'prop_desconto_medio': prop_desconto_medio,
    }


####### KPIS E GRÁFICOS QUARTA SEÇÃO ######


def kpi_fourth_section(df: pd.DataFrame):
    area_total = df['area'].sum()
    df_area = df[
        (df['contrato_assinado'] == True) &
        (df['receita_realizada'] > 0) &
        (df['nome_fantasia'] != 'VACÂNCIA')
    ].copy()
    area_preenchida = df_area['area'].sum()
    prop_area_preenchida = (area_preenchida / area_total) * 100 if area_total > 0 else 0
    area_disponivel = area_total - area_preenchida
    receita_realizada = df[df['contrato_assinado'] == True]['receita_realizada'].sum()
    receita_por_metro_quadrado = receita_realizada / area_preenchida if area_preenchida > 0 else 0
    receita_potencial_vaga = area_disponivel * receita_por_metro_quadrado

    return {
        'area_total': area_total,
        'area_preenchida': area_preenchida,
        'prop_area_preenchida': prop_area_preenchida,
        'area_disponivel': area_disponivel,
        'receita_por_metro_quadrado': receita_por_metro_quadrado,
        'receita_potencial_vaga': receita_potencial_vaga,
    }

def chart_area_disp_ocup(df: pd.DataFrame):
    area_total = df['area'].sum()
    df_area = df[
        (df['contrato_assinado'] == True) &
        (df['receita_realizada'] > 0) &
        (df['nome_fantasia'] != 'VACÂNCIA')
    ].copy()
    area_preenchida = df_area['area'].sum()
    area_disponivel = area_total - area_preenchida
    df_area = pd.DataFrame({
        'Tipo': ['Ocupada', 'Disponível'],
        'Área': [area_preenchida, area_disponivel]
    })
    fig_area = px.pie(
            df_area,
            names='Tipo',
            values='Área',
            hole=0.4,
        )
    fig_area.update_traces(marker_colors=['#6B3FA0', '#9B6FCC'], textinfo='percent+label')

    return fig_area

def chart_receita_area(df: pd.DataFrame):
    df_plot = df[df['nome_fantasia'] != 'VACÂNCIA']
    fig_scatter = px.scatter(
        df_plot,
        x='area',
        y='receita_realizada',
        hover_name='nome_fantasia',
    )
    fig_scatter.update_traces(marker_color='#6B3FA0')
    fig_scatter.update_layout(
        xaxis_title='Área',
        yaxis_title='Receita',
    )
    
    return fig_scatter


####### KPIS E GRÁFICOS QUINTA SEÇÃO ######


def kpi_fifth_section(df: pd.DataFrame):
    # Kpis de Fato
    df_comissionados = df[df['percentual_comissao'] > 0]
    qtde_expositores_comissionados = len(df_comissionados)
    area_total_comissionados = df_comissionados['area'].sum()
    media_area_por_expositor_comissionado = area_total_comissionados / qtde_expositores_comissionados if qtde_expositores_comissionados > 0 else 0
    df_comissionados_assinado = df_comissionados[df_comissionados['contrato_assinado'] == True]
    receita_realizada_comissionados = df_comissionados_assinado['receita_realizada'].sum()
    media_receita_por_expositor_comissionado = receita_realizada_comissionados / qtde_expositores_comissionados if qtde_expositores_comissionados > 0 else 0
    media_percentual_comissao = df_comissionados['percentual_comissao'].mean() * 100
    # Kpis para Resumo Geral
    qtde_expositores = (df['nome_fantasia'] != 'VACÂNCIA').sum()
    pct_clientes_comissionados = qtde_expositores_comissionados / qtde_expositores if qtde_expositores > 0 else 0
    df_area = df[
        (df['contrato_assinado'] == True) &
        (df['receita_realizada'] > 0) &
        (df['nome_fantasia'] != 'VACÂNCIA')
    ].copy()
    area_preenchida = df_area['area'].sum()
    pct_area_comissionada_sobre_preenchida = area_total_comissionados / area_preenchida if area_preenchida > 0 else 0
    df_assinados = df[df["contrato_assinado"] == True]
    receita_realizada = df_assinados['receita_realizada'].sum()
    pct_receita_comissionada_sobre_total = receita_realizada_comissionados / receita_realizada if receita_realizada > 0 else 0
    media_receita_comissionada = df_comissionados['receita_realizada'].mean()
    media_receita_geral = df_assinados['receita_realizada'].mean()
    pct_media_receita_comissionado_vs_geral = media_receita_comissionada / media_receita_geral if media_receita_geral > 0 else 0

    return {
        'qtde_expositores_comissionados': qtde_expositores_comissionados,
        'area_total_comissionados': area_total_comissionados,
        'media_area_por_expositor_comissionado': media_area_por_expositor_comissionado,
        'receita_realizada_comissionados': receita_realizada_comissionados,
        'media_receita_por_expositor_comissionado': media_receita_por_expositor_comissionado,
        'media_percentual_comissao': media_percentual_comissao,
        'pct_clientes_comissionados': pct_clientes_comissionados,
        'pct_area_comissionada_sobre_preenchida': pct_area_comissionada_sobre_preenchida,
        'pct_receita_comissionada_sobre_total': pct_receita_comissionada_sobre_total,
        'pct_media_receita_comissionado_vs_geral': pct_media_receita_comissionado_vs_geral
    }


####### KPIS E GRÁFICOS QUINTA SEÇÃO ######


def kpi_sixth_section(df: pd.DataFrame, meta: int):
    df_assinados = df[df["contrato_assinado"] == True]
    df_area = df[
        (df['contrato_assinado'] == True) &
        (df['receita_realizada'] > 0) &
        (df['nome_fantasia'] != 'VACÂNCIA')
    ].copy()
    area_preenchida = df_area['area'].sum()
    area_total = df['area'].sum()
    prop_area_preenchida = (area_preenchida / area_total) * 100 if area_total > 0 else 0
    area_disponivel = area_total - area_preenchida
    receita_realizada = df_assinados['receita_realizada'].sum()
    receita_por_metro_quadrado = receita_realizada / area_preenchida if area_preenchida > 0 else 0
    receita_projetada = receita_realizada + (area_disponivel * receita_por_metro_quadrado)
    preco_necessario_m2 = (meta - receita_realizada) / area_disponivel if area_disponivel > 0 else 0
    bate_meta = receita_projetada >= meta

    return {
        'receita_projetada': receita_projetada,
        'preco_necessario_m2': preco_necessario_m2,
        'bate_meta': bate_meta
    }