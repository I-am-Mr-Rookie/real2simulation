"""Offline S06d checks: tiny synthetic npz -> contract-valid bundle; unapproved ids refused. No Modal/GPU."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scene_job as j


def fake_npz(path):
    rng = np.random.default_rng(1)  # SYNTHETIC arrays only: exercise the converter, not a scene
    arrays = {}
    for i in range(2):
        arrays[f"view{i}_pts3d"] = rng.normal(size=(1, 4, 5, 3)).astype(np.float32)
        arrays[f"view{i}_conf"] = rng.random((1, 4, 5)).astype(np.float32)
        arrays[f"view{i}_mask"] = np.ones((1, 4, 5, 1), np.float32)
        arrays[f"view{i}_img_no_norm"] = rng.random((1, 4, 5, 3)).astype(np.float32)
        pose = np.eye(4, dtype=np.float32)
        pose[0, 3] = i
        arrays[f"view{i}_camera_poses"] = pose[None]
    np.savez(path, **arrays)


class SceneJob(unittest.TestCase):
    def test_bundle_validates(self):
        with tempfile.TemporaryDirectory() as d:
            fake_npz(Path(d) / "x.npz")
            sc = j.build_bundle("RM02", Path(d) / "x.npz", Path(d) / "b", "unit test")
            self.assertFalse(sc["synthetic"])
            self.assertEqual(sc["scale"]["status"], "estimated")
            self.assertIsNone(sc["gravity"]["direction"])
            self.assertEqual(sc["camera_path"][1]["pose"]["position_m"], [1.0, 0.0, 0.0])
            self.assertEqual(sc["camera_path"][0]["pose"]["rotation_xyzw"], [0.0, 0.0, 0.0, 1.0])
            self.assertEqual(json.loads((Path(d) / "b/scene.json").read_text())["id"], sc["id"])

    def test_opencv_to_contract_axes(self):
        r = np.diag(j.F) @ np.eye(3) @ np.diag(j.F)  # identity stays identity after the basis change
        self.assertEqual(j.quat_xyzw(r), [0.0, 0.0, 0.0, 1.0])
        r180y = np.diag([-1.0, 1.0, -1.0])
        self.assertAlmostEqual(abs(j.quat_xyzw(r180y)[1]), 1.0)

    def test_unapproved_scene_refused(self):
        for bad in ("RM01", "PD02", "AP15"):
            with self.assertRaises(ValueError):
                j.clip_row(bad)

    def test_all_approved_room_scenes_allowlisted(self):
        for ok in sorted(j.SCENE_IDS):  # RM04 'Pexels License' spelling broke S06f preflight
            self.assertIn(j.LICENCES[j.clip_row(ok)["licence"]], {"Pexels", "Public-Domain"})


if __name__ == "__main__":
    unittest.main()
