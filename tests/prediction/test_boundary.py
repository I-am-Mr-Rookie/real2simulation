"""S12a boundary checks on visibly synthetic fixtures (plus committed ST03 record).

Not calibration, not Gate M (NOT_MET), no physical-accuracy claim.
"""
import copy
import dataclasses
import json
import unittest
from pathlib import Path
from unittest import mock

from Build.real2sim import boundary as b

ROOT = Path(__file__).resolve().parents[2]


def fixture(last=5, n=10):
    return {"clip_id": "SYNTHETIC", "source_sha256": "a" * 64, "last_training_frame": last,
            "height_px": 1000,
            "frames": [{"frame_index": i, "pts_s": i / 30, "x_px": 10.0,
                        "y_px": 100 + 20 * i + 3 * i * i} for i in range(n)]}


class BoundaryTests(unittest.TestCase):
    def test_split_keeps_suffix_values_out_of_boundary(self):
        boundary, sealed = b.split(fixture())
        self.assertEqual([f[0] for f in boundary.training], list(range(6)))
        self.assertEqual([f[0] for f in sealed], [6, 7, 8, 9])
        self.assertEqual(boundary.suffix_count, 4)
        text = repr(boundary)
        for _, pts, y in sealed:
            self.assertNotIn(repr(y), text)
        self.assertEqual(boundary.gate_m, "NOT_MET")

    def test_fitter_never_sees_suffix(self):
        boundary, sealed = b.split(fixture())
        with mock.patch.object(b, "select_model", wraps=b.select_model) as spy:
            fit = b.fit_prefix(boundary)
        times, positions = spy.call_args.args[:2]
        self.assertEqual(len(times), 6)
        self.assertLess(max(times), sealed[0][1] - boundary.training[0][1])
        suffix_y = {y for *_, y in sealed}
        self.assertFalse(suffix_y & set(positions))
        # Arbitrary suffix values cannot change the fit.
        tampered = fixture()
        for f in tampered["frames"][6:]:
            f["y_px"] = 999.0
        other = b.fit_prefix(b.split(tampered)[0])
        self.assertEqual(fit.selected_degree, other.selected_degree)
        self.assertEqual(fit.candidates[1].coefficients, other.candidates[1].coefficients)

    def test_frozen_prefix_and_suffix_detect_tampering(self):
        boundary, sealed = b.split(fixture())
        b.verify(boundary, sealed)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            boundary.last_training_frame = 7
        cases = (sealed[:-1], sealed[:1] + ((7, 0.5, sealed[1][2]),) + sealed[2:],
                 sealed[:1] + ((sealed[1][0], sealed[1][1], 0.5),) + sealed[2:])
        for bad in cases:
            with self.assertRaises(ValueError):
                b.verify(boundary, bad)
        hacked = copy.copy(boundary)
        object.__setattr__(hacked, "training", boundary.training + (sealed[0],))
        with self.assertRaisesRegex(ValueError, "training prefix"):
            b.verify(hacked, sealed)

    def test_untracked_suffix_identities_are_sealed(self):
        record = fixture(last=5, n=6)
        boundary, sealed = b.split(record, [(6, 0.2), (7, 7 / 30)])
        self.assertIsNone(boundary.suffix_observation_sha256)
        b.verify(boundary, sealed)
        with self.assertRaises(ValueError):
            b.verify(boundary, [(6, 0.2), (8, 0.3)])

    def test_invalid_or_leaking_splits_rejected(self):
        prefix_only = fixture(last=5, n=6)
        bad = (
            (fixture(last=1), None),                      # <3 training frames
            (prefix_only, None),                          # empty suffix
            (prefix_only, [(5, 0.3)]),                    # index overlap
            (prefix_only, [(6, 5 / 30)]),                 # PTS overlap
            (prefix_only, [(7, 0.3), (6, 0.4)]),          # not increasing
            (fixture(), [(10, 1.0)]),                     # observations AND identities
            (fixture(last=4) | {"last_training_frame": 4.0}, None),
        )
        for record, ids in bad:
            with self.assertRaises(ValueError):
                b.split(record, ids)
        swapped = fixture()
        swapped["frames"][3]["pts_s"] = 0.0
        with self.assertRaises(ValueError):
            b.split(swapped)

    def test_outputs_say_gate_m_not_met_and_no_g(self):
        out = b.record_json(b.split(fixture())[0])
        self.assertEqual(out["gate_m"], "NOT_MET")
        self.assertNotIn("g_m_s2", json.dumps(out))

    def test_committed_st03_record(self):
        out = json.loads((ROOT / "evidence/S12/boundary-ST03.json").read_text("utf-8"))
        self.assertEqual(out["gate_m"], "NOT_MET")
        self.assertEqual(out["gate_m_source"]["status"], "NOT_MET_INPUT_READINESS")
        self.assertFalse(out["fit_run"])
        self.assertEqual(out["boundary"]["last_training_frame"], 76)
        self.assertEqual(out["quarantined_suffix_frames"], [77])


if __name__ == "__main__":
    unittest.main()
