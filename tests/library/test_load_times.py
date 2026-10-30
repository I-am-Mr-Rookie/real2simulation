"""S18i timing summary math; the full HTTP benchmark is evidence, not a unit test (≈4 min)."""
import unittest

from Build.library.load_times import stats


class StatsTests(unittest.TestCase):
    def test_nearest_rank_summary(self):
        self.assertEqual(stats([5.0, 1.0, 3.0]), {"n": 3, "median_ms": 3.0, "p95_ms": 5.0, "max_ms": 5.0})
        twenty = stats([float(i) for i in range(1, 21)])
        self.assertEqual((twenty["median_ms"], twenty["p95_ms"]), (10.5, 19.0))


if __name__ == "__main__":
    unittest.main()
