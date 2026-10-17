import unittest

from search import to_records

RAW_ANSWER = {
    "documents": [["first text", "second text"]],
    "metadatas": [[{"source_file": "a.pdf", "chunk_idx": 4}, {"source_file": "b.pdf", "chunk_idx": 9}]],
    "distances": [[0.1, 0.5]],
}


class ToRecordsTest(unittest.TestCase):
    def test_converts_raw_chroma_answer_into_list_of_dicts(self):
        records = to_records(RAW_ANSWER)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["text"], "first text")
        self.assertEqual(records[0]["source_file"], "a.pdf")
        self.assertEqual(records[0]["chunk_idx"], 4)
        self.assertEqual(records[0]["distance"], 0.1)
        self.assertEqual(records[1]["source_file"], "b.pdf")

    def test_records_carry_only_objective_values(self):
        records = to_records(RAW_ANSWER)

        self.assertEqual(set(records[0]), {"text", "source_file", "chunk_idx", "distance"})

    def test_empty_answer_gives_empty_list(self):
        empty = {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        self.assertEqual(to_records(empty), [])


if __name__ == "__main__":
    unittest.main()
