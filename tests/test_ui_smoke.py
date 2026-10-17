import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import streamlit as st
from streamlit.testing.v1 import AppTest

from store import IndexNotFoundError
from tests.helpers import make_collection

APP_FILE = str(Path(__file__).resolve().parent.parent / "app.py")


def metric_values(at: AppTest) -> list[str]:
    """Valores dos cards de métrica da página (o texto dentro de .metric-value)."""
    values = []
    for markdown in at.markdown:
        if 'class="metric-value"' in markdown.value:
            values.append(markdown.value.split('class="metric-value">')[1].split("<")[0])
    return values


class AppSmokeTest(unittest.TestCase):
    def setUp(self):
        # os caches do Streamlit são globais no processo: limpar evita vazar dados entre testes
        st.cache_data.clear()
        st.cache_resource.clear()

    def open_app(self, **open_collection_kwargs) -> AppTest:
        with patch("store.open_collection", **open_collection_kwargs), \
             patch("quality_report.read_removed_ids", return_value=["x", "y"]):
            return AppTest.from_file(APP_FILE, default_timeout=30).run()

    def test_opens_on_home_without_exception_and_shows_three_metrics(self):
        collection = make_collection(np.random.default_rng(0).normal(size=(5, 4)))

        at = self.open_app(return_value=collection)

        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.sidebar.radio[0].value, "Home")
        self.assertEqual(metric_values(at), ["5", "2", "2"])  # chunks, PDFs distintos, removidos

    def test_open_search_card_goes_to_search_page(self):
        collection = make_collection(np.random.default_rng(0).normal(size=(5, 4)))
        at = self.open_app(return_value=collection)

        with patch("store.open_collection", return_value=collection):
            next(b for b in at.button if b.label == "Open Search").click().run()

        self.assertEqual(at.sidebar.radio[0].value, "Search")
        self.assertEqual(at.title[0].value, "Search")

    def test_shows_index_not_found_instead_of_crashing_when_no_database(self):
        at = self.open_app(side_effect=IndexNotFoundError("missing"))

        self.assertEqual(len(at.exception), 0)
        self.assertIn("Index not found", at.error[0].value)


if __name__ == "__main__":
    unittest.main()
