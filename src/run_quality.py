"""
run_quality.py - Orquestra o controle de qualidade do banco vetorial.

Passos:
    1. Abre a collection e carrega todos os embeddings.
    2. Roda o Isolation Forest e grava o relatório com o "antes".
    3. Remove os chunks anômalos do banco (a não ser com --dry-run).
    4. Recarrega o banco e grava o relatório final (antes + depois).

Uso:
    python src/run_quality.py
    python src/run_quality.py --dry-run
"""

import argparse
import logging
import sys

import numpy as np

from anomaly import CONTAMINATION, N_ESTIMATORS, RANDOM_STATE, AnomalyResult, detect_anomalies
from embedder import COLLECTION_NAME
from logging_config import configure_logging
from quality_report import (
    REMOVED_IDS_FILE,
    REPORT_FILE,
    build_stats,
    build_top_anomalies,
    read_removed_ids,
    render_report,
    write_removed_ids,
    write_report,
)
from store import Corpus, IndexNotFoundError, delete_ids, load_corpus, open_collection

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2 (ONNX, ChromaDB default)"


def build_after_stats(corpus_after: Corpus, scores_by_id: dict[str, float], removed: int) -> dict:
    """Estatísticas do banco depois da limpeza, usando as notas originais dos chunks que ficaram."""
    scores = np.array([scores_by_id[chunk_id] for chunk_id in corpus_after.ids])
    result = AnomalyResult(scores=scores, is_anomaly=np.zeros(len(scores), dtype=bool))
    stats = build_stats(corpus_after, result)
    stats["removed"] = removed
    return stats


def main() -> int:
    """Executa o fluxo completo; devolve o código de saída do processo."""
    configure_logging()
    parser = argparse.ArgumentParser(description="Isolation Forest quality check")
    parser.add_argument("--dry-run", action="store_true", help="detect and report only, do not delete")
    args = parser.parse_args()

    try:
        collection = open_collection()
    except IndexNotFoundError as error:
        logger.error("%s", error)
        return 1

    corpus = load_corpus(collection)
    result = detect_anomalies(corpus.embeddings)
    params = {
        "collection": COLLECTION_NAME,
        "model": MODEL_NAME,
        "contamination": CONTAMINATION,
        "n_estimators": N_ESTIMATORS,
        "random_state": RANDOM_STATE,
    }
    before = build_stats(corpus, result)
    top = build_top_anomalies(corpus, result)

    if REPORT_FILE.exists():
        logger.warning("Sobrescrevendo relatório anterior: %s", REPORT_FILE)
    write_report(render_report(before, None, top, params), REPORT_FILE)

    if args.dry_run:
        logger.info("Dry run: %d anômalos detectados, nada foi removido", before["n_anomalies"])
        return 0

    # Salva os ids antes de apagar (auditoria); acumula com execuções anteriores
    ids_to_remove = [cid for cid, flagged in zip(corpus.ids, result.is_anomaly) if flagged]
    write_removed_ids(read_removed_ids(REMOVED_IDS_FILE) + ids_to_remove, REMOVED_IDS_FILE)
    removed = delete_ids(collection, ids_to_remove)

    corpus_after = load_corpus(collection)
    scores_by_id = dict(zip(corpus.ids, result.scores))
    after = build_after_stats(corpus_after, scores_by_id, removed)
    write_report(render_report(before, after, top, params), REPORT_FILE)
    logger.info("Chunks: %d antes, %d removidos, %d depois", before["total"], removed, after["total"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
