"""Actual stager with synthetic Git blobs; normal/optimized execution, no uploads."""
from contextlib import redirect_stdout
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).with_name("stage.py")
REVISION = "a" * 40
FILES = {
    "Build/web/src/page.jsx": b"synthetic-web\n",
    "Build/web/package.json": b"{}\n",
    "Build/lab/session-service.mjs": b"synthetic-lab\n",
    "Build/library/loader.mjs": b"synthetic-loader\n",
    "Build/library/guest.py": b"synthetic-excluded\n",
    "Build/simulator/rk4.mjs": b"synthetic-sim\n",
    "Build/simulator/NUMERICS.md": b"synthetic-excluded\n",
    "Build/api/health/app.py": b"synthetic-api\n",
    "Build/api/health/dependencies.py": b"synthetic-shared\n",
    "Build/api/workspace/jobs.py": b"synthetic-workspace\n",
    "clips.csv": b"synthetic-clips\n",
    "evidence/S13/S13h/live/timing.json": b"{}\n",
    "evidence/S12/excluded.json": b"synthetic-excluded\n",
    "Build/worker/health/app.py": b"synthetic-worker\n",
    **{f"infra/railway/dev/{service}.Dockerfile": b"ARG R2S_SOURCE_REVISION\n"
       for service in ("web", "api", "worker")},
    ".env": b"SYNTHETIC_EXCLUDED",
    "archive/private.txt": b"SYNTHETIC_EXCLUDED",
}
OBJECT = b'{"synthetic":"trace"}'
SNAPSHOT = json.dumps({"manifest": {"demos": []}, "objects": {
    hashlib.sha256(OBJECT).hexdigest(): base64.b64encode(OBJECT).decode()}}).encode()


class StageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / "fresh"

    def stage(self, service="api", *, optimize=0, files=None, snapshot=SNAPSHOT, dirty=False):
        files = FILES if files is None else files
        def git(command, **kwargs):
            if command[0] == sys.executable:
                self.assertEqual(command[1:3], ["-B", "-c"])
                self.assertIn("load_guest()", command[3])
                return snapshot
            if command[1] == "rev-parse": return REVISION + "\n"
            if command[1] == "ls-tree": return "\n".join(files)
            if command[1] == "diff":
                if dirty: raise subprocess.CalledProcessError(1, command)
                return b""
            if command[1] == "show":
                self.assertTrue(command[2].startswith(REVISION + ":"))
                return files[command[2].split(":", 1)[1]]
            self.fail(command)
        with patch.object(sys, "argv", [str(SOURCE), service, str(self.target)]), \
             patch("subprocess.check_output", side_effect=git), redirect_stdout(io.StringIO()):
            exec(compile(SOURCE.read_text(), str(SOURCE), "exec", optimize=optimize),
                 {"__file__": str(SOURCE), "__name__": "__main__"})

    def test_existing_destination_untouched_in_both_modes(self):
        self.target.mkdir()
        sentinel = self.target / "Build/api/health/app.py"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_bytes(b"keep-existing")
        for optimize in (0, 1):
            with self.subTest(optimize=optimize), self.assertRaises(FileExistsError):
                self.stage(optimize=optimize)
            self.assertEqual(sentinel.read_bytes(), b"keep-existing")
            self.assertFalse((self.target / "context-manifest.json").exists())

    def test_invalid_service_never_creates_destination(self):
        for optimize in (0, 1):
            with self.subTest(optimize=optimize), self.assertRaises(ValueError):
                self.stage("invalid", optimize=optimize)
            self.assertFalse(self.target.exists())

    def test_existing_file_destination_is_not_replaced(self):
        self.target.write_bytes(b"keep-existing-file")
        for optimize in (0, 1):
            with self.subTest(optimize=optimize), self.assertRaises(FileExistsError):
                self.stage(optimize=optimize)
            self.assertEqual(self.target.read_bytes(), b"keep-existing-file")

    def test_competing_destination_creation_is_not_overwritten(self):
        original_mkdir = Path.mkdir
        def competing_mkdir(path, *args, **kwargs):
            if path == self.target and not path.exists():
                original_mkdir(path, parents=True)
                (path / "competitor.txt").write_bytes(b"keep-competitor")
            return original_mkdir(path, *args, **kwargs)
        with patch.object(Path, "mkdir", competing_mkdir), self.assertRaises(FileExistsError):
            self.stage(optimize=1)
        self.assertEqual((self.target / "competitor.txt").read_bytes(), b"keep-competitor")
        self.assertEqual(list(self.target.iterdir()), [self.target / "competitor.txt"])

    def test_missing_committed_inputs_never_create_destination(self):
        for files in ({}, {"Build/api/health/app.py": b"synthetic"},
                      {"infra/railway/dev/api.Dockerfile": b"synthetic"}):
            for optimize in (0, 1):
                with self.subTest(files=list(files), optimize=optimize), self.assertRaises(ValueError):
                    self.stage(files=files, optimize=optimize)
                self.assertFalse(self.target.exists())

    def test_forbidden_nested_source_is_rejected_before_any_write(self):
        for optimize in (0, 1):
            with self.subTest(optimize=optimize), self.assertRaises(ValueError):
                self.stage(files=FILES | {"Build/api/health/archive/private.txt": b"synthetic"}, optimize=optimize)
            self.assertFalse(self.target.exists())

    def test_service_manifests_preserve_committed_bytes_hashes_and_allowlists(self):
        for service in ("web", "api", "worker"):
            for optimize in (0, 1):
                with self.subTest(service=service, optimize=optimize):
                    self.target = Path(self.temp.name) / f"{service}-{optimize}"
                    self.stage(service, optimize=optimize)
                    manifest = json.loads((self.target / "context-manifest.json").read_text())
                    self.assertEqual(manifest["source_revision"], REVISION)
                    self.assertEqual(manifest["service"], service)
                    expected = {
                        "web": {"Build/web/src/page.jsx", "Build/web/package.json", "Build/lab/session-service.mjs",
                                "Build/library/loader.mjs", "Build/simulator/rk4.mjs", "Dockerfile",
                                "Build/web/library-snapshot/guest.json"},
                        "api": {"Build/api/health/app.py", "Build/api/health/dependencies.py", "Build/api/workspace/jobs.py",
                                "clips.csv", "evidence/S13/S13h/live/timing.json", "Dockerfile"},
                        "worker": {"Build/worker/health/app.py", "Build/api/health/dependencies.py", "Dockerfile"},
                    }[service]
                    self.assertEqual(set(manifest["files"]), expected)
                    for name, digest in manifest["files"].items():
                        content = (self.target / name).read_bytes()
                        self.assertEqual(hashlib.sha256(content).hexdigest(), digest)
                        if name != "Dockerfile": self.assertEqual(content, FILES.get(name, SNAPSHOT))
                    self.assertEqual((self.target / "Dockerfile").read_bytes(),
                                     f"ARG R2S_SOURCE_REVISION={REVISION}\n".encode())

    def test_web_snapshot_rejected_before_any_write(self):
        bad = SNAPSHOT.replace(base64.b64encode(OBJECT), base64.b64encode(OBJECT + b" "))  # hash mismatch
        self.assertNotEqual(bad, SNAPSHOT)
        for kwargs, err in (({"snapshot": bad}, ValueError), ({"snapshot": b"not json"}, ValueError),
                            ({"dirty": True}, subprocess.CalledProcessError)):
            with self.subTest(**{k: str(v)[:20] for k, v in kwargs.items()}), self.assertRaises(err):
                self.stage("web", **kwargs)
            self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
