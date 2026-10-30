"""Offline checks for parameterized modal_track (fake modal module; no GPU, no network)."""
import importlib.util
import inspect
import json
import os
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
from Build.measurement.tracking import _context, sanitize_responses  # noqa: E402


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
            "out": "evidence/S07/S07b/orch14/result.json", "masks": False, "chunk": 0,
            "approval": "evidence/owner/S02/APPROVAL.md", "batch": ""})
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
             mock.patch("Build.guardrails.standalone.admit_standalone") as admission, \
             mock.patch.object(MT.track, "remote", remote):
            MT.main(out=str(dest))
            admission.assert_called_once_with("modal-track:ST03")
            with self.assertRaises(FileExistsError):
                MT.main(out=str(dest))
        grab.assert_called_once_with(MT.CLIP, 58, 76)
        args = remote.call_args.args
        self.assertEqual(args[1], accepted)  # exact accepted ST03 metadata incl. source_sha256
        self.assertEqual(args[3:], ("apple", 2, False, 0))
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

    def test_scoped_approval_file_gates_owner_clips(self):
        # S07g: owner clips are approved by their own receipt, never by widening S02 APPROVAL.md
        tmp = str(Path(tempfile.mkdtemp()) / "o.json")
        with self.assertRaises(ValueError):
            MT.plan("OWN01", 40, 60, "yellow book", tmp)
        if shutil.which("ffprobe") and (MT.CANONICAL / "Videos for Meta AI Hackathon/01_demo_hero__035735.mp4").exists():
            path, md, _ = MT.plan("OWN01", 40, 60, "yellow book", tmp, "evidence/S07/S07g/OWNER-APPROVAL.md")
            self.assertEqual((path.name, md["width_px"], md["height_px"]), ("01_demo_hero__035735.mp4", 1080, 1920))
            self.assertEqual(md["approval"]["evidence"], "evidence/S07/S07g/OWNER-APPROVAL.md")

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


class _ChunkPredictor:
    """Two objects: target moves 1 px/frame right, decoy static; later sessions swap their IDs."""
    def __init__(self, jump_at=None):
        self.sessions, self.jump_at, self.offset = [], jump_at, 0

    def handle_request(self, request):
        if request["type"] == "start_session":
            n = len(list(Path(request["resource_path"]).iterdir()))
            self.sessions.append((len(self.sessions), self.offset, n))
            return {"session_id": str(len(self.sessions) - 1)}
        return {}

    def handle_stream_request(self, request):
        k, _, n = self.sessions[int(request["session_id"])]
        start = sum(s[2] - 1 for s in self.sessions[:k])
        for local in range(n):
            g = start + local
            target, decoy = np.zeros((8, 40), bool), np.zeros((8, 40), bool)
            x = g + (10 if self.jump_at is not None and g >= self.jump_at and local == 0 and k else 0)
            target[2:6, x:x + 4], decoy[0:2, 36:40] = True, True
            ids = [7, 3] if k % 2 else [3, 7]  # target id differs between sessions
            yield {"frame_index": local, "outputs": {"out_obj_ids": np.array(ids),
                   "out_binary_masks": np.stack([target, decoy] if ids[0] == 7 or not k % 2 else [decoy, target]),
                   "out_boxes_xywh": [[0.1, 0.2, 0.1, 0.5], [0.9, 0.0, 0.1, 0.25]]}}


