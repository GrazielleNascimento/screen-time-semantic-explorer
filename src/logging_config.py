"""
logging_config.py - Configuração central de logging e saída do pipeline.

Cada script (loader.py, clean.py, embedder.py, search.py, test_search.py,
demo.py, main.py) chama `configure_logging()` uma vez no início do próprio
main() e usa `logging.getLogger(__name__)` para logar. Manter a configuração
em um único lugar evita duplicar formato/nível em cada arquivo.

Nível pode ser ajustado sem mexer no código:
    LOG_LEVEL=DEBUG python src/loader.py
"""

import logging
import os
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# exemplo: 2024-01-01 12:00:00 | INFO     | src.loader | Encontrados 10 PDFs em data/raw

# Essas bibliotecas logam muito em INFO (ex.: uma linha por request HTTP) e
# afogariam os logs do próprio pipeline, por isso ficam restritas a WARNING+.
NOISY_LOGGERS = ["httpx", "httpcore", "huggingface_hub", "sentence_transformers", "urllib3"]


def configure_logging(level=None):
    """
    Configura o logging raiz, reduz o nível das bibliotecas ruidosas (NOISY_LOGGERS)
    e força stdout/stderr para UTF-8.

    Deve ser chamada uma vez, no início do main() de cada script.
    `level` tem prioridade sobre a variável de ambiente LOG_LEVEL, que por sua
    vez tem prioridade sobre o default "INFO".
    """
    resolved_level = level or os.environ.get("LOG_LEVEL", "INFO")
    logging.basicConfig(level=resolved_level, format=LOG_FORMAT, datefmt=DATE_FORMAT)

    for noisy_logger in NOISY_LOGGERS:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    # Os PDFs científicos têm caracteres (letras gregas, símbolos) fora do
    # codepage legado (cp1252) que o Windows usa por padrão no console; sem
    # isso, print() quebra com UnicodeEncodeError ao exibi-los.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
