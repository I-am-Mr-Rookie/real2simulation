"""SYNTHETIC S12a boundary checks; not clip, calibration or Gate M evidence."""
import json
import unittest
from dataclasses import replace
from unittest.mock import patch

from Build.real2sim import boundary as b

NOT_MET = "NOT_MET_INPUT_READINESS"


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.data = b.synthetic_fixture()
        self.boundary, self.held_out = b.split(self.data, NOT_MET)

    def test_split_freezes_prefix_and_commits_suffix_before_fit(self):
        self.assertEqual([f.frame_index for f in self.boundary.training], list(range(12)))
        self.assertEqual([f.frame_index for f in self.held_out], list(range(12, 18)))
        self.assertEqual(self.boundary.held_out_sha256, b.digest(self.held_out))
        self.data["frames"][0]["x_px"] = 999.0
        self.data["frames"][-1]["y_px"] = 999.0
        self.assertEqual(self.boundary.training[0].x_px, 100.0)
        self.assertEqual(self.boundary.held_out_sha256, b.digest(self.held_out))
        with self.assertRaises(Exception):
            self.boundary.training[0].x_px = 1.0

    def test_fitter_never_sees_suffix(self):
        seen = []
        real = b.fit_motion
        def spy(times, positions, degree=2, **kw):
            seen.append(list(times))
            return real(times, positions, degree, **kw)
        with patch.object(b, "fit_motion", spy):
            b.fit_prefix(self.boundary)
        t0 = self.boundary.training[0].pts_s
        suffix_times = {f.pts_s - t0 for f in self.held_out}
        self.assertEqual(len(seen), 2)
        for times in seen:
            self.assertEqual(len(times), 12)
            self.assertFalse(suffix_times & set(times))
        self.assertFalse(hasattr(self.boundary, "held_out"))

    def test_tampered_or_substituted_suffix_or_prefix_rejected(self):
        fitted = b.fit_prefix(self.boundary)
        moved = (replace(self.held_out[0], y_px=self.held_out[0].y_px + 1),) + self.held_out[1:]
        for bad in (moved, self.held_out[:-1], self.held_out + self.held_out[-1:]):
            with self.assertRaises(ValueError):
                b.evaluate(self.boundary, fitted, bad)
        forged = replace(self.boundary, training=self.boundary.training[:-1] + (
            replace(self.boundary.training[-1], x_px=0.0),))
        with self.assertRaises(ValueError):
            b.fit_prefix(forged)
        other, _ = b.split(dict(self.data, last_training_frame=13), NOT_MET)
        with self.assertRaises(ValueError):
            b.evaluate(other, fitted, self.held_out)

    def test_exact_quadratic_extrapolates_and_error_is_scale_free(self):
        result = b.evaluate(self.boundary, b.fit_prefix(self.boundary), self.held_out)
        self.assertLess(result["max"], 1e-9)
        self.assertEqual(result["unit"], "dimensionless")
        self.assertIn("NOT_MET", result["gate_m_notice"])
        def bent(scale):
            data = b.synthetic_fixture()
            for f in data["frames"]:
                f["x_px"] *= scale
                f["y_px"] *= scale
            data["frames"][-1]["y_px"] += 20 * scale
            bd, ho = b.split(data, NOT_MET)
            return b.evaluate(bd, b.fit_prefix(bd), ho)["max"]
        self.assertGreater(bent(1), 0.01)
        self.assertAlmostEqual(bent(0.5), bent(1), places=9)

    def test_gate_m_required_and_never_met(self):
        for status in (None, "", "MET", "PASSED"):
            with self.assertRaises(ValueError):
                b.split(b.synthetic_fixture(), status)
        record = self.boundary.record()
        self.assertEqual(record["gate_m_status"], NOT_MET)
        text = json.dumps(record)
        for f in self.held_out:
            self.assertNotIn(repr(f.y_px), text)

    def test_leaky_or_short_split_rejected_by_reused_validator(self):
        for split_at in (1, 17, 99):
            with self.assertRaises(ValueError):
                b.split(dict(b.synthetic_fixture(), last_training_frame=split_at), NOT_MET)

    def test_degenerate_prefix_abstains(self):
        data = b.synthetic_fixture()
        for f in data["frames"]:
            f["x_px"], f["y_px"] = 5.0, 5.0
        bd, _ = b.split(data, NOT_MET)
        with self.assertRaises(b.FitAbstention):
            b.fit_prefix(bd)


if __name__ == "__main__":
    unittest.main()
