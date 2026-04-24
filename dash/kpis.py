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


####### KPIS E GRÁFICOS FORECASTING ######

import plotly.graph_objects as go
 
 
def kpi_forecast_section(df: pd.DataFrame):
    """
    KPIs executivos do forecasting.
    Retorna dict com todos os valores necessários para o dashboard.
    """

    total_expositores = len(df[df["modelo_origem"] != "SEM DADOS TRENDS"])
 
    # Receita base (piso garantido, independe de comissão)
    piso_total = df["minimo_garantido"].sum()
 
    # Receita esperada no cenário base (mediana da simulação MC)
    receita_estimada_total = df["receita_estimada_media"].sum()
 
    # Receita no cenário otimizado
    receita_otimizada_total = df["receita_otimizada"].sum()
 
    # Upside: quanto ainda está "em jogo" acima do piso
    upside_total = receita_otimizada_total - piso_total
 
    # Probabilidade média da carteira
    prob_media = (df[df["modelo_origem"] != "SEM DADOS TRENDS"]["prob_vale_a_pena_pct"]).mean()

    # Ganho Real Médio

    ganho_real_medio = df['ganho_real_medio'].mean()
    ganho_real_total = df['ganho_real_medio'].sum()
 
    # Percentual quantos valeram a pena
    total_expositores_base = len(df)

    count_valeu_a_pena = (df["status_decisao"] != "Comissão Não Vale A Pena").sum()

    pct_valeu_a_pena = (count_valeu_a_pena / total_expositores_base) * 100 if total_expositores_base > 0 else 0

    # Distribuição de status
    status_counts = (df[df["modelo_origem"] != "SEM DADOS TRENDS"]["status_decisao"]).value_counts().to_dict()
 
    # Expositores críticos: alta influência + baixa probabilidade
    # "Alta influência" = ganho_real_medio acima da mediana
    mediana_ganho = (df[df["modelo_origem"] != "SEM DADOS TRENDS"])["ganho_real_medio"].median()
    criticos = (df[df["modelo_origem"] != "SEM DADOS TRENDS"])[
        ((df[df["modelo_origem"] != "SEM DADOS TRENDS"])["ganho_real_medio"] > mediana_ganho) &
        ((df[df["modelo_origem"] != "SEM DADOS TRENDS"])["prob_vale_a_pena_pct"] < 50)
    ]
    qtde_criticos = len(criticos)
    
    meta_comissao = df["meta_total"].sum()

    
    return {
        "total_expositores": total_expositores,
        "piso_total": piso_total,
        "receita_estimada_total": receita_estimada_total,
        "receita_otimizada_total": receita_otimizada_total,
        "upside_total": upside_total,
        "prob_media": prob_media,
        "ganho_real_medio": ganho_real_medio,
        "ganho_real_total": ganho_real_total,
        "count_valeu_a_pena": count_valeu_a_pena,
        "pct_valeu_a_pena": pct_valeu_a_pena,
        "total_expositores_base": total_expositores_base,
        "status_counts": status_counts,
        "qtde_criticos": qtde_criticos,
        "meta_comissao": meta_comissao
    }
 
 
def scatter_prob_ganho(df: pd.DataFrame):
    """
    Scatter: Probabilidade de valer a pena (x) vs Ganho Real Médio (y).
    Quadrantes definem prioridades comerciais.
    """
    df = df.copy()
 
    mediana_prob = df["prob_vale_a_pena_pct"].median()
    mediana_ganho = df["ganho_real_medio"].median()
 
    # Cor por quadrante
    def quadrante(row):
        alta_prob = row["prob_vale_a_pena_pct"] >= mediana_prob
        alto_ganho = row["ganho_real_medio"] >= mediana_ganho
        if alta_prob and alto_ganho:
            return "Prioridade Máxima"
        elif not alta_prob and alto_ganho:
            return "Risco Alto"
        elif alta_prob and not alto_ganho:
            return "Seguro / Pequeno"
        else:
            return "Reconsiderar"
 
    df["quadrante"] = df.apply(quadrante, axis=1)
 
    color_map = {
        "Prioridade Máxima": "#6B3FA0",
        "Risco Alto": "#E040FB",
        "Seguro / Pequeno": "#9B6FCC",
        "Reconsiderar": "#555566",
    }
 
    fig = px.scatter(
        df,
        x="prob_vale_a_pena_pct",
        y="ganho_real_medio",
        color="quadrante",
        hover_name="nome_fantasia",
        hover_data={"status_decisao": True, "prob_vale_a_pena_pct": ":.1f", "ganho_real_medio": ":,.0f"},
        color_discrete_map=color_map,
        labels={
            "prob_vale_a_pena_pct": "Probabilidade (%)",
            "ganho_real_medio": "Ganho Real Médio (R$)",
            "quadrante": "Quadrante",
        },
    )
 
    # Linhas de medianas (divisores de quadrante)
    fig.add_vline(x=mediana_prob, line_dash="dash", line_color="rgba(255,255,255,0.2)", line_width=1)
    fig.add_hline(y=mediana_ganho, line_dash="dash", line_color="rgba(255,255,255,0.2)", line_width=1)
 
    fig.update_traces(marker=dict(size=10, opacity=0.85))
    fig.update_layout(
        legend=dict(orientation="h", y=-0.2),
        xaxis_title="Probabilidade de Valer a Pena (%)",
        yaxis_title="Ganho Real Médio (R$)",
    )
    return fig
 
 
