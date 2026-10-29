"""Offline checks for parameterized modal_track (fake modal module; no GPU, no network)."""
import importlib.util
import inspect
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.measurement.tracking import _context  # noqa: E402


class _Chain:
    def __getattr__(self, name):
        return lambda *a, **k: self


class _App:
    def __init__(self, *a, **k):
        pass

    def function(self, **k):
        return lambda f: types.SimpleNamespace(remote=None, local=f)

    def local_entrypoint(self):
        return lambda f: f


FAKE = types.SimpleNamespace(Image=_Chain(), Secret=_Chain(), App=_App)
with mock.patch.dict(sys.modules, {"modal": FAKE}):
    spec = importlib.util.spec_from_file_location(
        "modal_track", ROOT / "Build/measurement/runtime/modal_track.py")
    MT = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(MT)
ACCEPTED = ROOT / MT.DEFAULT_OUT
MEDIA = shutil.which("ffprobe") and MT.CLIP.exists()


def rle_decode(rle):
    flat, value, at = np.zeros(rle["size"][0] * rle["size"][1], bool), False, 0
    for count in rle["counts"]:
        flat[at:at + count] = value
        at, value = at + count, not value
    return flat.reshape(rle["size"], order="F")


class ModalTrackTest(unittest.TestCase):
    def test_defaults_are_accepted_st03_values(self):
        params = inspect.signature(MT.main).parameters
        self.assertEqual({k: p.default for k, p in params.items()}, {
            "clip": "ST03", "first": 58, "last": 76, "prompt": "apple", "object_id": 2,
            "out": "evidence/S07/S07b/orch14/result.json", "masks": False})
        remote = inspect.signature(MT.track.local).parameters
        self.assertEqual((remote["object_id"].default, remote["masks"].default), (2, False))

    def test_default_never_overwrites_accepted_evidence(self):
        before = ACCEPTED.read_bytes()
        remote = mock.Mock()
        with mock.patch.object(MT.track, "remote", remote), self.assertRaises(FileExistsError):
            MT.main()
        remote.assert_not_called()
        self.assertEqual(ACCEPTED.read_bytes(), before)

    @unittest.skipUnless(MEDIA, "local ST03 media/ffprobe unavailable")
    def test_default_metadata_and_remote_args_match_accepted_run(self):
        record = json.loads(ACCEPTED.read_text())["record"]
        accepted = {k: v for k, v in record.items() if k not in ("frames", "tracking")}
        dest = Path(tempfile.mkdtemp()) / "r.json"
        frames, fmap = [(b"x", "0" * 64)], [(76, 2.5)]
        remote = mock.Mock(return_value=json.dumps({"stages": ["tracked"]}))
        with mock.patch.object(MT, "_frames", return_value=(frames, fmap)) as grab, \
             mock.patch.object(MT.track, "remote", remote):
            MT.main(out=str(dest))
            with self.assertRaises(FileExistsError):
                MT.main(out=str(dest))
        grab.assert_called_once_with(MT.CLIP, 58, 76)
        args = remote.call_args.args
        self.assertEqual(args[1], accepted)  # exact accepted ST03 metadata incl. source_sha256
        self.assertEqual(args[3:], ("apple", 2, False))
        self.assertEqual(json.loads(dest.read_text())["frame_map"], [[76, 2.5]])

    def test_parameter_validation_before_gpu(self):
        tmp = str(Path(tempfile.mkdtemp()) / "o.json")
        for bad in (dict(clip="AP15"), dict(clip="ST05"), dict(clip="XX99"),
                    dict(first=10, last=11), dict(first=-1), dict(prompt=" ")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                MT.plan(**{"out": tmp, **bad})
        remote = mock.Mock()
        with mock.patch.object(MT.track, "remote", remote), mock.patch.object(MT, "_frames") as grab:
            for bad in (-1, 1.0, "2"):
                with self.subTest(object_id=bad), self.assertRaises(ValueError):
                    MT.main(object_id=bad, out=tmp)
        remote.assert_not_called(), grab.assert_not_called()

    @unittest.skipUnless(shutil.which("ffprobe") and (MT.CANONICAL / "test-data/public/RM04.mp4").exists(),
                         "local RM04 media unavailable")
    def test_room_clip_metadata_passes_tracking_contract(self):
        path, md, _ = MT.plan("RM04", 0, 7, "chair", str(Path(tempfile.mkdtemp()) / "o.json"))
        self.assertEqual((path.name, md["motion"], md["width_px"], md["height_px"]), ("RM04.mp4", "scene", 3840, 2160))
        md["source_sha256"] = "a" * 64
        _context(md, [(i, i / 25) for i in range(8)], 0)  # accepted sanitizer contract

    def test_imports_at_container_root(self):
        # orch38 live run 1 died here: Modal copies the file to /root/modal_track.py (shallow path)
        src = (ROOT / "Build/measurement/runtime/modal_track.py").read_text("utf-8")
        with mock.patch.dict(sys.modules, {"modal": FAKE}):
            exec(compile(src, "/root/modal_track.py", "exec"),
                 {"__file__": "/root/modal_track.py", "__name__": "modal_track"})

    @unittest.skipUnless(MT.CLIP.exists() and shutil.which("ffprobe"), "local ST03 + ffprobe needed")
    def test_pts_presentation_order_st03(self):
        # S07b-errata: hash-verified ST03 f76 = 2.535867 s (orch14 recorded f77's 2.569233)
        pts = MT._pts(MT.CLIP, MT.LAST)
        self.assertEqual(len(pts), 77)
        self.assertAlmostEqual(pts[75], 2.5025, places=6)
        self.assertAlmostEqual(pts[76], 2.535867, places=6)

    def test_mask_rle_roundtrip(self):
        rng = np.random.default_rng(0)
        for mask in (rng.random((7, 5)) > 0.5, np.ones((3, 4), bool), np.zeros((2, 2), bool)):
            rle = MT.mask_rle(mask)
            self.assertEqual(sum(rle["counts"]), mask.size)
            np.testing.assert_array_equal(rle_decode(rle), mask)


if __name__ == "__main__":
    unittest.main()
