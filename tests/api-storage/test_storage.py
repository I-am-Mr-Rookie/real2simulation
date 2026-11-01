"""N03: /internal/workspace/files + /projects via TestClient. Offline; synthetic bytes only, no Meta/Modal call."""
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.api.storage import files as storage

TOKEN = "synthetic-test-token"
A = {"x-workspace-token": TOKEN, "x-workspace-owner": "user_synthA"}
B = {**A, "x-workspace-owner": "user_synthB"}
MP4 = b"\x00\x00\x00\x18ftypmp42" + b"SYNTHETIC-N03" * 100
PNG = b"\x89PNG\r\n\x1a\n" + b"SYNTHETIC" * 10


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.clock = [datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)]  # 16:00 Dhaka
        self.store = storage.Store(self.dir, now=lambda: self.clock[0])
        self.probe = mock.Mock(return_value=5.0)
        app = FastAPI()
        app.include_router(storage.create_router(self.store, probe=self.probe))
        self.c = TestClient(app)
        env = mock.patch.dict("os.environ", {"WORKSPACE_INTERNAL_TOKEN": TOKEN})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(lambda: (self.store.db.close(), shutil.rmtree(self.dir, ignore_errors=True)))

    def up(self, headers=A, name="clip.mp4", data=MP4, **form):
        return self.c.post("/internal/workspace/files", headers=headers, files={"file": (name, data)}, data=form)

    def test_auth_required(self):
        for h in ({}, {"x-workspace-token": "wrong", "x-workspace-owner": "user_synthA"}, {"x-workspace-token": TOKEN}):
            self.assertEqual(self.up(headers=h).status_code, 401)
            self.assertEqual(self.c.get("/internal/workspace/files", headers=h).status_code, 401)

    def test_upload_list_range_download_and_isolation(self):
        r = self.up()
        self.assertEqual(r.status_code, 201, r.text)
        f = r.json()["file"]
        self.assertEqual((f["media_type"], f["size"], f["duration_s"]), ("video/mp4", len(MP4), 5.0))
        self.assertEqual(r.json()["quota"]["uploads_remaining_today"], 19)
        full = self.c.get(f"/internal/workspace/files/{f['id']}/content", headers=A)
        self.assertEqual((full.status_code, full.content), (200, MP4))
        part = self.c.get(f"/internal/workspace/files/{f['id']}/content", headers={**A, "range": "bytes=4-11"})
        self.assertEqual((part.status_code, part.content), (206, MP4[4:12]))
        self.assertEqual(part.headers["content-range"], f"bytes 4-11/{len(MP4)}")
        # user B sees nothing of A's
        self.assertEqual(self.c.get("/internal/workspace/files", headers=B).json()["files"], [])
        for method, path in (("get", ""), ("get", "/content"), ("delete", "")):
            self.assertEqual(getattr(self.c, method)(f"/internal/workspace/files/{f['id']}{path}", headers=B).status_code, 404)
        self.assertEqual([x["id"] for x in self.c.get("/internal/workspace/files", headers=A).json()["files"]], [f["id"]])

    def test_type_checks(self):
        self.assertEqual(self.up(name="x.gif").status_code, 415)
        self.assertEqual(self.up(name="x.mp4", data=PNG).status_code, 415)  # content must match extension
        r = self.up(name="x.png", data=PNG)
        self.assertEqual(r.status_code, 201)
        self.assertIsNone(r.json()["file"]["duration_s"])
        self.probe.return_value = 120.5
        r = self.up()
        self.assertEqual((r.status_code, r.json()["detail"]["code"]), (422, "VIDEO_TOO_LONG"))
        self.assertEqual(self.c.post("/internal/workspace/files", headers=A, data={"x": "1"}).status_code, 422)

    def test_file_size_limit_edge(self):
        with mock.patch.object(storage, "MAX_FILE", len(MP4)):
            self.assertEqual(self.up().status_code, 201)
            r = self.up(data=MP4 + b"x")
        self.assertEqual((r.status_code, r.json()["detail"]["code"]), (413, "FILE_TOO_LARGE"))
        self.assertEqual(len(list(Path(self.dir, "tmp").iterdir())), 0)  # refused bytes not left on disk

    def test_storage_quota_edge_and_delete_frees(self):
        with mock.patch.object(storage, "MAX_USER", 2 * len(MP4)):
            first = self.up().json()["file"]
            self.assertEqual(self.up().status_code, 201)  # exactly at the limit
            r = self.up()
            self.assertEqual((r.status_code, r.json()["detail"]["code"]), (413, "QUOTA_STORAGE"))
            self.assertEqual(r.json()["detail"]["quota"]["storage_bytes_remaining"], 0)
            self.assertEqual(self.up(headers=B).status_code, 201)  # quota is per user
            d = self.c.delete(f"/internal/workspace/files/{first['id']}", headers=A)
            self.assertEqual(d.json()["quota"]["storage_bytes_remaining"], len(MP4))
            self.assertFalse(self.store.path("user_synthA", first["id"]).exists())
            self.assertEqual(self.up().status_code, 201)

    def test_daily_upload_limit_dhaka_day(self):
        for _ in range(20):
            self.assertEqual(self.up(name="p.png", data=PNG).status_code, 201)
        r = self.up(name="p.png", data=PNG)
        self.assertEqual((r.status_code, r.json()["detail"]["code"]), (429, "QUOTA_UPLOADS"))
        d = r.json()["detail"]  # N25 F8: plain reason and reset time in the body
        self.assertEqual((d["reason"], d["reset_at"]), ("daily_upload_limit", "2026-11-01T18:00:00Z"))
        self.assertIn("resets at 2026-11-01T18:00:00Z", d["message"])
        q = r.json()["detail"]["quota"]
        self.assertEqual((q["uploads_remaining_today"], q["uploads_reset_at"]), (0, "2026-11-01T18:00:00Z"))
        first = self.c.get("/internal/workspace/files", headers=A).json()["files"][0]["id"]
        self.c.delete(f"/internal/workspace/files/{first}", headers=A)
        self.assertEqual(self.up(name="p.png", data=PNG).status_code, 429)  # delete does not refund daily count
        self.assertEqual(self.up(headers=B, name="p.png", data=PNG).status_code, 201)
        self.clock[0] = datetime(2026, 11, 1, 18, 0, tzinfo=timezone.utc)  # Dhaka midnight
        self.assertEqual(self.up(name="p.png", data=PNG).status_code, 201)

    def test_projects(self):
        r = self.c.post("/internal/workspace/projects", headers=A, json={"mode": "room", "title": " My room "})
        self.assertEqual(r.status_code, 201)
        p = r.json()["project"]
        self.assertEqual((p["mode"], p["title"], p["user"]), ("room", "My room", "user_synthA"))
        for bad in ({"mode": "lab", "title": "x"}, {"mode": "room", "title": ""}, {"mode": "room"}):
            self.assertEqual(self.c.post("/internal/workspace/projects", headers=A, json=bad).status_code, 422)
        self.assertEqual(self.up(project_id=p["id"]).status_code, 201)
        self.assertEqual(self.up(headers=B, project_id=p["id"]).status_code, 404)  # cannot attach to another's project
        got = self.c.get(f"/internal/workspace/projects/{p['id']}", headers=A).json()
        self.assertEqual(len(got["files"]), 1)
        self.assertEqual(self.c.get(f"/internal/workspace/projects/{p['id']}", headers=B).status_code, 404)
        self.assertEqual(self.c.get("/internal/workspace/projects", headers=B).json()["projects"], [])


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg/ffprobe not installed")
class FfprobeTests(unittest.TestCase):
    def test_real_duration(self):
        with tempfile.TemporaryDirectory() as d:
            for secs, expect in ((1, 1.0), (121, None)):
                out = Path(d, f"{secs}.mp4")
                subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", f"color=c=gray:s=32x32:r=1:d={secs}",
                                "-pix_fmt", "yuv420p", str(out)], check=True, timeout=60)
                got = storage.video_seconds(out)
                self.assertGreater(got, 120) if expect is None else self.assertAlmostEqual(got, expect, delta=0.1)
            bad = Path(d, "bad.mp4")
            bad.write_bytes(b"\x00\x00\x00\x18ftypmp42garbage")
            with self.assertRaises(Exception) as e:
                storage.video_seconds(bad)
            self.assertEqual(e.exception.status_code, 415)


if __name__ == "__main__":
    unittest.main()
