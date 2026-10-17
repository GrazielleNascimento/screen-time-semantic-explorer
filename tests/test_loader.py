import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import loader


class ReadTextTest(unittest.TestCase):
    def test_reads_utf8_txt_keeping_accents_and_normalizing_spaces(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "note.txt"
            path.write_text("Crianças  e\n adolescentes: ação", encoding="utf-8")

            self.assertEqual(loader.read_text(path), "Crianças e adolescentes: ação")

    def test_routes_pdf_to_the_pdf_extractor(self):
        with patch("loader.extract_text", return_value="from pdf") as extractor:
            text = loader.read_text(Path("paper.pdf"))

        self.assertEqual(text, "from pdf")
        extractor.assert_called_once()

    def test_unsupported_suffix_raises_value_error(self):
        with self.assertRaises(ValueError):
            loader.read_text(Path("slides.docx"))


class MainFileTypeTest(unittest.TestCase):
    def test_chunks_have_file_type_txt_or_pdf(self):
        with tempfile.TemporaryDirectory() as folder:
            raw = Path(folder) / "raw"
            raw.mkdir()
            (raw / "a.txt").write_text("some plain text " * 30, encoding="utf-8")
            (raw / "b.pdf").write_bytes(b"")  # a extração é simulada abaixo
            output = Path(folder) / "chunks.jsonl"

            with patch("loader.RAW_DIR", raw), patch("loader.OUTPUT_FILE", output), \
                 patch("loader.extract_text", return_value="pdf words " * 30):
                loader.main()

            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            types = {row["source_file"]: row["file_type"] for row in rows}
            self.assertEqual(types, {"a.txt": "txt", "b.pdf": "pdf"})


if __name__ == "__main__":
    unittest.main()
