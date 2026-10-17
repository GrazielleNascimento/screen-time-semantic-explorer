"""
theme.py - Todo o CSS do app (um único lugar), paleta e layout do gráfico Plotly.

`inject_css()` é chamada uma vez em app.py. As páginas só usam as classes daqui.
"""

import streamlit as st

# Paleta categórica dos clusters (distinguível e coerente com o indigo da marca)
CLUSTER_COLORS = [
    "#4F46E5", "#F59E0B", "#10B981", "#EC4899", "#0EA5E9",
    "#8B5CF6", "#EF4444", "#14B8A6", "#64748B", "#84CC16",
]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --primary: #4F46E5;
    --primary-dark: #4338CA;
    --primary-soft: #EEF2FF;
    --bg: #F8FAFC;
    --surface: #FFFFFF;
    --border: #E2E8F0;
    --text: #0F172A;
    --muted: #64748B;
    --danger: #DC2626;
    --radius: 12px;
    --shadow: 0 1px 3px rgba(15, 23, 42, .08);
    --shadow-hover: 0 8px 20px rgba(15, 23, 42, .12);
}

/* Base */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
    font-size: 16px;
    color: var(--text);
    background: var(--bg);
}
/* Esconde menu, deploy e rodapé; o stToolbar fica porque guarda o botão que reabre a sidebar */
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbarActions"],
[data-testid="stMainMenu"], .stAppDeployButton { display: none; }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1200px; padding-top: 1.5rem; padding-bottom: 3rem; }
h1, h2, h3, h4 { font-weight: 700; letter-spacing: -0.02em; color: var(--text); }
p, li { line-height: 1.6; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }
.brand { display: flex; align-items: center; gap: 14px; margin-bottom: 2rem; }
.brand-icon { width: 52px; height: 52px; border-radius: 12px; background: var(--primary);
    color: #fff; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; }
.brand-name { font-weight: 700; font-size: 1.3rem; letter-spacing: -0.02em; }
.brand-sub { color: var(--muted); font-size: .95rem; }
.sidebar-footer { color: var(--muted); font-size: .9rem; margin-top: 2rem;
    padding-top: 1rem; border-top: 1px solid var(--border); }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] { gap: 4px; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] {
    width: 100%; padding: 14px 16px; border-radius: 10px; border-left: 4px solid transparent;
    transition: background 150ms; cursor: pointer; }
