"""N08 live room pipeline + /internal/workspace/rooms. Offline: synthetic point cloud, fake reconstruct, no Modal."""
import io
import json
import shutil
import sqlite3
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.api import gpu
from Build.api.room import create_router
from Build.api.storage.files import Store
from Build.reconstruction import live_room

ROOT = Path(__file__).resolve().parents[2]
TOKEN = "synthetic-test-token"
A = {"x-workspace-token": TOKEN, "x-workspace-owner": "user_synthA"}
B = {**A, "x-workspace-owner": "user_synthB"}
H = W = 96  # >=96 rows: one floor row + one wall row stays under S05d's 3% plane support
A4_REF = {"view": 0, "p0": [60, 40], "p1": [60, 50]}  # floor row: model distance 3 * 10 / 95, a plausible A4 edge
WIDE_REF = {"view": 0, "p0": [60, 20], "p1": [60, 80]}  # model distance 3 * 60 / 95: far too long for A4


def synthetic_npz(msf=None):
    """Two OpenCV-frame views (y down): ceiling 1.5 above (top rows), floor 1.0 below the cameras (bottom rows)."""
    rng = np.random.default_rng(1)
    arrays = {}
    for i in range(2):
        pts = np.zeros((H, W, 3))
        x = -1.5 + 3 * np.arange(W) / (W - 1)
        for r in range(H):
            pts[r, :, 0] = x
            pts[r, :, 1:] = (-1.5, 1 + 1.5 * r / 47) if r < 48 else (1.0, 1 + 1.5 * (r - 48) / 47)
        pose = np.eye(4)
        pose[0, 3] = 0.3 * i
        arrays.update({f"view{i}_pts3d": (pts + rng.normal(0, 0.002, pts.shape))[None],
                       f"view{i}_conf": np.ones((1, H, W)), f"view{i}_mask": np.ones((1, H, W)),
                       f"view{i}_img_no_norm": np.full((1, H, W, 3), 0.5), f"view{i}_camera_poses": pose[None]})
        if msf:
            arrays[f"view{i}_metric_scaling_factor"] = np.array([[msf[i]]])
    buf = io.BytesIO()
    np.savez_compressed(buf, **arrays)
    return buf.getvalue()


def fake_remote(frames):
    t = time.time()
    return {"npz": synthetic_npz(), "container_start_epoch": t, "function_start_epoch": t, "function_end_epoch": t + 1,
            "model_load_s": 0.5, "inference_s": 0.5}


def lab_scene_ok(scene):
    """Validate with the N10 editor's own lab-scene-v1 validator (node)."""
    url = (ROOT / "Build/web/src/lab-editor/scene.mjs").as_uri()
    code = f"import {{validateScene}} from '{url}'; import fs from 'node:fs'; validateScene(JSON.parse(fs.readFileSync(0, 'utf8')));"
    return subprocess.run(["node", "--input-type=module", "-e", code], input=json.dumps(scene), text=True,
                          capture_output=True).returncode == 0


