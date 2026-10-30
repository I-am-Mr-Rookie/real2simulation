import copy
import hashlib
import json
import subprocess
import unittest
from unittest.mock import patch

from Build.library import guest, playable
from Build.library.validate import ROOT, validate_file


class PlayableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = playable.load_index()
        cls.demo = next(d for d in validate_file(ROOT / "test-data/library-artifacts/projectile.json")["demos"]
                        if d["id"] == "simulated-projectile-baseline-short")
        cls.item = cls.index["entries"][cls.demo["id"]]
        cls.trace = json.loads((ROOT / "test-data/library-artifacts" / cls.item["artifact"]["path"]).read_bytes())

    def test_preserved_inputs_reproduce_exact_stored_traces(self):
        for name in ("free-fall.json", "projectile.json", "pendulum.json"):
            demos = validate_file(ROOT / "test-data/library-artifacts" / name)["demos"]
            demo = next(d for d in demos if d["id"] in playable.SOURCES)
            generated, custody = playable.generate(ROOT, demo)
            item = self.index["entries"][demo["id"]]
            self.assertEqual(custody, item["custody"])
            self.assertEqual(hashlib.sha256(playable.encode(generated)).hexdigest(), item["artifact"]["sha256"])
            self.assertEqual(len(playable.encode(generated)), item["artifact"]["bytes"])

    def test_pendulum_model_update_is_recorded_not_claimed_historically_identical(self):
        demo = next(d for d in validate_file(ROOT / "test-data/library-artifacts/pendulum.json")["demos"]
                    if d["id"] in playable.SOURCES)
        trace, custody = playable.generate(ROOT, demo)
        self.assertNotEqual(custody["accepted_trace_sha256"], custody["produced_trace_sha256"])
        self.assertEqual(trace["kind"], "pendulum")
        self.assertEqual(custody, self.index["entries"][demo["id"]]["custody"])

    def test_trace_schema_bounds_and_numeric_safety(self):
        self.assertIs(playable.validate_trace(self.trace), self.trace)
        for mutate in (
            lambda t: t.update(kind="mystery-g"), lambda t: t.update(source="measured"),
            lambda t: t.update(inputProvenance="image-derived"), lambda t: t.update(label="MEASURED"),
            lambda t: t.update(dt_s=True), lambda t: t.update(dt_s=float("inf")),
            lambda t: t.update(samples=[]), lambda t: t.update(samples=[t["samples"][0]] * 4097),
            lambda t: t["samples"][1].update(step=True), lambda t: t["samples"][1].update(time_s=0),
            lambda t: t["samples"][1].update(position_m=[0, 1]),
            lambda t: t["samples"][1].update(position_m=[True, 0, 0]),
            lambda t: t["samples"][1].update(position_m=[float("nan"), 0, 0]),
            lambda t: t.update(seed=42), lambda t: t.update(sha256="self-hash"),
        ):
            value = copy.deepcopy(self.trace)
            mutate(value)
            with self.assertRaises(ValueError):
                playable.validate_trace(value)
        with patch.object(playable, "MANIFEST_BYTES", 1):
            with self.assertRaisesRegex(ValueError, "byte limit"):
                playable.validate_trace(self.trace)

    def test_custody_tampering_is_rejected(self):
        for mutate in (
            lambda i: i["artifact"].update(bytes=1),
            lambda i: i["artifact"].update(path="../escape.json"),
            lambda i: i["custody"].update(record_pointer="/cases/0"),
            lambda i: i["custody"].update(accepted_trace_sha256="0" * 64),
            lambda i: i["custody"].update(produced_trace_sha256="invalid"),
            lambda i: i["custody"]["setup"].update(sha256="0" * 64),
            lambda i: i["custody"]["input_pointers"].update(setup=[]),
            lambda i: i["custody"]["producers"][0].update(sha256="0" * 64),
            lambda i: i.update(samples=1),
        ):
            index = copy.deepcopy(self.index)
            mutate(index["entries"][self.demo["id"]])
            with self.assertRaises(ValueError):
                playable.load_trace(ROOT, self.demo, index)

    def test_guest_withholds_challenge_shared_trace_and_raw_objects(self):
        manifest, objects = guest.load_guest()
        entries = {d["id"]: d for d in manifest["demos"]}
        shared = entries["simulated-free-fall-baseline-short"]
        self.assertEqual(shared["label"], "UNAVAILABLE")
        self.assertIn("Mystery-g", shared["reason"])
        hidden_sha = self.index["entries"][shared["id"]]["artifact"]["sha256"]
        self.assertNotIn(hidden_sha, objects)
        self.assertNotIn(hidden_sha, json.dumps(manifest))
        self.assertEqual(guest.artifact_response(hidden_sha, objects).status_code, 404)
        self.assertEqual(sum(d["availability"] == "playable" for d in entries.values()), 2)
        for data in objects.values():
            body = json.loads(data)
            self.assertNotEqual(body.get("artifact_version"), "s10-replay-v1")
            self.assertTrue(set(body).isdisjoint({"seed", "parameters", "traceHash", "replayHash", "gravity"}))

    def test_runtime_guest_path_never_starts_generator(self):
        with patch.object(subprocess, "Popen", side_effect=AssertionError("offline generation only")):
            manifest, _ = guest.load_guest()
            self.assertTrue(any(d["availability"] == "playable" for d in manifest["demos"]))

    def test_withholding_follows_current_challenge_record_not_a_hardcoded_demo(self):
        real_validate = guest.validate_file

        def validated_catalogue(*args):
            catalogue = real_validate(*args)
            for demo in catalogue["demos"]:
                if "challenge" in demo:
                    demo["provenance"]["record_pointer"] = "/cases/4"
            return catalogue

        with patch.object(guest, "validate_file", side_effect=validated_catalogue):
            manifest, objects = guest.load_guest()
        entries = {d["id"]: d for d in manifest["demos"]}
        self.assertEqual(entries[self.demo["id"]]["availability"], "unavailable")
        self.assertNotIn(self.item["artifact"]["sha256"], objects)
        self.assertEqual(entries["simulated-free-fall-baseline-short"]["availability"], "playable")

    def test_generation_does_not_hide_unexpected_validation_failures(self):
        before = (ROOT / playable.INDEX).read_bytes()
        with patch.object(playable, "generate", side_effect=ValueError("corrupt source")):
            with self.assertRaisesRegex(ValueError, "corrupt source"):
                playable.build()
        self.assertEqual((ROOT / playable.INDEX).read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
