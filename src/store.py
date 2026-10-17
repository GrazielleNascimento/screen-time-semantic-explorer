"""
store.py - Acesso aos embeddings guardados no ChromaDB (ler e remover).

Não calcula nada: só lê o corpus da collection e apaga ids. As outras etapas
(anomalias, clusters, relatório) recebem o resultado como argumento.
"""

import logging
from dataclasses import dataclass

import numpy as np
from chromadb.api.models.Collection import Collection

from embedder import COLLECTION_NAME, get_client, get_embedding_function

logger = logging.getLogger(__name__)

DELETE_BATCH_SIZE = 500  # quantos ids apagar por chamada ao ChromaDB


class IndexNotFoundError(Exception):
    """A collection não existe ou está vazia (falta rodar o embedder)."""


def open_collection() -> Collection:
    """Abre a collection existente; lança IndexNotFoundError se não houver índice."""
    try:
        collection = get_client().get_collection(
            name=COLLECTION_NAME,
            embedding_function=get_embedding_function(),
        )
    except Exception as exc:
        raise IndexNotFoundError(
            f"Collection '{COLLECTION_NAME}' not found. Run: python src/embedder.py"
        ) from exc
    if collection.count() == 0:
        raise IndexNotFoundError(
            f"Collection '{COLLECTION_NAME}' is empty. Run: python src/embedder.py"
        )
    return collection


@dataclass
class Corpus:
    """Todo o conteúdo da collection, em listas/arrays alinhados pela posição."""

    ids: list[str]
    embeddings: np.ndarray  # shape (n, 384), float32
    documents: list[str]
    metadatas: list[dict]


def load_corpus(collection: Collection) -> Corpus:
    """Lê ids, embeddings, textos e metadados de todos os chunks da collection."""
    data = collection.get(include=["embeddings", "documents", "metadatas"])
    embeddings = np.asarray(data["embeddings"], dtype=np.float32)
    logger.info("Corpus carregado: %d chunks", len(data["ids"]))
    return Corpus(
        ids=list(data["ids"]),
        embeddings=embeddings,
        documents=list(data["documents"]),
        metadatas=list(data["metadatas"]),
    )


def delete_ids(collection: Collection, ids: list[str]) -> int:
    """Remove os ids da collection, em lotes, e devolve quantos foram removidos."""
    for start in range(0, len(ids), DELETE_BATCH_SIZE):
        collection.delete(ids=ids[start:start + DELETE_BATCH_SIZE])
    logger.info("%d chunks removidos da collection", len(ids))
    return len(ids)
