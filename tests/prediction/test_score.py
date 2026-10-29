"""S12e: Gate RS scoring verifies seal + committed sha BEFORE reading suffix observations."""
import dataclasses
import unittest

from Build.real2sim import boundary as b
from Build.real2sim import predict as pr
from Build.real2sim import score as s


def ids_only():
    # SYNTHETIC: y_px = 100 + 20 i + 3 i^2 on frames 0..9 (H=1000); suffix identities 10..14 only (untracked seal).
    frames = [{"frame_index": i, "pts_s": i / 30, "y_px": 100 + 20 * i + 3 * i * i} for i in range(10)]
    boundary, sealed = b.split({"clip_id": "SYNTHETIC", "source_sha256": "a" * 64, "last_training_frame": 9,
                                "height_px": 1000, "frames": frames}, [(i, i / 30) for i in range(10, 15)])
    return boundary, sealed, pr.projectile(boundary, sealed)


class ScoreTests(unittest.TestCase):
    def test_exact_truth_scores_zero_and_loader_runs_after_checks(self):
        boundary, sealed, pred = ids_only()
        calls = []
        truth = {i: (t, (100 + 20 * i + 3 * i * i) / 1000) for i, t in sealed}
        r = s.score(boundary, sealed, pred, pred.sha256, lambda: calls.append(1) or truth)
        self.assertEqual(calls, [1])
        self.assertLess(r["normalized_rms"], 1e-9)
        self.assertEqual((r["coverage"], r["scored"], r["gate_m"]), (1.0, True, "NOT_MET"))

    def test_tampered_seal_or_uncommitted_prediction_never_reads_suffix(self):
        boundary, sealed, pred = ids_only()
        never = lambda: self.fail("suffix read before verification")  # noqa: E731
        with self.assertRaises(ValueError):
            s.score(boundary, sealed[:-1], pred, pred.sha256, never)
        with self.assertRaises(ValueError):
            s.score(boundary, sealed, pred, "0" * 64, never)
        with self.assertRaises(ValueError):  # trace edited after hashing
            s.score(boundary, sealed, dataclasses.replace(pred, trace=pred.trace[:-1]), pred.sha256, never)

    def test_pts_mismatch_low_coverage_and_rms(self):
        boundary, sealed, pred = ids_only()
        with self.assertRaises(ValueError):
            s.score(boundary, sealed, pred, pred.sha256, lambda: {10: (10 / 30 + 0.01, 0.0)})
        rows = {i: (t, y + 0.1) for i, t, y, _ in pred.trace}  # constant 0.1 H offset
        r = s.score(boundary, sealed, pred, pred.sha256, lambda: rows)
        self.assertAlmostEqual(r["normalized_rms"], 0.1)
        r = s.score(boundary, sealed, pred, pred.sha256, lambda: {10: rows[10], 11: rows[11]})
        self.assertEqual((r["coverage"], r["scored"]), (0.4, False))

    def test_gate_needs_every_category(self):
        ok = {"scored": True, "normalized_rms": 0.01}
        self.assertEqual(s.gate({"projectile": ok})["status"], "NOT_MET")
        self.assertEqual(s.gate({"projectile": ok})["shortfall"], ["bounce", "pendulum"])
        g = s.gate({c: ok for c in s.CATEGORIES} | {"pendulum": {"scored": True, "normalized_rms": 0.5}})
        self.assertEqual((g["status"], g["median"]), ("MET", 0.01))


if __name__ == "__main__":
    unittest.main()
