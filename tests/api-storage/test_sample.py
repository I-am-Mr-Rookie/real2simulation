"""N11: SAMPLE project seeding. Offline; synthetic bytes stand in for the recorded RM04 bundle."""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.api import experiment, room
from Build.api.storage import create_router, sample, files as storage

TOKEN = "synthetic-test-token"
A = {"x-workspace-token": TOKEN, "x-workspace-owner": "user_synthA"}
B = {**A, "x-workspace-owner": "user_synthB"}
PLY = b"ply\nformat ascii 1.0\nelement vertex 2\nend_header\n0 0 0 1 2 3\n1 1 1 4 5 6\n"


class SampleTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.bundle = self.dir / "bundle"
        self.bundle.mkdir()
        (self.bundle / "points-mobile.ply").write_bytes(PLY)
        (self.bundle / "scene.json").write_text(json.dumps({"camera_path": [{"pose": {"position_m": [0, 0, 0]}}]}))
        self.manifest = self.dir / "manifest.json"
        self.manifest.write_text(json.dumps({"files": {"points-mobile.ply": {"sha256": hashlib.sha256(PLY).hexdigest()}}}))
        self.store = storage.Store(self.dir / "data")
        app = FastAPI()
        app.include_router(create_router(self.store))
        app.include_router(room.create_router(self.store))
        self.c = TestClient(app)
        for target, value in (("BUNDLE", self.bundle), ("MANIFEST", self.manifest)):
            patcher = mock.patch.object(sample, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        env = mock.patch.dict("os.environ", {"WORKSPACE_INTERNAL_TOKEN": TOKEN})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(lambda: (self.store.db.close(), shutil.rmtree(self.dir, ignore_errors=True)))

    def projects(self, h=A):
        return self.c.get("/internal/workspace/projects", headers=h).json()["projects"]

    def test_seeds_once_per_user_on_first_list(self):
        self.assertEqual(len(self.projects()), 1)
        self.assertEqual(len(self.projects()), 1)
        self.assertEqual(self.c.get("/internal/workspace/files", headers=A).json()["files"], [])
        p = self.projects()[0]
        self.assertTrue(p["title"].startswith("SAMPLE (RECORDED)"))
        self.assertEqual(len(self.projects(B)), 1)
        self.assertNotEqual(self.projects(B)[0]["id"], p["id"])

    def test_files_list_seeds_too_and_unauthorised_does_not(self):
        self.assertEqual(self.c.get("/internal/workspace/files").status_code, 401)
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM projects").fetchone()[0], 0)
        self.c.get("/internal/workspace/files", headers=A)
        self.assertEqual(len(self.projects()), 1)

    def test_experiment_and_room_are_recorded_and_attached(self):
        pid = self.projects()[0]["id"]
        row = self.store.db.execute("SELECT id FROM experiments WHERE project_id=?", (pid,)).fetchone()
        e = experiment.get(self.store, "user_synthA", row["id"])["experiment"]
        self.assertEqual(e["status"], "done")
        self.assertIn("SAMPLE / RECORDED", e["result"]["sample"]["label"])
        self.assertEqual(e["result"]["fit"]["y"]["model"], "constant_acceleration")
        self.assertNotIn("cost_usd", e["result"])
        job = next((self.store.root / "rooms" / "user_synthA").iterdir()).name
        r = self.c.get(f"/internal/workspace/rooms/{job}/result", headers=A).json()
        self.assertEqual(r["room"]["labels"]["scale"], "scale unverified")
        self.assertEqual(self.c.get(f"/internal/workspace/rooms/{job}/room.ply", headers=A).content, PLY)
        self.assertEqual(self.c.get(f"/internal/workspace/rooms/{job}/result", headers=B).status_code, 404)

    def test_missing_or_altered_bundle_keeps_experiment_only(self):
        (self.bundle / "points-mobile.ply").write_bytes(PLY + b"x")
        self.assertEqual(len(self.projects()), 1)
        self.assertFalse((self.store.root / "rooms").exists())
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM experiments").fetchone()[0], 1)

    def test_failed_seed_rolls_back_and_list_still_works(self):
        with mock.patch.object(sample, "EXPERIMENT", self.dir / "absent.json"):
            self.assertEqual(self.projects(), [])
        self.assertEqual(len(self.projects()), 1)  # retried once the cause is gone
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM samples").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
