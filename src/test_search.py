"""
test_search.py - Teste simples da busca semântica.

Compara as distâncias de:
  a) uma busca relacionada ao domínio  -> espero distâncias MENORES
  b) uma busca sem relação com o tema  -> espero distâncias MAIORES

Uso:
    python src/test_search.py
"""

import logging

from logging_config import configure_logging
from search import search

logger = logging.getLogger(__name__)

RELATED_QUERY = "screen time and obesity"
UNRELATED_QUERY = "recipe for chocolate cake"


def main():
    """Compara as distâncias das duas buscas e loga se o índice discrimina bem entre elas."""
    configure_logging()

    related = search(RELATED_QUERY)["distances"][0]
    unrelated = search(UNRELATED_QUERY)["distances"][0]

    print(f"{'Rank':<6}{RELATED_QUERY:<30}{UNRELATED_QUERY:<30}")
    for rank, (d1, d2) in enumerate(zip(related, unrelated), start=1):
        print(f"{rank:<6}{d1:<30.4f}{d2:<30.4f}")

    avg_related = sum(related) / len(related)
    avg_unrelated = sum(unrelated) / len(unrelated)
    print(f"{'Média':<6}{avg_related:<30.4f}{avg_unrelated:<30.4f}")

    # Verificação simples: a busca do domínio deve ficar mais próxima
    if avg_related < avg_unrelated:
        logger.info("OK: a busca do domínio retornou distâncias menores que a busca sem relação.")
    else:
        logger.warning("a busca sem relação teve distâncias menores ou iguais - verifique o índice.")


if __name__ == "__main__":
    main()
