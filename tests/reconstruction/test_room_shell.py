"""N39 room shell: Manhattan wall fit, openings cut into walls, table top under clutter, keyframes."""
import unittest

import numpy as np

from Build.reconstruction import room_shell as rs


def box_room(yaw_deg=30.0, n=4000, seed=0):
    """Points on 3 walls of a 4 x 3 m room (one side open) plus floor, rotated by yaw about +Y."""
    rng = np.random.default_rng(seed)
    y = rng.uniform(0, 2.5, (3, n))
    walls = [np.column_stack([np.full(n, -2.0), y[0], rng.uniform(-1.5, 1.5, n)]),
             np.column_stack([np.full(n, 2.0), y[1], rng.uniform(-1.5, 1.5, n)]),
             np.column_stack([rng.uniform(-2, 2, n), y[2], np.full(n, -1.5)])]
    floor = np.column_stack([rng.uniform(-2, 2, n), np.zeros(n), rng.uniform(-1.5, 1.5, n)])
    p = np.concatenate([*walls, floor]) + rng.normal(0, 0.01, (4 * n, 3))
    a = np.radians(yaw_deg)
    ex, ez = rs._axes(a)  # local u, v -> world x, z
    xz = np.outer(p[:, 0], ex) + np.outer(p[:, 2], ez)
    return np.column_stack([xz[:, 0], p[:, 1], xz[:, 1]])


