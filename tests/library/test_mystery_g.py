import copy
import csv
import json
from pathlib import Path
import tempfile
import unittest

from Build.library.example import store
from Build.library.free_fall import ACCEPTANCE
from Build.library.mystery_g import build
from Build.library.validate import ROOT, pointer, validate, validate_file
from contracts.scene.validate_scene import load_json


class MysteryGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = ROOT / "test-data/library-artifacts"
        cls.manifest = load_json(cls.artifacts / "mystery-g.json")

    def reject(self, change, message):
        value = copy.deepcopy(self.manifest)
        change(value)
        with self.assertRaisesRegex(ValueError, message):
            validate(value, self.artifacts)

    def test_validates(self):
        self.assertEqual(validate_file(self.artifacts / "mystery-g.json"), self.manifest)

    def test_rebuild_preserves_all_bytes(self):
        before = {p.relative_to(self.artifacts): p.read_bytes() for p in self.artifacts.rglob("*.json")}
        self.assertEqual(build(), self.artifacts / "mystery-g.json")
        self.assertEqual(before, {p.relative_to(self.artifacts): p.read_bytes()
                                  for p in self.artifacts.rglob("*.json")})

    def test_default_display_and_artifact_withhold_answer(self):
        demo = self.manifest["demos"][0]
        public = load_json(self.artifacts / demo["artifact"]["path"])
        self.assertEqual(set(public), {"source", "mode", "answer_visibility", "duration_s", "time_step_s"})
        self.assertEqual(public["answer_visibility"], "withheld-until-fit")
        self.assertEqual(self.manifest["defaults"]["parameters"], [])
        self.assertFalse(self.manifest["defaults"]["physics_enabled"])
        self.assertFalse(self.manifest["defaults"]["autoplay"])
        self.assertNotIn("gravity", json.dumps(self.manifest).lower())
        self.assertEqual(demo["label"], "simulated")
        self.assertEqual(demo["scale_label"], "SCALE_UNVERIFIED")
        self.assertEqual(demo["gates"], {"M": "NOT_MET", "RS": "NOT_MET", "R": "NOT_RUN"})

    def test_numeric_pointers_match_artifact_and_original_case(self):
        demo = self.manifest["demos"][0]
        provenance = demo["provenance"]
        original = load_json(ROOT / ACCEPTANCE)
        public = load_json(self.artifacts / demo["artifact"]["path"])
        record = pointer(original, provenance["record_pointer"])
        for numeric in provenance["numeric"]:
            self.assertEqual(numeric["value"], pointer(public, numeric["pointer"]))
            self.assertEqual(numeric["value"], record[numeric["name"]])

    def test_answer_in_numeric_metadata_rejected(self):
        self.reject(lambda m: m["demos"][0]["provenance"]["numeric"][0].update(name="gravity_m_s2"), "withhold answer")

    def test_numeric_pointer_to_raw_evidence_rejected(self):
        self.reject(lambda m: m["demos"][0]["provenance"]["numeric"][0].update(pointer="/cases/0/gravity_m_s2"), "withhold answer")

    def test_default_parameters_rejected_even_if_source_bound(self):
        self.reject(lambda m: m["defaults"].update(parameters=m["demos"][0]["provenance"]["numeric"]), "withhold parameters")

    def test_kind_metadata_pair_required(self):
        self.reject(lambda m: m["demos"][0].pop("challenge"), "metadata/kind mismatch")
        self.reject(lambda m: m["demos"][0]["artifact"].update(kind="simulation-record"), "metadata/kind mismatch")

    def test_reveal_flag_and_gate_promotion_rejected(self):
        self.reject(lambda m: m["demos"][0]["challenge"].update(answer_visibility="visible"), "was expected")
        self.reject(lambda m: m["demos"][0]["gates"].update(M="MET"), "was expected")

    def test_stale_source_hash_rejected(self):
        self.reject(lambda m: m["demos"][0]["provenance"]["artifact_evidence"].update(sha256="0" * 64), "sha256 mismatch")

    def test_unknown_case_rejected(self):
        self.reject(lambda m: m["demos"][0]["provenance"].update(record_pointer="/cases/9999"), "record pointer not found")

    def test_rehashed_answer_or_setup_tampering_rejected(self):
        for field in ("gravity_m_s2", "seed", "replayHash", "duration_s"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                manifest = copy.deepcopy(self.manifest)
                demo = manifest["demos"][0]
                public = load_json(self.artifacts / demo["artifact"]["path"])
                public[field] = "not-an-accepted-public-field"
                demo["artifact"] = store(Path(tmp), json.dumps(public).encode(), "challenge-record")
                with self.assertRaisesRegex(ValueError, "answer-free setup projection"):
                    validate(manifest, tmp)

    def test_raw_acceptance_artifact_cannot_be_served_as_challenge(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = copy.deepcopy(self.manifest)
            manifest["demos"][0]["artifact"] = store(Path(tmp), (ROOT / ACCEPTANCE).read_bytes(), "challenge-record")
            with self.assertRaisesRegex(ValueError, "answer-free setup projection"):
                validate(manifest, tmp)

    def test_apollo_is_unavailable_not_a_numeric_demo(self):
        note = (ROOT / "evidence/S18/Apollo-UNAVAILABLE.md").read_text(encoding="utf-8")
        self.assertIn("Moon result not measured", note)
        self.assertIn("NOT_TRACKABLE", note)
        with (ROOT / "clips.csv").open(encoding="utf-8", newline="") as stream:
            row = next(r for r in csv.DictReader(stream) if r["clip_id"] == "AP15")
        self.assertEqual(row["owner_approved"], "NO")
        self.assertFalse((self.artifacts / "apollo.json").exists())


if __name__ == "__main__":
    unittest.main()
