import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

import run_quality
from tests.helpers import make_collection

OUTLIER_IDS = {"c100", "c101", "c102"}


def synthetic_embeddings() -> np.ndarray:
    """100 pontos agrupados + 3 pontos muito distantes (ids c100..c102)."""
    rng = np.random.default_rng(0)
    return np.vstack([rng.normal(size=(100, 8)) * 0.1, rng.normal(size=(3, 8)) * 0.1 + 50])


class RunQualityTest(unittest.TestCase):
    def setUp(self):
        self.collection = make_collection(synthetic_embeddings())
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.report = Path(self.folder.name) / "quality_report.md"
        self.removed_file = Path(self.folder.name) / "removed_ids.json"

    def run_main(self, *args: str) -> int:
        with patch("run_quality.open_collection", return_value=self.collection), \
             patch("run_quality.REPORT_FILE", self.report), \
             patch("run_quality.REMOVED_IDS_FILE", self.removed_file), \
             patch("sys.argv", ["run_quality.py", *args]):
            return run_quality.main()

    def test_dry_run_keeps_database_and_writes_only_before_section(self):
        exit_code = self.run_main("--dry-run")

        text = self.report.read_text(encoding="utf-8")
        self.assertEqual(exit_code, 0)
        self.assertEqual(self.collection.count(), 103)
        self.assertFalse(self.removed_file.exists())
        self.assertIn("## Before cleaning", text)
        self.assertIn("Dry run", text)
        self.assertNotIn("Chunks remaining", text)

    def test_full_run_removes_anomalies_and_saves_their_ids(self):
        self.run_main()

        removed = json.loads(self.removed_file.read_text(encoding="utf-8"))["removed_ids"]
        remaining = set(self.collection.get()["ids"])
        self.assertTrue(OUTLIER_IDS <= set(removed))
        self.assertEqual(len(removed) + len(remaining), 103)
        self.assertTrue(remaining.isdisjoint(removed))

    def test_full_run_report_has_before_and_after_with_matching_numbers(self):
        self.run_main()

        text = self.report.read_text(encoding="utf-8")
        removed = len(json.loads(self.removed_file.read_text(encoding="utf-8"))["removed_ids"])
        self.assertIn("Total chunks: 103", text)
        self.assertIn(f"Chunks removed: {removed}", text)
        self.assertIn(f"Chunks remaining: {103 - removed}", text)
        self.assertEqual(self.collection.count(), 103 - removed)


if __name__ == "__main__":
    unittest.main()
