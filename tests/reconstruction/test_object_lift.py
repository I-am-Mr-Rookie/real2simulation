"""N14 object lift: synthetic room with a box on the floor, fake SAM; no network, no paid calls."""
import io
import json
import shutil
import tempfile
import unittest

import numpy as np
from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.api.room.objects import create_router
from Build.api.storage.files import Store
from Build.reconstruction import live_room, object_lift

TOKEN = "synthetic-test-token"
A = {"x-workspace-token": TOKEN, "x-workspace-owner": "user_synthA"}
H, W, F = 120, 160, 100.0  # pinhole grid, focal 100 px, centre (80, 60)
# square pyramid (base y=0, apex y=1): not a box, so mesh and box colliders differ
PYRAMID = {"vertices": [[-1, 0, -1], [1, 0, -1], [1, 0, 1], [-1, 0, 1], [0, 1, 0]],
           "faces": [[0, 1, 2], [0, 2, 3], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]}


def fake_sf3d(seen):
    def gen(png):
        seen.append(png)
        return {**PYRAMID, "glb": b"glTF-fake", "gpu": "L4", "gpu_name": "NVIDIA L4", "wall_s": 1.0,
                "estimated_usd": 0.2}
    return gen


def room_npz():
    """Two identical-pose OpenCV views (camera 1.2 m above a floor, looking along +z, y down) with a
    0.4 x 0.3 x 0.4 m box on the floor centred 3 m ahead: depths are ray-cast exactly."""
    rr, cc = np.mgrid[0:H, 0:W]
    d = np.stack([(cc - 80) / F, (rr - 60) / F, np.ones_like(rr, float)], -1)
    pts = np.full((H, W, 3), np.nan)
    floor_t = np.where(d[..., 1] > 0, 1.2 / np.where(d[..., 1] > 0, d[..., 1], 1), np.inf)
    t = np.minimum(floor_t, 8.0)  # back wall at z = 8
    box_front = 2.8 / d[..., 2]
    p = d * box_front[..., None]
    hit = (abs(p[..., 0]) <= 0.2) & (p[..., 1] >= 0.9) & (p[..., 1] <= 1.2)  # front face z=2.8, y 0.9..1.2 (down)
    t = np.where(hit, box_front, t)
    pts = d * t[..., None]
    arrays = {}
    for i in range(2):
        arrays.update({f"view{i}_pts3d": pts[None], f"view{i}_conf": np.ones((1, H, W)),
                       f"view{i}_mask": np.ones((1, H, W)), f"view{i}_camera_poses": np.eye(4)[None],
                       f"view{i}_img_no_norm": np.full((1, H, W, 3), 0.5)})
    buf = io.BytesIO()
    np.savez(buf, **arrays)
    return buf.getvalue(), hit


