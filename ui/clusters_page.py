"""
clusters_page.py - K-Means + mapa t-SNE interativo, com a leitura de cada cluster.
"""

import html
from pathlib import Path
from typing import Callable

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from clustering import ClusterSummary
from store import Corpus
from ui.components import chips, page_header, section_title
from ui.theme import CLUSTER_COLORS, plotly_layout

FIGURES_DIR = Path(__file__).resolve().parent.parent / "reports" / "figures"
HOVER_CHARS = 120   # tamanho do trecho mostrado no tooltip
NAME_TERMS = 3      # quantos termos formam o nome curto de um cluster
CARDS_PER_ROW = 3

HOW_TO_READ = (
    '<div class="howto">'
    "<div><b>Each dot</b> is one chunk (a ~250-character passage) of the articles.</div>"
    "<div><b>Closer dots</b> have a more similar meaning (t-SNE map of the embeddings).</div>"
    "<div><b>Each color</b> is a K-Means cluster; the numbers mark each cluster's center.</div>"
    "</div>"
)

METHOD_NOTES = """
**Why K-Means?** It is simple and sufficient: it groups the 384-dimensional embeddings into N groups
around the nearest center. You choose N with the slider.

**Why t-SNE and not PCA?** t-SNE keeps neighbours together when many dimensions are squeezed into 2,
so groups are easier to see. It only *draws* the points; the clusters are computed on the original embeddings.

**Why do clusters overlap?** K-Means always returns N groups, even when the data has no natural
boundaries. Overlap means the themes share vocabulary (for example, a passage about sleep and screens).
Read the clusters as a guide, not as hard borders.

**How to choose N?** There is no single right answer. Try 2, 3 and 5 and keep the one whose terms
tell a clear story.
"""


def cluster_names(summaries: list[ClusterSummary]) -> dict[int, str]:
    """Nome curto de cada cluster: seus primeiros termos característicos."""
    return {s.cluster: " · ".join(s.top_terms[:NAME_TERMS]) for s in summaries}


def build_figure(corpus: Corpus, coords: np.ndarray, labels: np.ndarray,
                 names: dict[int, str] | None = None) -> go.Figure:
    """Gráfico t-SNE por cluster; o tooltip mostra PDF, chunk_idx e um trecho. Números marcam os centros."""
    names = names or {}
    fig = go.Figure()
    for label in sorted(set(labels.tolist())):
        idx = np.flatnonzero(labels == label)
        hover = [
            [corpus.metadatas[i]["source_file"], corpus.metadatas[i]["chunk_idx"],
             corpus.documents[i][:HOVER_CHARS]]
            for i in idx
        ]
        color = CLUSTER_COLORS[label % len(CLUSTER_COLORS)]
        title = f"Cluster {label}" + (f" · {names[label]}" if label in names else "")
        fig.add_trace(go.Scatter(
            x=coords[idx, 0], y=coords[idx, 1], mode="markers", name=title,
            marker={"size": 8, "opacity": 0.8, "color": color, "line": {"width": 0}},
            customdata=hover,
            hovertemplate="<b>%{customdata[0]}</b> · chunk %{customdata[1]}<br>%{customdata[2]}...<extra></extra>",
        ))
        # número do cluster no centro (mediana), em uma etiqueta branca para ler sobre os pontos
        fig.add_annotation(
            x=float(np.median(coords[idx, 0])), y=float(np.median(coords[idx, 1])), text=f"<b>{label}</b>",
            showarrow=False, bgcolor="#FFFFFF", bordercolor=color, borderwidth=2, borderpad=4,
            font={"size": 15, "color": "#0F172A"},
        )
    fig.update_layout(**plotly_layout())
    return fig


def _cluster_card(summary: ClusterSummary, total: int) -> str:
    """HTML de um card de cluster: cor, tamanho, termos (chips) e PDFs principais."""
    color = CLUSTER_COLORS[summary.cluster % len(CLUSTER_COLORS)]
    pdfs = ", ".join(f"{html.escape(pdf)} ({count})" for pdf, count in summary.top_pdfs)
    return (
        f'<div class="card cluster-card" style="border-left-color:{color}">'
        f'<div class="cluster-title">Cluster {summary.cluster}</div>'
        f'<div class="cluster-size">{summary.size:,} chunks · {summary.size / total:.0%} of the corpus</div>'
        f"{chips(summary.top_terms)}"
        f'<div class="pdf-line"><b>Main PDFs:</b> {pdfs}</div></div>'
    )


def render(corpus: Corpus, coords: np.ndarray, get_clusters: Callable) -> None:
    """Desenha a página. `get_clusters(n)` devolve (labels, resumos)."""
    page_header("Clusters", "See how the passages group by meaning, and what each group is about.")

    st.markdown(f'<div class="card">{HOW_TO_READ}</div>', unsafe_allow_html=True)

    with st.container(key="card_controls"):
        n_clusters = st.slider("Number of clusters (K-Means)", min_value=2, max_value=10, value=3)
    labels, summaries = get_clusters(n_clusters)

    fig = build_figure(corpus, coords, labels, cluster_names(summaries))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    if st.button("Export this chart as HTML"):
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        path = FIGURES_DIR / f"clusters_k{n_clusters}.html"
        fig.write_html(path)
        st.success(f"Saved to {path}")

    section_title("What each cluster has in common")
    for start in range(0, len(summaries), CARDS_PER_ROW):
        cols = st.columns(CARDS_PER_ROW)
        for col, summary in zip(cols, summaries[start:start + CARDS_PER_ROW]):
            col.markdown(_cluster_card(summary, len(corpus.ids)), unsafe_allow_html=True)

    with st.expander("Method notes: K-Means, t-SNE, overlap and choosing N"):
        st.markdown(METHOD_NOTES)