class RoomShell(unittest.TestCase):
    def test_walls_found_and_open_side_reported(self):
        yaw, walls = rs.walls(box_room())
        self.assertAlmostEqual(np.degrees(yaw), 30.0, delta=1.5)
        fit = {(w["axis"], w["side"]): w for w in walls if w["status"] == "FIT"}
        self.assertEqual(set(fit), {(0, -1), (0, 1), (1, -1)})
        self.assertAlmostEqual(fit[(0, -1)]["plane"], -2.0, delta=0.05)
        self.assertAlmostEqual(fit[(0, 1)]["plane"], 2.0, delta=0.05)
        self.assertAlmostEqual(fit[(1, -1)]["plane"], -1.5, delta=0.05)
        self.assertEqual(fit[(1, -1)]["span"], sorted([fit[(0, -1)]["plane"], fit[(0, 1)]["plane"]]))
        self.assertTrue(all(w["p95_residual"] < 0.05 for w in fit.values()))

    def test_door_and_window_become_openings(self):
        holes = [{"along": [0.5, 1.4], "y": [0.0, 2.0]}, {"along": [-1.5, -0.5], "y": [0.9, 1.8]}]
        parts = rs.pieces([-2.0, 2.0], 2.5, holes)
        self.assertEqual(parts, [(-2.0, -1.5, 0.0, 2.5), (-1.5, -0.5, 0.0, 0.9), (-1.5, -0.5, 1.8, 2.5),
                                 (-0.5, 0.5, 0.0, 2.5), (0.5, 1.4, 2.0, 2.5), (1.4, 2.0, 0.0, 2.5)])
        area = sum((a1 - a0) * (y1 - y0) for a0, a1, y0, y1 in parts)
        self.assertAlmostEqual(area, 4.0 * 2.5 - 0.9 * 2.0 - 1.0 * 0.9)
        yaw, walls = rs.walls(box_room(0.0))
        fit = [w for w in walls if w["status"] == "FIT"]
        objs = rs.wall_objects(yaw, fit, [{"wall": 0, **holes[0]}])
        self.assertEqual(len(objs), len(fit) - 1 + 3)  # wall 0 split in 3 around the door
        self.assertTrue(all(o["fixed"] and o["kind"] == "block" and o["id"].startswith("wall-") for o in objs))

    def test_table_top_ignores_laptop(self):
        rng = np.random.default_rng(1)
        h = np.concatenate([rng.normal(0.72, 0.01, 5000), rng.uniform(0.73, 0.95, 400), rng.uniform(0.0, 0.7, 300)])
        top, w = rs.top_surface(h)
        self.assertAlmostEqual(top, 0.735, delta=0.02)
        self.assertLess((h > top + w).sum(), 420)

    def test_front_view_finds_desk_top_not_book_stack(self):
        rng = np.random.default_rng(2)  # desk front face 0..0.75, thin visible desk top, dense book stack 1.0..1.26
        h = np.concatenate([rng.uniform(0, 0.75, 3000), rng.normal(0.75, 0.005, 200), rng.normal(1.2, 0.01, 4000)])
        flat = np.r_[np.zeros(3000, bool), np.ones(200, bool), np.zeros(4000, bool)]
        self.assertGreater(rs.top_surface(h)[0], 1.1)  # N39 failure: the 1.26 m "table"
        self.assertAlmostEqual(rs.top_surface(h, flat=flat)[0], 0.76, delta=0.03)

    def test_desk_and_hutch_merge_into_one_box(self):
        def det(view, noun, pos, size, n):
            return {"noun": noun, "view": view, "proxy": {"position": pos, "size": size, "rotation": [0, 0, 0, 1], "points": n}}
        desk = det(0, "desk", [0.0, 0.375, 0.0], [1.2, 0.75, 0.6], 900)
        hutch = det(3, "shelf", [0.0, 0.6, -0.2], [1.1, 1.2, 0.3], 500)  # on the desk's back half, other noun group
        frac, lo, hi = rs._footprint_overlap(desk["proxy"], hutch["proxy"])
        self.assertGreater(frac, rs.MERGE_OVERLAP)
        rs._grow(desk["proxy"], lo, hi)
        self.assertEqual(desk["proxy"]["size"], [1.2, 0.75, 0.65])  # union: hutch sticks out 5 cm at the back
        self.assertEqual(desk["proxy"]["position"], [0.0, 0.375, -0.025])
        side = det(5, "table", [1.0, 0.375, 0.0], [1.2, 0.75, 0.6], 400)  # same desk, view shifted 1 m: half overlap
        frac, lo, hi = rs._footprint_overlap(desk["proxy"], side["proxy"])
        self.assertAlmostEqual(frac, 0.2 / 1.2, places=3)
        self.assertEqual(rs._footprint_overlap(desk["proxy"], det(1, "chair", [3, 0.4, 3], [0.5, 0.8, 0.5], 99)["proxy"])[0], 0.0)

    def test_flatten_top_holds_and_clamps_blobs(self):
        from Build.reconstruction import object_lift
        # unit box table: slab top at y 0.3 (tilted lumps +-0.05) over the front half only, a blob up to 0.5, legs
        top = [[x, 0.3 + 0.05 * (x > 0), z] for x in (-0.5, 0.0, 0.5) for z in (-0.5, 0.0)]
        blob = [[0.0, 0.5, -0.25], [0.1, 0.5, -0.25], [0.0, 0.5, -0.15]]
        legs = [[-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, -0.5, 0.5], [-0.5, -0.5, 0.5]]
        v = np.array(top + blob + legs, float)
        f = np.array([[0, 1, 2], [1, 3, 2], [2, 3, 4], [3, 5, 4], [6, 7, 8], [0, 9, 10], [4, 11, 12]])
        out, plane, n = object_lift.flatten_top(v, f)
        self.assertTrue(0.3 <= plane <= 0.35)
        self.assertEqual(out.shape, (len(v) + n, 3))
        self.assertTrue(np.allclose(out[:6, 1], 0.5) and np.allclose(out[6:9, 1], 0.5))  # top + blob on the plane
        self.assertTrue(np.allclose(out[-n:, 1], 0.5) and n == 4)  # plan outline = the 4 corners, at the top
        self.assertTrue(np.allclose(out[9:13, 1], -0.5) and np.abs(out).max() <= 0.5 + 1e-9)

    def test_keyframes(self):
        self.assertEqual(rs.keyframes(8, 3), [0, 4, 7])
        self.assertEqual(rs.keyframes(8), list(range(8)))
        self.assertEqual(rs.keyframes(2), [0, 1])

    def test_shell_endpoint_keeps_furniture_drops_rest(self):
        import json
        import os
        import shutil
        import tempfile
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from Build.api.room.objects import create_router
        from Build.api.storage.files import Store
        from Build.reconstruction import live_room
        from tests.reconstruction.test_object_lift import TOKEN, A, fake_sf3d, room_npz
        os.environ["WORKSPACE_INTERNAL_TOKEN"] = TOKEN
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        npz, hit = room_npz()
        rows, cols = np.nonzero(hit)
        box = (cols.min(), rows.min(), cols.max(), rows.max())
        d = Store(tmp).root / "rooms" / "user_synthA" / ("c" * 32)
        d.mkdir(parents=True)
        (d / "mapanything.npz").write_bytes(npz)
        live_room.finish(d)
        live_room.set_status(d, state="done")
        nouns, seen = [], []

        def detect(png, noun, w, h):  # fake SAM: the box is a "table" and also a "chair" (overlap); tiny "bed" clutter
            nouns.append(noun)
            return [box] if noun in ("table", "chair") else [(0, 0, 2, 2)] if noun == "bed" else []
        app = FastAPI()
        app.include_router(create_router(Store(tmp), detect=detect, generate=fake_sf3d(seen)))
        c = TestClient(app)
        for _ in range(2):  # rerun replaces the shell, no duplicates
            r = c.post(f"/internal/workspace/rooms/{'c' * 32}/shell", headers=A, json={})
            self.assertEqual(r.status_code, 200, r.text)
        shell = json.loads((d / "room.json").read_text())["shell"]
        scene = json.loads((d / "scene.json").read_text())
        self.assertEqual(len(nouns), 2 * 2 * (len(rs.FURNITURE) + len(rs.FEATURES)))  # 2 views x nouns, twice
        self.assertEqual([k["category"] for k in shell["kept"]], ["table"])
        self.assertGreaterEqual(shell["dropped"], 3)  # chair twin x2 views, bed clutter, second table view
        obj = [o for o in scene["objects"] if o["id"].startswith("room-object-")]
        self.assertEqual(len(obj), 1)
        self.assertEqual(obj[0]["shape"]["type"], "mesh")
        self.assertAlmostEqual(obj[0]["position"][1], obj[0]["size"][1] / 2, places=3)  # reaches the floor
        self.assertLess(obj[0]["size"][1], 0.32)
        self.assertEqual(shell["labels"]["scale"], "scale unverified")


if __name__ == "__main__":
    unittest.main()
