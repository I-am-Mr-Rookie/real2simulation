import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from Build.library import guest
from Build.library.validate import APPROVAL, REGISTRY, ROOT


class GuestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.objects = guest.load_guest()
        cls.client = TestClient(guest.create_app())

    def test_anonymous_manifest_labels_and_safe_defaults(self):
        response = self.client.get("/api/library/manifest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.manifest)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["content-type"], "application/json")
        self.assertEqual(len(self.manifest["demos"]), 18)
        self.assertEqual({d["label"] for d in self.manifest["demos"]},
                         {"SIMULATED", "UNAVAILABLE"})
        for demo in self.manifest["demos"]:
            with self.subTest(demo=demo["id"]):
                self.assertNotIn("provenance", demo)
                if demo["label"] == "UNAVAILABLE":
                    self.assertIsNone(demo["artifact"])
                    continue
                self.assertTrue(demo["display_only"])
                self.assertFalse(demo["scale_verified"])
                self.assertEqual(demo["availability"], "playable" if demo["artifact"]["kind"] ==
                                 "simulation-trace" else "metadata-only")
                self.assertEqual(demo["scale_label"], "SCALE_UNVERIFIED")
                defaults = demo["defaults"]
                self.assertFalse(defaults["autoplay"])
                self.assertFalse(defaults["physics_enabled"])
                self.assertEqual(defaults["parameters"], [])
                self.assertEqual(defaults["real_scene_prediction"], "WITHHELD")
                self.assertNotIn("fallback_evidence", defaults)
        self.assertEqual(self.manifest["defaults"]["demo_id"], "simulated-mystery-g")

    def test_all_guest_objects_hash_size_headers_and_content(self):
        for sha, data in self.objects.items():
            with self.subTest(sha=sha):
                response = guest.artifact_response(sha, self.objects)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.body, data)
                self.assertEqual(hashlib.sha256(data).hexdigest(), sha)
                self.assertEqual(response.headers["content-type"], "application/json")
                self.assertEqual(response.headers["content-length"], str(len(data)))
                self.assertEqual(response.headers["etag"], f'"{sha}"')
                self.assertEqual(response.headers["cache-control"], "public, max-age=31536000, immutable")
                self.assertEqual(response.headers["x-content-type-options"], "nosniff")
                payload = json.loads(data)
                for key in ("gravity_m_s2", "seed", "replayHash", "cases", "position_error_m", "relative_error"):
                    self.assertNotIn(key, payload)
                if "gravity" in payload:
                    self.assertIsNone(payload["gravity"]["magnitude_m_s2"])
        for demo in self.manifest["demos"]:
            if demo["artifact"]:
                artifact = demo["artifact"]
                self.assertEqual(artifact["bytes"], len(self.objects[artifact["sha256"]]))

    def test_challenge_http_and_other_catalogues_do_not_expose_answer(self):
        challenge = next(d for d in self.manifest["demos"] if "challenge" in d)
        response = self.client.get(challenge["artifact"]["href"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()),
                         {"source", "mode", "answer_visibility", "duration_s", "time_step_s"})
        self.assertEqual(response.json()["answer_visibility"], "withheld-until-fit")
        source = json.loads((ROOT / "test-data/library-artifacts/mystery-g.json").read_text(encoding="utf-8"))
        raw_hash = source["demos"][0]["provenance"]["artifact_evidence"]["sha256"]
        self.assertNotIn(raw_hash, self.objects)
        self.assertNotIn(raw_hash, json.dumps(self.manifest))
        response = self.client.get(f"/api/library/artifacts/{raw_hash}")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "artifact_not_found"})

    def test_invalid_unknown_and_unsafe_ids_refuse_without_reading(self):
        for artifact_id in ("", "../clips.csv", "a/b", "a\\b", "A" * 64, "g" * 64,
                            "a" * 63, "a" * 65, "C:secret", "a" * 64 + ".json", "\x00"):
            with self.subTest(artifact_id=artifact_id):
                response = guest.artifact_response(artifact_id, self.objects)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.headers["cache-control"], "no-store")
        with patch.object(guest, "load_guest", side_effect=AssertionError("must reject before I/O")):
            self.assertEqual(self.client.get("/api/library/artifacts/not-a-hash").status_code, 400)
            self.assertEqual(self.client.get("/api/library/artifacts/%2e%2e%2fclips.csv").status_code, 400)
        self.assertEqual(guest.artifact_response("0" * 64, self.objects).status_code, 404)

    def test_hash_and_size_are_checked_before_serving(self):
        sha = next(iter(self.objects))
        self.assertEqual(guest.artifact_response(sha, {sha: b"tampered"}).status_code, 503)
        data = b"12345"
        sha = hashlib.sha256(data).hexdigest()
        with patch.object(guest, "ARTIFACT_BYTES", 4):
            self.assertEqual(guest.artifact_response(sha, {sha: data}).status_code, 503)
        with patch.object(guest, "MANIFEST_BYTES", 1):
            with self.assertRaisesRegex(ValueError, "manifest exceeds byte limit"):
                guest.load_guest()

    def seed_root(self, root):
        artifacts = ROOT / "test-data/library-artifacts"
        shutil.copytree(artifacts, root / "test-data/library-artifacts")
        paths = {"clips.csv", APPROVAL, REGISTRY, "evidence/S12/S12f-fallback.json"}
        index = json.loads((artifacts / "playable.json").read_text())
        for item in index["entries"].values():
            if "custody" in item:
                custody = item["custody"]
                paths.update(p["path"] for p in custody["producers"])
                paths.add(custody["setup"]["path"])
        fallback = json.loads((ROOT / "evidence/S12/S12f-fallback.json").read_text(encoding="utf-8"))
        paths.add(fallback["gate_rs"]["path"])
        for name in guest.CATALOGUES:
            manifest = json.loads((artifacts / name).read_text(encoding="utf-8"))
            for demo in manifest["demos"]:
                paths.update(ref["path"] for ref in demo["provenance"].values()
                             if isinstance(ref, dict) and "path" in ref)
        for relative in paths:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def test_readonly_and_current_corruption_revocation_missing_catalogue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.seed_root(root)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            client = TestClient(guest.create_app(root))
            self.assertEqual(client.get("/api/library/manifest").status_code, 200)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            approval = root / APPROVAL
            saved = approval.read_bytes()
            approval.write_text("Revoked: no clips approved.", encoding="utf-8")
            response = client.get("/api/library/manifest")
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json(), {"error": "library_unavailable"})
            approval.write_bytes(saved)
            sha = json.loads((root / "test-data/library-artifacts/scenes.json").read_text())["demos"][0]["artifact"]["sha256"]
            path = root / f"test-data/library-artifacts/objects/sha256/{sha}.json"
            original = path.read_bytes()
            path.write_bytes(b"corrupt")
            self.assertEqual(client.get(f"/api/library/artifacts/{sha}").status_code, 503)
            path.write_bytes(original)
            (root / "test-data/library-artifacts/scenes.json").unlink()
            self.assertEqual(client.get("/api/library/manifest").status_code, 503)

    def test_api_is_get_only_and_errors_do_not_disclose_paths(self):
        for path in ("/api/library/manifest", "/api/library/artifacts/" + "a" * 64):
            self.assertEqual(self.client.post(path).status_code, 405)
        with patch.object(guest, "load_guest", side_effect=OSError("private path, not for guests")):
            response = self.client.get("/api/library/manifest")
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("private", response.text)
            self.assertEqual(response.headers["cache-control"], "no-store")

    def test_fresh_process_imports_and_calls_no_paid_or_network_path(self):
        code = r'''
import importlib.abc, json, socket, subprocess, sys
from unittest.mock import patch
blocked = ("Build.agent", "Build.gpu", "Build.guardrails", "modal", "boto3", "botocore",
           "openai", "anthropic", "torch", "transformers", "huggingface_hub", "requests")
class NoPaidImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        assert not any(fullname == p or fullname.startswith(p + ".") for p in blocked), fullname
sys.meta_path.insert(0, NoPaidImports())
with patch.object(socket.socket, "connect", side_effect=AssertionError("network forbidden")), \
     patch.object(subprocess, "Popen", side_effect=AssertionError("process forbidden")):
    from Build.library.guest import create_app
    # Windows ASGI TestClient initializes asyncio with a loopback socketpair.
    # Call the same route functions directly while forbidding every socket call.
    routes = {r.path: r.endpoint for r in create_app().routes}
    response = routes["/api/library/manifest"]()
    assert response.status_code == 200, response.body
    sha = next(d["artifact"]["sha256"] for d in json.loads(response.body)["demos"] if "challenge" in d)
    assert routes["/api/library/artifacts/{artifact_id:path}"](sha).status_code == 200
    assert not any(n == p or n.startswith(p + ".") for n in sys.modules for p in blocked)
print("PASS: no paid/provider/guardrail imports, network or child process calls")
'''
        result = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT,
                                capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS:", result.stdout)


if __name__ == "__main__":
    unittest.main()
