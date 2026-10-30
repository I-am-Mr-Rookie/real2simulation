import copy
import unittest

from Build.library.free_fall import ACCEPTANCE, RUN, simulated_demos
from Build.library.projectile import build
from Build.library.validate import ROOT, pointer, validate, validate_file
from contracts.scene.validate_scene import load_json


class ProjectileLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = ROOT / "test-data/library-artifacts"
        cls.path = cls.artifacts / "projectile.json"
        cls.manifest = load_json(cls.path)

    def reject(self, change, message=None):
        manifest = copy.deepcopy(self.manifest)
        change(manifest["demos"][0])
        with self.assertRaises(ValueError) as raised:
            validate(manifest, self.artifacts)
        if message:
            self.assertIn(message, str(raised.exception))

    def test_all_and_only_accepted_projectile_cases(self):
        self.assertEqual(validate_file(self.path), self.manifest)
        acceptance = load_json(ROOT / ACCEPTANCE)
        cases = [(i, c) for i, c in enumerate(acceptance["cases"])
                 if c["template"] == "projectile"]
        self.assertTrue(cases)
        self.assertEqual(len(self.manifest["demos"]), len(cases))
        for demo, (index, case) in zip(self.manifest["demos"], cases):
            self.assertEqual(demo["id"], "simulated-projectile-" + case["case"])
            self.assertEqual(demo["provenance"]["record_pointer"], f"/cases/{index}")
            self.assertEqual(demo["provenance"]["run_id"], RUN)
            self.assertEqual((self.artifacts / demo["artifact"]["path"]).read_bytes(),
                             (ROOT / ACCEPTANCE).read_bytes())
            for number in demo["provenance"]["numeric"]:
                self.assertEqual(number["value"], pointer(acceptance, number["pointer"]))
                self.assertEqual(number["label"], "simulated")

    def test_reuses_shared_object_and_builder_without_changing_free_fall(self):
        before = self.path.read_bytes()
        free_fall = (self.artifacts / "free-fall.json").read_bytes()
        objects = {p.name: p.read_bytes() for p in (self.artifacts / "objects/sha256").glob("*.json")}
        self.assertEqual(build(), self.path)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual((self.artifacts / "free-fall.json").read_bytes(), free_fall)
        self.assertEqual(objects, {p.name: p.read_bytes()
                                  for p in (self.artifacts / "objects/sha256").glob("*.json")})
        prior = load_json(self.artifacts / "free-fall.json")
        self.assertEqual(self.manifest["demos"][0]["artifact"], prior["demos"][1]["artifact"])

    def test_truth_labels_and_no_clip_job_or_bounce_invention(self):
        for demo in self.manifest["demos"]:
            self.assertEqual(demo["source"]["kind"], "synthetic")
            self.assertNotIn("clip_id", demo["source"])
            self.assertNotIn("app_id", demo["provenance"])
            self.assertNotIn("ledger", demo["provenance"])
            self.assertEqual(demo["label"], "simulated")
            self.assertFalse(demo["scale_verified"])
            self.assertEqual(demo["scale_label"], "SCALE_UNVERIFIED")
            self.assertEqual(demo["gates"], {"M": "NOT_MET", "RS": "NOT_MET", "R": "NOT_RUN"})
            self.assertEqual(demo["availability"], "metadata-only")
            self.assertIn("Gate M: NOT_MET_INPUT_READINESS", demo["limitations"])
            self.assertIn("Pre-contact analytic motion only; no rebound or contact-response claim.",
                          demo["limitations"])
        with self.assertRaisesRegex(ValueError, "no accepted simulation cases for bounce"):
            simulated_demos(ROOT, "bounce")
        self.assertFalse((self.artifacts / "bounce.json").exists())

    def test_cross_template_or_case_selection_rejected(self):
        for selected in ("/cases/0", "/cases/5"):
            self.reject(lambda d: d["provenance"].update(record_pointer=selected), "simulation identity")
        self.reject(lambda d: d["provenance"].update(record_pointer="/cases/8"),
                    "passed deterministic")
        self.reject(lambda d: d.update(id="simulated-bounce-baseline-short"), "simulation identity")

    def test_numeric_forgery_and_cross_case_pointer_rejected(self):
        self.reject(lambda d: d["provenance"]["numeric"][0].update(value=123), "numeric evidence")
        self.reject(lambda d: d["provenance"]["numeric"][0].update(pointer="/cases/0/gravity_m_s2"),
                    "selected simulated case")
        self.reject(lambda d: d["provenance"]["numeric"][0].update(label="measured"))

    def test_gate_scale_label_and_playable_promotions_rejected(self):
        for gate in ("M", "RS", "R"):
            self.reject(lambda d: d["gates"].update({gate: "MET"}))
        self.reject(lambda d: d.update(label="measured"))
        self.reject(lambda d: d.update(scale_verified=True))
        self.reject(lambda d: d.update(availability="playable"))

    def test_missing_case_and_wrong_run_report_rejected(self):
        self.reject(lambda d: d["provenance"].update(record_pointer="/cases/999"), "record pointer")
        self.reject(lambda d: d["provenance"].update(run_id="S18c-orch94"), "report path")

    def test_bounce_unavailable_note_links_actual_shortfalls(self):
        note = (self.artifacts / "bounce-UNAVAILABLE.md").read_text(encoding="utf-8")
        for text in ("UNAVAILABLE", "31/176", "S07-chunktrack-orch67/REPORT.md",
                     "evidence/S12/gate-rs/gate-rs.json", "Gate RS NOT_MET", "SCALE_UNVERIFIED"):
            self.assertIn(text, note)
        gate = load_json(ROOT / "evidence/S12/gate-rs/gate-rs.json")
        self.assertIsNone(gate["clips"]["bounce"])
        self.assertIsNone(gate["result"]["per_category_normalized_rms"]["bounce"])
        self.assertEqual(gate["result"]["status"], "NOT_MET")


if __name__ == "__main__":
    unittest.main()
