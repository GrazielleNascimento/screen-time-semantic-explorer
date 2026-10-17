"""
embedder.py - Etapa 3 do pipeline: geração de embeddings e indexação.

Passos:
    1. Lê data/processed/chunks.jsonl (já limpo pelo clean.py).
    2. Recria a collection do ChromaDB (apaga se já existir, para não duplicar).
    3. Gera os embeddings de cada chunk com o modelo all-MiniLM-L6-v2
       (normalizados) e insere tudo em lotes na collection.

A collection é persistida em disco na pasta data/chroma/.

Uso:
    python src/embedder.py
"""

import json
import logging
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from logging_config import configure_logging

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
CHUNKS_FILE = ROOT_DIR / "data" / "processed" / "chunks.jsonl"
CHROMA_DIR = ROOT_DIR / "data" / "chroma"

COLLECTION_NAME = "screen_time_children"


BATCH_SIZE = 500  # quantos chunks inserir por vez no ChromaDB


def get_embedding_function():
    """Função de embedding usada tanto na indexação quanto na busca."""
    return DefaultEmbeddingFunction()


def get_client():
    """Cliente do ChromaDB que salva/lê o banco em disco (data/chroma/)."""
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def main():
    """Lê os chunks, recria a collection do ChromaDB e insere tudo em lotes."""
    configure_logging()

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]
    logger.info("%d chunks lidos de %s", len(chunks), CHUNKS_FILE)

    client = get_client()

    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        logger.warning("Collection '%s' já existe, apagando para recriar do zero", COLLECTION_NAME)
        client.delete_collection(COLLECTION_NAME)


    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )

    # O ChromaDB chama a função de embedding automaticamente para cada texto em `documents`
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[
                {
                    "source_file": c["source_file"],
                    "file_type": c["file_type"],
                    "chunk_idx": c["chunk_idx"],
                    "char_count": c["char_count"],
                }
                for c in batch
            ],
        )
        logger.info("lote %d: %d/%d", start // BATCH_SIZE + 1, start + len(batch), len(chunks))

    logger.info("Total de chunks indexados na collection '%s': %d", COLLECTION_NAME, collection.count())


if __name__ == "__main__":
    main()