def bar_ranking_expositores(df: pd.DataFrame, top_n: int = 10):
    """
    Bar chart horizontal: top N expositores por receita otimizada,
    com cor indicando o status da decisão.
    """
    df_top = (
        df.sort_values("receita_otimizada", ascending=False)
        .head(top_n)
        .copy()
    )
    # Ordena para o bar horizontal ficar crescente (maior no topo)
    df_top = df_top.sort_values("receita_otimizada", ascending=True)
 
    color_map = {
        "APROVADO": "#6B3FA0",
        "EM ANÁLISE": "#E040FB",
        "REPROVADO": "#555566",
    }
 
    # Fallback: usa status como está no campo
    colors = [
        color_map.get(str(s).upper(), "#9B6FCC")
        for s in df_top["status_decisao"]
    ]
 
    fig = go.Figure(go.Bar(
        x=df_top["receita_otimizada"],
        y=df_top["nome_fantasia"],
        orientation="h",
        marker_color=colors,
        text=df_top["receita_otimizada"].apply(lambda v: f"R$ {v:,.0f}"),
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Receita Otimizada: R$ %{x:,.0f}<br>"
            "<extra></extra>"
        ),
    ))
 
    fig.update_layout(
        xaxis_title="Receita Otimizada (R$)",
        yaxis_title="",
        margin=dict(l=10, r=60),
    )
    return fig
 
 
def waterfall_piso_upside(kpis: dict):
    """
    Waterfall: piso garantido → + upside → receita estimada.
    Mostra visivelmente o que já está no bolso e o que ainda depende de performance.
    """
    piso = kpis["piso_total"]
    upside = kpis["upside_total"]
    meta = kpis["meta_comissao"]
    estimada = kpis["receita_estimada_total"]
 
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "total"],
        x=["Piso Garantido", "Upside Potencial", "Receita Estimada"],
        y=[piso, upside, estimada],
        text=[f"R$ {piso:,.0f}", f"+ R$ {upside:,.0f}", f"R$ {estimada:,.0f}"],
        textposition="outside",
        connector={"line": {"color": "rgba(255,255,255,0.15)"}},
        increasing={"marker": {"color": "#6B3FA0"}},
        totals={"marker": {"color": "#9B6FCC"}},
        decreasing={"marker": {"color": "#E040FB"}},
    ))
 
    # Linha da meta
    fig.add_hline(
        y=meta,
        line_dash="dot",
        line_color="#F48FB1",
        line_width=2,
        annotation_text=f"Meta: R$ {meta:,.0f}",
        annotation_position="top right",
        annotation_font_color="#F48FB1",
    )
 
    fig.update_layout(
        showlegend=False,
        yaxis_title="Receita (R$)",
    )
    return fig
 
def get_filter_options(df: pd.DataFrame) -> dict:
    status_opcoes = ["Todos"] + sorted(
        df["status_decisao"].dropna().unique().tolist()
    )
    prob_min = float(df["prob_vale_a_pena_pct"].min())
    prob_max = float(df["prob_vale_a_pena_pct"].max())

    # Garante que min < max mesmo quando todos os valores são iguais
    if prob_min >= prob_max:
        prob_min = 0.0
        prob_max = 100.0

    colunas_ordenacao = [
        "receita_otimizada",
        "prob_vale_a_pena_pct",
        "ganho_real_medio",
        "minimo_garantido",
    ]

    return {
        "status_opcoes": status_opcoes,
        "prob_min": prob_min,
        "prob_max": prob_max,
        "colunas_ordenacao": colunas_ordenacao,
    }
 
 
def aplicar_filtros_forecast(
    df: pd.DataFrame,
    filtro_status: str,
    prob_min: float,
    ordenar_por: str,
) -> pd.DataFrame:
    """
    Aplica os filtros da seção Forecasting e retorna o df filtrado e ordenado.
    """
    df = df.copy()
 
    if filtro_status != "Todos":
        df = df[df["status_decisao"] == filtro_status]
 
    df = df[df["prob_vale_a_pena_pct"] >= prob_min]
    df = df.sort_values(ordenar_por, ascending=False)
 
    return df
 
 
def get_tabela_forecast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Seleciona e ordena as colunas para exibição na tabela detalhada.
    """
    colunas = [
        "nome_fantasia",
        "porte",
        "status_decisao",
        "prob_vale_a_pena_pct",
        "ganho_real_medio",
        "minimo_garantido",
        "receita_estimada_media",
        "receita_otimizada",
        "volume_vendas",
    ]
    return df[[c for c in colunas if c in df.columns]]
 
 
def get_tabela_riscos(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Retorna os expositores com maior risco:
    ganho acima da mediana + menor probabilidade.
    """
    mediana_ganho = df["ganho_real_medio"].median()
    colunas = ["nome_fantasia", "prob_vale_a_pena_pct", "ganho_real_medio", "status_decisao"]
 
    return (
        df[df["ganho_real_medio"] > mediana_ganho]
        .sort_values("prob_vale_a_pena_pct", ascending=True)
        .head(top_n)
        [[c for c in colunas if c in df.columns]]
    )
 
 
def get_tabela_oportunidades(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Retorna os expositores com maior oportunidade:
    maior probabilidade + maior ganho.
    """
    colunas = ["nome_fantasia", "prob_vale_a_pena_pct", "ganho_real_medio", "status_decisao"]
 
    return (
        df
        .sort_values(["prob_vale_a_pena_pct", "ganho_real_medio"], ascending=False)
        .head(top_n)
        [[c for c in colunas if c in df.columns]]
    )
