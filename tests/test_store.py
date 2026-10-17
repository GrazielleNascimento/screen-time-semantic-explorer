import unittest
from unittest.mock import patch

import chromadb
import numpy as np

from store import IndexNotFoundError, delete_ids, load_corpus, open_collection
from tests.helpers import make_collection


class LoadCorpusTest(unittest.TestCase):
    def setUp(self):
        self.embeddings = np.random.default_rng(0).normal(size=(5, 4)).astype(np.float32)
        self.collection = make_collection(self.embeddings)

    def test_returns_float32_embeddings_with_n_by_dim_shape(self):
        corpus = load_corpus(self.collection)

        self.assertEqual(corpus.embeddings.dtype, np.float32)
        self.assertEqual(corpus.embeddings.shape, (5, 4))

    def test_keeps_ids_embeddings_documents_and_metadatas_aligned(self):
        corpus = load_corpus(self.collection)

        for i, chunk_id in enumerate(corpus.ids):
            original = int(chunk_id[1:])
            self.assertEqual(corpus.documents[i], f"text {original}")
            self.assertEqual(corpus.metadatas[i]["chunk_idx"], original)
            np.testing.assert_allclose(corpus.embeddings[i], self.embeddings[original], atol=1e-5)


class DeleteIdsTest(unittest.TestCase):
    def setUp(self):
        self.collection = make_collection(np.random.default_rng(0).normal(size=(5, 4)))

    def test_removes_only_requested_ids_and_returns_count(self):
        removed = delete_ids(self.collection, ["c1", "c3"])

        self.assertEqual(removed, 2)
        self.assertEqual(sorted(self.collection.get()["ids"]), ["c0", "c2", "c4"])

    def test_empty_list_removes_nothing(self):
        removed = delete_ids(self.collection, [])

        self.assertEqual(removed, 0)
        self.assertEqual(self.collection.count(), 5)


class OpenCollectionTest(unittest.TestCase):
    def test_missing_or_empty_collection_raises_error_mentioning_embedder(self):
        client = chromadb.EphemeralClient()
        empty = client.get_or_create_collection("screen_time_empty_test", embedding_function=None)
        cases = {
            "missing": ("collection_that_does_not_exist", None),
            "empty": ("screen_time_empty_test", empty),
        }
        for label, (name, _) in cases.items():
            with self.subTest(label):
                with patch("store.get_client", return_value=client), \
                     patch("store.COLLECTION_NAME", name), \
                     patch("store.get_embedding_function", return_value=None):
                    with self.assertRaises(IndexNotFoundError) as ctx:
                        open_collection()
                self.assertIn("embedder.py", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
