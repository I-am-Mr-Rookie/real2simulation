"""S13f segment/reconstruct workers, offline: fake Modal launcher + fake SAM call, SYNTHETIC npz. No GPU or spend."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from Build.pipeline import gpu_stages as g
from Build.pipeline.contracts import STAGES
from Build.pipeline.jobs import JobRunner, MemoryStore, StageError

sys.path.insert(0, str(g.ROOT / "Build/gpu"))
import scene_job  # noqa: E402 - offline converter (no modal client installed locally)
from test_scene_job import fake_npz  # noqa: E402 - reuse the S06d synthetic MapAnything npz

SCENE = {"scene_id": "synthetic-room-v1", "scene_version": "1.0.0", "access": "private", "evidence": "synthetic"}
RLE = {"size": [2, 3], "counts": [1, 4, 1]}  # SYNTHETIC 2x3 COCO RLE
SAM_OK = {"stages": ["preflight", "checkpoint", "model_loaded", "tracked"], "gpu": "NVIDIA L4, 23034 MiB",
          "checkpoint": {"sha256": "ab" * 32}, "frame_map": [[0, 0.0], [1, 0.04]],
          "stream": [[0, [0, 3], [[0.4, 0.3, 0.1, 0.1], [0, 0, 1, 1]]], [1, [0], [[0.4, 0.31, 0.1, 0.1]]]],
          "masks": [[0, {"0": RLE}], [1, {"0": RLE}]],
          "record": {"clip_id": "SYN", "height_px": 2, "width_px": 3, "tracking": {"object_id": 0},
                     "frames": [{"frame_index": 0, "x_px": 1.0, "y_px": 1.0}, {"frame_index": 1, "x_px": 1.0, "y_px": 1.2}]}}


def sam_raw(**kw):
    return json.dumps({**SAM_OK, **kw})


def fake_run(calls, rc=0, stderr=""):
    """Stands in for `uv run ... modal run scene_job.py`: writes the bundle the real local entrypoint writes."""
    def run(cmd, **kw):
        calls["run"] += 1
        a = dict(zip(cmd, cmd[1:]))
        if rc == 0:
            out = Path(a["--out"])
            out.mkdir(parents=True, exist_ok=True)
            fake_npz(out / "x.npz")
            scene_job.build_bundle(a["--scene"], out / "x.npz", out, "S13f unit test (synthetic npz)")
            (out / f"{a['--scene']}-scene-log.json").write_text(json.dumps({"app_id": "ap-fake", "cost": {"estimated": {"total_usd": 0.01}}}))
        return subprocess.CompletedProcess(cmd, rc, "", stderr)
    return run


class GpuStages(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.ledger = self.d / "ledger.jsonl"

    def test_reconstruct_validated_output(self):
        calls = Counter()
        sha = g.reconstruct("reconstruct:aa", "RM02", "m.json", self.d, self.ledger, run=fake_run(calls))
        doc = json.loads((self.d / "reconstruction.json").read_text(encoding="utf-8"))
        self.assertEqual((doc["kind"], calls["run"], len(sha)), ("reconstruction", 1, 64))
        self.assertGreater(doc["point_count"], 0)

    def test_reconstruct_errors_readable(self):
        with self.assertRaises(StageError) as e:
            g.reconstruct("k", "RM09", "m.json", self.d, self.ledger, run=fake_run(Counter(), 1, "ValueError: RM09: not an owner-approved scene id"))
        self.assertEqual((e.exception.code, e.exception.retryable), ("INVALID_INPUT", False))
        self.assertIn("not an owner-approved", e.exception.message)
        with self.assertRaises(StageError) as e:
            g.reconstruct("k", "RM02", "m.json", self.d, self.ledger, run=fake_run(Counter(), 1, "modal.exception.FunctionTimeoutError: timeout"))
        self.assertEqual((e.exception.code, e.exception.retryable), ("PROCESSING_FAILED", True))
        self.assertIn("FunctionTimeoutError", e.exception.message)

    def test_budget_guard(self):
        g.reserve(self.ledger, "reconstruct", "a", 0.5)
        g.reserve(self.ledger, "segment", "b", 0.5)
        with self.assertRaises(StageError) as e:
            g.reserve(self.ledger, "reconstruct", "c", 0.01)
        self.assertEqual((e.exception.code, e.exception.retryable), ("SPEND_PAUSED", False))

    def test_segment_validates_and_rejects(self):
        sha = g.segment("segment:aa", sam_raw, self.d, self.ledger, "chair", 0)
        self.assertEqual(len(sha), 64)
        doc = json.loads((self.d / "segmentation.json").read_text(encoding="utf-8"))
        self.assertEqual([(f["frame_index"], f["pts_s"], f["box_xywh_norm"][1]) for f in doc["frames"]], [(0, 0.0, 0.3), (1, 0.04, 0.31)])
        self.assertEqual(g.validate_segment(sam_raw(), "chair", 0, [[0, 0.0], [1, 0.05]])["frames"][1]["pts_s"], 0.05)  # errata wins
        cases = [(sam_raw(stages=["preflight"], error="Traceback...\nRuntimeError: CUDA out of memory"), None, "CUDA out of memory"),
                 (sam_raw(), None, "record tracks object 0, expected 3"),
                 (sam_raw(masks=[[0, {"0": {"size": [2, 3], "counts": [1, 4]}}], [1, {"0": RLE}]]), None, "RLE mask is not 2x3"),
                 (sam_raw(masks=[[0, {"0": RLE}]]), None, "frame 1: object 0 has no box, centroid or mask"),
                 (sam_raw(), [[0, 0.04], [1, 0.04]], "PTS not increasing")]
        for raw, fmap, msg in cases:
            with self.assertRaises(StageError) as e:
                g.validate_segment(raw, "chair", 3 if "expected 3" in msg else 0, fmap)
            self.assertEqual((e.exception.code, e.exception.retryable), ("PROCESSING_FAILED", True))
            self.assertIn(msg, e.exception.message)

    def test_jobrunner_retry_and_no_duplicate_dispatch(self):
        """Failed segment retries once; resumed/duplicate jobs reuse out:<key> so no paid stage dispatches twice."""
        calls, sam = Counter(), iter([RuntimeError("modal: container lost"), json.dumps(SAM_OK)])

        def sam_call():
            calls["sam"] += 1
            r = next(sam)
            if isinstance(r, Exception):
                raise r
            return r
        cheap = {s: (lambda key: hashlib.sha256(key.encode()).hexdigest()) for s in STAGES}
        workers = {**cheap,
                   "segment": lambda key: g.segment(key, sam_call, self.d / "seg", self.d / "seg.jsonl", "chair", 0),
                   "reconstruct": lambda key: g.reconstruct(key, "RM02", "m.json", self.d / "rec", self.d / "rec.jsonl", run=fake_run(calls))}
        store = MemoryStore()
        runner = JobRunner(store, workers, sleep=lambda s: None)
        snap = runner.run("job-1", "cd" * 32, SCENE)
        self.assertEqual(snap["status"], "ready", snap)
        self.assertEqual((calls["sam"], calls["run"]), (2, 1))
        self.assertEqual(runner.run("job-2", "cd" * 32, SCENE)["status"], "ready")  # same input: every stage reused
        self.assertEqual((calls["sam"], calls["run"]), (2, 1))
        seg = [e for e in runner.events("job-1") if e["stage"] == "segment"]
        self.assertEqual([e["status"] for e in seg], ["started", "failed", "started", "succeeded"])
        self.assertIn("container lost", seg[1]["error"]["message"])

    def test_sam_call_cli_reuse_retry_and_bad_input(self):
        """Parameterized S07b CLI: clean raw reused (no 2nd dispatch); errored raw moved aside + redispatched; bad input not retried."""
        cmds, replies = [], iter([sam_raw(error="RuntimeError: boom"), sam_raw()])
        raw = self.d / "seg" / "raw-result.json"

        def run(cmd, **kw):
            cmds.append(cmd)
            out = Path(dict(zip(cmd, cmd[1:]))["--out"])
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(next(replies), encoding="utf-8")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        call = g.sam_call("RM04", 0, 11, "chair", 0, raw, run=run)
        with self.assertRaises(StageError) as e:
            g.segment("segment:cc", call, self.d / "seg", self.ledger, "chair", 0)
        self.assertIn("boom", e.exception.message)
        g.segment("segment:cc", call, self.d / "seg", self.d / "l2.jsonl", "chair", 0)
        g.segment("segment:cc", call, self.d / "seg", self.d / "l3.jsonl", "chair", 0)  # reuses clean raw
        a = dict(zip(cmds[0], cmds[0][1:]))
        self.assertEqual((len(cmds), a["--clip"], a["--object-id"], a["--last"], cmds[0][-1]), (2, "RM04", "0", "11", "--masks"))
        self.assertEqual(len(list(raw.parent.glob("raw-result.failed-*.json"))), 1)
        rej = lambda cmd, **kw: subprocess.CompletedProcess(cmd, 1, "", "ValueError: RM09 not in scoped owner approval evidence/owner/S02/APPROVAL.md")
        with self.assertRaises(StageError) as e:
            g.sam_call("RM09", 0, 11, "chair", 0, self.d / "x" / "raw.json", run=rej)()
        self.assertEqual((e.exception.code, e.exception.retryable), ("INVALID_INPUT", False))
        self.assertIn("RM09 not in scoped owner approval", e.exception.message)


if __name__ == "__main__":
    unittest.main()