class ObjectLift(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.npz, hit = room_npz()
        rows, cols = np.nonzero(hit)
        self.box = (cols.min(), rows.min(), cols.max(), rows.max())
        self.click = [int(rows.mean()), int(cols.mean())]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_lift_measures_visible_box(self):
        _, _, room, scene = live_room.analyse(self.npz)
        proxy = object_lift.lift(self.npz, 0, self.click, self.box, room)
        sx, sy, sz = proxy["size"]
        self.assertAlmostEqual(max(sx, sz), 0.4 * 0.9, delta=0.06)  # p5-p95 of a 0.4 m face
        self.assertAlmostEqual(sy, 0.3 * 0.9, delta=0.05)
        self.assertLess(min(sx, sz), 0.05)  # only the front face is visible: depth is a lower bound
        rot, origin = object_lift._room_frame(self.npz)  # visible face centre (0, 1.05, 2.8) in camera coords
        np.testing.assert_allclose(proxy["position"], (np.array([0, 1.05, 2.8]) - origin) @ rot.T, atol=0.03)
        _, obj = object_lift.to_scene(scene, proxy)
        self.assertEqual((obj["id"], obj["kind"], obj["fixed"]), ("room-object-1", "block", False))  # "other"
        self.assertTrue(object_lift.to_scene(scene, proxy, category="desk")[1]["fixed"])
        self.assertEqual(proxy["mask"].sum(), proxy["points"])  # the SF3D cut-out = the measured object pixels
        png = object_lift.crop_rgba(self.npz, 0, self.box, proxy["mask"])
        from PIL import Image
        self.assertEqual(Image.open(io.BytesIO(png)).mode, "RGBA")

    def test_fit_mesh_faces_camera_in_unit_box(self):
        proxy = {"position": [0, 0.5, 3], "rotation": [0, 0, 0, 1], "camera": [0, 1.2, 0]}  # camera at -z of object
        turns, v, idx, _ = object_lift.fit_mesh(PYRAMID["vertices"], PYRAMID["faces"], proxy)
        self.assertEqual(turns, 2)  # +Z front turned 180 deg to face the camera
        v = np.reshape(v, (-1, 3))
        np.testing.assert_allclose([v.min(0), v.max(0)], [[-0.5] * 3, [0.5] * 3])
        self.assertEqual(len(idx), 18)
        yawed = {**proxy, "rotation": [0, np.sin(np.pi / 4), 0, np.cos(np.pi / 4)]}  # box turned +90 deg
        self.assertEqual(object_lift.fit_mesh(PYRAMID["vertices"], PYRAMID["faces"], yawed)[0], 1)
        with self.assertRaises(ValueError):
            object_lift.fit_mesh(PYRAMID["vertices"], [[0, 1, 9]], proxy)

    def test_pick_box_and_reject_miss(self):
        text = "1<|box;x1=10;y1=10;x2=50;y2=50;w=160;h=120|>,2<|box;x1=20;y1=20;x2=30;y2=30;w=160;h=120|>"
        self.assertEqual(object_lift.pick_box(text, [25, 25]), (20, 20, 30, 30))
        with self.assertRaises(ValueError):
            object_lift.pick_box(text, [100, 100])

    def test_endpoint_appends_block_and_validates(self):
        import os
        os.environ["WORKSPACE_INTERNAL_TOKEN"] = TOKEN
        d = Store(self.tmp).root / "rooms" / "user_synthA" / ("a" * 32)
        d.mkdir(parents=True)
        (d / "mapanything.npz").write_bytes(self.npz)
        live_room.finish(d)
        live_room.set_status(d, state="done")
        calls, seen = [], []
        app = FastAPI()
        app.include_router(create_router(Store(self.tmp), segment=lambda *a: (calls.append(a), (self.box, {}))[1],
                                         generate=fake_sf3d(seen)))
        c = TestClient(app)
        url = f"/internal/workspace/rooms/{'a' * 32}/objects"
        self.assertEqual(c.post(url, headers=A, json={"view": 0, "point": [500, 5]}).status_code, 422)
        self.assertEqual(c.post(url, headers=A, json={"view": 9, "point": [5, 5]}).status_code, 422)
        self.assertEqual(c.post(url, headers=A, json={"view": 0, "point": self.click, "category": "x"}).status_code, 422)
        self.assertEqual((calls, seen), ([], []))  # bad input never reaches the paid calls
        r = c.post(url, headers=A, json={"view": 0, "point": self.click, "category": "desk"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual((len(calls), len(seen)), (1, 1))
        scene = json.loads((d / "scene.json").read_text())
        self.assertEqual([o["id"] for o in scene["objects"]], ["room-object-1"])
        shape = scene["objects"][0]["shape"]
        self.assertEqual((shape["type"], shape["label"], shape["credit"], scene["objects"][0]["fixed"]),
                         ("mesh", "MODEL-GENERATED shape", "Powered by Stability AI", True))
        self.assertEqual(c.get(shape["glb"].replace("/api/workspace", "/internal/workspace"), headers=A).content,
                         b"glTF-fake")
        self.assertEqual(r.json()["object"]["sf3d"]["estimated_usd"], 0.2)
        self.assertEqual(r.json()["object"]["labels"]["scale"], "scale unverified")
        self.assertEqual(c.get(f"/internal/workspace/rooms/{'a' * 32}/views/0.png", headers=A).content[:4], b"\x89PNG")
        self.assertEqual(c.post(url, headers={**A, "x-workspace-owner": "user_synthB"},
                                json={"view": 0, "point": self.click}).status_code, 404)

    def test_sf3d_failure_keeps_the_box_with_reason(self):
        import os
        os.environ["WORKSPACE_INTERNAL_TOKEN"] = TOKEN
        d = Store(self.tmp).root / "rooms" / "user_synthA" / ("b" * 32)
        d.mkdir(parents=True)
        (d / "mapanything.npz").write_bytes(self.npz)
        live_room.finish(d)
        live_room.set_status(d, state="done")

        def broken(png):
            raise RuntimeError("SF3D gave no result within 600s (no GPU capacity?)")
        app = FastAPI()
        app.include_router(create_router(Store(self.tmp), segment=lambda *a: (self.box, {}), generate=broken))
        r = TestClient(app).post(f"/internal/workspace/rooms/{'b' * 32}/objects", headers=A,
                                 json={"view": 0, "point": self.click, "category": "chair"})
        self.assertEqual(r.status_code, 200, r.text)
        shape = json.loads((d / "scene.json").read_text())["objects"][0]["shape"]
        self.assertEqual(shape["type"], "box")
        self.assertIn("no GPU capacity", shape["fallback_reason"])
        self.assertEqual(r.json()["object"]["labels"]["shape"], "box fallback")


if __name__ == "__main__":
    unittest.main()
