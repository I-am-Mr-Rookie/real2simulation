"""S12c: predictions come from the prefix only; held-out observations are never read."""
import dataclasses
import json
import math
import unittest
from pathlib import Path

from Build.real2sim import boundary as b
from Build.real2sim import params as p
from Build.real2sim import predict as pr

ROOT = Path(__file__).resolve().parents[2]


class Spy(tuple):
    """Sealed suffix row that logs any read of the held-out observation (index >= 2 or iteration)."""
    reads = []

    def __getitem__(self, k):
        if not isinstance(k, int) or k >= 2 or k < 0:
            Spy.reads.append(k)
        return super().__getitem__(k)

    def __iter__(self):
        Spy.reads.append("iter")
        return super().__iter__()


def synthetic(suffix_y):
    # SYNTHETIC: y_px = 100 + 20 i + 3 i^2 (+/-0.5 px noise) on frames 0..9; suffix y_px authored per test.
    frames = [{"frame_index": i, "pts_s": i / 30, "y_px": 100 + 20 * i + 3 * i * i + (-1) ** i * 0.5}
              for i in range(10)] + [{"frame_index": 10 + k, "pts_s": (10 + k) / 30, "y_px": y}
                                     for k, y in enumerate(suffix_y)]
    return b.split({"clip_id": "SYNTHETIC", "source_sha256": "a" * 64, "last_training_frame": 9,
                    "height_px": 1000, "frames": frames})


def spied(sealed):
    Spy.reads = []
    return tuple(Spy(r) for r in sealed)


class PredictTests(unittest.TestCase):
    def test_projectile_never_reads_heldout_and_is_hashed_before_scoring(self):
        boundary, sealed = synthetic([500, 520, 999])
        rows = spied(sealed)
        pred = pr.projectile(boundary, rows)
        self.assertEqual(Spy.reads, [])  # no held-out value touched while predicting
        pr.check(pred)
        b.verify(boundary, rows)  # scoring-stage integrity check DOES read them -> spy is live
        self.assertTrue(Spy.reads)
        self.assertEqual([r[0] for r in pred.trace], [10, 11, 12])
        for i, t, y, s in pred.trace:  # authored curve: y = 0.1 + 0.6 t + 2.7 t^2 (image heights)
            self.assertAlmostEqual(y, 0.1 + 0.6 * t + 2.7 * t * t, delta=3 * s)
            self.assertTrue(s > 0)

    def test_prediction_identical_whatever_the_heldout_values(self):
        a = pr.projectile(*synthetic([500, 520, 540]))
        c = pr.projectile(*synthetic([1, 2, 3]))
        self.assertEqual((a.trace, a.sha256), (c.trace, c.sha256))

    def test_trace_is_immutable_and_tamper_or_reseal_refused(self):
        boundary, sealed = synthetic([500, 520, 540])
        pred = pr.projectile(boundary, sealed)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            pred.trace = ()
        with self.assertRaises(TypeError):
            pred.trace[0][2] = 0.0
        with self.assertRaisesRegex(ValueError, "changed after hashing"):
            pr.check(dataclasses.replace(pred, trace=pred.trace[:1]))
        with self.assertRaisesRegex(ValueError, "frozen seal"):
            pr.projectile(boundary, sealed[:-1])

    def test_synthetic_bounce_reflects_with_restitution_without_reading_heldout(self):
        boundary, sealed = synthetic([0] * 20)
        src = {"input_provenance": "synthetic", "method": "SYNTHETIC authored fixture", "source_sha256": "b" * 64}
        e = p.parameter("restitution", 0.5, 0.0, src)
        floor = 0.95
        rows = spied(sealed)
        pred = pr.bounce(boundary, rows, e, floor)
        self.assertEqual(Spy.reads, [])
        pr.check(pred)
        ys = [r[2] for r in pred.trace]
        self.assertTrue(all(y <= floor for y in ys))
        low = ys.index(min(ys[ys.index(max(ys)):]))  # first apex after the first floor contact
        self.assertLess(ys[low], floor)
        # Exact rebound apex for e=0.5: rise = e^2 * v_hit^2 / (2 g) from the prefix fit's own g, v.
        c0, c1, c2 = b.fit_prefix(boundary, (2,)).candidates[0].coefficients
        v_hit = math.sqrt(c1 * c1 + 4 * c2 * (floor - c0))
        self.assertLessEqual(floor - min(ys[ys.index(max(ys)):]), 0.25 * v_hit ** 2 / (4 * c2) + 1e-12)
        self.assertIn("synthetic", pred.model)

    def test_committed_st03_prediction(self):
        record, suffix, _ = pr.st03_record(ROOT)
        boundary, sealed = b.split(record, suffix)
        regen = pr.projectile(boundary, sealed)  # regenerates byte-identical v2 prediction
        for name, commitment in (("prediction-ST03.json", pr.LEGACY), ("prediction-ST03-v2.json", pr.COMMITMENT)):
            rec = json.loads((ROOT / "evidence/S12" / name).read_text(encoding="utf-8"))
            self.assertEqual(rec["gate_m"], "NOT_MET")
            self.assertFalse(rec["suffix_observations_read"])
            self.assertIsNone(rec["boundary"]["suffix_observation_sha256"])
            trace = tuple(tuple(r) for r in rec["prediction"]["trace"])
            self.assertEqual(len(trace), rec["boundary"]["suffix_count"])
            p = pr.Prediction(**dict(rec["prediction"], trace=trace))
            pr.check(p)
            self.assertEqual(p.commitment, commitment)
            # v1 kept untouched (legacy-audited); v2 re-commits the same frozen trace
            self.assertEqual(pr.commitment_sha256(dataclasses.replace(regen, commitment=commitment)), p.sha256)
            self.assertEqual(p.trace, regen.trace)
            self.assertEqual([r["name"] for r in rec["parameters"] if "abstained" not in r], ["g", "speed"])
        pr.require_v2(p, boundary)
        with self.assertRaisesRegex(ValueError, "legacy"):
            pr.require_v2(pr.Prediction(**dict(json.loads((ROOT / "evidence/S12/prediction-ST03.json").read_text(
                encoding="utf-8"))["prediction"], trace=trace)), boundary)


if __name__ == "__main__":
    unittest.main()
