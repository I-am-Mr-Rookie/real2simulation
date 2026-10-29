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
SAM_OK = {"stages": ["preflight", "checkpoint", "model_loaded", "tracked"], "gpu": "NVIDIA L4, 23034 MiB",
          "checkpoint": {"sha256": "ab" * 32}, "stream": [[0, [2], [[0.4, 0.3, 0.1, 0.1]]]], "record": {"synthetic": True}}


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
        sha = g.segment("segment:aa", lambda: json.dumps(SAM_OK), self.d, self.ledger, "apple")
        self.assertEqual(len(sha), 64)
        self.assertEqual(json.loads((self.d / "segmentation.json").read_text(encoding="utf-8"))["frames"], 1)
        bad = {**SAM_OK, "stages": ["preflight", "checkpoint"], "error": "Traceback...\nRuntimeError: CUDA out of memory"}
        with self.assertRaises(StageError) as e:
            g.segment("segment:bb", lambda: json.dumps(bad), self.d, self.d / "l2.jsonl", "apple")
        self.assertEqual((e.exception.code, e.exception.retryable), ("PROCESSING_FAILED", True))
        self.assertIn("CUDA out of memory", e.exception.message)

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
                   "segment": lambda key: g.segment(key, sam_call, self.d / "seg", self.d / "seg.jsonl", "apple"),
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

    def test_sam_call_uses_track_function_not_entrypoint(self):
        import contextlib
        import types
        seen = []
        fake = types.SimpleNamespace(app=types.SimpleNamespace(run=lambda: contextlib.nullcontext()),
                                     track=types.SimpleNamespace(remote=lambda *a: seen.append(a) or json.dumps(SAM_OK)))
        sys.modules["modal_track"] = fake
        try:
            sha = g.segment("segment:cc", g.sam_call(["f"], {"clip_id": "ST03"}, [(58, 1.0)], "apple"), self.d, self.ledger, "apple")
        finally:
            del sys.modules["modal_track"]
        self.assertEqual((len(sha), seen), (64, [(["f"], {"clip_id": "ST03"}, [(58, 1.0)], "apple")]))


if __name__ == "__main__":
    unittest.main()
