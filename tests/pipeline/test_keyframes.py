"""S13c keyframe tests on SYNTHETIC ffmpeg lavfi clips in a temp dir; not real-scene or gate evidence."""
import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Build.pipeline import keyframes as k
from Build.pipeline.contracts import ROOT
from Build.pipeline.uploads import UploadError

LAVFI = ["ffmpeg", "-v", "error", "-nostdin", "-y", "-f", "lavfi", "-i"]


def make(path, src, *args):
    subprocess.run([*LAVFI, src, *args, str(path)], check=True)
    return path


class KeyframeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d = cls.d = Path(cls.tmp.name)
        # VFR: frame n at n^2*10 ms; keyframes forced at frames 0, 5, 12 -> 0, 0.25, 1.44 s.
        make(d / "vfr.mp4", "testsrc=size=64x48:rate=10:duration=2",
             "-vf", "settb=1/1000,setpts=N*N*10", "-fps_mode", "passthrough", "-enc_time_base", "1/1000",
             "-c:v", "libx264",
             "-bf", "0", "-g", "1000", "-sc_threshold", "0", "-pix_fmt", "yuv420p",
             "-force_key_frames", "expr:eq(n,0)+eq(n,5)+eq(n,12)")
        # Nonzero container start: GOP 5 at 5 fps, shifted +3 s -> keyframes at 3.0, 4.0 s.
        make(d / "offset.mkv", "testsrc=size=64x48:rate=5:duration=2", "-c:v", "mpeg4", "-g", "5",
             "-output_ts_offset", "3")
        make(d / "long.mp4", "testsrc=size=32x24:rate=1:duration=61", "-c:v", "mpeg4")
        with open(ROOT / "clips.csv", encoding="utf-8", newline="") as f:
            header = next(csv.reader(f))  # same columns as the real licence table
        rows = [("SYN01", "CC0-1.0", "vfr.mp4"), ("SYN02", "CC0-1.0", "offset.mkv"),
                ("SYN03", "CC0-1.0", "long.mp4"), ("NC01", "CC-BY-NC-4.0", "vfr.mp4"),
                ("ND01", "CC BY-ND 4.0", "vfr.mp4"), ("NOLIC", "", "vfr.mp4")]
        cls.csv = d / "clips.csv"
        with open(cls.csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, header, restval="")
            w.writeheader()
            for cid, lic, p in rows:
                w.writerow({"clip_id": cid, "licence": lic, "local_path": p, "title": "synthetic lavfi testsrc",
                            "attribution": "synthetic", "source_url": "lavfi:testsrc"})

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_clip(self, cid, name):
        out = Path(tempfile.mkdtemp(dir=self.d))
        return out, k.extract(cid, self.d / name, out, self.csv)

    def test_vfr_keyframes_keep_original_times(self):
        out, m = self.run_clip("SYN01", "vfr.mp4")
        self.assertEqual([round(x["time_s"], 3) for x in m["keyframes"]], [0.0, 0.25, 1.44])
        self.assertTrue(all(x["time_source"] == "pts" for x in m["keyframes"]))
        for x in m["keyframes"]:
            self.assertTrue((out / x["file"]).stat().st_size > 0)
        self.assertEqual(json.loads((out / "manifest.json").read_text(encoding="utf-8")), m)
        self.assertEqual(m["provenance"]["clip_id"], "SYN01")
        self.assertEqual(m["provenance"]["licence"], "CC0-1.0")
        self.assertEqual(len(m["source"]["sha256"]), 64)

    def test_nonzero_start_is_not_rebased(self):
        _, m = self.run_clip("SYN02", "offset.mkv")
        self.assertEqual([round(x["time_s"], 3) for x in m["keyframes"]], [3.0, 4.0])
        self.assertAlmostEqual(m["source"]["start_time_s"], 3.0, places=3)

    def test_rejects_bad_provenance(self):
        for cid in ("NC01", "ND01", "NOLIC", "MISSING"):
            with self.assertRaises(UploadError, msg=cid):
                k.provenance(cid, self.d / "vfr.mp4", self.csv)
        with self.assertRaises(UploadError):  # row's file is offset.mkv, not vfr.mp4
            k.provenance("SYN02", self.d / "vfr.mp4", self.csv)

    def test_rejects_over_duration_and_non_video(self):
        with self.assertRaises(UploadError):
            k.metadata(self.d / "long.mp4")
        with self.assertRaises(UploadError):
            k.metadata(self.csv)

    def test_refuses_to_mix_with_existing_frames(self):
        out, _ = self.run_clip("SYN02", "offset.mkv")
        with self.assertRaises(UploadError):
            k.extract("SYN02", self.d / "offset.mkv", out, self.csv)


if __name__ == "__main__":
    unittest.main()