class AnalyseTests(unittest.TestCase):
    def test_floor_gravity_aligned_scale_unverified(self):
        pts, rgb, room, scene = live_room.analyse(synthetic_npz())
        self.assertEqual(room["floor"]["status"], "FIT")
        self.assertEqual(room["gravity"]["status"], "MODEL-ESTIMATED")
        self.assertLess(room["gravity"]["uncertainty_deg"], 1.0)
        floor_pts = pts[np.abs(pts[:, 1]) < 0.05]
        self.assertGreater(len(floor_pts), len(pts) * 0.3)  # floor lands at y = 0 in the lab frame
        for cam in room["camera_positions_m"]:
            self.assertAlmostEqual(cam[1], 1.0, delta=0.02)  # cameras 1.0 above the floor, +Y up
        self.assertEqual(room["scale"]["status"], "scale unverified")
        self.assertIsNone(room["scale"]["sd"])
        self.assertFalse(scene["room"]["scale_verified"])
        self.assertEqual(rgb.dtype, np.uint8)
        self.assertTrue(lab_scene_ok(scene))

    def test_a4_reference_is_measured_with_uncertainty(self):
        pts, _, room, scene = live_room.analyse(synthetic_npz(), A4_REF)
        s = room["scale"]
        expected = 0.297 / (3 * 10 / 95)
        self.assertEqual(s["status"], "MEASURED")
        self.assertAlmostEqual(s["metres_per_model_unit"], expected, delta=expected * 0.01)
        self.assertGreater(s["sd"], 0)
        self.assertAlmostEqual(room["camera_positions_m"][0][1], expected, delta=0.02 * expected)
        self.assertTrue(scene["room"]["scale_verified"])

    def test_user_size_and_model_estimate(self):
        s = live_room.analyse(synthetic_npz(), {**WIDE_REF, "length_m": 1.0, "length_sd_m": 0.01})[2]["scale"]
        self.assertAlmostEqual(s["metres_per_model_unit"], 1.0 / (180 / 95), delta=0.01)
        self.assertEqual(s["reference"]["source"], "user-given size")

    def test_implausible_a4_clicks_rejected_not_measured(self):
        """N25 F6: two clicks that cannot be one A4 edge are not applied and never labelled MEASURED."""
        _, _, room, scene = live_room.analyse(synthetic_npz(), WIDE_REF)
        s = room["scale"]
        self.assertEqual((s["status"], s["metres_per_model_unit"]), ("scale unverified", 1.0))
        self.assertAlmostEqual(s["reference_rejected"]["metres_per_model_unit"], 0.297 / (180 / 95), places=3)
        self.assertIn("not applied", s["reference_rejected"]["reason"])
        self.assertNotIn("\u2014", s["reference_rejected"]["reason"])
        self.assertFalse(scene["room"]["scale_verified"])
        m = live_room.analyse(synthetic_npz(msf=(1.0, 1.1)))[2]["scale"]
        self.assertEqual(m["status"], "MODEL-ESTIMATED")
        self.assertAlmostEqual(m["sd"], 0.05 / 1.05, places=6)

    def test_bad_reference_rejected(self):
        for ref in ({**A4_REF, "p1": A4_REF["p0"]}, {**A4_REF, "view": 5}, {**A4_REF, "length_m": -1}, {"view": 0}):
            with self.assertRaises(ValueError):
                live_room.analyse(synthetic_npz(), ref)

    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg missing")
    def test_sample_frames(self):
        with tempfile.TemporaryDirectory() as d:
            v = Path(d) / "v.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=duration=1:size=64x48:rate=10",
                            str(v)], check=True)
            frames = live_room.sample_frames(v, 1.0, n=3)
        self.assertEqual(len(frames), 3)
        self.assertTrue(all(f.startswith(b"\x89PNG") for f in frames))


class JobTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, True)
        p = mock.patch.object(live_room, "sample_frames", return_value=[b"frame"] * 2)
        p.start()
        self.addCleanup(p.stop)
        self.gpu_db, self.cap_db = self.dir / "gpu.sqlite3", self.dir / "spend.sqlite3"

    def run_job(self, remote):
        d = self.dir / "job"
        d.mkdir()
        live_room.run_job(d, "v.mp4", 5.0, "user_synthA", remote=remote, gpu_db=self.gpu_db, cap_db=self.cap_db)
        return d, json.loads((d / "status.json").read_text())

    def ledger(self):
        con = sqlite3.connect(self.cap_db)
        try:
            return con.execute("SELECT provider, reserved, actual FROM spend").fetchall()
        finally:
            con.close()

    def test_success_ledgers_queues_and_saves_scene(self):
        d, s = self.run_job(fake_remote)
        self.assertEqual(s["state"], "done", s)
        self.assertEqual((s["scale"], s["gravity"]), ("scale unverified", "MODEL-ESTIMATED"))
        [(provider, reserved, actual)] = self.ledger()
        self.assertEqual(provider, "Modal")
        self.assertTrue(0 < actual <= reserved)
        self.assertEqual(gpu.status("user_synthA", None, self.gpu_db)["queue_length"], 0)
        self.assertTrue(lab_scene_ok(json.loads((d / "scene.json").read_text())))
        self.assertTrue((d / "room.ply").read_bytes().startswith(b"ply"))

    def test_remote_failure_settles_and_frees_queue(self):
        def boom(frames):
            raise RuntimeError("synthetic GPU failure")
        _, s = self.run_job(boom)
        self.assertEqual((s["state"], s["code"]), ("failed", "ERROR"))
        [(_, _, actual)] = self.ledger()
        self.assertIsNotNone(actual)
        self.assertEqual(gpu.status("user_synthA", None, self.gpu_db)["queue_length"], 0)

    def test_oom_retries_once_and_ledgers_each_gpu(self):
        calls = []

        def remote(frames, gpu="L4"):
            calls.append(gpu)
            if gpu == "L4":
                raise RuntimeError("CUDA out of memory")
            return {**fake_remote(frames), "gpu": gpu}

        d, s = self.run_job(remote)
        self.assertEqual(calls, ["L4", "A10G"])
        self.assertEqual((s["state"], s["gpu"]), ("done", "A10G"))
        rows = self.ledger()
        self.assertEqual(len(rows), 2)
        for (_, reserved, actual), device in zip(rows, calls):
            self.assertEqual(reserved, round(live_room.cost(1440, device, 2, 16)["total_usd"] * 1e8))
            self.assertTrue(0 < actual <= reserved)
        self.assertAlmostEqual(s["estimated_usd"], sum(row[2] for row in rows) / 1e8)
        self.assertEqual(json.loads((d / "cost-log.json").read_text())["gpu"], "A10G")
        self.assertEqual(gpu.status("user_synthA", None, self.gpu_db)["queue_length"], 0)

    def test_capacity_then_fallback_failure_has_no_third_attempt(self):
        remote = mock.Mock(side_effect=[RuntimeError("no GPU capacity"), RuntimeError("CUDA out of memory")])
        _, s = self.run_job(remote)
        self.assertEqual(remote.call_count, 2)
        self.assertEqual(s["state"], "failed")
        self.assertEqual(len(self.ledger()), 2)
        self.assertTrue(all(row[2] is not None for row in self.ledger()))
        self.assertEqual(gpu.status("user_synthA", None, self.gpu_db)["queue_length"], 0)

    def test_start_budget_cancels_l4_then_runs_a10g(self):
        from types import SimpleNamespace
        timeout = type("TimeoutError", (Exception,), {})
        fn = mock.Mock()
        fn.spawn.return_value.get.side_effect = timeout("still waiting for capacity")
        fallback = fn.with_options.return_value.spawn.return_value
        fallback.get.return_value = {**fake_remote([b"frame"]), "gpu": "A10G"}
        sdk = SimpleNamespace(Function=SimpleNamespace(from_name=mock.Mock(return_value=fn)),
                              exception=SimpleNamespace(TimeoutError=timeout))
        def fallback_options(**kwargs):
            fn.spawn.return_value.cancel.assert_called_once_with(terminate_containers=True)
            return fn.with_options.return_value
        fn.with_options.side_effect = fallback_options
        with mock.patch.dict("sys.modules", modal=sdk):
            _, s = self.run_job(live_room.modal_reconstruct)
        self.assertEqual((s["state"], s["gpu"]), ("done", "A10G"))
        fn.spawn.return_value.get.assert_called_once_with(timeout=live_room.ROOM_START_BUDGET_S)
        fallback.get.assert_called_once_with(timeout=540)
        self.assertEqual(len(self.ledger()), 2)
        self.assertTrue(all(row[2] > 0 for row in self.ledger()))  # unknown start: conservative timeout upper bound
        self.assertEqual(gpu.status("user_synthA", None, self.gpu_db)["queue_length"], 0)

    def test_daily_cap_denies_retry_and_frees_queue(self):
        remote = mock.Mock(side_effect=RuntimeError("CUDA out of memory"))
        from Build.guardrails import daily_cap
        original = daily_cap.reserve
        def reserve(provider, amount, label, **kwargs):
            if "A10G" in label:
                raise daily_cap.CapExceeded("synthetic exhausted cap")
            return original(provider, amount, label, **kwargs)
        with mock.patch.object(daily_cap, "reserve", side_effect=reserve):
            _, s = self.run_job(remote)
        self.assertEqual((s["state"], s["code"]), ("failed", "DAILY_CAP"))
        self.assertEqual(remote.call_count, 1)
        self.assertEqual(len(self.ledger()), 1)
        self.assertEqual(gpu.status("user_synthA", None, self.gpu_db)["queue_length"], 0)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.store = Store(self.dir)
        self.addCleanup(lambda: (self.store.db.close(), shutil.rmtree(self.dir, ignore_errors=True)))
        for p in (mock.patch.dict("os.environ", {"WORKSPACE_INTERNAL_TOKEN": TOKEN, "R2S_DATA_DIR": str(self.dir)}),
                  mock.patch.object(live_room, "sample_frames", return_value=[b"frame"] * 2)):
            p.start()
            self.addCleanup(p.stop)
        app = FastAPI()
        app.include_router(create_router(self.store, remote=fake_remote, stats=lambda: None))
        self.c = TestClient(app)
        tmp = self.dir / "tmp" / "clip"
        tmp.write_bytes(b"synthetic")
        self.file = self.store.add("user_synthA", "room.mp4", "video/mp4", tmp, 5.0)

    def test_start_poll_result_rescale_and_isolation(self):
        url = "/internal/workspace/rooms"
        self.assertEqual(self.c.post(url, json={"file_id": self.file["id"]}).status_code, 401)
        self.assertEqual(self.c.post(url, headers=B, json={"file_id": self.file["id"]}).status_code, 404)
        r = self.c.post(url, headers=A, json={"file_id": self.file["id"]})
        self.assertEqual(r.status_code, 202, r.text)
        job = r.json()["job"]["job_id"]
        for _ in range(100):
            s = self.c.get(f"{url}/{job}", headers=A).json()["job"]
            if s["state"] in ("done", "failed"):
                break
            time.sleep(0.1)
        self.assertEqual(s["state"], "done", s)
        res = self.c.get(f"{url}/{job}/result", headers=A).json()
        self.assertEqual(res["scene"]["version"], "lab-scene-v1")
        self.assertEqual(self.c.get(f"{url}/{job}/room.ply", headers=A).status_code, 200)
        self.assertEqual(self.c.get(f"{url}/{job}", headers=B).status_code, 404)
        self.assertEqual(self.c.get(f"{url}/..%2F..", headers=A).status_code, 404)
        out = self.c.post(f"{url}/{job}/scale", headers=A, json={"reference": A4_REF}).json()
        self.assertEqual(out["room"]["scale"]["status"], "MEASURED")
        bad = self.c.post(f"{url}/{job}/scale", headers=A, json={"reference": {**A4_REF, "view": 9}})
        self.assertEqual(bad.status_code, 422)

    def test_list_rooms_newest_first_and_isolated(self):
        url = "/internal/workspace/rooms"
        self.assertEqual(self.c.get(url, headers=A).json(), {"rooms": []})
        first = self.c.post(url, headers=A, json={"file_id": self.file["id"]}).json()["job"]["job_id"]
        time.sleep(1.1)  # created_at has 1 s resolution
        second = self.c.post(url, headers=A, json={"file_id": self.file["id"]}).json()["job"]["job_id"]
        rooms = self.c.get(url, headers=A).json()["rooms"]
        self.assertEqual([r["id"] for r in rooms], [second, first])
        self.assertEqual(self.c.get(url, headers=B).json(), {"rooms": []})
        self.assertEqual(self.c.get(url).status_code, 401)
        for _ in range(100):  # let background jobs finish before the temp dir is removed
            if all(r["state"] in ("done", "failed") for r in self.c.get(url, headers=A).json()["rooms"]):
                break
            time.sleep(0.1)


if __name__ == "__main__":
    unittest.main()
