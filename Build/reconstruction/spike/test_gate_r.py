"""Synthetic Gate R checks: thresholds, unmeasured -> failure (never pass), GPU amortisation."""
import unittest

import gate_r as g


def clip(mpu=None, angle=None, gravity="estimated"):
    return {"floor": {"status": "FIT"}, "gravity": {"status": gravity},
            "metric_scale": {"status": "FIT" if mpu else "ABSTAIN", "metres_per_model_unit": mpu,
                             "missing_reference": None if mpu else "no ref"},
            "a4_plane_normal": {"status": "MEASURED" if angle is not None else "ABSTAIN",
                                "angle_to_gravity_deg": angle}}


JOBS = [{"app_id": "a", "scenes": ["A"], "function_s": 160, "lifetime_s": 190, "cost_usd": 0.06},
        {"app_id": "b", "scenes": ["B", "C"], "function_s": 178, "lifetime_s": 262, "cost_usd": 0.06}]


class GateR(unittest.TestCase):
    def test_pass_when_measured_within_thresholds(self):
        r = g.evaluate({"A": clip(1.05, 2.0), "B": clip(0.95, 4.9), "C": clip(1.5, 9.0)}, JOBS)
        self.assertEqual(r["verdict"], "PASS")
        self.assertEqual(r["summary"]["scale_passes"], 2)
        self.assertEqual(r["clips"]["B"]["gpu"]["lifetime_min_amortized"], round(262 / 120, 3))
        self.assertEqual([f["kind"] for f in r["failures"]], ["measured_above_threshold"] * 2)

    def test_abstain_everywhere_fails_as_unmeasured(self):
        r = g.evaluate({"A": clip(), "B": clip(), "C": clip(gravity="ABSTAIN")}, JOBS)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual(r["summary"]["gpu_passes"], 3)
        self.assertTrue(all(f["kind"] == "unmeasured" for f in r["failures"]))
        self.assertEqual(len(r["failures"]), 6)

    def test_slow_gpu_or_missing_timing_fails(self):
        slow = [{"app_id": "a", "scenes": ["A", "B"], "function_s": 300, "lifetime_s": 300, "cost_usd": 0}]
        r = g.evaluate({"A": clip(1.0, 1.0), "B": clip(1.0, 1.0), "C": clip(1.0, 1.0)}, slow)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual(r["summary"]["gpu_passes"], 0)  # A,B 5 min unamortized function; C no timing


if __name__ == "__main__":
    unittest.main()
