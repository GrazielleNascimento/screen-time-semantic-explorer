"""
loader.py - Etapa 1 do pipeline: extração de texto e divisão em chunks.

Passos:
    1. Lê todos os PDFs e arquivos .txt de data/raw/.
    2. Extrai e normaliza o texto de cada arquivo.
    3. Divide o texto em chunks de tamanho fixo, com sobreposição (overlap).
    4. Salva cada chunk como uma linha JSON em data/processed/chunks.jsonl.

Nenhum modelo de IA é usado aqui: só a biblioteca pypdf e tratamento de string.

Uso:
    python src/loader.py
"""

import json
import logging
from pathlib import Path

from pypdf import PdfReader

from logging_config import configure_logging

logger = logging.getLogger(__name__)

# Caminhos calculados a partir deste arquivo, para funcionar de qualquer cwd
ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
OUTPUT_FILE = ROOT_DIR / "data" / "processed" / "chunks.jsonl"

CHUNK_SIZE = 250  # tamanho de cada chunk, em caracteres
OVERLAP = 50      # quantos caracteres do chunk anterior se repetem no próximo


def extract_text(pdf_path):
    """Extrai o texto de todas as páginas do PDF, concatena e normaliza os espaços em branco."""
    reader = PdfReader(pdf_path)
    pages_text = []
    for page in reader.pages:
        # extract_text() pode retornar None em páginas sem texto (ex.: imagens)
        pages_text.append(page.extract_text() or "")
    full_text = " ".join(pages_text)
    return " ".join(full_text.split())


def read_text(path):
    """Lê o texto de um arquivo .pdf ou .txt (escolhido pelo sufixo); outro sufixo gera ValueError."""
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return extract_text(path)
    if suffix == ".txt":
        raw = Path(path).read_text(encoding="utf-8", errors="replace")
        return " ".join(raw.split())
    raise ValueError(f"Formato não suportado: {suffix}")


def split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """
    Divide o texto em chunks de `chunk_size` caracteres.
    Cada chunk novo começa `overlap` caracteres antes do fim do anterior,
    ou seja, o "passo" entre o início de um chunk e o próximo é chunk_size - overlap.
    Ex.: chunk_size=250, overlap=50 -> chunks começam em 0, 200, 400, 600...
    """
    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)
        # Se este chunk já chegou ao fim do texto, paramos
        if start + chunk_size >= len(text):
            break
    return chunks


def main():
    """Extrai o texto de cada PDF, gera os chunks e grava tudo em OUTPUT_FILE."""
    configure_logging()

    pdf_files = sorted(RAW_DIR.glob("*.pdf")) + sorted(RAW_DIR.glob("*.txt"))
    logger.info("Encontrados %d arquivos (.pdf/.txt) em %s", len(pdf_files), RAW_DIR)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    total_chunks = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for pdf_path in pdf_files:
            try:
                text = read_text(pdf_path)
            except Exception:
                # Um arquivo corrompido/ilegível não pode derrubar o lote inteiro
                logger.error("Falha ao ler %s, pulando arquivo", pdf_path.name, exc_info=True)
                continue

            chunks = split_into_chunks(text)

            for idx, chunk_text in enumerate(chunks):
                record = {
                    "id": f"{pdf_path.stem}_{idx}",  # id único: nome do arquivo + índice
                    "source_file": pdf_path.name,
                    "file_type": pdf_path.suffix.lower().lstrip("."),  # "pdf" ou "txt"
                    "chunk_idx": idx,
                    "char_count": len(chunk_text),
                    "text": chunk_text,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")

            total_chunks += len(chunks)
            logger.info("%s: %d chunks", pdf_path.name, len(chunks))

    logger.info("Total: %d chunks salvos em %s", total_chunks, OUTPUT_FILE)


if __name__ == "__main__":
    main()
