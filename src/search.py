"""
search.py - Busca semântica na collection do ChromaDB.

Recebe uma pergunta pela linha de comando, converte em embedding com o MESMO
modelo usado no embedder.py e retorna os chunks mais parecidos.

Uso:
    python src/search.py "sua pergunta aqui"
"""

import logging
import sys

from embedder import COLLECTION_NAME, get_client, get_embedding_function
from logging_config import configure_logging

logger = logging.getLogger(__name__)

N_RESULTS = 5  # quantos chunks retornar


def search(question, n_results=N_RESULTS):
    """
    Busca os `n_results` chunks mais parecidos com `question` na collection do ChromaDB.

    Lança a exceção original do ChromaDB se a collection ainda não existir
    (nesse caso, rodar embedder.py antes).
    """
    client = get_client()
    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=get_embedding_function(),
        )
    except Exception:
        logger.error("Collection '%s' não encontrada, rode embedder.py antes de buscar", COLLECTION_NAME)
        raise

    logger.info('Buscando: "%s" (n_results=%d)', question, n_results)
    # query_texts: o ChromaDB gera o embedding da pergunta e busca os vizinhos mais próximos
    results = collection.query(query_texts=[question], n_results=n_results)
    logger.info("%d resultados retornados", len(results["documents"][0]))
    return results


def print_results(question, results):
    """Imprime, para uma pergunta, os chunks retornados com PDF de origem e distância."""
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("\n" + "=" * 100)
    print(f'❓ PERGUNTA: "{question}"')
    print("=" * 100 + "\n")

    for rank, (text, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
        relevance = "🟢 Alta" if dist < 0.2 else "🟡 Média" if dist < 0.35 else "🔴 Baixa"
        print(f"📄 Resultado #{rank} | Relevância: {relevance} | Distância: {dist:.4f}")
        print(f"   Arquivo: {meta['source_file']} | Chunk: {meta['chunk_idx']}")
        print(f"   ─" * 50)

        # Trunca e formata o texto para melhor legibilidade
        truncated_text = text[:250] + "..." if len(text) > 250 else text
        print(f"   {truncated_text}")
        print()

    print("─" * 100 + "\n")


def main():
    """CLI: lê a pergunta da linha de comando, busca e imprime os resultados."""
    configure_logging()

    if len(sys.argv) < 2:
        print('Uso: python src/search.py "sua pergunta aqui"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    results = search(question)
    print_results(question, results)


if __name__ == "__main__":
    main()
