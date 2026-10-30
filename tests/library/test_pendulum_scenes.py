import copy
import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from Build.library.example import ref
from Build.library.free_fall import ACCEPTANCE
from Build.library.pendulum import build as build_pendulum
from Build.library.scenes import build as build_scenes
from Build.library.validate import APPROVAL, REGISTRY, ROOT, pointer, validate, validate_file
from contracts.scene.validate_scene import load_json


class PendulumSceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = ROOT / "test-data/library-artifacts"
        cls.pendulum = load_json(cls.artifacts / "pendulum.json")
        cls.scenes = load_json(cls.artifacts / "scenes.json")

    def reject(self, manifest, change, message=None):
        value = copy.deepcopy(manifest)
        change(value)
        with self.assertRaises(ValueError) as raised:
            validate(value, self.artifacts)
        if message:
            self.assertIn(message, str(raised.exception))

    def test_catalogues_validate(self):
        for name, manifest in (("pendulum", self.pendulum), ("scenes", self.scenes)):
            self.assertEqual(validate_file(self.artifacts / (name + ".json")), manifest)

    def test_builds_reproducible_and_preserve_existing_catalogues(self):
        names = ("manifest.json", "free-fall.json", "projectile.json", "pendulum.json", "scenes.json")
        before = {name: (self.artifacts / name).read_bytes() for name in names}
        objects = {p.name: p.read_bytes() for p in (self.artifacts / "objects/sha256").glob("*.json")}
        self.assertEqual(build_pendulum(), self.artifacts / "pendulum.json")
        self.assertEqual(build_scenes(), self.artifacts / "scenes.json")
        self.assertEqual(before, {name: (self.artifacts / name).read_bytes() for name in names})
        self.assertEqual(objects, {p.name: p.read_bytes()
                                  for p in (self.artifacts / "objects/sha256").glob("*.json")})

    def test_all_accepted_pendulum_cases_exact_bytes_and_pointers(self):
        acceptance = load_json(ROOT / ACCEPTANCE)
        expected = [i for i, case in enumerate(acceptance["cases"]) if case["template"] == "pendulum"]
        self.assertEqual(len(self.pendulum["demos"]), len(expected))
        for index, demo in zip(expected, self.pendulum["demos"]):
            self.assertEqual(demo["provenance"]["record_pointer"], f"/cases/{index}")
            self.assertEqual((self.artifacts / demo["artifact"]["path"]).read_bytes(),
                             (ROOT / ACCEPTANCE).read_bytes())
            for number in demo["provenance"]["numeric"]:
                self.assertEqual(number["value"], pointer(acceptance, number["pointer"]))
            self.assertEqual(demo["source"]["kind"], "synthetic")
            self.assertEqual(demo["label"], "simulated")
            self.assertIn("SYNTHETIC", " ".join(demo["limitations"]))
            self.assertNotIn("clip_id", demo["source"])
            self.assertNotIn("ledger", demo["provenance"])

    def test_pendulum_defaults_shortest_horizon_and_recorded_parameters(self):
        defaults = self.pendulum["defaults"]
        demo = next(d for d in self.pendulum["demos"] if d["id"] == defaults["demo_id"])
        parameters = {n["name"]: n["value"] for n in defaults["parameters"]}
        self.assertEqual(set(parameters), {"gravity_m_s2", "duration_s", "time_step_s"})
        durations = [n["value"] for d in self.pendulum["demos"] for n in d["provenance"]["numeric"]
                     if n["name"] == "duration_s"]
        self.assertEqual(parameters["duration_s"], min(durations))
        self.assertTrue(all(n in demo["provenance"]["numeric"] for n in defaults["parameters"]))

    def test_scene_source_credit_exact_csv_and_original_descriptors(self):
        with (ROOT / "clips.csv").open(encoding="utf-8", newline="") as stream:
            rows = {row["clip_id"]: row for row in csv.DictReader(stream)}
        self.assertEqual([d["source"]["clip_id"] for d in self.scenes["demos"]], ["RM02", "RM04"])
        for demo in self.scenes["demos"]:
            source = demo["source"]
            for key in ("source_url", "licence", "licence_url", "attribution"):
                self.assertEqual(source[key], rows[source["clip_id"]][key])
            provenance = demo["provenance"]
            self.assertEqual((self.artifacts / demo["artifact"]["path"]).read_bytes(),
                             (ROOT / provenance["artifact_evidence"]["path"]).read_bytes())
        # The CSV's Pexels License spelling must retain its credit while scene-v1 uses Pexels.
        self.assertEqual(self.scenes["demos"][1]["source"]["licence"], "Pexels License")
        self.assertEqual(self.scenes["defaults"]["demo_id"], self.scenes["demos"][0]["id"])
        self.assertEqual(self.scenes["defaults"]["parameters"], [])

    def test_rm04_uses_successful_job_not_refused_preflight(self):
        provenance = self.scenes["demos"][1]["provenance"]
        ledger = load_json(ROOT / provenance["ledger"]["path"])
        self.assertNotEqual(ledger["jobs"][0]["rc"], 0)
        self.assertEqual(provenance["app_id"], ledger["jobs"][1]["app_id"])
        self.assertEqual(ledger["jobs"][1]["rc"], 0)
        for number in provenance["numeric"]:
            self.assertTrue(number["pointer"].startswith("/jobs/1/"))
            self.assertEqual(number["value"], pointer(ledger, number["pointer"]))
        self.reject(self.scenes, lambda m: m["demos"][1]["provenance"].update(
            app_id=ledger["jobs"][0]["app_id"]), "successful ledger app missing")

    def test_defaults_reject_unknown_demo_forged_numbers_and_cross_case(self):
        self.reject(self.pendulum, lambda m: m["defaults"].update(demo_id="missing"), "default demo not found")
        self.reject(self.pendulum, lambda m: m["defaults"]["parameters"][0].update(value=123),
                    "default parameters must match")
        self.reject(self.pendulum, lambda m: m["defaults"].update(
            parameters=[m["demos"][1]["provenance"]["numeric"][0]]), "default parameters must match")
        self.reject(self.scenes, lambda m: m["defaults"].update(
            parameters=m["demos"][0]["provenance"]["numeric"]), "cannot expose physics parameters")

    def test_default_safety_switches_fail_closed(self):
        for manifest in (self.pendulum, self.scenes):
            for key, value in (("autoplay", True), ("physics_enabled", True),
                               ("real_scene_prediction", "ENABLED"), ("extra", True)):
                with self.subTest(key=key):
                    self.reject(manifest, lambda m: m["defaults"].update({key: value}))
            self.reject(manifest, lambda m: m["defaults"].pop("parameters"))

    def test_fallback_custody_required(self):
        self.reject(self.pendulum, lambda m: m["defaults"]["fallback_evidence"].update(sha256="0" * 64),
                    "sha256 mismatch")
        self.reject(self.scenes, lambda m: m["defaults"].update(
            fallback_evidence=ref(ROOT, "evidence/S12/gate-rs/gate-rs.json")), "expected S12f")

    def test_changed_fallback_decision_or_gate_hash_rejected(self):
        for change, message in ((lambda f: f["decision"].update(tier="REAL_SCENE"), "review S12f"),
                                (lambda f: f["gate_rs"].update(sha256="0" * 64), "sha256 mismatch")):
            with self.subTest(message=message), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                manifest = copy.deepcopy(self.pendulum)
                paths = {"clips.csv", APPROVAL, REGISTRY, "evidence/S12/S12f-fallback.json",
                         "evidence/S12/gate-rs/gate-rs.json"}
                for demo in manifest["demos"]:
                    paths.update(demo["provenance"][key]["path"] for key in ("report", "artifact_evidence"))
                for name in paths:
                    target = root / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / name, target)
                path = root / "evidence/S12/S12f-fallback.json"
                fallback = load_json(path)
                change(fallback)
                path.write_text(json.dumps(fallback), encoding="utf-8")
                manifest["defaults"]["fallback_evidence"] = ref(root, "evidence/S12/S12f-fallback.json")
                with self.assertRaisesRegex(ValueError, message):
                    validate(manifest, self.artifacts, evidence_root=root)

    def test_pendulum_cross_case_or_numeric_forgery_rejected(self):
        self.reject(self.pendulum, lambda m: m["demos"][0]["provenance"].update(record_pointer="/cases/0"),
                    "simulation identity")
        self.reject(self.pendulum, lambda m: m["demos"][0]["provenance"]["numeric"][0].update(value=123),
                    "numeric evidence mismatch")

    def test_scene_credit_forgery_rejected(self):
        self.reject(self.scenes, lambda m: m["demos"][1]["source"].update(licence="Pexels"),
                    "source licence mismatch")
        self.reject(self.scenes, lambda m: m["demos"][1]["source"].update(attribution="invented"),
                    "source attribution mismatch")

    def test_no_gate_scale_or_playable_promotions(self):
        for manifest in (self.pendulum, self.scenes):
            for demo in manifest["demos"]:
                self.assertFalse(demo["scale_verified"])
                self.assertEqual(demo["scale_label"], "SCALE_UNVERIFIED")
                self.assertEqual(demo["gates"]["RS"], "NOT_MET")
                self.assertEqual(demo["availability"], "metadata-only")
                self.assertIn("VIRTUAL_LAB_ONLY", " ".join(demo["limitations"]))
            for key, value in (("scale_verified", True), ("availability", "playable"), ("label", "fixture")):
                self.reject(manifest, lambda m: m["demos"][0].update({key: value}))
            self.reject(manifest, lambda m: m["demos"][0]["gates"].update(RS="MET"))

    def test_rm05_unavailable_note_has_real_evidence_links(self):
        note = (self.artifacts / "RM05-scene-UNAVAILABLE.md").read_text(encoding="utf-8")
        for value in ("UNAVAILABLE", "S05/S05c/RESULT.json", "S05c-orch19/REPORT.md",
                      "SCALE_UNVERIFIED", "VIRTUAL_LAB_ONLY"):
            self.assertIn(value, note)
        self.assertNotIn("RM05", [d["source"]["clip_id"] for d in self.scenes["demos"]])
        self.assertEqual(load_json(ROOT / "evidence/S12/S12f-fallback.json")["decision"]["tier"],
                         "VIRTUAL_LAB_ONLY")


if __name__ == "__main__":
    unittest.main()
