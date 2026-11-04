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

    def test_quota_counts_owner_room_tree_and_tracks_removed_bytes(self):
        self.assertEqual(self.up().status_code, 201)
        room = Path(self.dir, "rooms", "user_synthA", "c" * 32)
        artifacts = {"room.ply": b"ply", "mapanything.npz": b"archive", "scene.json": b"{}",
                     "room.json": b"{}", "objects/crop.png": b"png", "objects/mesh.glb": b"glb"}
        for name, data in artifacts.items():
            path = room / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        other = Path(self.dir, "rooms", "user_synthB", "other.ply")
        other.parent.mkdir(parents=True)
        other.write_bytes(b"other owner's room")
        url = "/internal/workspace/files"
        used = len(MP4) + sum(map(len, artifacts.values()))
        q = self.c.get(url, headers=A).json()["quota"]
        self.assertEqual(q["storage_bytes_used"], used)
        self.assertEqual(q["storage_bytes_remaining"], storage.MAX_USER - used)
        self.assertEqual(self.c.get(url, headers=B).json()["quota"]["storage_bytes_used"], other.stat().st_size)
        (room / "room.ply").unlink()
        self.assertEqual(self.c.get(url, headers=A).json()["quota"]["storage_bytes_used"], used - len(b"ply"))

    def test_upload_quota_includes_room_artifacts(self):
        room = Path(self.dir, "rooms", "user_synthA", "c" * 32)
        room.mkdir(parents=True)
        (room / "room.ply").write_bytes(b"room")
        with mock.patch.object(storage, "MAX_USER", len(MP4) + len(b"room")):
            self.assertEqual(self.up().status_code, 201)  # exactly at the combined limit
            r = self.up()
            self.assertEqual((r.status_code, r.json()["detail"]["code"]), (413, "QUOTA_STORAGE"))
            self.assertEqual(r.json()["detail"]["quota"]["storage_bytes_used"], storage.MAX_USER)
            self.assertEqual(len(self.store.list("user_synthA")), 1)
            self.assertEqual(list(Path(self.dir, "tmp").iterdir()), [])

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
        url = f"/internal/workspace/projects/{p['id']}"
        self.assertEqual(self.c.patch(url, headers=B, json={"title": "x"}).status_code, 404)
        self.assertEqual(self.c.patch(url, headers=A, json={"title": " "}).status_code, 422)
        self.assertEqual(self.c.patch(url, headers=A, json={"title": " Classroom lab "}).json()["project"]["title"], "Classroom lab")
        self.assertEqual(self.c.delete(url, headers=B).status_code, 404)
        self.assertEqual(self.c.delete(url, headers=A).json(), {"deleted": p["id"]})
        self.assertEqual(self.c.get(url, headers=A).status_code, 404)

    def test_template_copy_save_lab_and_copy_use_owner_quota(self):
        """N89: a template copy is a saved lab project; copies count against the owner's 1 GB and delete frees it."""
        scene = {"version": "lab-scene-v1", "room": {"kind": "plane", "floor_y": 0},
                 "objects": [{"id": "wall-back", "kind": "block", "position": [0, 1.6, -6], "size": [12, 3.2, 0.15], "fixed": True,
                              "look": {"category": "wall", "color": "#d6d3d1"}}, {"id": "ball-1", "kind": "ball", "position": [0, 1, 0]}]}
        made = lambda body, h=A: self.c.post("/internal/workspace/projects", headers=h, json={"mode": "room", "title": "Physics lab", **body})
        for bad in ({"scene": {"objects": [{"kind": "ufo"}]}}, {"scene": "x"}):
            self.assertEqual(made(bad).status_code, 422)
        self.assertEqual(self.c.post("/internal/workspace/projects", headers=A, json={"mode": "experiment", "title": "x", "scene": scene}).status_code, 422)
        self.assertEqual(self.c.get("/internal/workspace/projects", headers=A).json()["projects"], [])  # refused = no row
        r = made({"scene": scene})
        self.assertEqual(r.status_code, 201, r.text)
        p = r.json()["project"]
        self.assertTrue(p["lab"])
        saved = self.store.lab_dir("user_synthA", p["id"]) / "scene.json"
        self.assertEqual(r.json()["quota"]["storage_bytes_used"], saved.stat().st_size)
        self.assertEqual([x["lab"] for x in self.c.get("/internal/workspace/projects", headers=A).json()["projects"]], [True])
        self.assertEqual(self.c.post(f"/internal/workspace/projects/{p['id']}/copy", headers=B).status_code, 404)
        c = self.c.post(f"/internal/workspace/projects/{p['id']}/copy", headers=A)
        self.assertEqual(c.status_code, 201, c.text)
        self.assertEqual((c.json()["project"]["title"], c.json()["quota"]["storage_bytes_used"]), ("Physics lab copy", 2 * saved.stat().st_size))
        self.assertEqual(self.c.get("/internal/workspace/projects", headers=B).json()["projects"], [])
        self.assertEqual(self.store.quota("user_synthB")["storage_bytes_used"], 0)
        plain = self.c.post("/internal/workspace/projects", headers=A, json={"mode": "room", "title": "No lab"}).json()["project"]
        self.assertEqual(self.c.post(f"/internal/workspace/projects/{plain['id']}/copy", headers=A).status_code, 409)
        with mock.patch.object(storage, "MAX_USER", 2 * saved.stat().st_size + 10):
            self.assertEqual(made({"scene": scene}).status_code, 413)
            self.assertEqual(self.c.post(f"/internal/workspace/projects/{p['id']}/copy", headers=A).status_code, 413)
        self.assertEqual(len(self.c.get("/internal/workspace/projects", headers=A).json()["projects"]), 3)
        self.assertEqual(self.c.delete(f"/internal/workspace/projects/{p['id']}", headers=A).status_code, 200)
        self.assertFalse(saved.exists())
        copy = self.store.lab_dir("user_synthA", c.json()["project"]["id"]) / "scene.json"
        self.assertEqual(self.store.quota("user_synthA")["storage_bytes_used"], copy.stat().st_size)

    def test_project_snapshot_owner_scoped_typed_and_size_limited(self):
        p = self.c.post("/internal/workspace/projects", headers=A, json={"mode": "room", "title": "Lab"}).json()["project"]
        url = f"/internal/workspace/projects/{p['id']}/snapshot"
        self.assertIsNone(self.c.get("/internal/workspace/projects", headers=A).json()["projects"][0]["snapshot_url"])
        jpg = b"\xff\xd8\xff\xe0" + b"SYNTHETIC" * 10
        put = lambda data, t="image/jpeg", h=A: self.c.put(url, headers={**h, "content-type": t}, content=data)
        self.assertEqual(put(jpg, h=B).status_code, 404)  # not B's project
        self.assertEqual(put(jpg, t="text/html").status_code, 415)
        self.assertEqual(put(PNG, t="image/jpeg").status_code, 415)  # bytes must match the type
        self.assertEqual(put(b"\xff\xd8\xff" + b"0" * (256 * 1024)).status_code, 413)
        r = put(jpg)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertTrue(r.json()["snapshot_url"].startswith(f"/api/workspace/projects/{p['id']}/snapshot?v="))
        self.assertEqual(self.c.get("/internal/workspace/projects", headers=A).json()["projects"][0]["snapshot_url"], r.json()["snapshot_url"])
        got = self.c.get(url, headers=A)
        self.assertEqual((got.status_code, got.content, got.headers["content-type"]), (200, jpg, "image/jpeg"))
        self.assertEqual(self.c.get(url, headers=B).status_code, 404)

    def test_delete_project_removes_snapshot_bytes_and_type_but_keeps_upload(self):
        p = self.c.post("/internal/workspace/projects", headers=A, json={"mode": "room", "title": "Lab"}).json()["project"]
        upload = self.up(project_id=p["id"]).json()["file"]
        url = f"/internal/workspace/projects/{p['id']}"
        self.assertEqual(self.c.put(url + "/snapshot", headers={**A, "content-type": "image/png"}, content=PNG).status_code, 200)
        path = self.store.root / "snapshots" / "user_synthA" / p["id"]
        self.assertTrue(path.is_file())
        self.assertEqual(self.c.delete(url, headers=B).status_code, 404)
        self.assertTrue(path.is_file())
        self.assertEqual(self.c.delete(url, headers=A).status_code, 200)
        self.assertFalse(path.exists())
        self.assertFalse(path.with_suffix(".type").exists())
        self.assertIsNone(self.c.get("/internal/workspace/files", headers=A).json()["files"][0]["project_id"])
        self.assertTrue(self.store.path("user_synthA", upload["id"]).is_file())

    def test_room_project_survives_upload_job_and_lists_without_changing_null_rows(self):
        from Build.api.room import create_router

        self.c.app.include_router(create_router(self.store, remote=lambda *a: None))
        legacy = self.up().json()["file"]
        with mock.patch("Build.api.room.threading.Thread"):
            legacy_room = self.c.post("/internal/workspace/rooms", headers=A,
                                      json={"file_id": legacy["id"]}).json()["job"]["job_id"]
        project = self.c.post("/internal/workspace/projects", headers=A,
                              json={"mode": "room", "title": "My room"}).json()["project"]
        uploaded = self.up(project_id=project["id"]).json()["file"]
        self.assertEqual(uploaded["project_id"], project["id"])
        with mock.patch("Build.api.room.threading.Thread"):
            for payload in ({"file_id": uploaded["id"], "project_id": project["id"]},
                            {"file_id": uploaded["id"]}):
                r = self.c.post("/internal/workspace/rooms", headers=A, json=payload)
                self.assertEqual(r.status_code, 202, r.text)
                self.assertEqual(r.json()["job"]["project_id"], project["id"])
        rooms = self.c.get("/internal/workspace/rooms", headers=A).json()["rooms"]
        self.assertEqual([r["project_id"] for r in rooms if r["id"] != legacy_room], [project["id"]] * 2)
        self.assertIsNone(next(r for r in rooms if r["id"] == legacy_room)["project_id"])
        files = self.c.get(f"/internal/workspace/projects/{project['id']}", headers=A).json()["files"]
        self.assertEqual([f["id"] for f in files], [uploaded["id"]])
        self.assertIsNone(self.store.get("user_synthA", legacy["id"])["project_id"])


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
