"""
exagerado_theme.py
Aplique no início do seu app com:  inject_theme()
"""

from streamlit.components.v1 import html
import streamlit as st

def inject_theme():
    st.markdown("""
    <style>
    /* =============================================
       MEU EXAGERADO — Custom Streamlit Theme
       Identidade visual: meuexagerado.com.br
    ============================================= */

    /* --- VARIÁVEIS --- */
    :root {
        --ex-black:         #1A1A1A;
        --ex-white:         #F6F4EE;
        --ex-purple:        #6B3FA0;
        --ex-purple-light:  #EDE8F5;
        --ex-purple-mid:    #9B6FCC;
        --ex-gray:          #F2F1EE;
        --ex-gray-mid:      #D4D2CC;
        --ex-gray-dark:     #6B6963;
        --ex-green:         #2E7D5C;
        --ex-green-light:   #E8F4EE;
        --ex-red:           #C0392B;
        --ex-red-light:     #FBEAE8;
        --ex-amber:         #B07818;
        --ex-amber-light:   #FBF3E0;
        --ex-border:        rgba(26,26,26,0.1);
    }

    /* --- FONTE BASE --- */
    html, body, [class*="css"] {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display:ital@0;1&display=swap');

    /* --- FUNDO PRINCIPAL --- */
    .stApp {
        background-color: var(--ex-white) !important;
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: var(--ex-black) !important;
    }

    [data-testid="stSidebar"] * {
        color: rgba(255,255,255,0.7) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: rgba(255,255,255,0.95) !important;
    }

    [data-testid="stSidebar"] .stMarkdown h1 {
        font-family: 'DM Serif Display', serif !important;
        font-style: italic;
        font-size: 20px !important;
        color: #FAFAF8 !important;
        margin-bottom: 2px !important;
    }

    /* Logo / título sidebar */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p:first-child {
        font-family: 'DM Serif Display', serif !important;
    }

    /* Inputs dentro da sidebar */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] .stMultiSelect label {
        color: rgba(255,255,255,0.45) !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
    }

    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stMultiSelect > div > div {
        background-color: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 8px !important;
        color: rgba(255,255,255,0.8) !important;
    }

    /* Divisor sidebar */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 16px 0 !important;
    }

    /* --- RADIO (menu de seção na sidebar) --- */
    [data-testid="stSidebar"] .stRadio label {
        padding: 8px 10px !important;
        border-radius: 8px !important;
        transition: background 0.15s !important;
        color: rgba(255,255,255,0.55) !important;
        font-size: 13px !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.06) !important;
        color: rgba(255,255,255,0.9) !important;
    }

    /* Radio selecionado */
    [data-testid="stSidebar"] .stRadio [data-checked="true"] {
        background: var(--ex-purple) !important;
        color: #fff !important;
    }

    /* --- MÉTRICAS (st.metric) --- */
    [data-testid="stMetricContainer"] {
        background-color: var(--ex-white) !important;
        border: 1px solid var(--ex-border) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        transition: border-color 0.2s !important;
    }

    [data-testid="stMetricContainer"]:hover {
        border-color: rgba(107,63,160,0.3) !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 10px !important;
        font-weight: 500 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        color: var(--ex-gray-dark) !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'DM Serif Display', serif !important;
        font-size: 28px !important;
        font-style: italic !important;
        color: var(--ex-black) !important;
        line-height: 1.1 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    /* --- BOTÕES --- */
    .stButton > button {
        background-color: var(--ex-purple) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 8px 20px !important;
        transition: background 0.15s !important;
    }

    .stButton > button:hover {
        background-color: #5A348A !important;
    }

    /* Botão secundário */
    .stButton > button[kind="secondary"] {
        background-color: var(--ex-purple-light) !important;
        color: var(--ex-purple) !important;
        border: 1px solid rgba(107,63,160,0.2) !important;
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--ex-gray) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 2px !important;
        border-bottom: none !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        color: var(--ex-gray-dark) !important;
        padding: 8px 16px !important;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--ex-white) !important;
        color: var(--ex-black) !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
    }

    /* --- SELECTBOX / INPUTS --- */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        border: 1px solid var(--ex-border) !important;
        border-radius: 8px !important;
        background-color: var(--ex-white) !important;
    }

    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--ex-purple) !important;
        box-shadow: 0 0 0 2px rgba(107,63,160,0.15) !important;
    }

    /* --- LABELS DOS INPUTS --- */
    .stSelectbox label,
    .stMultiSelect label,
    .stDateInput label,
    .stNumberInput label,
    .stTextInput label {
        font-size: 11px !important;
        font-weight: 500 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        color: var(--ex-gray-dark) !important;
        margin-bottom: 4px !important;
    }

    /* --- CABEÇALHOS DA PÁGINA --- */
    h1 {
        font-family: 'DM Serif Display', serif !important;
        font-style: italic !important;
        font-size: 28px !important;
        color: var(--ex-black) !important;
        font-weight: 400 !important;
        letter-spacing: -0.5px !important;
    }

    h2 {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        color: var(--ex-black) !important;
        margin-top: 8px !important;
    }

    h3 {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        color: var(--ex-gray-dark) !important;
    }

    /* --- DATAFRAMES / TABELAS --- */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--ex-border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* --- DIVISORES --- */
    hr {
        border: none !important;
        border-top: 1px solid var(--ex-border) !important;
        margin: 20px 0 !important;
    }

    /* --- EXPANDERS --- */
    .streamlit-expanderHeader {
        font-size: 13px !important;
        font-weight: 500 !important;
        color: var(--ex-black) !important;
        background-color: var(--ex-gray) !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
    }

    /* --- CAIXAS DE ALERTA (success / warning / error / info) --- */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
        border-left-width: 4px !important;
    }

    /* --- SPINNER --- */
    .stSpinner > div {
        border-top-color: var(--ex-purple) !important;
    }

    /* --- SCROLLBAR GLOBAL --- */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--ex-gray-mid); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--ex-gray-dark); }

    /* --- RODAPÉ HIDE --- */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    </style>
    """, unsafe_allow_html=True)


