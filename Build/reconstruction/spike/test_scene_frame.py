"""Synthetic S05d checks: known plane/gravity recovered; scale only from a cited reference."""
import tempfile
import unittest
from pathlib import Path

import numpy as np

import scene_frame as sf


def synth_npz(path, tilt_deg=10.0, scale=1.0):
    rng = np.random.default_rng(1)
    t = np.radians(tilt_deg)
    down = np.array([0.0, np.cos(t), np.sin(t)])   # world down, tilted from +y
    u = np.cross(down, [1.0, 0, 0]); u /= np.linalg.norm(u)
    v = np.cross(down, u)
    data = {}
    for i in range(2):
        ab = rng.uniform(-2, 2, (294 * 518, 2))
        pts = ab[:, :1] * u + ab[:, 1:] * v + rng.normal(0, 0.003, (len(ab), 1)) * down
        pts[: len(pts) // 4] -= 1.0 * down              # clutter plane 1 unit above floor
        pose = np.eye(4); pose[:3, 1] = down; pose[:3, 2] = np.cross([1.0, 0, 0], down)
        pose[:3, 3] = -1.5 * down + [i * 0.3, 0, 0]
        p = f"view{i}_"
        data[p + "pts3d"] = (pts * scale).reshape(1, 294, 518, 3).astype(np.float32)
        data[p + "conf"] = np.ones((1, 294, 518), np.float32)
        data[p + "mask"] = np.ones((1, 294, 518, 1), np.float32)
        pose[:3, 3] *= scale
        data[p + "camera_poses"] = pose[None].astype(np.float32)
        data[p + "metric_scaling_factor"] = np.ones((1, 1), np.float32)
    np.savez(path, **data)
    return down


class SceneFrameTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "s.npz"

    def test_floor_and_gravity_recovered(self):
        down = synth_npz(self.path)
        r = sf.analyse(self.path)
        self.assertEqual(r["floor"]["status"], "FIT")
        self.assertLess(sf.angle_deg(np.array(r["gravity"]["direction"]), down), 0.5)
        self.assertLess(r["floor"]["rms_residual"], 0.01)
        self.assertAlmostEqual(r["floor"]["camera_heights_model_units"][0], 1.5, places=2)
        self.assertIsNone(r["gravity"]["magnitude_m_s2"])

    def test_reproducible(self):
        synth_npz(self.path)
        self.assertEqual(sf.analyse(self.path), sf.analyse(self.path))

    def test_abstains_without_reference_or_gravity(self):
        synth_npz(self.path)
        r = sf.analyse(self.path, gravity_applicable=False)
        self.assertEqual(r["metric_scale"]["status"], "ABSTAIN")
        self.assertIsNone(r["metric_scale"]["metres_per_model_unit"])
        self.assertEqual(r["gravity"]["status"], "ABSTAIN")
        self.assertEqual(r["a4_plane_normal"]["status"], "ABSTAIN")

    def test_scale_from_cited_reference(self):
        synth_npz(self.path, scale=0.5)        # one model unit = 2 m
        views = sf.load_views(self.path)
        img = views[0]["pts_img"]
        p0, p1 = (100, 100), (200, 300)
        true_len = float(np.linalg.norm(img[p0] - img[p1])) * 2.0
        ref = {"view": 0, "p0": p0, "p1": p1, "length_m": true_len, "length_sd_m": 0.01 * true_len,
               "source": "synthetic fixture"}
        s = sf.known_object_scale(views, ref)
        self.assertAlmostEqual(s["metres_per_model_unit"], 2.0, places=4)
        self.assertAlmostEqual(s["sd"], 0.02, places=4)
        r = sf.analyse(self.path, refs=[ref])
        self.assertEqual(r["metric_scale"]["status"], "calibrated")
        with self.assertRaises(ValueError):
            sf.known_object_scale(views, {**ref, "source": ""})


if __name__ == "__main__":
    unittest.main()
