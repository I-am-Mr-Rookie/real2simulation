import copy
import tempfile
from pathlib import Path
import unittest

from Build.library.example import ref, store
from Build.library.free_fall import ACCEPTANCE, RUN, build
from Build.library.validate import ROOT, pointer, validate, validate_file
from contracts.scene.validate_scene import load_json


class FreeFallLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = ROOT / "test-data/library-artifacts"
        cls.path = cls.artifacts / "free-fall.json"
        cls.manifest = load_json(cls.path)

    def check(self, manifest):
        return validate(manifest, self.artifacts)

    def reject(self, change, message=None):
        manifest = copy.deepcopy(self.manifest)
        change(manifest["demos"][1])
        with self.assertRaises(ValueError) as raised:
            self.check(manifest)
        if message:
            self.assertIn(message, str(raised.exception))

    def test_accepted_case_coverage_and_original_bytes(self):
        self.assertEqual(validate_file(self.path), self.manifest)
        acceptance = load_json(ROOT / ACCEPTANCE)
        cases = [(i, c) for i, c in enumerate(acceptance["cases"]) if c["template"] == "free_fall"]
        self.assertEqual(len(self.manifest["demos"]), len(cases) + 1)
        for demo, (index, case) in zip(self.manifest["demos"][1:], cases):
            self.assertEqual(demo["provenance"]["record_pointer"], f"/cases/{index}")
            self.assertEqual(demo["provenance"]["run_id"], RUN)
            self.assertTrue(demo["id"].endswith(case["case"]))
            self.assertEqual((self.artifacts / demo["artifact"]["path"]).read_bytes(),
                             (ROOT / ACCEPTANCE).read_bytes())
            for number in demo["provenance"]["numeric"]:
                self.assertEqual(number["value"], pointer(acceptance, number["pointer"]))

    def test_builder_is_byte_reproducible(self):
        before = self.path.read_bytes()
        objects = {p.name: p.read_bytes() for p in (self.artifacts / "objects/sha256").glob("*.json")}
        self.assertEqual(build(), self.path)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(objects, {p.name: p.read_bytes()
                                  for p in (self.artifacts / "objects/sha256").glob("*.json")})

    def test_truth_labels_and_no_invented_clip_or_job(self):
        for demo in self.manifest["demos"]:
            self.assertFalse(demo["scale_verified"])
            self.assertEqual(demo["availability"], "metadata-only")
            self.assertIn("Gate M: NOT_MET_INPUT_READINESS", demo["limitations"])
        for demo in self.manifest["demos"][1:]:
            self.assertEqual(demo["label"], "simulated")
            self.assertNotIn("clip_id", demo["source"])
            self.assertNotIn("ledger", demo["provenance"])
            self.assertNotIn("app_id", demo["provenance"])
        real = self.manifest["demos"][0]
        self.assertEqual(real["source"]["clip_id"], "RM02")
        self.assertIn("not a measured free-fall fit", " ".join(real["limitations"]))

    def test_no_simulation_promotion(self):
        for label in ("measured", "fixture"):
            self.reject(lambda d: d.update(label=label))
        for gate in ("M", "RS", "R"):
            self.reject(lambda d: d["gates"].update({gate: "MET"}))
        self.reject(lambda d: d.update(scale_verified=True))
        self.reject(lambda d: d.update(availability="playable"))

    def test_cross_case_numeric_pointer_rejected(self):
        self.reject(lambda d: d["provenance"]["numeric"][0].update(pointer="/cases/1/gravity_m_s2"),
                    "selected simulated case")
        self.reject(lambda d: d["provenance"]["numeric"][0].update(evidence="ledger"),
                    "selected simulated case")

    def test_forged_numeric_rejected(self):
        self.reject(lambda d: d["provenance"]["numeric"][0].update(value=123), "numeric evidence")
        self.reject(lambda d: d["provenance"]["numeric"][0].update(value=True))
        self.reject(lambda d: d["provenance"]["numeric"][0].update(label="measured"))
        self.reject(lambda d: d["provenance"]["numeric"][0].update(pointer="/cases/0/missing"),
                    "numeric pointer not found")

    def test_non_free_fall_and_missing_selection_rejected(self):
        self.reject(lambda d: d["provenance"].update(record_pointer="/cases/4"),
                    "simulation identity")
        self.reject(lambda d: d["provenance"].update(record_pointer="/cases/999"),
                    "record pointer not found")

    def test_report_binding_rejected(self):
        self.reject(lambda d: d["provenance"].update(run_id="S07c"), "report path")
        report = ref(ROOT, "Run-System/Runs/S07c/REPORT.md")
        self.reject(lambda d: d["provenance"].update(run_id="S07c", report=report),
                    "does not identify simulation evidence")

    def test_clip_cannot_use_synthetic_provenance(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["demos"][0]["provenance"] = copy.deepcopy(manifest["demos"][1]["provenance"])
        with self.assertRaisesRegex(ValueError, "clip source requires job provenance"):
            self.check(manifest)

    def test_synthetic_cannot_use_job_provenance_or_forged_clip(self):
        provenance = self.manifest["demos"][0]["provenance"]
        self.reject(lambda d: d.update(provenance=provenance), "local simulation provenance")
        self.reject(lambda d: d["source"].update(clip_id="RM02"))

    def test_corrupt_simulation_object_rejected_and_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = self.manifest["demos"][1]["artifact"]
            record = store(directory, (ROOT / ACCEPTANCE).read_bytes(), "simulation-record")
            self.assertEqual(record, source)
            target = directory / source["path"]
            target.write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError, "immutable artifact is corrupt"):
                store(directory, (ROOT / ACCEPTANCE).read_bytes(), "simulation-record")
            self.assertEqual(target.read_bytes(), b"corrupt")
            manifest = copy.deepcopy(self.manifest)
            manifest["demos"] = manifest["demos"][1:]
            with self.assertRaisesRegex(ValueError, "sha256"):
                validate(manifest, directory)

    def test_hashes_do_not_replace_original_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            record = store(directory, b'{"source":"simulated"}', "simulation-record")
            manifest = copy.deepcopy(self.manifest)
            manifest["demos"] = [manifest["demos"][1]]
            manifest["demos"][0]["artifact"] = record
            with self.assertRaisesRegex(ValueError, "differs from accepted evidence"):
                validate(manifest, directory)


if __name__ == "__main__":
    unittest.main()
