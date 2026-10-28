import copy
import hashlib
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parents[2]
PREFLIGHT = ROOT / "Build/measurement/runtime/preflight.py"
SPEC = importlib.util.spec_from_file_location("sam_runtime_preflight", PREFLIGHT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SamRuntimePreflightTests(unittest.TestCase):
    def _repo(self):
        directory = Path(tempfile.mkdtemp())
        for relative in MODULE.MANIFEST["files"]:
            path = directory / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(("fixture:" + relative).encode())
        subprocess.run(["git", "init", "-q", str(directory)], check=True)
        subprocess.run(["git", "-C", str(directory), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(directory), "config", "user.name", "test"], check=True)
        subprocess.run(["git", "-C", str(directory), "add", "."], check=True)
        subprocess.run(["git", "-C", str(directory), "commit", "-qm", "fixture"], check=True)
        revision = subprocess.run(["git", "-C", str(directory), "rev-parse", "HEAD"], check=True,
                                  capture_output=True, text=True).stdout.strip()
        manifest = copy.deepcopy(MODULE.MANIFEST)
        manifest["revision"] = revision
        manifest["files"] = {relative: hashlib.sha256(("fixture:" + relative).encode()).hexdigest()
                              for relative in manifest["files"]}
        return directory, manifest

    def test_positive_identity_fixture_and_dependency_metadata(self):
        directory, manifest = self._repo()
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as stream:
            stream.write("fixture-package==1.0.0\n")
            lock = Path(stream.name)
        with mock.patch.object(MODULE, "MANIFEST", manifest), \
             mock.patch.object(MODULE.importlib.metadata, "version", return_value="1.0.0"), \
             mock.patch.object(MODULE.platform, "system", return_value="Linux"), \
             mock.patch.object(MODULE.platform, "machine", return_value="x86_64"):
            result = MODULE.preflight(directory)
            dependencies = MODULE.dependency_preflight(lock)
        self.assertTrue(result["source_ok"])
        self.assertTrue(dependencies["dependency_ok"])
        self.assertFalse(result["runtime_ok"])

    def test_each_key_file_missing_or_corrupt_fails_source_identity(self):
        directory, manifest = self._repo()
        for relative in manifest["files"]:
            with self.subTest(relative=relative):
                path = directory / relative
                original = path.read_bytes()
                path.write_bytes(original + b"corrupt")
                with mock.patch.object(MODULE, "MANIFEST", manifest):
                    self.assertFalse(MODULE.preflight(directory)["source_ok"])
                path.unlink()
                with mock.patch.object(MODULE, "MANIFEST", manifest):
                    self.assertFalse(MODULE.preflight(directory)["source_ok"])
                path.write_bytes(original)

    def test_wrong_and_ancestor_revision_fail_closed(self):
        directory, manifest = self._repo()
        with mock.patch.object(MODULE, "MANIFEST", manifest), \
             mock.patch.object(MODULE.platform, "system", return_value="Linux"), \
             mock.patch.object(MODULE.platform, "machine", return_value="x86_64"):
            self.assertTrue(MODULE.preflight(directory)["source_ok"])
            first = subprocess.run(["git", "-C", str(directory), "rev-parse", "HEAD"], check=True,
                                   capture_output=True, text=True).stdout.strip()
            (directory / "extra.txt").write_text("second", encoding="utf-8")
            subprocess.run(["git", "-C", str(directory), "add", "."], check=True)
            subprocess.run(["git", "-C", str(directory), "commit", "-qm", "second"], check=True)
            self.assertFalse(MODULE.preflight(directory)["source_ok"])
            manifest["revision"] = first
            self.assertFalse(MODULE.preflight(directory)["source_ok"])

    def test_missing_source_and_symlink_source_fail_closed(self):
        missing = Path(tempfile.mkdtemp()) / "missing"
        self.assertFalse(MODULE.preflight(missing)["source_ok"])
        directory, manifest = self._repo()
        link = directory.parent / (directory.name + "-link")
        try:
            link.symlink_to(directory, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlink creation unavailable")
        with mock.patch.object(MODULE, "MANIFEST", manifest):
            self.assertFalse(MODULE.preflight(link)["source_ok"])

    def test_missing_dependency_lock_is_not_runtime_ready(self):
        result = MODULE.dependency_preflight(Path("C:/missing-sam-lock.txt"))
        self.assertFalse(result["dependency_ok"])


if __name__ == "__main__":
    unittest.main()
