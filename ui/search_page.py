"""
search_page.py - Pagina de busca semantica.
"""

from typing import Callable

import streamlit as st

from ui.components import empty_state, page_header, result_card

DEFAULT_RESULTS = 5
LONG_TEXT_CHARS = 300

EXAMPLES = [
    "is screen time associated with childhood obesity?",
    "what is the recommended screen time limit for children?",
    "what are the best recipes for chocolate cake?",
]

HOW_TO_READ = (
    '<div class="howto">'
    '<div><b>Each result</b> is a chunk (~250 characters) from the articles, ranked by how well it answers your question.</div>'
    '<div><b>Smaller distance</b> = <b>higher similarity</b> = the embedding is closer to your question in the semantic space.</div>'
    '<div><b>The bar</b> shows similarity as a percentage (converted from distance); longer bar = better match.</div>'
    '</div>'
)

METHOD_NOTES = """
**How does semantic search work?** Your question and each chunk are converted to embeddings (384-dimensional vectors)
by MiniLM. Distance measures how different they are: 0 = identical, ~2 = unrelated.

**Why distance and not similarity directly?** The embeddings use cosine distance, which is standard in NLP.
We convert it to similarity (0-100%) for easier reading: similarity = 1 - distance (capped at 0-1).

**Why might the top result not be about your question?** If the corpus has no direct answer, semantic search
finds the closest match. Sometimes that's a passage about related concepts--it's a feature, not a bug.

**Can I export the results?** Not yet--but you can copy the text from each card, or use the Quality report
page to download a CSV of all chunks.
"""


def run_example(question: str) -> None:
    """Callback: coloca o exemplo na barra de busca e dispara a busca."""
    st.session_state["search_text"] = question
    st.session_state["last_query"] = question


def _submit_form() -> None:
    """Callback do formulário: guarda o texto digitado como a busca atual."""
    st.session_state["last_query"] = st.session_state.get("search_text", "").strip()


def render(search_fn: Callable[[str, int], list[dict]]) -> None:
    """Desenha a busca. `search_fn(pergunta, n)` devolve uma lista de dicionários."""
    page_header("Search", "Ask a question and find the most similar passages across the articles.")

    st.markdown(f'<div class="card">{HOW_TO_READ}</div>', unsafe_allow_html=True)

    with st.form("search_form", border=False):
        bar, button = st.columns([6, 1], vertical_alignment="bottom")
        bar.text_input(
            "Your question", key="search_text", label_visibility="collapsed",
            placeholder="🔎  Ask a question about screen time...",
        )
        button.form_submit_button("Search", type="primary", on_click=_submit_form, width="stretch")
        with st.expander("Options"):
            n_results = st.slider("Number of results", min_value=1, max_value=10, value=DEFAULT_RESULTS)

    question = st.session_state.get("last_query", "")
    if not question:
        empty_state("💬", "Start with a question",
                    "Type above and press Enter, or try one of these examples:")
        for i, example in enumerate(EXAMPLES):
            st.button(example, key=f"example_{i}", on_click=run_example, args=(example,))
        return

    try:
        results = search_fn(question, n_results)
    except Exception as error:
        st.error(f"Search failed: {error}")
        return

    st.caption(f"{len(results)} results for: {question}")
    for rank, item in enumerate(results, start=1):
        text = item["text"]
        long_text = len(text) > LONG_TEXT_CHARS
        result_card(
            rank, item["source_file"], item["chunk_idx"], item["distance"],
            text[:LONG_TEXT_CHARS] + "..." if long_text else text,
        )
        if long_text:
            with st.expander("Show full text"):
                st.write(text)

    with st.expander("Method notes: How semantic search works"):
        st.markdown(METHOD_NOTES)
