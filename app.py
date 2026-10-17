"""
app.py - Interface Streamlit: só monta a tela e chama funções de src/ e ui/.

Uso:
    streamlit run app.py
"""

import sys
from pathlib import Path

import numpy as np
import streamlit as st
from chromadb.api.models.Collection import Collection

# Os módulos de src/ importam uns aos outros pelo nome simples (ex.: "from embedder import ...")
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from clustering import ClusterSummary, cached_projection, cluster, summarize_clusters  # noqa: E402
from quality_report import REPORT_FILE, read_removed_ids  # noqa: E402
from search import search_records  # noqa: E402
from store import Corpus, IndexNotFoundError, load_corpus, open_collection  # noqa: E402
from ui import clusters_page, home_page, quality_page, search_page  # noqa: E402
from ui.components import sidebar_brand, sidebar_footer  # noqa: E402
from ui.theme import inject_css  # noqa: E402

PAGES = ["Home", "Search", "Clusters", "Quality report"]

st.set_page_config(page_title="Semantic Explorer", page_icon="🔎", layout="wide", initial_sidebar_state="expanded")


@st.cache_resource
def get_collection() -> Collection:
    return open_collection()


@st.cache_data
def get_corpus() -> Corpus:
    return load_corpus(get_collection())


@st.cache_data
def get_coords() -> np.ndarray:
    return cached_projection(get_corpus().embeddings)


@st.cache_data
def get_clusters(n_clusters: int) -> tuple[np.ndarray, list[ClusterSummary]]:
    corpus = get_corpus()
    labels = cluster(corpus.embeddings, n_clusters)
    return labels, summarize_clusters(labels, corpus.documents, corpus.metadatas)


def main() -> None:
    inject_css()
    with st.sidebar:
        sidebar_brand()
        page = st.radio("Navigate", PAGES, key="page", label_visibility="collapsed")
        sidebar_footer()

    try:
        corpus = get_corpus()
    except IndexNotFoundError:
        st.error("Index not found. Run the pipeline first: `python src/embedder.py`", icon="🗄️")
        return

    if page == "Home":
        n_documents = len({meta["source_file"] for meta in corpus.metadatas})
        home_page.render(len(corpus.ids), n_documents, len(read_removed_ids()))
    elif page == "Search":
        search_page.render(search_records)
    elif page == "Clusters":
        with st.spinner("Computing the t-SNE map (cached after the first run)..."):
            coords = get_coords()
        clusters_page.render(corpus, coords, get_clusters)
    else:
        report = REPORT_FILE.read_text(encoding="utf-8") if REPORT_FILE.exists() else None
        quality_page.render(len(corpus.ids), len(read_removed_ids()), report)


main()