[data-testid="stSidebar"] [data-testid="stRadioOption"]:hover { background: var(--bg); }
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child { display: none; }
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] {
    background: var(--primary-soft); border-left-color: var(--primary); }
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] p {
    color: var(--primary); font-weight: 600; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] p { font-size: 1.2rem; margin: 0; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-of-type(1) p::before { content: "🏠  "; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-of-type(2) p::before { content: "🔎  "; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-of-type(3) p::before { content: "🧭  "; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-of-type(4) p::before { content: "🛡️  "; }

/* Page header */
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 2rem; margin: 0 0 .25rem 0; padding: 0; }
.page-header p { color: var(--muted); margin: 0; font-size: 1.02rem; }

/* Cards */
.card, [class*="st-key-card"], [class*="st-key-action"], [class*="st-key-topic"] {
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
    box-shadow: var(--shadow); padding: 1.25rem; margin-bottom: 1rem; }
[class*="st-key-action"], [class*="st-key-topic"] { transition: transform 150ms, box-shadow 150ms; }
[class*="st-key-action"] { min-height: 240px; }
[class*="st-key-topic"] { min-height: 340px; }
.kpi { min-height: 64px; }
[class*="st-key-action"]:hover, [class*="st-key-topic"]:hover { transform: translateY(-2px); box-shadow: var(--shadow-hover); }
.topic-img { height: 120px; border-radius: 8px; display: flex; align-items: center;
    justify-content: center; margin-bottom: .75rem; overflow: hidden; }
.topic-img img { height: 100%; width: 100%; object-fit: contain; }
.topic-emoji { font-size: 3.5rem; }
.kpi { display: flex; align-items: center; gap: 16px; }
.kpi-icon { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 1.4rem; flex-shrink: 0; }
.tone-primary { background: var(--primary-soft); }
.tone-success { background: #DCFCE7; }
.tone-warning { background: #FEF3C7; }
.tone-danger { background: #FEE2E2; }
.metric-value { font-size: 1.9rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; }
.metric-label { color: var(--muted); font-size: .85rem; margin-top: 2px; }
.action-icon { font-size: 1.6rem; margin-bottom: .25rem; }
.action-title { font-weight: 700; font-size: 1.1rem; letter-spacing: -0.02em; }
.action-desc { color: var(--muted); font-size: .92rem; margin-bottom: .75rem; }

/* Hero */
[class*="st-key-hero"] {
    background: linear-gradient(135deg, #4F46E5 0%, #8B5CF6 60%, #C4B5FD 100%);
    border-radius: 16px; padding: 2.5rem 2rem; margin-bottom: 1.5rem; }
[class*="st-key-hero"] h1, [class*="st-key-hero"] p { color: #fff; }
[class*="st-key-hero"] h1 { font-size: 2.4rem; margin: 0 0 .5rem 0; }
[class*="st-key-hero"] p { font-size: 1.1rem; max-width: 640px; opacity: .95; }
[class*="st-key-hero"] button { background: #fff !important; border-color: #fff !important; }
[class*="st-key-hero"] button p { color: var(--primary-dark) !important; }
[class*="st-key-hero"] button:hover { background: var(--primary-soft) !important; }

.section-title { font-weight: 700; font-size: 1.15rem; letter-spacing: -0.02em; margin: 1.5rem 0 .75rem 0; }

/* Chips */
.chip { display: inline-block; background: var(--primary-soft); color: var(--primary-dark);
    padding: 2px 10px; border-radius: 999px; font-size: .82rem; margin: 0 6px 6px 0; }

/* Search results */
.result-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: .5rem; }
.result-rank { font-weight: 700; color: var(--primary); }
.result-meta { color: var(--muted); font-size: .85rem; }
.result-text { line-height: 1.6; margin: .5rem 0; }
.sim-track { height: 6px; background: var(--border); border-radius: 999px; overflow: hidden; }
.sim-fill { height: 100%; background: var(--primary); border-radius: 999px; }
.sim-label { color: var(--muted); font-size: .78rem; margin-top: 4px; }
.empty { text-align: center; padding: 2rem 1rem; color: var(--muted); }
.empty .emoji { font-size: 2.5rem; }

/* Clusters */
.cluster-card { border-left: 6px solid var(--primary); }
.cluster-title { font-weight: 700; font-size: 1.05rem; letter-spacing: -0.02em; }
.cluster-size { color: var(--muted); font-size: .85rem; margin-bottom: .5rem; }
.pdf-line { color: var(--muted); font-size: .85rem; }
.howto { display: flex; gap: 16px; flex-wrap: wrap; }
.howto div { flex: 1 1 220px; }
.howto b { color: var(--primary-dark); }

/* Inputs and buttons */
.stTextInput input { height: 48px; font-size: 1rem; border-radius: 10px; }
.stTextInput input:focus, .stTextInput > div:focus-within { box-shadow: 0 0 0 3px rgba(79, 70, 229, .25);
    border-color: var(--primary); }
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    border-radius: 10px; font-weight: 600; transition: all 150ms; border: 1px solid var(--border); }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background: var(--primary); border-color: var(--primary); color: #fff; }
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {
    background: var(--primary-dark); border-color: var(--primary-dark); }
.stFormSubmitButton > button { height: 48px; }
[data-testid="stForm"] { border: none; padding: 0; }

/* Alerts (erros e avisos) */
[data-testid="stAlert"] { border-radius: var(--radius); border: 1px solid var(--border);
    border-left: 5px solid var(--primary); background: var(--surface); box-shadow: var(--shadow); }

/* Tables (relatório) */
.stMarkdown table { width: 100%; border-collapse: collapse; font-size: .88rem; }
.stMarkdown th { background: #F1F5F9; text-align: left; padding: 8px 10px; }
.stMarkdown td { padding: 8px 10px; border-top: 1px solid var(--border); }
.stMarkdown tr:nth-child(even) td { background: #F8FAFC; }

/* Footer: linha fina no final */
.page-footer {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #E2E8F0;
    color: #64748B;
    font-size: 0.8125rem;
    line-height: 1.4;
    text-align: center;
}

/* Rodapé e scrollbar */
.footer { color: var(--muted); font-size: .8rem; margin-top: 2rem; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 8px; }
</style>
"""


def inject_css() -> None:
    """Injeta o CSS do app (chamar uma vez, em app.py)."""
    st.markdown(CSS, unsafe_allow_html=True)


def plotly_layout() -> dict:
    """Layout do gráfico t-SNE: template claro, fundo transparente, legenda embaixo."""
    return {
        "template": "plotly_white",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, system-ui, sans-serif", "color": "#0F172A", "size": 13},
        "height": 620,
        "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
        "legend": {"orientation": "h", "yanchor": "top", "y": -0.02, "xanchor": "left", "x": 0},
        "xaxis": {"showticklabels": False, "title": "", "gridcolor": "#EEF2F7", "zeroline": False},
        "yaxis": {"showticklabels": False, "title": "", "gridcolor": "#EEF2F7", "zeroline": False},
        "hoverlabel": {"bgcolor": "#FFFFFF", "font": {"family": "Inter, system-ui, sans-serif", "size": 13}},
    }