# =============================================
# COMPONENTES HELPER
# =============================================
# =============================================

def chart_card(title: str, fig, height: int = 720):
    """Renderiza um card visual completo para um gráfico Plotly."""
    fig.update_layout(
        autosize=True,
        height=560,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, b=20, l=0, r=0),
    )
    chart_html = fig.to_html(
        full_html=False,
        include_plotlyjs='cdn',
        config={'displayModeBar': False, 'responsive': True},
    )
    html(f"""
    <div style="background:#ffffff; border:1px solid rgba(26,26,26,0.12); border-radius:12px; padding:18px 20px 16px; margin-bottom:16px;">
        <div style="font-size:13px; font-weight:600; color:#6B6963; margin-bottom:14px;">{title}</div>
        <div style="width:100%; min-height:560px;">
            {chart_html}
        </div>
    </div>
    """, height=height, scrolling=True)

def kpi_card(label, value, delta=None, delta_type="neutral", color="default"):
    """
    Renderiza um card de KPI com estilo Exagerado.

    color: "default" | "purple" | "green" | "red" | "amber"
    delta_type: "positive" | "negative" | "neutral"
    """
    colors = {
        "purple": ("var(--ex-purple-light)", "var(--ex-purple)"),
        "green":  ("var(--ex-green-light)",  "var(--ex-green)"),
        "red":    ("var(--ex-red-light)",    "var(--ex-red)"),
        "amber":  ("var(--ex-amber-light)",  "var(--ex-amber)"),
        "default":("#FAFAF8",                "rgba(26,26,26,0.1)"),
    }
    bg, border = colors.get(color, colors["default"])

    delta_colors = {
        "positive": "var(--ex-green)",
        "negative": "var(--ex-red)",
        "neutral":  "var(--ex-gray-dark)",
    }
    delta_color = delta_colors.get(delta_type, "var(--ex-gray-dark)")

    delta_html = f'<div style="font-size:12px;font-weight:500;color:{delta_color};margin-top:6px">{delta}</div>' if delta else ""

    st.markdown(f"""
    <div style="
        background:{bg};
        border:1px solid {border};
        border-radius:12px;
        padding:16px;
        height:100%;
    ">
        <div style="font-size:10px;font-weight:500;letter-spacing:1px;text-transform:uppercase;color:var(--ex-gray-dark);margin-bottom:8px">{label}</div>
        <div style="font-family:'DM Serif Display',serif;font-size:28px;font-style:italic;color:var(--ex-black);line-height:1.1">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def resumo_estrategico(items):
    """Renderiza o card de Resumo Estratégico com um estilo próximo ao mockup."""
    dot_colors = {"ok": "#4CAF87", "warn": "#E8933A", "alert": "#E05A5A"}

    item_html = ""
    for item in items:
        dot = dot_colors.get(item.get('type', 'warn'), '#888')
        item_html += f"""
        <div style="display:flex;align-items:flex-start;gap:10px;font-size:13px;color:rgba(255,255,255,0.8);line-height:1.6;margin-bottom:12px">
            <span style="width:7px;height:7px;border-radius:50%;background:{dot};flex-shrink:0;margin-top:6px;display:inline-block"></span>
            <div>
                <div style="font-size:14px;color:#FAFAF8;font-weight:600;margin-bottom:4px">{item.get('label', '')}</div>
                <div>{item.get('delta', item.get('text', ''))}</div>
            </div>
        </div>
        """

    total_height = 180 + len(items) * 70
    html(f"""
    <div style="background:#1A1A1A; border-radius:12px; padding:20px 24px; margin-top:12px; color:#FAFAF8; border:1px solid rgba(255,255,255,0.08);">
        <div style="font-family:'DM Serif Display',serif; font-size:17px; font-style:italic; color:#FAFAF8; margin-bottom:16px;">
            Resumo Estratégico
        </div>
        {item_html}
    </div>
    """, height=total_height, scrolling=False)


def section_header(title, pill_text=None):
    """Cabeçalho de seção com pílula de badge opcional."""
    pill = f'<span style="font-size:10px;font-weight:500;padding:3px 10px;border-radius:10px;background:var(--ex-purple-light);color:var(--ex-purple);margin-left:10px">{pill_text}</span>' if pill_text else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;margin-bottom:12px">
        <span style="font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--ex-black)">{title}</span>
        {pill}
    </div>
    """, unsafe_allow_html=True)


def sidebar_logo():
    """Renderiza o logo na sidebar."""
    st.sidebar.markdown("""
    <div style="padding:8px 0 16px">
        <div style="font-family:'DM Serif Display',serif;font-size:20px;font-style:italic;color:#FAFAF8;line-height:1.1">
            Meu Exagerado
        </div>
        <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,0.3);margin-top:3px;font-weight:300">
            Dashboard
        </div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0 0 16px">
    """, unsafe_allow_html=True)
