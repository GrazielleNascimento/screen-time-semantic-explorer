"""
clustering.py - Agrupa os embeddings (K-Means) e os projeta em 2D (t-SNE).

K-Means decide os grupos; t-SNE só serve para desenhar. O t-SNE é lento,
então as coordenadas ficam em cache no disco.
"""

import logging
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
TSNE_CACHE_FILE = ROOT_DIR / "data" / "processed" / "tsne_coords.npy"

RANDOM_STATE = 42
MAX_TFIDF_FEATURES = 5000  # vocabulário máximo do TF-IDF


@dataclass
class ClusterSummary:
    """O que um cluster tem em comum: tamanho, termos típicos e PDFs principais."""

    cluster: int
    size: int
    top_terms: list[str]
    top_pdfs: list[tuple[str, int]]  # (PDF, quantos chunks do cluster vêm dele)


def cluster(embeddings: np.ndarray, n_clusters: int, random_state: int = RANDOM_STATE) -> np.ndarray:
    """K-Means: devolve o rótulo de cluster de cada embedding."""
    model = KMeans(n_clusters=n_clusters, n_init="auto", random_state=random_state)
    return model.fit_predict(embeddings)


def project_2d(embeddings: np.ndarray, random_state: int = RANDOM_STATE) -> np.ndarray:
    """t-SNE: projeta os embeddings em 2D (array n x 2). Lento com milhares de pontos."""
    tsne = TSNE(
        n_components=2,
        metric="cosine",
        init="pca",
        random_state=random_state,
    )
    return tsne.fit_transform(embeddings)


def cached_projection(
    embeddings: np.ndarray,
    cache_file: Path = TSNE_CACHE_FILE,
    random_state: int = RANDOM_STATE,
) -> np.ndarray:
    """Devolve o t-SNE do cache; recalcula se o número de chunks mudou."""
    if cache_file.exists():
        coords = np.load(cache_file)
        if coords.shape[0] == len(embeddings):
            return coords
        logger.info("Cache do t-SNE desatualizado (%d != %d), recalculando", coords.shape[0], len(embeddings))
    coords = project_2d(embeddings, random_state)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache_file, coords)
    return coords


def summarize_clusters(
    labels: np.ndarray,
    documents: list[str],
    metadatas: list[dict],
    top_n: int = 8,
) -> list[ClusterSummary]:
    """Para cada cluster: tamanho, termos mais característicos (TF-IDF) e PDFs mais frequentes."""
    vectorizer = TfidfVectorizer(stop_words="english", max_features=MAX_TFIDF_FEATURES)
    tfidf = vectorizer.fit_transform(documents)
    vocabulary = vectorizer.get_feature_names_out()

    summaries = []
    for label in sorted(set(labels.tolist())):
        members = np.flatnonzero(labels == label)
        mean_weights = np.asarray(tfidf[members].mean(axis=0)).ravel()
        top_terms = [str(vocabulary[i]) for i in mean_weights.argsort()[::-1][:top_n]]
        pdf_counts = Counter(metadatas[i]["source_file"] for i in members)
        summaries.append(ClusterSummary(
            cluster=int(label),
            size=len(members),
            top_terms=top_terms,
            top_pdfs=pdf_counts.most_common(3),
        ))
    return summaries
