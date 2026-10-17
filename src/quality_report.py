"""
quality_report.py - Gera o relatório de qualidade em Markdown.

Funções puras: recebem os números já calculados e devolvem texto. Quem
chama (run_quality.py) decide quando ler o banco e quando gravar.
"""

import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np

from anomaly import AnomalyResult
from store import Corpus

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT_DIR / "reports"
REPORT_FILE = REPORTS_DIR / "quality_report.md"
REMOVED_IDS_FILE = REPORTS_DIR / "removed_ids.json"

TOP_N = 15          # quantos chunks mais anômalos entram na tabela
SNIPPET_CHARS = 150  # tamanho do trecho de texto mostrado na tabela

CURATION_NOTE = (
    "Not every flagged chunk is garbage: a short but legitimate passage can be "
    "flagged, and some noise can slip through. Review the table above before "
    "trusting the removal."
)


def build_stats(corpus: Corpus, result: AnomalyResult) -> dict:
    """Resume o corpus: total, anômalos, estatística das notas e anômalos por PDF."""
    by_pdf = Counter(
        meta["source_file"]
        for meta, flagged in zip(corpus.metadatas, result.is_anomaly)
        if flagged
    )
    n_anomalies = int(result.is_anomaly.sum())
    total = len(corpus.ids)
    return {
        "total": total,
        "n_anomalies": n_anomalies,
        "pct": 100 * n_anomalies / total if total else 0.0,
        "score_min": float(np.min(result.scores)),
        "score_median": float(np.median(result.scores)),
        "score_max": float(np.max(result.scores)),
        "by_pdf": dict(by_pdf),
    }


def build_top_anomalies(corpus: Corpus, result: AnomalyResult, n: int = TOP_N) -> list[dict]:
    """Os `n` chunks mais anômalos, com o que a tabela do relatório precisa."""
    top = []
    for i in result.ranked_indices()[:n]:
        top.append({
            "id": corpus.ids[i],
            "source_file": corpus.metadatas[i]["source_file"],
            "chunk_idx": corpus.metadatas[i]["chunk_idx"],
            "score": float(result.scores[i]),
            "text": corpus.documents[i],
        })
    return top


def _escape_cell(text: str) -> str:
    """Deixa o texto seguro para uma célula de tabela Markdown."""
    return " ".join(text.split()).replace("|", "\\|")


def _score_line(stats: dict) -> str:
    return (
        f"- Scores (min / median / max): {stats['score_min']:.4f} / "
        f"{stats['score_median']:.4f} / {stats['score_max']:.4f}"
    )


def render_report(before: dict, after: dict | None, top_anomalies: list[dict], params: dict) -> str:
    """Monta o texto do relatório. `after` é None quando nada foi removido (dry run)."""
    lines = [
        "# Quality Report",
        "",
        f"- Generated at: {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"- Collection: `{params['collection']}`",
        f"- Embedding model: {params['model']}",
        f"- Isolation Forest: contamination={params['contamination']}, "
        f"n_estimators={params['n_estimators']}, random_state={params['random_state']}",
        "",
        "## Before cleaning",
        "",
        f"- Total chunks: {before['total']}",
        f"- Anomalous chunks: {before['n_anomalies']} ({before['pct']:.2f}%)",
        _score_line(before),
        "",
        f"## Most anomalous chunks (top {len(top_anomalies)})",
        "",
        "Lower score = more anomalous.",
        "",
        "| id | PDF | chunk_idx | score | text |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in top_anomalies:
        snippet = _escape_cell(row["text"][:SNIPPET_CHARS])
        lines.append(
            f"| {row['id']} | {row['source_file']} | {row['chunk_idx']} | "
            f"{row['score']:.4f} | {snippet} |"
        )

    lines += ["", "## Anomalies per PDF", "", "| PDF | anomalous chunks |", "| --- | --- |"]
    for pdf, count in sorted(before["by_pdf"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {pdf} | {count} |")

    lines += ["", "## After cleaning", ""]
    if after is None:
        lines.append("Dry run: nothing was removed from the database.")
    else:
        lines += [
            f"- Chunks remaining: {after['total']}",
            f"- Chunks removed: {after['removed']}",
            _score_line(after) + " (original scores of the remaining chunks, not recomputed)",
            "- Database updated: yes (anomalous chunks deleted from the collection).",
        ]

    lines += ["", "## Curation note", "", CURATION_NOTE, ""]
    return "\n".join(lines)


def read_removed_ids(path: Path = REMOVED_IDS_FILE) -> list[str]:
    """Ids já removidos em execuções anteriores (lista vazia se o arquivo não existe)."""
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))["removed_ids"]


def write_removed_ids(ids: list[str], path: Path = REMOVED_IDS_FILE) -> None:
    """Grava a lista de ids removidos (auditoria)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"removed_ids": ids}, indent=2), encoding="utf-8")


def write_report(text: str, path: Path) -> None:
    """Grava o relatório em `path`, criando a pasta se preciso."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    logger.info("Relatório gravado em %s", path)
