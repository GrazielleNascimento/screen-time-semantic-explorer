import unittest

import numpy as np

from anomaly import detect_anomalies


def clustered_points(n: int = 100) -> np.ndarray:
    return np.random.default_rng(0).normal(size=(n, 16)).astype(np.float32) * 0.1


class DetectAnomaliesTest(unittest.TestCase):
    def test_flags_distant_point_as_anomaly(self):
        data = np.vstack([clustered_points(), np.full((1, 16), 50.0, dtype=np.float32)])

        result = detect_anomalies(data, contamination=0.02, n_estimators=100, random_state=42)

        self.assertTrue(result.is_anomaly[-1])

    def test_distant_point_gets_the_lowest_score(self):
        data = np.vstack([clustered_points(), np.full((1, 16), 50.0, dtype=np.float32)])

        result = detect_anomalies(data, contamination=0.02, n_estimators=100, random_state=42)

        self.assertEqual(int(np.argmin(result.scores)), len(data) - 1)
        self.assertEqual(result.ranked_indices()[0], len(data) - 1)

    def test_anomaly_fraction_is_close_to_contamination(self):
        data = clustered_points(400)

        result = detect_anomalies(data, contamination=0.05, n_estimators=100, random_state=42)

        self.assertAlmostEqual(result.is_anomaly.mean(), 0.05, delta=0.02)

    def test_same_random_state_gives_same_result(self):
        data = clustered_points()

        first = detect_anomalies(data, contamination=0.05, n_estimators=50, random_state=7)
        second = detect_anomalies(data, contamination=0.05, n_estimators=50, random_state=7)

        np.testing.assert_array_equal(first.scores, second.scores)
        np.testing.assert_array_equal(first.is_anomaly, second.is_anomaly)


if __name__ == "__main__":
    unittest.main()
