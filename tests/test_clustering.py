import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from clustering import cached_projection, cluster, project_2d, summarize_clusters


def three_blobs(n_per_blob: int = 15) -> np.ndarray:
    rng = np.random.default_rng(0)
    centers = rng.normal(size=(3, 32)) * 5
    return np.vstack([c + rng.normal(size=(n_per_blob, 32)) * 0.1 for c in centers]).astype(np.float32)


class ClusterTest(unittest.TestCase):
    def test_returns_one_label_per_point_and_n_distinct_labels(self):
        points = three_blobs()

        labels = cluster(points, n_clusters=3, random_state=42)

        self.assertEqual(len(labels), len(points))
        self.assertEqual(len(set(labels.tolist())), 3)

    def test_points_of_the_same_blob_share_a_cluster(self):
        labels = cluster(three_blobs(15), n_clusters=3, random_state=42)

        for blob in range(3):
            self.assertEqual(len(set(labels[blob * 15:(blob + 1) * 15].tolist())), 1)


class ProjectionTest(unittest.TestCase):
    def test_project_2d_returns_n_by_2_coordinates(self):
        coords = project_2d(three_blobs(), random_state=42)

        self.assertEqual(coords.shape, (45, 2))

    def test_cache_is_reused_and_recomputed_when_point_count_changes(self):
        fake = lambda embeddings, random_state: np.zeros((len(embeddings), 2))
        with tempfile.TemporaryDirectory() as folder, \
             patch("clustering.project_2d", side_effect=fake) as projector:
            cache = Path(folder) / "coords.npy"

            cached_projection(np.zeros((10, 4)), cache)
            cached_projection(np.zeros((10, 4)), cache)
            self.assertEqual(projector.call_count, 1)

            coords = cached_projection(np.zeros((12, 4)), cache)
            self.assertEqual(projector.call_count, 2)
            self.assertEqual(coords.shape, (12, 2))


class SummarizeClustersTest(unittest.TestCase):
    def test_returns_size_terms_and_main_pdfs_per_cluster(self):
        documents = ["sleep bedtime night sleep"] * 3 + ["obesity weight diet obesity"] * 2
        metadatas = [{"source_file": "sleep.pdf"}] * 3 + [{"source_file": "diet.pdf"}] * 2
        labels = np.array([0, 0, 0, 1, 1])

        summaries = summarize_clusters(labels, documents, metadatas, top_n=2)

        self.assertEqual([s.size for s in summaries], [3, 2])
        self.assertIn("sleep", summaries[0].top_terms)
        self.assertIn("obesity", summaries[1].top_terms)
        self.assertEqual(summaries[0].top_pdfs[0], ("sleep.pdf", 3))
        self.assertEqual(summaries[1].top_pdfs[0], ("diet.pdf", 2))


if __name__ == "__main__":
    unittest.main()
