"""
clean.py - Etapa 2 do pipeline: limpeza dos chunks.

Passos:
    1. Lê data/processed/chunks.jsonl (gerado pelo loader.py).
    2. Remove os chunks inválidos: vazios, curtos, quase só números ou com
       muitos caracteres inválidos/lixo.
    3. Sobrescreve data/processed/chunks.jsonl apenas com os chunks válidos.

Usa só tratamento de string e 1 regex.

Uso:
    python src/clean.py
"""

import json
import logging
import re
from pathlib import Path

from logging_config import configure_logging

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
CHUNKS_FILE = ROOT_DIR / "data" / "processed" / "chunks.jsonl"

MIN_CHARS = 30            # chunks menores que isso são descartados
MAX_DIGIT_RATIO = 0.5     # acima disso, o chunk é considerado "quase só números"
MIN_VALID_RATIO = 0.7     # abaixo disso, o chunk é considerado "lixo"

# Caracteres aceitos em texto científico em inglês: letras, espaços e pontuação comum
VALID_CHARS = re.compile(r"[A-Za-z\s.,;:!?()'\"%\-]")


def get_reason_to_remove(text):
    """
    Avalia se um chunk deve ser descartado.

    Retorna o motivo ("vazio", "curto", "quase_so_numeros" ou "lixo"),
    ou None se o chunk for válido.
    """
    stripped = text.strip()

    if not stripped:
        return "vazio"

    if len(stripped) < MIN_CHARS:
        return "curto"

    # proporção de dígitos entre os caracteres que não são espaço
    no_spaces = stripped.replace(" ", "")
    digits = sum(ch.isdigit() for ch in no_spaces)
    if digits / len(no_spaces) > MAX_DIGIT_RATIO:
        return "quase_so_numeros"

    # proporção de caracteres válidos (VALID_CHARS) sobre o total
    valid = len(VALID_CHARS.findall(stripped))
    if valid / len(stripped) < MIN_VALID_RATIO:
        return "lixo"

    return None


def main():
    """Filtra os chunks inválidos e sobrescreve CHUNKS_FILE apenas com os válidos."""
    configure_logging()

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]
    logger.info("Chunks lidos: %d de %s", len(chunks), CHUNKS_FILE)

    valid_chunks = []
    removed = {}  # contador de chunks removidos por motivo

    for chunk in chunks:
        reason = get_reason_to_remove(chunk["text"])
        if reason is None:
            valid_chunks.append(chunk)
        else:
            removed[reason] = removed.get(reason, 0) + 1

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        for chunk in valid_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    logger.info("Chunks válidos: %d", len(valid_chunks))
    logger.info("Chunks removidos: %d %s", len(chunks) - len(valid_chunks), removed)


if __name__ == "__main__":
    main()
