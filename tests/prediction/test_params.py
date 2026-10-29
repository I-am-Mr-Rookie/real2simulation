"""S12b parameter-transfer checks on visibly SYNTHETIC fixtures (plus committed ST03 record).

Not calibration, not Gate M (NOT_MET); 'g' is image-height/s^2, never m/s^2.
"""
import copy
import json
import math
import unittest
from pathlib import Path

from Build.real2sim import boundary as b
from Build.real2sim import params as p

ROOT = Path(__file__).resolve().parents[2]
SETUP = {"initial_height": 1.0, "dt": 0.001, "steps": 2000, "floorY": 0.0,
         "floorHalfExtents": [1.0, 0.1, 1.0], "sphereRadius": 0.05, "density": 1.0}


def synthetic_boundary(curve=3.0):
    # SYNTHETIC: y_norm = 0.1 + 0.6 t + 0.9*curve t^2 with +/-0.5 px alternating noise.
    frames = [{"frame_index": i, "pts_s": i / 30, "y_px": 100 + 20 * i + curve * i * i + (-1) ** i * 0.5}
              for i in range(12)]
    record = {"clip_id": "SYNTHETIC", "source_sha256": "a" * 64, "last_training_frame": 9,
              "height_px": 1000, "frames": frames}
    return b.split(record)[0]


def synthetic_records():
    gs = p.from_fit(synthetic_boundary(), "synthetic")
    src = {"input_provenance": "synthetic", "method": "SYNTHETIC authored fixture", "source_sha256": "b" * 64}
    return gs + [p.parameter("friction", 0.4, 0.05, src), p.parameter("restitution", 0.6, 0.1, src)]


class ParamsTests(unittest.TestCase):
    def test_fit_records_carry_value_uncertainty_provenance(self):
        boundary = synthetic_boundary()
        g, speed = p.from_fit(boundary, "synthetic")
        self.assertEqual((g["name"], g["unit"], speed["unit"]), ("g", "image-height/s^2", "image-height/s"))
        for r in (g, speed):
            self.assertGreater(r["uncertainty"], 0)
            self.assertEqual(r["gate_m"], "NOT_MET")
            self.assertEqual(r["provenance"]["boundary_training_sha256"], boundary.training_sha256)
            self.assertEqual(len(r["provenance"]["fit_sha256"]), 64)
        self.assertLess(abs(g["value"] - 5.4), 4 * g["uncertainty"] + 0.2)
        self.assertLess(abs(speed["value"] - 0.6), 4 * speed["uncertainty"] + 0.05)
        self.assertNotIn("m/s", json.dumps([g, speed]))

    def test_linear_motion_abstains_and_transfer_refuses(self):
        records = p.from_fit(synthetic_boundary(curve=0.0), "synthetic")
        self.assertTrue(all("abstained" in r for r in records))
        with self.assertRaisesRegex(ValueError, "refused"):
            p.transfer(records + synthetic_records()[2:])

    def test_missing_or_invalid_params_are_refused_not_defaulted(self):
        records = synthetic_records()
        with self.assertRaisesRegex(ValueError, r"refused.*friction"):
            p.transfer([r for r in records if r["name"] != "friction"])
        with self.assertRaisesRegex(ValueError, r"refused.*restitution"):
            p.transfer(records[:3] + [p.abstain("restitution", "no bounce")])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            p.transfer(records + records[:1])
        for field, bad in (("value", None), ("value", math.nan), ("uncertainty", -1.0), ("uncertainty", None)):
            broken = copy.deepcopy(records)
            broken[2][field] = bad
            with self.assertRaises(ValueError):
                p.transfer(broken)
        broken = copy.deepcopy(records)
        del broken[0]["provenance"]["source_sha256"]
        with self.assertRaisesRegex(ValueError, "provenance"):
            p.transfer(broken)

    def test_simulator_consumes_values_and_records_survive(self):
        records = synthetic_records()
        out = p.simulate(records, SETUP)
        self.assertEqual(out["gate_m"], "NOT_MET")
        for r in records:  # value, uncertainty and provenance unchanged through transfer
            self.assertEqual(out["parameters"][r["name"]], r)
        g, v = out["parameters"]["g"]["value"], out["parameters"]["speed"]["value"]
        physics = out["simulator_input"]["physics"]
        self.assertEqual((physics["friction"], physics["restitution"]), (0.4, 0.6))
        samples = out["simulation"]["samples"]
        self.assertTrue(samples[-1]["contact"])
        for s in samples[::250]:  # RK4 is exact for constant g: proves g and speed were used
            t = s["time_s"]
            self.assertAlmostEqual(s["position_m"][1], 1.0 - v * t - 0.5 * g * t * t, places=9)

    def test_simulator_rejection_and_nonsynthetic_refusal_surface(self):
        records = synthetic_records()
        records[3] = p.parameter("restitution", 1.5, 0.1, records[3]["provenance"])
        with self.assertRaisesRegex(ValueError, r"simulator rejected.*restitution must be finite in \[0,1\]"):
            p.simulate(records, SETUP)  # proves restitution reaches the simulator unaltered
        real = synthetic_records()
        real[0]["provenance"]["input_provenance"] = "image-derived"
        with self.assertRaisesRegex(ValueError, "only synthetic"):
            p.simulate(real, SETUP)

    def test_committed_st03_params_abstain(self):
        record = json.loads((ROOT / "evidence/S12/params-ST03.json").read_text(encoding="utf-8"))
        self.assertEqual(record["gate_m"], "NOT_MET")
        self.assertFalse(record["simulated"])
        self.assertTrue(all("abstained" in r for r in record["parameters"]))
        self.assertIn("refused", record["transfer_refused"])


if __name__ == "__main__":
    unittest.main()
