"""
exagerado_theme.py
Aplique no início do seu app com:  inject_theme()
"""

from streamlit.components.v1 import html
import streamlit as st
import pandas as pd

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
    }
                
    /* Cor do texto nos selects da Sidebar */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] span {
        color: rgba(255,255,255,0.85) !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
        fill: white !important;
    }

    /* Divisor sidebar */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 16px 0 !important;
    }

    /* --- SPINNER --- */
    /* Main: fundo claro → texto escuro */
    [data-testid="stMain"] [data-testid="stSpinner"] p,
    [data-testid="stMain"] [data-testid="stSpinner"] span {
        color: var(--ex-black) !important;
    }

    /* Sidebar: fundo escuro → texto claro */
    [data-testid="stSidebar"] [data-testid="stSpinner"] p,
    [data-testid="stSidebar"] [data-testid="stSpinner"] span {
        color: rgba(255,255,255,0.85) !important;
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
        position: relative !important;
        z-index: 999 !important;
        pointer-events: auto !important;
        cursor: pointer !important;
    }

    .stButton {
        position: relative !important;
        z-index: 999 !important;
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

    /* --- SELECTBOX / INPUTS (MAIN) --- */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        border: 1px solid var(--ex-border) !important;
        border-radius: 8px !important;
        background-color: var(--ex-white) !important;
    }

    /* Texto e Seta no Main */
    [data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] div,
    [data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] span {
        color: var(--ex-black) !important;
    }
    [data-testid="stMain"] [data-testid="stSelectbox"] svg {
        fill: var(--ex-black) !important;
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

    /* --- INPUTS UNIFICADOS (SELECT, TEXT, NUMBER) --- */
    /* Força o fundo branco e bordas padrão em todos os campos no Main */
    [data-testid="stMain"] .stSelectbox > div > div,
    [data-testid="stMain"] .stTextInput > div > div,
    [data-testid="stMain"] .stNumberInput > div > div,
    [data-testid="stMain"] div[data-baseweb="input"],
    [data-testid="stMain"] [data-testid="stNumberInput"] > div > div,
    [data-testid="stMain"] [data-testid="stNumberInput"] div[data-baseweb="input"] {
        background-color: var(--ex-white) !important;
        border: 1px solid var(--ex-border) !important;
        border-radius: 8px !important;
    }

    /* NumberInput: container principal (envolve botões + input) - ALTA SPECIFICITY */
    [data-testid="stMain"] div[data-testid="stNumberInput"] > div,
    [data-testid="stMain"] div[data-testid="stNumberInput"] > div > div {
        background-color: var(--ex-white) !important;
        border: 1px solid var(--ex-border) !important;
        border-radius: 8px !important;
    }

    /* NumberInput: container interno do input (onde digita o número) */
    [data-testid="stMain"] .stNumberInput > div > div,
    [data-testid="stMain"] [data-testid="stNumberInput"] > div > div {
        background-color: var(--ex-white) !important;
    }

    /* NumberInput: TODOS os containers internos */
    [data-testid="stMain"] .stNumberInput > div,
    [data-testid="stMain"] .stNumberInput > div > div,
    [data-testid="stMain"] .stNumberInput > div > div > div,
    [data-testid="stMain"] [data-testid="stNumberInput"] > div,
    [data-testid="stMain"] [data-testid="stNumberInput"] > div > div,
    [data-testid="stMain"] [data-testid="stNumberInput"] > div > div > div {
        background-color: var(--ex-white) !important;
    }

    /* Esconde os botões de + e - para um visual clean de digitação */
    [data-testid="stMain"] .stNumberInput button,
    [data-testid="stMain"] [data-testid="stNumberInput"] button {
        display: none !important;
    }

    /* Ajuste fino do texto digitado e do cursor */
    [data-testid="stMain"] input,
    [data-testid="stMain"] [data-testid="stNumberInput"] input {
        color: var(--ex-black) !important;
        caret-color: var(--ex-black) !important;
        cursor: text !important;
        padding-left: 12px !important;
        background-color: transparent !important;
    }

    /* Cursor (caret) piscando - animação de foco */
    [data-testid="stMain"] input:focus,
    [data-testid="stMain"] [data-testid="stNumberInput"] input:focus {
        caret-color: var(--ex-purple) !important;
        animation: cursor-blink 1s infinite;
    }

    @keyframes cursor-blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }

    /* Remove a borda/tracejado branco que aparece ao clicar */
    [data-testid="stMain"] input:focus,
    [data-testid="stMain"] [data-testid="stNumberInput"] input:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    /* Placeholder legível (Dica interna da caixa) */
    [data-testid="stMain"] input::placeholder,
    [data-testid="stMain"] [data-testid="stNumberInput"] input::placeholder {
        color: rgba(26, 26, 26, 0.4) !important;
    }

    /* X de limpar o campo (clear button) — ícone preto */
    [data-testid="stMain"] [data-baseweb="input"] [data-baseweb="clear-icon"],
    [data-testid="stMain"] [data-baseweb="input"] button[aria-label="Clear value"],
    [data-testid="stMain"] [data-baseweb="input"] button svg,
    [data-testid="stMain"] [data-baseweb="input"] button svg path,
    [data-testid="stMain"] div[data-baseweb="input"] svg {
        color: var(--ex-black) !important;
        fill: var(--ex-black) !important;
        stroke: var(--ex-black) !important;
        opacity: 0.5 !important;
    }

    [data-testid="stMain"] [data-baseweb="input"] button:hover svg,
    [data-testid="stMain"] [data-baseweb="input"] button:hover svg path,
    [data-testid="stMain"] div[data-baseweb="input"] button:hover svg {
        opacity: 1 !important;
    }

    /* Efeito de foco roxo ao clicar */
    [data-testid="stMain"] div[data-baseweb="input"]:focus-within,
    [data-testid="stMain"] [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
        border-color: var(--ex-purple) !important;
        box-shadow: 0 0 0 2px rgba(107,63,160,0.15) !important;
    }

    /* Selectbox foco no Main */
    [data-testid="stMain"] .stSelectbox > div > div:focus-within,
    [data-testid="stMain"] .stMultiSelect > div > div:focus-within {
        border-color: var(--ex-purple) !important;
        box-shadow: 0 0 0 2px rgba(107,63,160,0.15) !important;
    }

    /* Container interno do NumberInput */
    [data-testid="stMain"] .stNumberInput [data-baseweb="input"],
    [data-testid="stMain"] [data-testid="stNumberInput"] [data-baseweb="input"] {
        background-color: var(--ex-white) !important;
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
    
    /* Slider fora da sidebar */
    [data-testid="stMain"] .stSlider label,
    [data-testid="stMain"] .stSlider [data-testid="stTickBar"] {
        color: var(--ex-black) !important;
    }

    /* Garante que iframes de componentes customizados não bloqueiem cliques */
    iframe {
        pointer-events: none !important;
    }

    /* Reativa pointer-events apenas dentro dos iframes (afeta só o conteúdo externo) */
    .stButton, .stButton > button,
    .stTextInput, .stNumberInput, .stSelectbox,
    [data-testid="stWidgetLabel"] {
        pointer-events: auto !important;
    }

    /* --- RODAPÉ HIDE --- */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
                
    div[data-baseweb="popover"],
    div[data-baseweb="menu"] {
        background-color: var(--ex-white) !important;
        color: var(--ex-black) !important;
    }

    /* Itens da lista */
    div[role="option"] {
        color: var(--ex-black) !important;
        background-color: var(--ex-white) !important;
    }

    /* Hover */
    div[role="option"]:hover {
        background-color: var(--ex-purple-light) !important;
        color: var(--ex-black) !important;
    }

    /* Esconde o overlay "Press Enter to apply" do Streamlit */
    [data-testid="stNumberInputInstructions"],
    [data-testid="InputInstructions"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0 !important;
        overflow: hidden !important;
        position: absolute !important;
    }

    /* Remove a barrinha/linha branca que aparece embaixo do number input ao digitar */
    [data-testid="stMain"] .stNumberInput [data-baseweb="input"]::after,
    [data-testid="stMain"] .stNumberInput [data-baseweb="input"]::before,
    [data-testid="stMain"] .stNumberInput > div > div::after,
    [data-testid="stMain"] .stNumberInput > div > div::before,
    [data-testid="stMain"] [data-testid="stNumberInput"] [data-baseweb="input"]::after,
    [data-testid="stMain"] [data-testid="stNumberInput"] [data-baseweb="input"]::before {
        display: none !important;
        content: none !important;
        border: none !important;
        background: none !important;
    }

    /* Garante que o input interno não mostre borda/sublinhado extra */
    [data-testid="stMain"] .stNumberInput input,
    [data-testid="stMain"] [data-testid="stNumberInput"] input {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

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
        value = item.get('value', '')
        value_html = (
            f'<span style="font-size:13px;color:rgba(255,255,255,0.72);font-weight:500;margin-left:8px">{value}</span>'
            if value not in (None, '')
            else ''
        )
        item_html += f"""
        <div style="display:flex;align-items:flex-start;gap:10px;font-size:13px;color:rgba(255,255,255,0.8);line-height:1.6;margin-bottom:12px">
            <span style="width:7px;height:7px;border-radius:50%;background:{dot};flex-shrink:0;margin-top:6px;display:inline-block"></span>
            <div>
                <div style="font-size:14px;color:#FAFAF8;font-weight:600;margin-bottom:4px">{item.get('label', '')}{value_html}</div>
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

def _df_to_html_rows(df: pd.DataFrame, col_labels: dict = None) -> str:
    """Converte um DataFrame em linhas HTML para uso interno."""
    cols = list(df.columns)
    labels = col_labels or {}
 
    header_cells = "".join(
        f'<th style="'
        f'padding:10px 14px;'
        f'font-size:10px;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;'
        f'color:#6B6963;border-bottom:1px solid rgba(26,26,26,0.08);'
        f'text-align:left;white-space:nowrap;">'
        f'{labels.get(c, c)}</th>'
        for c in cols
    )
 
    row_html = ""
    for i, (_, row) in enumerate(df.iterrows()):
        bg = "#ffffff" if i % 2 == 0 else "#FAFAF8"
        cells = ""
        for c in cols:
            val = row[c]
            if isinstance(val, float):
                if c in (col_labels or {}) and "%" in col_labels.get(c, ""):
                    formatted = f"{val:.1f}%"
                elif abs(val) >= 10:
                    formatted = f"R$ {val:,.0f}"
                else:
                    formatted = f"{val:.2f}"
            else:
                formatted = str(val) if val is not None else "—"
 
            cells += (
                f'<td style="'
                f'padding:10px 14px;font-size:13px;color:#1A1A1A;'
                f'border-bottom:1px solid rgba(26,26,26,0.05);">'
                f'{formatted}</td>'
            )
        row_html += f'<tr style="background:{bg};">{cells}</tr>'
 
    return f"""
    <table style="width:100%;border-collapse:collapse;">
        <thead><tr>{header_cells}</tr></thead>
        <tbody>{row_html}</tbody>
    </table>
    """
 
 
def table_card(df: pd.DataFrame, col_labels: dict = None, title: str = None):
    """
    Renderiza um DataFrame como card branco com borda sutil,
    igual ao chart_card — sem o tema escuro do st.dataframe.
 
    col_labels: dict mapeando nome_coluna → label exibido
                ex: {
                    "nome_fantasia": "Expositor",
                    "prob_vale_a_pena_pct": "Prob. (%)",
                    "ganho_real_medio": "Ganho Médio",
                }
    """
    title_html = ""
    if title:
        title_html = f"""
        <div style="
            font-size:11px;font-weight:600;letter-spacing:1.5px;
            text-transform:uppercase;color:#6B6963;
            margin-bottom:14px;
        ">{title}</div>
        """
 
    table_html = _df_to_html_rows(df, col_labels)
    n_rows = len(df)
    card_height = 56 + (n_rows * 42) + (44 if title else 0) + 24
 
    html(f"""
    <div style="
        background:#ffffff;
        border:1px solid rgba(26,26,26,0.10);
        border-radius:12px;
        padding:18px 20px;
        margin-bottom:16px;
        overflow-x:auto;
    ">
        {title_html}
        {table_html}
    </div>
    """, height=card_height, scrolling=False)
 
 
def filter_header():
    """Renderiza o cabeçalho da área de filtros."""
    html("""
    <div style="
        background:#F2F1EE;
        border:1px solid rgba(26,26,26,0.08);
        border-radius:10px;
        padding:10px 16px;
        margin-bottom:4px;
        display:flex;align-items:center;gap:8px;
    ">
        <span style="
            font-size:10px;font-weight:600;
            letter-spacing:1.5px;text-transform:uppercase;color:#6B6963;
        ">Filtros</span>
    </div>
    """, height=44, scrolling=False)
 
 
def priority_header(tipo: str):
    """
    Cabeçalho colorido das tabelas de prioridade.
    tipo: "risco" | "oportunidade"
    """
    if tipo == "risco":
        dot_color, label, sublabel = "#E05A5A", "Maiores Riscos", "— alto ganho, baixa probabilidade"
    else:
        dot_color, label, sublabel = "#4CAF87", "Maiores Oportunidades", "— alta probabilidade, alto ganho"
 
    html(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
        <span style="
            width:7px;height:7px;border-radius:50%;
            background:{dot_color};display:inline-block;flex-shrink:0;
        "></span>
        <span style="
            font-size:11px;font-weight:600;
            letter-spacing:1.2px;text-transform:uppercase;color:#1A1A1A;
        ">{label}</span>
        <span style="font-size:10px;color:#6B6963;">{sublabel}</span>
    </div>
    """, height=36, scrolling=False)



def simulacao_card(resultado: dict):
    """
    Renderiza o card de resultado da simulação.

    Lógica de volume de vendas:
      - ja_otimo=True              → exibe volume_vendas como métrica extra ao lado das demais
      - tem_otimizacao=True        → exibe coluna "Vol. Vendas" na tabela, lida de l["volume_vendas"]
      - nem ótimo nem otimizável   → sem alteração (comportamento original)
    """
    from streamlit.components.v1 import html
 
    nome_fantasia  = resultado.get("nome_fantasia", "—")
    status_atual   = resultado.get("status_atual", "—")
    prob_atual     = resultado.get("prob_atual", 0)
    tem_otimizacao = resultado.get("tem_otimizacao", False)
    tem_tabela     = resultado.get("tem_tabela", False)
    linhas         = resultado.get("linhas", [])
    ja_otimo       = resultado.get("ja_otimo", False)
    volume_vendas  = resultado.get("volume_vendas", 0)
    ganho_real_medio = resultado.get("ganho_real_medio", 0)
    receita_otimizada = resultado.get("receita_otimizada", 0)
 
    vale_a_pena = prob_atual >= 60
    if vale_a_pena:
        status_bg     = "#E8F4EE"
        status_border = "#2E7D5C"
        status_label  = "✅ Vale a pena"
        status_sub    = "Os parâmetros informados são viáveis."
    else:
        status_bg     = "#FBEAE8"
        status_border = "#C0392B"
        status_label  = "❌ Não vale a pena"
        status_sub    = "Os parâmetros informados não são viáveis. Veja os cenários otimizados abaixo."
 
    receita_mft = f"R$ {float(receita_otimizada):,.0f}"
    label_receita = "Receita Otimizada"

    # ── coluna extra de volume (só quando ja_otimo) ────────────────────────
    if ja_otimo and volume_vendas:
        volume_fmt = f"{int(volume_vendas):,}".replace(",", ".")
        volume_col_html = f"""
        <div style="display:flex;flex-direction:column;padding:12px 16px;min-width:120px;flex:1;
                    border-left:1px solid rgba(26,26,26,0.07);">
            <div style="font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#6B6963;margin-bottom:6px;">Vol. de Vendas</div>
            <div style="font-family:'DM Serif Display',serif;font-style:italic;font-size:20px;color:#1A1A1A;line-height:1.1;">{volume_fmt}</div>
        </div>
        """
    else:
        volume_col_html = ""

    # ── coluna extra de ganho real medio (só quando ja_otimo) ────────────────────────
    if ja_otimo and ganho_real_medio:
        ganho_fmt = f"R$ {ganho_real_medio:,.2f}".replace(",", ".")
        ganho_col_html = f"""
        <div style="display:flex;flex-direction:column;padding:12px 16px;min-width:120px;flex:1;
                    border-left:1px solid rgba(26,26,26,0.07);">
            <div style="font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#6B6963;margin-bottom:6px;">Ganho Real Médio</div>
            <div style="font-family:'DM Serif Display',serif;font-style:italic;font-size:20px;color:#1A1A1A;line-height:1.1;">{ganho_fmt}</div>
        </div>
        """
    else:
        ganho_col_html = ""

    # ── métricas do cenário atual ──────────────────────────────────────────
    metricas_html = f"""
    <div style="display:flex;flex-wrap:wrap;border-top:1px solid rgba(26,26,26,0.07);margin-top:14px;">
        <div style="display:flex;flex-direction:column;padding:12px 16px;border-right:1px solid rgba(26,26,26,0.07);min-width:120px;flex:1;">
            <div style="font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#6B6963;margin-bottom:6px;">Probabilidade Atual</div>
            <div style="font-family:'DM Serif Display',serif;font-style:italic;font-size:20px;color:#1A1A1A;line-height:1.1;">{prob_atual:.1f}%</div>
        </div>
        <div style="display:flex;flex-direction:column;padding:12px 16px;border-right:1px solid rgba(26,26,26,0.07);min-width:120px;flex:1;">
            <div style="font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#6B6963;margin-bottom:6px;">Status</div>
            <div style="font-family:'DM Serif Display',serif;font-style:italic;font-size:20px;color:#1A1A1A;line-height:1.1;">{status_atual}</div>
        </div>
        <div style="display:flex;flex-direction:column;padding:12px 16px;min-width:120px;flex:1;">
            <div style="font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#6B6963;margin-bottom:6px;">{label_receita}</div>
            <div style="font-family:'DM Serif Display',serif;font-style:italic;font-size:20px;color:#1A1A1A;line-height:1.1;">{receita_mft}</div>
        </div>
        {volume_col_html}
        {ganho_col_html}
    </div>
    """
 
    # ── bloco de otimização ────────────────────────────────────────────────
    if not tem_otimizacao:
        if ja_otimo:
            otimizacao_html = """
            <div style="margin-top:16px;background:#E8F4EE;border:1px solid rgba(46,125,92,0.3);
                        border-radius:10px;padding:16px 18px;text-align:center;">
                <div style="font-size:12px;font-weight:600;color:#2E7D5C;">✨ Parâmetros já são ótimos!</div>
                <div style="font-size:11px;color:#2E7D5C;margin-top:4px;opacity:0.8;">
                    Não há necessidade de ajustes. Os valores atuais são ideais.
                </div>
            </div>
            """
        else:
            otimizacao_html = """
            <div style="margin-top:16px;background:#FBEAE8;border:1px solid rgba(192,57,43,0.25);
                        border-radius:10px;padding:16px 18px;text-align:center;">
                <div style="font-size:12px;font-weight:600;color:#C0392B;">
                    ⚠️ Sem cenário viável nos parâmetros comerciais aceitos
                </div>
                <div style="font-size:11px;color:#C0392B;margin-top:6px;opacity:0.85;">
                    A receita esperada deste expositor não comporta nenhuma combinação de 
                    comissão (1%–15%) e mínimo garantido (R$5.000–R$35.000) com probabilidade 
                    mínima de 60%. Considere não firmar contrato de comissão com este expositor.
                </div>
            </div>
            """
    else:
        # cabeçalho da tabela — inclui coluna de volume de vendas
        cabecalho = """
        <div style="display:grid;grid-template-columns: 1fr 1fr 1fr 1.5fr 1.5fr 1.5fr;
                    gap:0;border-bottom:1px solid rgba(26,26,26,0.1);padding:8px 0;margin-bottom:4px;">
            <div style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#6B6963;">Prob. alvo</div>
            <div style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#6B6963;">Prob. real</div>
            <div style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#6B6963;">Comissão</div>
            <div style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#6B6963;">MG</div>
            <div style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#6B6963;">Receita empresa</div>
            <div style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#6B6963;">Vol. Vendas</div>
        </div>
        """
 
        linhas_html = ""
        for l in linhas:
            if l["recomendado"]:
                row_bg     = "background:rgba(107,63,160,0.06);"
                tag        = '<span style="font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#6B3FA0;background:rgba(107,63,160,0.12);border-radius:4px;padding:2px 6px;margin-left:6px;">recomendado</span>'
                prob_color = "#6B3FA0"
            else:
                row_bg     = ""
                tag        = ""
                prob_color = "#1A1A1A"

            vol_raw = volume_vendas
            if vol_raw is not None:
                vol_fmt = f"{int(vol_raw):,}".replace(",", ".")
            else:
                vol_fmt = "—"
 
            linhas_html += f"""
            <div style="display:grid;grid-template-columns: 1fr 1fr 1fr 1.5fr 1.5fr 1.5fr;
                        gap:0;padding:10px 8px;border-radius:6px;{row_bg}
                        border-bottom:1px solid rgba(26,26,26,0.05);align-items:center;">
                <div style="font-family:'DM Serif Display',serif;font-style:italic;font-size:16px;color:{prob_color};">{l['prob_alvo']}{tag}</div>
                <div style="font-size:13px;color:#6B6963;">{l['prob_real']}%</div>
                <div style="font-size:13px;color:#1A1A1A;font-weight:500;">{l['comissao']}</div>
                <div style="font-size:13px;color:#1A1A1A;font-weight:500;">{l['mg']}</div>
                <div style="font-size:13px;color:#1A1A1A;">{l['receita_empresa']}</div>
                <div style="font-size:13px;color:#1A1A1A;">{vol_fmt}</div>
            </div>
            """
 
        subtitulo = "Cenários por faixa de probabilidade" if tem_tabela else "Melhor cenário possível — abaixo de 60%"
 
        otimizacao_html = f"""
        <div style="margin-top:16px;background:#F6F4EE;border:1px solid rgba(107,63,160,0.2);
                    border-radius:10px;padding:14px 18px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
                <span style="width:6px;height:6px;border-radius:50%;background:#6B3FA0;display:inline-block;flex-shrink:0;"></span>
                <span style="font-size:10px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;color:#6B3FA0;">Cenários Otimizados</span>
                <span style="font-size:11px;color:#6B6963;margin-left:4px;">{subtitulo}</span>
            </div>
            {cabecalho}
            {linhas_html}
        </div>
        """
 
    # ── card completo ──────────────────────────────────────────────────────
    card_html = f"""
    <div style="background:#ffffff;border:1px solid rgba(26,26,26,0.10);
                border-radius:12px;padding:18px 20px;margin-top:8px;">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px;">
            <div>
                <div style="font-size:10px;font-weight:600;letter-spacing:1.2px;
                            text-transform:uppercase;color:#6B6963;margin-bottom:4px;">Simulação — {nome_fantasia}</div>
                <div style="font-size:12px;color:#6B6963;">{status_sub}</div>
            </div>
            <div style="background:{status_bg};border:1px solid {status_border};border-radius:20px;
                        padding:5px 14px;font-size:12px;font-weight:600;color:{status_border};
                        white-space:nowrap;flex-shrink:0;">{status_label}</div>
        </div>
        <div style="margin-top:16px;">
            <div style="font-size:11px;font-weight:600;letter-spacing:1px;color:#6B6963;
                        margin-bottom:8px;text-transform:uppercase;">Cenário Atual</div>
            {metricas_html}
        </div>
        {otimizacao_html}
    </div>
    """
 
    altura = 280 + (len(linhas) * 48) + (80 if not tem_otimizacao else 0)
    html(card_html, height=altura, scrolling=False)