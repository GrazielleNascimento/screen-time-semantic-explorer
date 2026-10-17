"""
home_page.py - Tela de abertura: hero, KPIs, cards de ação e temas de pesquisa.
"""

import streamlit as st

from ui.components import action_card, kpi_card, section_title, topic_card
from ui.search_page import run_example
from ui.topics import TOPICS, TOPICS_DIR

SECTIONS = [
    ("🔎", "Search", "Ask a question and get the most similar passages, with source PDF and distance."),
    ("🧭", "Clusters", "Group the passages with K-Means and explore them on an interactive t-SNE map."),
    ("🛡️", "Quality report", "See which passages the Isolation Forest flagged and what was removed."),
]

def _go_to(page: str) -> None:
    """Callback do botão: troca a página selecionada na barra lateral."""
    st.session_state["page"] = page


def _open_topic(question: str) -> None:
    """Callback do card de tema: preenche a pergunta (como os exemplos da Search) e abre a Search."""
    run_example(question)
    _go_to("Search")


def render(total_chunks: int, n_documents: int, n_removed: int) -> None:
    """Desenha a Home. Recebe os números prontos; não acessa o banco."""
    with st.container(key="hero"):
        st.markdown(
            "<h1>Explore the screen-time research corpus</h1>"
            "<p>Semantic search, clustering and quality control over 30 open-access "
            "scientific articles on the effects of screen use in children and adolescents.</p>",
            unsafe_allow_html=True,
        )
        st.button("Start searching", key="start_searching", type="primary", on_click=_go_to, args=("Search",))

    cols = st.columns(3)
    with cols[0]:
        kpi_card("Chunks indexed", f"{total_chunks:,}", "📄", "primary")
    with cols[1]:
        kpi_card("Source documents", str(n_documents), "🗂️", "success")
    with cols[2]:
        kpi_card("Removed by quality check", f"{n_removed:,}", "🧹", "warning")

    cols = st.columns(3)
    for col, (icon, name, description) in zip(cols, SECTIONS):
        with col:
            action_card(icon, name, description, f"Open {name}", _go_to, (name,))

    section_title("Research topics")
    for start in range(0, len(TOPICS), 3):
        cols = st.columns(3)
        for offset, (col, topic) in enumerate(zip(cols, TOPICS[start:start + 3])):
            with col:
                topic_card(start + offset, topic["title"], topic["text"], TOPICS_DIR / topic["svg"],
                           topic["emoji"], topic["color"], topic["tint"], topic["border"], _open_topic, (topic["question"],))


    st.markdown(
        '<div class="footer">Author: Grazielle Nascimento · Data: PubMed Central (open access)</div>',
        unsafe_allow_html=True,
    )
