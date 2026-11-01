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
        self.assertEqual((obj["id"], obj["kind"], obj["fixed"]), ("room-object-1", "block", True))

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
        calls = []
        app = FastAPI()
        app.include_router(create_router(Store(self.tmp), segment=lambda *a: (calls.append(a), (self.box, {}))[1]))
        c = TestClient(app)
        url = f"/internal/workspace/rooms/{'a' * 32}/objects"
        self.assertEqual(c.post(url, headers=A, json={"view": 0, "point": [500, 5]}).status_code, 422)
        self.assertEqual(c.post(url, headers=A, json={"view": 9, "point": [5, 5]}).status_code, 422)
        self.assertEqual(calls, [])  # bad input never reaches the paid call
        r = c.post(url, headers=A, json={"view": 0, "point": self.click})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(len(calls), 1)
        scene = json.loads((d / "scene.json").read_text())
        self.assertEqual([o["id"] for o in scene["objects"]], ["room-object-1"])
        self.assertEqual(r.json()["object"]["labels"]["scale"], "scale unverified")
        self.assertEqual(c.get(f"/internal/workspace/rooms/{'a' * 32}/views/0.png", headers=A).content[:4], b"\x89PNG")
        self.assertEqual(c.post(url, headers={**A, "x-workspace-owner": "user_synthB"},
                                json={"view": 0, "point": self.click}).status_code, 404)


if __name__ == "__main__":
    unittest.main()
