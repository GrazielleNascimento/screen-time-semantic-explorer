"""Helper dos testes: collection do Chroma em memória, com embeddings fornecidos à mão (sem ONNX)."""

import uuid

import chromadb
import numpy as np


def make_collection(embeddings: np.ndarray):
    """Cria uma collection nova com ids c0..cN, documentos 'text i' e 2 PDFs alternados."""
    client = chromadb.EphemeralClient()
    collection = client.create_collection(f"test_{uuid.uuid4().hex}", embedding_function=None)
    n = len(embeddings)
    collection.add(
        ids=[f"c{i}" for i in range(n)],
        embeddings=embeddings.tolist(),
        documents=[f"text {i}" for i in range(n)],
        metadatas=[
            {"source_file": f"doc{i % 2}.pdf", "file_type": "pdf", "chunk_idx": i, "char_count": 6}
            for i in range(n)
        ],
    )
    return collection
