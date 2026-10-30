import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from Build.library.example import build
from Build.library.validate import APPROVAL, REGISTRY, ROOT, file_under, pointer, validate, validate_file
from contracts.scene.validate_scene import load_json


class LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example_root = ROOT / "test-data/library-artifacts"
        cls.manifest = load_json(cls.example_root / "manifest.json")

    def check(self, value):
        return validate(value, self.example_root)

    def mutate(self, change, message=None):
        value = copy.deepcopy(self.manifest)
        change(value["demos"][0])
        with self.assertRaises(ValueError) as raised:
            self.check(value)
        if message:
            self.assertIn(message, str(raised.exception))

    def test_accepted_example(self):
        self.assertEqual(self.check(self.manifest), self.manifest)
        self.assertEqual(validate_file(self.example_root / "manifest.json"), self.manifest)

    def test_example_is_reproducible(self):
        before = (self.example_root / "manifest.json").read_bytes()
        build()
        self.assertEqual((self.example_root / "manifest.json").read_bytes(), before)

    def test_strict_manifest_and_demo_shape(self):
        for field in self.manifest["demos"][0]:
            with self.subTest(field=field):
                self.mutate(lambda d: d.pop(field))
        for key, value in (("schema_version", "2.0.0"), ("audience", "public"), ("demos", []), ("extra", True)):
            document = copy.deepcopy(self.manifest)
            document[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check(document)

    def test_duplicate_demo(self):
        document = copy.deepcopy(self.manifest)
        document["demos"].append(copy.deepcopy(document["demos"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check(document)

    def test_unapproved_and_forged_source(self):
        for key, value in (("clip_id", "AP15"), ("source_url", "https://example.com/"),
                           ("licence", "CC-BY-NC-4.0"), ("licence_url", "https://example.com/"),
                           ("attribution", "invented"), ("sha256", "0" * 64)):
            with self.subTest(key=key):
                self.mutate(lambda d: d["source"].update({key: value}))

    def test_no_gate_or_scale_promotion(self):
        for gate in ("M", "RS", "R"):
            self.mutate(lambda d: d["gates"].update({gate: "PASS"}))
        self.mutate(lambda d: d.update(scale_verified=True))
        self.mutate(lambda d: d.update(scale_label="VERIFIED"))
        self.mutate(lambda d: d.update(availability="playable"))

    def test_labels(self):
        for label in ("simulated", "fixture", "real", "MEASURED"):
            self.mutate(lambda d: d.update(label=label))
        self.mutate(lambda d: d["provenance"]["numeric"][0].update(label="fixture"))
        self.mutate(lambda d: d["artifact"].update(kind="fixture-record"))

    def test_run_and_app_binding(self):
        self.mutate(lambda d: d["provenance"].update(run_id="S06f-orch23"))
        self.mutate(lambda d: d["provenance"].update(app_id="ap-invented"))
        self.mutate(lambda d: d["provenance"]["report"].update(sha256="0" * 64))
        self.mutate(lambda d: d["provenance"]["ledger"].update(sha256="0" * 64))
        self.mutate(lambda d: d["provenance"]["artifact_evidence"].update(sha256="0" * 64))
        self.mutate(lambda d: d["provenance"]["ledger"].update(path=".env"))

    def test_numeric_custody(self):
        for update in ({"value": 12345}, {"value": True}, {"value": float("inf")},
                       {"pointer": "/jobs/0/not_found"}, {"pointer": "/actual_usd"},
                       {"pointer": "/jobs/00/function_elapsed_s"}, {"pointer": "/jobs/~2/rc"}):
            with self.subTest(update=update):
                self.mutate(lambda d: d["provenance"]["numeric"][0].update(update))
        document = copy.deepcopy(self.manifest)
        document["demos"][0]["provenance"]["numeric"] = [{
            "name": "point_count", "value": 20000, "unit": "points", "label": "measured",
            "evidence": "artifact", "pointer": "/render/point_count"}]
        self.check(document)  # copied from accepted artifact, not a physical measurement

    def test_artifact_limits_identity_and_digest(self):
        for update in ({"sha256": "0" * 64}, {"bytes": 1}, {"bytes": 67108865},
                       {"path": "objects/sha256/../../secret.json"}, {"media_type": "text/html"}):
            self.mutate(lambda d: d["artifact"].update(update))
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            artifact = self.manifest["demos"][0]["artifact"]
            path = directory / artifact["path"]
            path.parent.mkdir(parents=True)
            path.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "sha256"):
                validate(self.manifest, directory)

    def test_content_address_does_not_replace_evidence_custody(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            data = b'{"invented": 42}'
            digest = hashlib.sha256(data).hexdigest()
            document = copy.deepcopy(self.manifest)
            artifact = document["demos"][0]["artifact"]
            artifact.update(sha256=digest, path=f"objects/sha256/{digest}.json", bytes=len(data))
            path = directory / artifact["path"]
            path.parent.mkdir(parents=True)
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "accepted evidence"):
                validate(document, directory)

    def test_paths_and_json_parser(self):
        for path in ("../clips.csv", "/clips.csv", "C:/clips.csv", "evidence\\x.json", "evidence//x.json"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                file_under(ROOT, path)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            for data in ('{"x":1,"x":2}', '{"x":NaN}'):
                path.write_text(data, encoding="utf-8")
                with self.assertRaises(ValueError):
                    validate_file(path)
            path.write_bytes(b" " * (256 * 1024 + 1))
            with self.assertRaisesRegex(ValueError, "byte limit"):
                validate_file(path)

    def test_pointer_escapes(self):
        self.assertEqual(pointer({"a/b": {"~c": [5]}}, "/a~1b/~0c/0"), 5)

    def seed_evidence(self, root):
        demo = self.manifest["demos"][0]
        paths = ["clips.csv", APPROVAL, REGISTRY]
        paths += [demo["provenance"][k]["path"] for k in ("artifact_evidence", "ledger", "report")]
        for relative in paths:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, path)

    def test_current_authority_is_rechecked_not_cached(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.seed_evidence(root)
            validate(self.manifest, self.example_root, root)
            path = root / APPROVAL
            path.write_text(path.read_text(encoding="utf-8").replace("local scene/tracking pipeline work ONLY", "local scene/tracking pipeline work ONLY revoked"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not approved"):
                validate(self.manifest, self.example_root, root)

    def test_immutable_example_writer_refuses_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.seed_evidence(root)
            manifest_path = build(root)
            document = load_json(manifest_path)
            artifact_path = manifest_path.parent / document["demos"][0]["artifact"]["path"]
            artifact_path.write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError, "immutable artifact is corrupt"):
                build(root)
            self.assertEqual(artifact_path.read_bytes(), b"corrupt")

    def test_nested_unknown_fields_are_rejected(self):
        for key in ("source", "artifact", "provenance", "gates"):
            with self.subTest(key=key):
                self.mutate(lambda d: d[key].update(untrusted=True))


if __name__ == "__main__":
    unittest.main()
