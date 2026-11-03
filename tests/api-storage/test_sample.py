"""N11: SAMPLE project seeding. Offline; synthetic bytes stand in for the recorded RM04 bundle."""
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import numpy as np

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
        arrays = {}
        rng = np.random.default_rng(42)
        pts = rng.random((32, 32, 3))
        for i in range(2):
            arrays.update({f"view{i}_pts3d": pts[None], f"view{i}_conf": np.ones((1, 32, 32)),
                           f"view{i}_mask": np.ones((1, 32, 32)), f"view{i}_camera_poses": np.eye(4)[None],
                           f"view{i}_img_no_norm": np.full((1, 32, 32, 3), .5)})
        buf = io.BytesIO()
        np.savez(buf, **arrays)
        self.archive = buf.getvalue()
        (self.bundle / "RM04-mapanything.npz").write_bytes(self.archive)
        manifest = json.loads(self.manifest.read_text())
        manifest["files"]["RM04-mapanything.npz"] = {"sha256": hashlib.sha256(self.archive).hexdigest()}
        self.manifest.write_text(json.dumps(manifest))
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

    def shell_bundle(self):
        """Synthetic stand-in for the once-generated, public hash-checked RM02 pack."""
        manifest = json.loads(self.manifest.read_text())
        template = {"schema": "sample-room-shell/1", "archive": "RM02-mapanything.npz",
                    "point_cloud": "RM02-room.ply", "scene": "RM02-scene.json", "room": "RM02-room.json",
                    "meshes": {"room-object-1": "RM02-room-object-1.glb"}}
        block = {"kind": "block", "position": [0, 1, 0], "size": [1, 1, 1], "fixed": True}
        scene = {"version": "lab-scene-v1", "label": "SIMULATED", "units": "m", "gravity": [0, -9.81, 0],
                 "room": {"kind": "ply", "source": "room.ply", "floor_y": 0, "scale_verified": False},
                 "objects": [{**block, "id": "floor-1"}, {**block, "id": "wall-1"},
                             {**block, "id": "room-object-1", "shape": {"type": "mesh", "glb": "/stale/job.glb",
                              "label": "MODEL-GENERATED shape", "credit": "Powered by Stability AI"}}]}
        room_data = {"schema": "n08-room/1", "scale": {"status": "scale unverified", "sd": None},
                     "labels": {"input": "RECORDED", "geometry": "MODEL-ESTIMATED", "scale": "scale unverified"},
                     "shell": {"kept": [{"id": "room-object-1", "category": "chair", "shape": "mesh"}]}}
        assets = {template["archive"]: self.archive, template["point_cloud"]: PLY,
                  template["scene"]: json.dumps(scene).encode(), template["room"]: json.dumps(room_data).encode(),
                  "RM02-room-object-1.glb": b"glTF synthetic unit-test fixture"}
        for name, data in assets.items():
            (self.bundle / name).write_bytes(data)
            manifest["files"][name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        manifest["sample_shell"] = template
        self.manifest.write_text(json.dumps(manifest))

    def room_dir(self, owner="user_synthA"):
        return next((self.store.root / "rooms" / owner).iterdir())

    def test_fresh_seed_excludes_all_public_pack_bytes_but_counts_metadata(self):
        self.shell_bundle()
        self.projects()
        d = self.room_dir()
        public = json.loads((d / "public.json").read_text())
        self.assertEqual(set(public), {"room.ply", "mapanything.npz", "objects/room-object-1.glb"})
        for name, entry in public.items():
            path = d / name
            self.assertEqual(entry, {"size": path.stat().st_size, "mtime_ns": path.stat().st_mtime_ns,
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        # Quota uses only stat fingerprints, never reads/hashes public file contents.
        with mock.patch.object(sample.hashlib, "sha256", side_effect=AssertionError("quota must not hash")):
            quota = self.store.quota("user_synthA")
        self.assertEqual(quota["storage_bytes_public"], sum(entry["size"] for entry in public.values()))
        self.assertEqual(quota["storage_bytes_used"], sum(p.stat().st_size for p in d.rglob("*")
                                                       if p.is_file() and p.relative_to(d).as_posix() not in public))
        self.assertGreaterEqual(quota["storage_bytes_used"], (d / "scene.json").stat().st_size
                                + (d / "public.json").stat().st_size)
        response = self.c.get("/internal/workspace/files", headers=A)
        self.assertEqual(response.json()["quota"]["storage_bytes_public"], quota["storage_bytes_public"])

    def test_public_exemption_is_independent_of_sample_status_and_owner_isolated(self):
        self.shell_bundle()
        self.projects()
        d = self.room_dir()
        expected = self.store.quota("user_synthA")["storage_bytes_public"]
        status = json.loads((d / "status.json").read_text())
        status["sample"] = False
        (d / "status.json").write_text(json.dumps(status))
        self.assertEqual(self.store.quota("user_synthA")["storage_bytes_public"], expected)
        self.assertEqual(self.store.quota("user_synthB")["storage_bytes_public"], 0)
        (d / "public.json").unlink()
        status["sample"] = True
        (d / "status.json").write_text(json.dumps(status))
        self.assertEqual(self.store.quota("user_synthA")["storage_bytes_public"], 0)

    def test_initial_points_mobile_public_write_is_recorded_without_shell(self):
        manifest = json.loads(self.manifest.read_text())
        del manifest["files"]["RM04-mapanything.npz"]
        self.manifest.write_text(json.dumps(manifest))
        self.projects()
        d = self.room_dir()
        self.assertEqual(json.loads((d / "public.json").read_text())["room.ply"]["sha256"],
                         manifest["files"]["points-mobile.ply"]["sha256"])
        self.assertEqual(self.store.quota("user_synthA")["storage_bytes_public"], len(PLY))

    def test_edited_replaced_and_new_sample_files_count_whole_size(self):
        self.shell_bundle()
        self.projects()
        d = self.room_dir()
        original = self.store.quota("user_synthA")
        path = d / "room.ply"
        old = path.stat()
        # Same size, different bytes and mtime: no partial/delta charging.
        path.write_bytes(b"x" * old.st_size)
        os.utime(path, ns=(old.st_atime_ns, old.st_mtime_ns + 1_000_000_000))
        quota = self.store.quota("user_synthA")
        self.assertEqual(quota["storage_bytes_used"], original["storage_bytes_used"] + old.st_size)
        replacement = d / "replacement.tmp"
        replacement.write_bytes(b"user replacement")
        replacement.replace(d / "objects/room-object-1.glb")
        (d / "new.bin").write_bytes(b"user-created")
        self.assertEqual(self.store.quota("user_synthA")["storage_bytes_used"],
                         quota["storage_bytes_used"] + len(b"user replacement") + len(b"user-created"))
        # A returning-user repair must not renew exemptions for user edits.
        self.projects()
        self.assertEqual(self.store.quota("user_synthA")["storage_bytes_used"],
                         quota["storage_bytes_used"] + len(b"user replacement") + len(b"user-created"))

    def test_backfill_hashes_old_rooms_once_and_keeps_changed_bytes_counted(self):
        self.shell_bundle()
        self.projects()
        d = self.room_dir()
        (d / "public.json").unlink()
        (d / "objects/room-object-1.glb").write_bytes(b"user mesh")
        (d / "new.bin").write_bytes(b"new user file")
        self.projects()  # returning-user ensure_room_archive path
        public = json.loads((d / "public.json").read_text())
        self.assertEqual(set(public), {"room.ply", "mapanything.npz"})
        self.assertEqual(self.store.quota("user_synthA")["storage_bytes_public"], len(PLY) + len(self.archive))
        self.assertEqual(self.store.quota("user_synthA")["storage_bytes_used"],
                         sum(p.stat().st_size for p in d.rglob("*") if p.is_file()
                             and p.relative_to(d).as_posix() not in public))
        before = (d / "public.json").read_bytes()
        with mock.patch.object(sample.hashlib, "sha256", side_effect=AssertionError("backfill is one-time")):
            self.projects()
        self.assertEqual((d / "public.json").read_bytes(), before)

    def test_forged_fingerprints_and_scene_entries_never_hide_user_bytes(self):
        self.shell_bundle()
        self.projects()
        d = self.room_dir()
        index = d / "public.json"
        original = json.loads(index.read_text())
        for field in ("size", "mtime_ns"):
            with self.subTest(field=field):
                public = json.loads(json.dumps(original))
                public["room.ply"][field] += 1
                for path in (d / "scene.json", index):
                    stat = path.stat()
                    public[path.name] = {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
                index.write_text(json.dumps(public))
                quota = self.store.quota("user_synthA")
                self.assertEqual(quota["storage_bytes_public"], len(self.archive)
                                 + (d / "objects/room-object-1.glb").stat().st_size)
                self.assertEqual(quota["storage_bytes_used"], sum((d / name).stat().st_size
                                                               for name in ("room.ply", "scene.json", "room.json", "status.json", "public.json",
                                                                            "sample-previous-scene.json", "sample-previous-room.json")))

    def test_malformed_public_index_fails_closed(self):
        self.shell_bundle()
        self.projects()
        d = self.room_dir()
        for content in ("broken json", "[]", '{"room.ply": []}'):
            with self.subTest(content=content):
                (d / "public.json").write_text(content)
                quota = self.store.quota("user_synthA")
                self.assertEqual(quota["storage_bytes_public"], 0)
                self.assertEqual(quota["storage_bytes_used"], sum(p.stat().st_size for p in d.rglob("*") if p.is_file()))

    def test_seeds_once_per_user_on_first_list(self):
        self.assertEqual(len(self.projects()), 1)
        self.assertEqual(len(self.projects()), 1)
        self.assertEqual(self.c.get("/internal/workspace/files", headers=A).json()["files"], [])
        p = self.projects()[0]
        self.assertTrue(p["title"].startswith("SAMPLE (RECORDED)"))
        self.assertEqual(len(self.projects(B)), 1)
        self.assertNotEqual(self.projects(B)[0]["id"], p["id"])

    def test_sample_room_deletion_is_refused_and_shared_pack_stays_intact(self):
        self.shell_bundle()
        self.projects()
        d = self.room_dir()
        before = {p.name: p.read_bytes() for p in self.bundle.iterdir() if p.is_file()}
        used = self.store.quota(A["x-workspace-owner"])["storage_bytes_used"]
        response = self.c.delete("/internal/workspace/rooms/" + d.name, headers=A)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["detail"]["message"], "Sample rooms can't be deleted")
        self.assertTrue((d / "status.json").is_file())
        self.assertEqual({p.name: p.read_bytes() for p in self.bundle.iterdir() if p.is_file()}, before)
        self.assertEqual(self.store.quota(A["x-workspace-owner"])["storage_bytes_used"], used)

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
        app = FastAPI()  # N25 F2: the experiments list labels the seeded row SAMPLE instead of a bare hash
        app.include_router(experiment.create_router(self.store))
        rows = TestClient(app).get("/internal/workspace/experiments", headers=A).json()["experiments"]
        s = next(x for x in rows if x["file_id"] == "sample")
        self.assertIsNone(s["result"])
        self.assertTrue(s["sample"]["title"].startswith("SAMPLE (RECORDED)"))
        self.assertIn("SAMPLE / RECORDED", s["sample"]["label"])
        job = next((self.store.root / "rooms" / "user_synthA").iterdir()).name
        r = self.c.get(f"/internal/workspace/rooms/{job}/result", headers=A).json()
        self.assertEqual(r["room"]["labels"]["scale"], "scale unverified")
        self.assertTrue(self.c.get(f"/internal/workspace/rooms/{job}/room.ply", headers=A).content.startswith(b"ply\n"))
        self.assertEqual(self.c.get(f"/internal/workspace/rooms/{job}/result", headers=B).status_code, 404)

    def test_sample_archive_views_old_sample_repair_and_no_substitution_for_user_room(self):
        from Build.api.room.objects import create_router as object_router
        self.c.app.include_router(object_router(self.store))
        pid = self.projects()[0]["id"]
        d = next((self.store.root / "rooms" / "user_synthA").iterdir())
        url = f"/internal/workspace/rooms/{d.name}/views/0.png"
        self.assertEqual((d / "mapanything.npz").read_bytes(), self.archive)
        image = self.c.get(url, headers=A)
        self.assertEqual((image.status_code, image.headers["content-type"]), (200, "image/png"))
        self.assertTrue(image.content.startswith(b"\x89PNG"))
        self.assertEqual(self.c.get(url, headers=B).status_code, 404)
        (d / "mapanything.npz").unlink()
        self.assertEqual(self.c.get(url, headers=A).status_code, 200)  # pre-N58 sample upgrades on demand
        (d / "mapanything.npz").unlink()
        status = json.loads((d / "status.json").read_text())
        status["sample"] = False
        (d / "status.json").write_text(json.dumps(status))
        self.assertEqual(self.c.get(url, headers=A).status_code, 503)
        self.assertFalse((d / "mapanything.npz").exists())

    def test_sample_archive_rejects_bad_hash(self):
        self.projects()
        d = next((self.store.root / "rooms" / "user_synthA").iterdir())
        (d / "mapanything.npz").unlink()
        (self.bundle / "RM04-mapanything.npz").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            sample.ensure_room_archive(d)
        self.assertFalse((d / "mapanything.npz").exists())

    def test_new_samples_copy_shared_shell_meshes_without_inference(self):
        from Build.api.room.objects import create_router as object_router
        self.c.app.include_router(object_router(self.store))
        self.shell_bundle()
        with mock.patch("Build.api.room.objects.build_shell_files", side_effect=AssertionError("no inference")), \
             mock.patch("Build.gpu.sf3d.generate_remote", side_effect=AssertionError("no GPU")):
            self.projects()
            self.projects(B)
        for owner, headers in (("user_synthA", A), ("user_synthB", B)):
            d = self.room_dir(owner)
            result = self.c.get(f"/internal/workspace/rooms/{d.name}/result", headers=headers).json()
            scene, record = result["scene"], result["room"]
            self.assertEqual(len(scene["objects"]), 3)
            self.assertTrue(record["sample"])
            self.assertIn("SAMPLE / RECORDED", record["note"])
            self.assertIn("SAMPLE / RECORDED", record["labels"]["geometry"])
            self.assertEqual(record["scale"]["status"], "scale unverified")
            mesh = scene["objects"][-1]["shape"]
            self.assertEqual(mesh["label"], "MODEL-GENERATED shape")
            self.assertEqual(mesh["credit"], "Powered by Stability AI")
            self.assertEqual(mesh["glb"], f"/api/workspace/rooms/{d.name}/objects/room-object-1.glb")
            url = f"/internal/workspace/rooms/{d.name}/objects/room-object-1.glb"
            response = self.c.get(url, headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["content-type"], "model/gltf-binary")
            self.assertEqual(response.content, (self.bundle / "RM02-room-object-1.glb").read_bytes())
            self.assertEqual(self.c.get(url, headers=B if headers == A else A).status_code, 404)

    def test_existing_sample_list_backfills_once_and_preserves_later_edits(self):
        self.projects()
        d = self.room_dir()
        old_scene = json.loads((d / "scene.json").read_text())
        old_scene["gravity"] = [0, -4, 0]
        old_scene["objects"] = [{"id": "ball-1", "kind": "ball", "position": [1, 2, 3]}]
        (d / "scene.json").write_text(json.dumps(old_scene))
        self.shell_bundle()
        self.assertEqual(len(self.projects()), 1)  # existing samples-table row does not skip repair
        scene = json.loads((d / "scene.json").read_text())
        self.assertEqual(len(scene["objects"]), 4)
        self.assertEqual(scene["gravity"], [0, -4, 0])
        self.assertIn(old_scene["objects"][0], scene["objects"])
        self.assertEqual(json.loads((d / "sample-previous-scene.json").read_text()), old_scene)
        scene["objects"] = scene["objects"][1:]  # user deletes an installed wall/floor after the migration
        (d / "scene.json").write_text(json.dumps(scene))
        before = {p.name: p.read_bytes() for p in d.glob("*.json")}
        self.projects()
        self.c.get(f"/internal/workspace/rooms/{d.name}/result", headers=A)
        self.assertEqual(before, {p.name: p.read_bytes() for p in d.glob("*.json")})
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM projects").fetchone()[0], 1)

    def test_pre_n58_result_path_repairs_missing_archive_and_shell(self):
        self.projects()
        d = self.room_dir()
        (d / "mapanything.npz").unlink()
        self.shell_bundle()
        response = self.c.get(f"/internal/workspace/rooms/{d.name}/result", headers=A)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["scene"]["objects"]), 3)
        self.assertEqual((d / "mapanything.npz").read_bytes(), self.archive)

    def test_repair_restores_missing_mesh_without_resurrecting_deleted_objects(self):
        self.shell_bundle()
        self.projects()
        d = self.room_dir()
        mesh = d / "objects/room-object-1.glb"
        mesh.unlink()
        scene = (d / "scene.json").read_bytes()
        sample.ensure_room_archive(d)
        self.assertTrue(mesh.is_file())
        self.assertEqual((d / "scene.json").read_bytes(), scene)

    def test_corrupt_shell_asset_does_not_partially_migrate_existing_sample(self):
        self.projects()
        d = self.room_dir()
        self.shell_bundle()
        (self.bundle / "RM02-room-object-1.glb").write_bytes(b"tampered")
        before = {p.name: p.read_bytes() for p in d.iterdir() if p.is_file()}
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            sample.ensure_room_archive(d)
        self.assertEqual(before, {p.name: p.read_bytes() for p in d.iterdir() if p.is_file()})

    def test_shell_repair_never_changes_non_sample_room_even_with_existing_archive(self):
        self.projects()
        d = self.room_dir()
        status = json.loads((d / "status.json").read_text())
        status["sample"] = False
        (d / "status.json").write_text(json.dumps(status))
        self.shell_bundle()
        before = {p.name: p.read_bytes() for p in d.iterdir() if p.is_file()}
        self.projects()
        sample.ensure_room_archive(d)
        self.assertEqual(before, {p.name: p.read_bytes() for p in d.iterdir() if p.is_file()})

    def test_public_bundle_rejects_traversal_and_leaves_sample_untouched(self):
        self.projects()
        d = self.room_dir()
        self.shell_bundle()
        manifest = json.loads(self.manifest.read_text())
        manifest["sample_shell"]["archive"] = "../outside.npz"
        self.manifest.write_text(json.dumps(manifest))
        before = (d / "scene.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "asset name"):
            sample.ensure_room_archive(d)
        self.assertEqual(before, (d / "scene.json").read_bytes())

    def test_custom_sample_shell_is_not_overwritten(self):
        self.projects()
        d = self.room_dir()
        room_data = json.loads((d / "room.json").read_text())
        room_data["shell"] = {"kept": [{"id": "room-object-1", "custom": True}]}
        (d / "room.json").write_text(json.dumps(room_data))
        self.shell_bundle()
        before = (d / "room.json").read_bytes()
        self.projects()
        self.assertEqual(before, (d / "room.json").read_bytes())

    def test_existing_clicked_object_mesh_is_not_overwritten_by_same_template_id(self):
        self.projects()
        d = self.room_dir()
        scene = json.loads((d / "scene.json").read_text())
        scene["objects"] = [{"id": "room-object-1", "shape": {"type": "mesh"}}]
        (d / "scene.json").write_text(json.dumps(scene))
        (d / "objects").mkdir()
        glb = d / "objects/room-object-1.glb"
        glb.write_bytes(b"user-created-mesh")
        self.shell_bundle()
        self.projects()
        self.assertEqual(glb.read_bytes(), b"user-created-mesh")
        self.assertEqual(json.loads((d / "scene.json").read_text()), scene)

    def test_full_custom_scene_is_not_made_unloadable(self):
        self.projects()
        d = self.room_dir()
        scene = json.loads((d / "scene.json").read_text())
        scene["objects"] = [{"id": f"ball-{i}"} for i in range(50)]
        (d / "scene.json").write_text(json.dumps(scene))
        self.shell_bundle()
        self.projects()
        self.assertEqual(json.loads((d / "scene.json").read_text()), scene)

    def test_deleted_sample_project_is_not_backfilled_or_resurrected(self):
        pid = self.projects()[0]["id"]
        d = self.room_dir()
        self.assertEqual(self.c.delete(f"/internal/workspace/projects/{pid}", headers=A).status_code, 200)
        before = (d / "room.json").read_bytes()
        self.shell_bundle()
        self.assertEqual(self.projects(), [])
        self.assertEqual(before, (d / "room.json").read_bytes())

    def test_missing_or_altered_bundle_keeps_experiment_only(self):
        (self.bundle / "points-mobile.ply").write_bytes(PLY + b"x")
        self.assertEqual(len(self.projects()), 1)
        self.assertFalse((self.store.root / "rooms").exists())
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM experiments").fetchone()[0], 1)

    def test_old_experiment_only_sample_gains_room_when_bundle_becomes_available(self):
        (self.bundle / "points-mobile.ply").write_bytes(b"unavailable")
        self.projects()
        self.assertFalse((self.store.root / "rooms").exists())
        (self.bundle / "points-mobile.ply").write_bytes(PLY)
        self.shell_bundle()
        self.assertEqual(len(self.projects()), 1)
        self.assertEqual(len(json.loads((self.room_dir() / "scene.json").read_text())["objects"]), 3)
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM experiments").fetchone()[0], 1)

    def test_failed_seed_rolls_back_and_list_still_works(self):
        with mock.patch.object(sample, "EXPERIMENT", self.dir / "absent.json"):
            self.assertEqual(self.projects(), [])
        self.assertEqual(len(self.projects()), 1)  # retried once the cause is gone
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM samples").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
