"""
anomaly.py - Detecção de anomalias com Isolation Forest.

O modelo recebe TODOS os embeddings de uma vez: um chunk só é anômalo em
relação ao conjunto. Cada chunk ganha uma nota (score); quanto mais baixa,
mais anômalo.
"""

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest

# Fração do corpus que o modelo assume ser anômala (define o corte do predict)
CONTAMINATION = 0.03
N_ESTIMATORS = 200  # número de árvores
RANDOM_STATE = 42


@dataclass
class AnomalyResult:
    """Resultado por chunk, alinhado com a ordem dos embeddings."""

    scores: np.ndarray       # nota de cada chunk (mais baixa = mais anômalo)
    is_anomaly: np.ndarray   # True onde predict == -1

    def ranked_indices(self) -> list[int]:
        """Índices ordenados do chunk mais anômalo para o menos anômalo."""
        return [int(i) for i in np.argsort(self.scores)]


def detect_anomalies(
    embeddings: np.ndarray,
    contamination: float = CONTAMINATION,
    n_estimators: int = N_ESTIMATORS,
    random_state: int = RANDOM_STATE,
) -> AnomalyResult:
    """Treina o Isolation Forest com todos os embeddings e pontua cada chunk."""
    model = IsolationForest(
        contamination=contamination,
        n_estimators=n_estimators,
        random_state=random_state,
    )
    model.fit(embeddings)
    return AnomalyResult(
        scores=model.score_samples(embeddings),
        is_anomaly=model.predict(embeddings) == -1,
    )
