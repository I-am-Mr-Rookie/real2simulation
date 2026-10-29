"""S13h e2e driver, offline: SYNTHETIC bytes + fake keyframes/GPU stages (no ffmpeg, Modal or spend)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Build.pipeline import e2e
from Build.pipeline.jobs import StageError


class E2ETest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "clip.mp4").write_bytes(b"\0\0\0\x18ftypmp42" + b"x" * 100)  # SYNTHETIC
        (self.tmp / "clips.csv").write_text("clip_id,local_path\nSYN1,clip.mp4\n", encoding="utf-8")
        (self.tmp / "m.json").write_text("{}", encoding="utf-8")
        out = self.tmp / "out"

        def rec(key, scene, manifest, out_dir, ledger):
            out_dir.mkdir(parents=True)
            (out_dir / "reconstruction.json").write_text(json.dumps(
                {"scene_id": "syn", "scene_sha256": "0" * 64, "point_count": 3, "synthetic": True}))
            return "r" * 64
        self.patches = [mock.patch.object(e2e.keyframes, "extract", return_value={"keyframes": [1, 2]}),
                        mock.patch.object(e2e.gpu_stages, "sam_call", return_value=None),
                        mock.patch.object(e2e.gpu_stages, "segment", return_value="s" * 64),
                        mock.patch.object(e2e.gpu_stages, "reconstruct", side_effect=rec)]
        for p in self.patches:
            p.start()
        self.args = ("SYN1", 0, 1, "chair", 0, str(self.tmp / "m.json"), str(out), str(self.tmp / "clips.csv"))
        self.timing = out / "timing.json"

    def tearDown(self):
        mock.patch.stopall()

    def test_viewable(self):
        doc = e2e.main(*self.args)
        self.assertEqual([s["stage"] for s in doc["stages"]],
                         ["upload", "validate", "keyframes", "segment", "reconstruct", "viewable"])
        self.assertEqual(doc["status"], "viewable")
        self.assertTrue(doc["within_deadline"])
        self.assertEqual(json.loads(self.timing.read_text())["stages"][-1]["result"]["point_count"], 3)

    def test_measured_failure_stops(self):
        e2e.gpu_stages.segment.side_effect = StageError("PROCESSING_FAILED", "boom", True)
        with self.assertRaises(SystemExit):
            e2e.main(*self.args)
        doc = json.loads(self.timing.read_text())
        self.assertEqual(doc["status"], "failed")
        self.assertEqual(doc["stages"][-1]["stage"], "segment")
        self.assertIn("PROCESSING_FAILED", doc["stages"][-1]["error"])
        e2e.gpu_stages.reconstruct.assert_not_called()


if __name__ == "__main__":
    unittest.main()
