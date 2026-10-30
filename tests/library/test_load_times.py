"""S18i timing summary math; the full HTTP benchmark is evidence, not a unit test (≈4 min)."""
import unittest
from unittest import mock

from Build.library import load_times
from Build.library.load_times import stats


class StatsTests(unittest.TestCase):
    def test_nearest_rank_summary(self):
        self.assertEqual(stats([5.0, 1.0, 3.0]), {"n": 3, "median_ms": 3.0, "p95_ms": 5.0, "max_ms": 5.0})
        twenty = stats([float(i) for i in range(1, 21)])
        self.assertEqual((twenty["median_ms"], twenty["p95_ms"]), (10.5, 19.0))

    def test_web_cold_open_and_summary(self):
        row = lambda a, e0: {"availability": a, "canMount": a == "playable", "open_ms": [20.0, 30.0],
                             "entry_ms": [e0, 1.0], "manifest_ms": [10.0, 10.0]}
        runs = [(500.0, {"cold_manifest_ms": c, "entries": {"p": row("playable", 5.0), "u": row("unavailable", 0.0)}})
                for c in (2990.0, 100.0)]
        with mock.patch.object(load_times, "http", side_effect=runs) as http:
            out = load_times.measure_web(".", "guest.json", reps=2, cold_runs=2)
        self.assertIn("{port}", http.call_args.args[1])
        p = out["http"]["entries"]["p"]
        self.assertEqual(p["cold_open"]["max_ms"], 2995.0)
        self.assertTrue(p["under_3s_cold_max"] and p["under_3s_p95"])
        self.assertEqual(out["summary"]["openable_ids"], ["p"])
        self.assertFalse(out["summary"]["six_demo_target_met"])


if __name__ == "__main__":
    unittest.main()