class ChunkTrackTest(unittest.TestCase):
    META = {"height_px": 8, "width_px": 40}

    def run_chunks(self, predictor, n=20, chunk=6):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        (tmp / "prefix").mkdir()
        for i in range(n):
            (tmp / "prefix" / f"{i:05d}.jpg").write_bytes(b"x")
        fmap = [(100 + i, round(0.04 * i, 6)) for i in range(n)]
        merged, chunks = MT.track_chunks(predictor, tmp / "prefix", self.META, fmap, [f"{i:064x}" for i in range(n)],
                                         "ball", 3, chunk, lambda k: {"peak_vram_bytes": k})
        return merged, chunks

    def test_spans_overlap_one_frame_and_keep_tail_ge_3(self):
        self.assertEqual(MT.chunk_spans(10, 4), [(0, 4), (3, 7), (6, 10)])
        self.assertEqual(MT.chunk_spans(8, 4), [(0, 4), (3, 8)])  # 2-frame tail (6,8) merged
        for n, c in ((3, 3), (50, 3), (441, 16), (19, 26)):
            spans = MT.chunk_spans(n, c)
            self.assertEqual((spans[0][0], spans[-1][1]), (0, n))
            self.assertTrue(all(b[0] == a[1] - 1 and b[1] - b[0] >= 3 for a, b in zip(spans, spans[1:])))
        with self.assertRaises(ValueError):
            MT.chunk_spans(10, 2)

    def test_reseed_follows_target_across_id_swaps(self):
        merged, chunks = self.run_chunks(_ChunkPredictor())
        self.assertEqual([m["frame_index"] for m in merged], list(range(20)))
        xs = [int(np.flatnonzero(m["outputs"]["out_binary_masks"][0].any(axis=0))[0]) for m in merged]
        self.assertEqual(xs, list(range(20)))  # always the moving target, never the decoy
        self.assertTrue(all(list(m["outputs"]["out_obj_ids"]) == [3] for m in merged))
        self.assertEqual([c["local_object_id"] for c in chunks], [3, 7, 3, 7])
        self.assertEqual(chunks[1]["source_frames"], [105, 110])
        self.assertTrue(all(len(c["seal_sha256"]) == 64 and "stopped" not in c for c in chunks))
        meta = {"clip_id": "T", "licence": "CC0", "provenance": "fake", "motion": "bounce", "source_sha256": "0" * 64,
                "approval": {"scope": "scene_tracking", "evidence": "x"}, "width_px": 40, "height_px": 8,
                "last_training_frame": 119}
        rec = sanitize_responses(merged, meta, [(100 + i, 0.04 * i + 0.01) for i in range(20)], object_id=3)
        self.assertEqual(len(rec.training), 20)

    def test_low_reseed_iou_fails_closed(self):
        merged, chunks = self.run_chunks(_ChunkPredictor(jump_at=8))
        self.assertIn("stopped", chunks[-1])
        self.assertEqual(sum(len(m["outputs"]["out_obj_ids"]) for m in merged), 11)  # frames 0..10 only


