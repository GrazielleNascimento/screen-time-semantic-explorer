import tempfile
import unittest
from pathlib import Path

from quality_report import render_report, write_report

PARAMS = {"collection": "my_collection", "model": "my-model",
          "contamination": 0.03, "n_estimators": 200, "random_state": 42}

BEFORE = {"total": 100, "n_anomalies": 3, "pct": 3.0, "score_min": -0.7,
          "score_median": -0.4, "score_max": -0.3, "by_pdf": {"a.pdf": 2, "b.pdf": 1}}
AFTER = {**BEFORE, "total": 97, "removed": 3, "n_anomalies": 0}
TOP = [{"id": "a_1", "source_file": "a.pdf", "chunk_idx": 1, "score": -0.7, "text": "plain text"}]


class RenderReportTest(unittest.TestCase):
    def test_has_before_and_after_sections_and_parameters(self):
        text = render_report(BEFORE, AFTER, TOP, PARAMS)

        self.assertIn("## Before cleaning", text)
        self.assertIn("## After cleaning", text)
        for expected in ("my_collection", "my-model", "contamination=0.03", "n_estimators=200", "random_state=42"):
            self.assertIn(expected, text)

    def test_numbers_match_input_and_before_minus_removed_equals_after(self):
        text = render_report(BEFORE, AFTER, TOP, PARAMS)

        self.assertIn("Total chunks: 100", text)
        self.assertIn("Anomalous chunks: 3 (3.00%)", text)
        self.assertIn("Chunks removed: 3", text)
        self.assertIn("Chunks remaining: 97", text)
        self.assertEqual(BEFORE["total"] - AFTER["removed"], AFTER["total"])

    def test_escapes_pipes_and_newlines_so_table_rows_stay_on_one_line(self):
        top = [{**TOP[0], "text": "left | right\nsecond line"}]

        text = render_report(BEFORE, AFTER, top, PARAMS)

        row = next(line for line in text.splitlines() if line.startswith("| a_1"))
        self.assertIn("left \\| right second line", row)

    def test_dry_run_has_no_removal_numbers(self):
        text = render_report(BEFORE, None, TOP, PARAMS)

        self.assertIn("Dry run", text)
        self.assertNotIn("Chunks remaining", text)


class WriteReportTest(unittest.TestCase):
    def test_writes_file_creating_missing_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "nested" / "report.md"

            write_report("# hello", path)

            self.assertEqual(path.read_text(encoding="utf-8"), "# hello")


if __name__ == "__main__":
    unittest.main()
