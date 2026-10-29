"""Synthetic Gate R checks + R-R counterexample regressions (F1-F6). Synthetic only; no scene claim."""
import copy
import tempfile
import unittest
from pathlib import Path

import gate_r as g
import scene_frame as sf
from test_scene_frame import synth_npz

ABC = ("A", "B", "C")


def clip(mpu=None, angle=None, gravity="estimated", floor="FIT"):
    return {"floor": {"status": floor}, "gravity": {"status": gravity, "reason": None if gravity == "estimated" else "iss"},
            "metric_scale": {"status": "calibrated" if mpu else "ABSTAIN", "metres_per_model_unit": mpu,
                             "missing_reference": None if mpu else "no ref"},
            "a4_plane_normal": {"status": "MEASURED" if angle is not None else "ABSTAIN",
                                "angle_to_gravity_deg": angle}}


JOBS = [{"app_id": "a", "scenes": ["A"], "function_s": 160, "lifetime_s": 190, "cost_usd": 0.06},
        {"app_id": "b", "scenes": ["B", "C"], "function_s": 178, "lifetime_s": 262, "cost_usd": 0.06}]


def ev(frames, jobs=JOBS):
    return g.evaluate(frames, jobs, cohort=ABC)


def ok3():
    return {c: clip(1.0, 1.0) for c in ABC}


class GateR(unittest.TestCase):
    def test_pass_when_measured_within_thresholds(self):
        r = ev({"A": clip(1.05, 2.0), "B": clip(0.95, 4.9), "C": clip(1.5, 9.0)})
        self.assertEqual(r["verdict"], "PASS")
        self.assertEqual(r["summary"]["qualifying_clips"], 2)
        self.assertEqual(r["clips"]["B"]["gpu"]["lifetime_min_amortized"], round(262 / 120, 3))
        self.assertEqual([f["kind"] for f in r["failures"]], ["measured_above_threshold"] * 2)

    def test_abstain_everywhere_fails_as_unmeasured(self):
        r = ev({"A": clip(), "B": clip(), "C": clip(gravity="ABSTAIN")})
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual(r["summary"]["gpu_passes"], 3)
        self.assertEqual([f["kind"] for f in r["failures"]], ["unmeasured"] * 5 + ["ineligible"])

    def test_slow_gpu_or_missing_timing_fails(self):
        slow = [{"app_id": "a", "scenes": ["A", "B"], "function_s": 300, "lifetime_s": 300, "cost_usd": 0}]
        r = ev(ok3(), slow)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual(r["summary"]["gpu_passes"], 0)  # A,B 5 min unamortized function; C no timing

    def test_f1_actual_producer_calibrated_status(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.npz"
            synth_npz(p)
            img = sf.load_views(p)[0]["pts_img"]
            ref = {"view": 0, "p0": (100, 100), "p1": (200, 300), "length_m": float(sf.np.linalg.norm(
                img[100, 100] - img[200, 300])), "length_sd_m": 0.001, "source": "synthetic"}
            a4 = {"view": 0, "corners": [[100, 100], [100, 140], [130, 140], [130, 100]], "source": "synthetic"}
            prod = sf.analyse(p, refs=[ref], a4_refs=[a4])
        r = ev({c: copy.deepcopy(prod) for c in ABC})   # end-to-end producer output, no hand-written status
        self.assertEqual(r["verdict"], "PASS")
        self.assertEqual(r["summary"]["qualifying_clips"], 3)

    def test_f2_fixed_cohort(self):
        f = ok3(); del f["C"]
        with self.assertRaises(ValueError):
            ev(f)
        f = ok3(); f["D"] = clip(2.0, 1.0)
        with self.assertRaises(ValueError):
            ev(f)
        with self.assertRaises(ValueError):
            g.evaluate(ok3(), JOBS)        # default cohort is RM02/RM04/RM05

    def test_disjoint_criteria_do_not_combine(self):
        r = ev({"A": clip(1.0, 9.0), "B": clip(1.0, 1.0), "C": clip(2.0, 1.0)})
        self.assertEqual((r["summary"]["scale_passes"], r["summary"]["orientation_passes"]), (2, 2))
        self.assertEqual(r["verdict"], "FAIL")

    def test_f3_no_floor_fails(self):
        r = ev({c: clip(1.0, 1.0, floor="ABSTAIN") for c in ABC})
        self.assertEqual(r["verdict"], "FAIL")
        self.assertTrue(all(f["kind"] == "ineligible" for f in r["failures"]))

    def test_f3_invalid_values_error(self):
        for angle in (-999.0, float("-inf"), float("nan"), 91.0):
            f = ok3(); f["A"]["a4_plane_normal"]["angle_to_gravity_deg"] = angle
            with self.assertRaises(ValueError):
                ev(f)
        for mpu in (float("inf"), -1.0):
            f = ok3(); f["A"]["metric_scale"]["metres_per_model_unit"] = mpu
            with self.assertRaises(ValueError):
                ev(f)
        jobs = copy.deepcopy(JOBS)
        jobs[0]["function_s"] = -60.0
        with self.assertRaises(ValueError):
            ev(ok3(), jobs)
        f = ok3(); f["A"]["metric_scale"]["status"] = "FIT"   # unknown producer status
        with self.assertRaises(ValueError):
            ev(f)

    def test_f4_gpu_compared_before_rounding(self):
        jobs = copy.deepcopy(JOBS)
        jobs[0]["function_s"] = jobs[0]["lifetime_s"] = 240.029
        self.assertFalse(ev(ok3(), jobs)["clips"]["A"]["gpu_pass"])
        jobs[0]["function_s"] = jobs[0]["lifetime_s"] = 240.0
        self.assertTrue(ev(ok3(), jobs)["clips"]["A"]["gpu_pass"])

    def test_f5_abstained_gravity_reason(self):
        f = ok3(); f["A"] = clip(1.0, 1.0, gravity="ABSTAIN")
        fail = [x for x in ev(f)["failures"] if x["clip"] == "A"]
        self.assertEqual([x["kind"] for x in fail], ["ineligible"])
        self.assertIn("gravity ABSTAIN", fail[0]["reason"])

    def test_f6_inclusive_scale_boundary(self):
        for ratio in (0.9, 1.1):
            self.assertEqual(ev({c: clip(1.0 / ratio, 1.0) for c in ABC})["verdict"], "PASS")
        for ratio in (0.8999, 1.1001):
            self.assertEqual(ev({c: clip(1.0 / ratio, 1.0) for c in ABC})["verdict"], "FAIL")
        for angle, want in ((5.0, True), (5.00001, False)):
            f = ok3(); f["A"] = clip(1.0, angle)
            self.assertEqual(ev(f)["clips"]["A"]["orientation_pass"], want)


if __name__ == "__main__":
    unittest.main()