class BatchTest(unittest.TestCase):
    """S07i batch path with mocked plan/frames/remote/admission: no media, GPU or network."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / "clip.mp4").write_bytes(b"media")
        self.jobs = [{"clip": c, "first": 3, "last": 6, "prompt": "yellow book", "object_id": 0,
                      "out": f"out/{c}.json"} for c in ("OWN02", "OWN03")]

    def run_batch(self, results=None, dry=False):
        (self.tmp / "b.json").write_text(json.dumps({"clips": self.jobs}))
        remote = mock.Mock(return_value=json.dumps(results or []))
        admit = mock.Mock()
        plan = lambda clip, first, last, prompt, out, approval: (self.tmp / "clip.mp4", {"clip_id": clip},
                                                                 (self.tmp / out).resolve())
        frames = lambda path, first, last: ([(b"j", "s")] * (last - first + 1),
                                            [(first + i, .1 * i) for i in range(last - first + 1)])
        env = {"S07B_DRY": "1"} if dry else {}
        with mock.patch.multiple(MT, REPO=self.tmp, plan=plan, _frames=frames,
                                 track_batch=types.SimpleNamespace(remote=remote)), \
                mock.patch("Build.guardrails.standalone.admit_standalone", admit), \
                mock.patch.dict("os.environ", env, clear=False):
            if not dry:
                os.environ.pop("S07B_DRY", None)
            MT.main(batch="b.json", approval="receipt.md")
        return remote, admit

    def test_one_admission_one_remote_call_per_clip_outputs(self):
        remote, admit = self.run_batch([{"stages": ["tracked"]}, {"error": "lost"}])
        admit.assert_called_once_with("modal-track:batch:OWN02,OWN03")
        remote.assert_called_once()
        jobs = remote.call_args.args[0]
        self.assertEqual([j[3:] for j in jobs], [("yellow book", 0)] * 2)
        self.assertEqual(jobs[0][1]["source_sha256"], __import__("hashlib").sha256(b"media").hexdigest())
        second = json.loads((self.tmp / "out/OWN03.json").read_text())
        self.assertEqual((second["error"], second["frame_map"][0]), ("lost", [3, 0.0]))

    def test_dry_run_and_validation_never_admit(self):
        remote, admit = self.run_batch(dry=True)
        admit.assert_not_called(), remote.assert_not_called()
        self.jobs[1]["out"] = self.jobs[0]["out"]
        with self.assertRaises(ValueError):
            self.run_batch()
        self.jobs[1]["object_id"] = -1
        with self.assertRaises(ValueError):
            self.run_batch()

    def test_remote_batch_isolates_clip_failures(self):
        calls = []
        def one(*args):
            calls.append(args)
            return json.dumps({"error": "x"} if len(calls) == 1 else {"stages": ["tracked"]})
        with mock.patch.object(MT, "track_one", one):
            out = json.loads(MT.track_batch.local([("f", {}, [], "p", 0), ("f", {}, [], "p", 1)]))
        self.assertEqual(out, [{"error": "x"}, {"stages": ["tracked"]}])
        self.assertEqual([c[4] for c in calls], [0, 1])

    def test_committed_fall_windows_plan(self):
        fixed = json.loads((ROOT / "evidence/S07/S07i/fall-windows.json").read_text())["clips"]
        self.assertEqual([c["clip"] for c in fixed], [f"OWN{i:02d}" for i in range(2, 12)])  # OWN12 excluded
        self.assertTrue(all(0 <= c["first"] <= c["last"] - 2 < c["frames"] for c in fixed))
        self.assertTrue(all(c["last"] - c["first"] < 24 for c in fixed))  # OWN01: 21 frames peaked 16 GiB VRAM
        self.assertEqual(len({c["out"] for c in fixed}), len(fixed))
        worst = (300 + MT.BATCH_TIMEOUT_S) * (0.000306 + 2 * 0.0000131 + 16 * 0.00000222)
        self.assertLessEqual(worst, 0.40)  # Modal list prices 2026-10-31; A10 is the dearer allowed GPU

    def test_s07j_retrack_subset_is_unchanged_s07i_windows(self):
        old = {c["clip"]: c for c in json.loads((ROOT / "evidence/S07/S07i/fall-windows.json").read_text())["clips"]}
        new = json.loads((ROOT / "evidence/S07/S07j/fall-windows-own07-11.json").read_text())["clips"]
        self.assertEqual([c["clip"] for c in new], [f"OWN{i:02d}" for i in range(7, 12)])
        for c in new:
            self.assertEqual({**c, "out": old[c["clip"]]["out"]}, old[c["clip"]])  # only the output moved
            self.assertTrue(c["out"].startswith("evidence/S07/S07j/"))


class SharedPredictorTest(unittest.TestCase):
    """S07j: one SAM load per container (S07i per-clip reloads OOMed OWN07-OWN11 on the A10)."""

    def setUp(self):
        MT._MODEL.clear()
        self.addCleanup(MT._MODEL.clear)

    def test_loads_once_and_returns_unwrapped_originals(self):
        loads = []

        def load():
            loads.append(types.SimpleNamespace(handle_request="h", handle_stream_request="s"))
            return loads[-1]
        predictor, _, _ = MT.shared_predictor(load)
        predictor.handle_request = predictor.handle_stream_request = "clip-1 wrapper"
        self.assertEqual(MT.shared_predictor(load), (loads[0], "h", "s"))  # wrappers never stack across clips
        self.assertEqual(len(loads), 1)

    def test_failed_load_caches_nothing_and_next_clip_retries(self):
        def oom():
            raise RuntimeError("CUDA out of memory")
        with self.assertRaises(RuntimeError):
            MT.shared_predictor(oom)
        ok = types.SimpleNamespace(handle_request=1, handle_stream_request=2)
        self.assertIs(MT.shared_predictor(lambda: ok)[0], ok)

    def test_track_one_loads_only_through_shared_predictor(self):
        source = inspect.getsource(MT.track_one)
        self.assertEqual(source.count("load_local_predictor(path"), 1)
        self.assertIn("shared_predictor(load)", source)
        self.assertIn("predictor.handle_stream_request = stream if chunk else logged_stream", source)
