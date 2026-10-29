"""S13e understand stage, offline: fake post, SYNTHETIC frames/manifest. No network or spend."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Build.agent import muse
from Build.pipeline import understand
from Build.pipeline.contracts import STAGES
from Build.pipeline.jobs import JobRunner, MemoryStore, StageError

SID = "clip-st03"
SCENE = {"scene_id": "synthetic-room-v1", "scene_version": "1.0.0", "access": "private", "evidence": "synthetic"}


def reply(payload):
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return 200, {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}]}


class FakePost:
    def __init__(self, *replies):
        self.replies, self.calls = list(replies), []

    def __call__(self, body, key):
        self.calls.append((body, key))
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


class UnderstandTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d = cls.dir = Path(cls.tmp.name)
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=gray:s=64x48:d=1", "-frames:v", "1",
                        str(d / "kf_000000.jpg")], check=True)
        kfs = []
        for i in range(600):  # PD04-sized manifest; one real file is enough for the sampled ones we read
            f = d / f"kf_{i:06d}.jpg"
            if i:
                f.write_bytes((d / "kf_000000.jpg").read_bytes())
            kfs.append({"index": i, "file": f.name, "pts": i, "time_s": i / 10, "time_source": "pts", "pict_type": "I"})
        cls.manifest = d / "manifest.json"
        cls.manifest.write_text(json.dumps({"provenance": {"clip_id": "ST03", "title": "Synthetic test clip"},
                                            "keyframes": kfs}), encoding="utf-8")
        cls.video = d / "clip.mp4"
        cls.video.write_bytes(b"\0" * 1024)
        cls.valid = muse.ask_user(SID)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def out(self):
        return json.loads((self.dir / "understanding.json").read_text(encoding="utf-8"))

    def test_sample_caps_and_keeps_ends(self):
        kfs = [{"index": i} for i in range(600)]
        s = understand.sample(kfs)
        self.assertEqual(len(s), understand.MAX_FRAMES)
        self.assertEqual((s[0]["index"], s[-1]["index"]), (0, 599))
        self.assertEqual(understand.sample(kfs[:3]), kfs[:3])

    def test_video_ok_single_call_forwards_key(self):
        post = FakePost(reply(self.valid))
        sha = understand.run("understand:abc", self.manifest, SID, post, self.dir, self.video)
        self.assertEqual(len(sha), 64)
        self.assertEqual([k for _, k in post.calls], ["understand:abc#video"])
        parts = post.calls[0][0]["input"][0]["content"]
        self.assertEqual([p["type"] for p in parts], ["input_text", "input_video"])
        o = self.out()
        self.assertEqual((o["input_mode"], o["fallback_used"], o["frames"]), ("video", False, []))

    def test_video_fails_then_explicit_keyframe_fallback(self):
        post = FakePost((400, {"error": {"message": "video not supported"}}), reply(self.valid))
        understand.run("understand:abc", self.manifest, SID, post, self.dir, self.video)
        self.assertEqual([k for _, k in post.calls], ["understand:abc#video", "understand:abc#keyframes"])
        parts = post.calls[1][0]["input"][0]["content"]
        self.assertEqual([p["type"] for p in parts], ["input_text"] + ["input_image"] * understand.MAX_FRAMES)
        self.assertTrue(parts[1]["image_url"].startswith("data:image/jpeg;base64,"))
        o = self.out()
        self.assertEqual((o["input_mode"], o["fallback_used"]), ("keyframes", True))
        self.assertEqual(o["attempts"][0]["http"], 400)
        self.assertEqual([f["time_s"] for f in o["frames"]], [0.0, 20.0, 39.9, 59.9])  # manifest times, not model

    def test_transport_error_and_skips_fall_back(self):
        post = FakePost(OSError("reset"), reply(self.valid))
        understand.run("understand:abc", self.manifest, SID, post, self.dir, self.video)
        self.assertEqual(self.out()["attempts"][0]["error"], "OSError")
        post = FakePost(reply(self.valid))
        understand.run("understand:abc", self.manifest, SID, post, self.dir, None)
        self.assertEqual([k for _, k in post.calls], ["understand:abc#keyframes"])
        self.assertEqual(self.out()["attempts"][0]["skipped"], "no video path")

    def test_numbers_rejected_never_measurements(self):
        bad = dict(self.valid, segments=[{"type": "text", "text": "The ball falls 2 metres in 0.6 s."}])
        post = FakePost(reply(bad), reply(bad))
        with self.assertRaises(StageError) as cm:
            understand.run("understand:abc", self.manifest, SID, post, self.dir, self.video)
        self.assertEqual((cm.exception.code, cm.exception.retryable), ("PROCESSING_FAILED", True))

    def test_budget_guard_stops_before_call(self):
        ledger = self.dir / "ledger.jsonl"
        ledger.write_text("\n".join(json.dumps({"est_usd": 0.01}) for _ in range(understand.MAX_CALLS)), encoding="utf-8")
        body = understand.build(understand.clip_context(json.loads(self.manifest.read_text()), SID), [], "x")
        with self.assertRaises(StageError) as cm:
            understand.reserve(body, ledger)
        self.assertEqual(cm.exception.code, "SPEND_PAUSED")

    def test_jobrunner_forwards_key_and_reuses_output(self):
        post = FakePost(reply(self.valid))
        workers = {s: (lambda key: "a" * 64) for s in STAGES}
        workers["understand"] = lambda key: understand.run(key, self.manifest, SID, post, self.dir, self.video)
        store = MemoryStore()
        for job in ("job-1", "job-2"):  # job-2 = user retry: same input key, no second paid call
            snap = JobRunner(store, workers, sleep=lambda s: None).run(job, "b" * 64, SCENE)
            self.assertEqual(snap["status"], "ready")
        self.assertEqual([k for _, k in post.calls], ["understand:" + "a" * 64 + "#video"])


if __name__ == "__main__":
    unittest.main()

