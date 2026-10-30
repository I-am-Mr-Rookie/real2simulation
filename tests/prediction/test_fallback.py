import unittest

from Build.real2sim.fallback import decide, from_evidence, label
from Build.real2sim.score import gate


class Decide(unittest.TestCase):
    def test_thresholds(self):
        for m, tier in ((0.0, "SHOWN"), (0.05, "SHOWN"), (0.0500001, "SHOWN_WITH_ERROR"), (0.10, "SHOWN_WITH_ERROR"),
                        (0.1000001, "VIRTUAL_LAB_ONLY"), (0.198, "VIRTUAL_LAB_ONLY")):
            self.assertEqual(decide(m)["tier"], tier, m)
        self.assertEqual(decide(0.2)["error_label"], "measured")

    def test_unmeasured(self):
        for m in (None, float("nan"), float("inf"), -0.01, True, "0.01"):
            d = decide(m)
            self.assertEqual((d["tier"], d["real_scene_prediction"], d["error_label"]),
                             ("VIRTUAL_LAB_ONLY", "WITHHELD", "unmeasured"), m)

    def test_insufficient_coverage_gives_null_median(self):
        r = gate({"projectile": {"kind": "projectile", "scored": False, "coverage": 7 / 466}})
        self.assertIsNone(r["median"])
        self.assertEqual(decide(r["median"])["tier"], "VIRTUAL_LAB_ONLY")


class Labels(unittest.TestCase):
    doc = {"clip_id": "X", "units": "image-height fraction", "gate_m": "NOT_MET", "limits": ["l"]}

    def test_real_withheld_and_scale_unverified(self):
        lab = label(self.doc | {"provenance": "image-derived"}, decide(None))
        self.assertEqual((lab["display"], lab["trace_label"], lab["scale_label"], lab["error_label"]),
                         ("VIRTUAL_LAB_ONLY", "simulated", "SCALE_UNVERIFIED", "unmeasured"))
        self.assertIn("WITHHELD", lab["banner"])

    def test_synthetic_stays_synthetic(self):
        lab = label(self.doc | {"provenance": "synthetic"}, decide(0.01))
        self.assertEqual((lab["banner"], lab["display"]), ("SYNTHETIC", "VIRTUAL_LAB"))

    def test_current_evidence_withholds_real_prediction(self):
        doc, result = from_evidence()
        self.assertEqual(result["status"], "NOT_MET")
        self.assertEqual(decide(result["median"])["real_scene_prediction"], "WITHHELD")


if __name__ == "__main__":
    unittest.main()
