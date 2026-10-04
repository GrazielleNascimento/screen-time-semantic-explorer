"""
demo.py - Demonstração da busca semântica com perguntas do domínio.

Passos:
    1. Roda uma lista fixa de perguntas sobre o domínio do projeto (efeitos do
       uso de telas em crianças) contra o índice já construído, reaproveitando
       search() de search.py — não re-roda loader/clean/embedder.
    2. Imprime, para cada pergunta, os chunks mais parecidos com PDF de origem
       e distância.

Requer que o índice já exista (rodar embedder.py antes, se ainda não rodou).

Uso:
    python src/demo.py
"""

import logging

from logging_config import configure_logging
from search import print_results, search

logger = logging.getLogger(__name__)

# Uma pergunta por subtema do domínio (sono, obesidade, saúde mental,
# desenvolvimento cognitivo e diretrizes de uso), para mostrar que a busca
# recupera chunks relevantes em diferentes frentes do assunto.

   # "does screen time affect sleep in children?",
   # "does screen time impact cognitive development in children?"

DOMAIN_QUESTIONS = [
    "is screen time associated with childhood obesity?",
    "what is the recommended screen time limit for children?",
    "what are the best recipes for chocolate cake?",  # controle: fora do tema
]


def main():
    """Roda cada pergunta de DOMAIN_QUESTIONS contra o índice e imprime os resultados."""
    configure_logging()

    print("\n" + "╔" + "═" * 98 + "╗")
    print("║" + " " * 98 + "║")
    print("║" + "🔍 DEMONSTRAÇÃO: BUSCA SEMÂNTICA EM DOCUMENTOS CIENTÍFICOS".center(98) + "║")
    print("║" + "Efeitos do uso de telas em crianças".center(98) + "║")
    print("║" + " " * 98 + "║")
    print("╚" + "═" * 98 + "╝" + "\n")

    for i, question in enumerate(DOMAIN_QUESTIONS, 1):
        print(f"[Consulta {i}/{len(DOMAIN_QUESTIONS)}]")
        results = search(question)
        print_results(question, results)


if __name__ == "__main__":
    main()
