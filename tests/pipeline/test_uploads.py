"""S13b upload tests on SYNTHETIC bytes in a temp dir; not bucket, real-clip or scene evidence."""
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from Build.pipeline import uploads as u
from Build.pipeline.contracts import errors

CH = u.UP["chunk_bytes"]
MP4 = b"\x00\x00\x00\x18ftypisom" + b"\x00" * 4  # synthetic container header only
BODY = MP4 + bytes(range(256)) * ((CH + 1000) // 256)  # 2 chunks: full + remainder


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Clock:
    def __init__(self):
        self.t = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)

    def __call__(self):
        return self.t


class UploadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.clock = Clock()
        self.svc = u.UploadService(self.tmp.name, self.clock)
        self.s = self.svc.create("alice", "video/mp4", len(BODY), sha(BODY))
        self.id = self.s["upload_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def raises(self, code, fn, *a):
        with self.assertRaises(u.UploadError) as cm:
            fn(*a)
        self.assertEqual(code, cm.exception.code)
        return cm.exception

    def test_interrupted_upload_resumes_after_restart(self):
        self.assertEqual([], errors(self.s))
        self.svc.put_chunk("alice", self.id, 0, BODY[:CH])
        # crash mid-second-chunk: torn bytes (longer than the real remainder) on disk, meta never committed
        with open(self.svc.root / self.id / "data.part", "ab") as f:
            f.write(b"T" * (len(BODY) - CH + 50))
        svc2 = u.UploadService(self.tmp.name, self.clock)  # new process, same store
        sess = svc2.get("alice", self.id)
        self.assertEqual(CH, sess["committed_bytes"])
        dup = svc2.put_chunk("alice", self.id, 0, BODY[:CH])  # client unsure chunk 0 landed
        self.assertTrue(dup["duplicate"])
        self.assertEqual(CH, dup["committed_bytes"])
        ack = svc2.put_chunk("alice", self.id, sess["committed_bytes"], BODY[CH:])
        self.assertEqual([], errors(ack))
        self.assertEqual(len(BODY), ack["committed_bytes"])
        done = svc2.complete("alice", self.id)
        self.assertEqual("complete", done["status"])
        self.assertEqual([], errors(done))
        self.assertEqual(BODY, (svc2.root / self.id / "data.part").read_bytes())
        self.assertEqual(done, svc2.complete("alice", self.id))  # idempotent

    def test_gap_conflict_misaligned_length_rejected_with_resume_point(self):
        e = self.raises("INVALID_INPUT", self.svc.put_chunk, "alice", self.id, CH, BODY[CH:])
        self.assertEqual(("reject_gap", 0), (e.decision, e.committed_bytes))
        self.svc.put_chunk("alice", self.id, 0, BODY[:CH])
        bad = b"\xff" + BODY[1:CH]
        self.assertEqual("reject_conflict", self.raises("INVALID_INPUT", self.svc.put_chunk, "alice", self.id, 0, bad).decision)
        self.assertEqual("reject_misaligned", self.raises("INVALID_INPUT", self.svc.put_chunk, "alice", self.id, 5, b"x").decision)
        self.assertEqual("reject_length", self.raises("INVALID_INPUT", self.svc.put_chunk, "alice", self.id, CH, BODY[CH:] + b"x").decision)
        self.assertEqual("reject_misaligned", self.raises("INVALID_INPUT", self.svc.put_chunk, "alice", self.id, 2 * CH, b"x").decision)
        self.assertEqual("incomplete", self.raises("INVALID_INPUT", self.svc.complete, "alice", self.id).decision)
        self.raises("INVALID_INPUT", self.svc.put_chunk, "alice", self.id, -CH, b"x")
        self.raises("INVALID_INPUT", self.svc.put_chunk, "alice", self.id, 0, "str")
        self.assertEqual(CH, self.svc.get("alice", self.id)["committed_bytes"])  # nothing written

    def test_unauthorized_and_unknown_rejected_without_disclosure(self):
        self.svc.put_chunk("alice", self.id, 0, BODY[:CH])
        for owner in ("mallory", "", None, "../alice"):
            e = self.raises("UNAUTHORIZED", self.svc.get, owner, self.id)
            self.assertNotIn(self.id, str(e))
            self.raises("UNAUTHORIZED", self.svc.put_chunk, owner, self.id, CH, BODY[CH:])
            self.raises("UNAUTHORIZED", self.svc.complete, owner, self.id)
        self.raises("UNAUTHORIZED", self.svc.create, None, "video/mp4", 10, "ab" * 32)
        self.raises("NOT_FOUND", self.svc.get, "alice", "up_missing")
        for bad_id in ("../meta", "..", "a/b", "", None, "x" * 97):
            self.raises("INVALID_INPUT", self.svc.get, "alice", bad_id)
        self.assertEqual(CH, self.svc.get("alice", self.id)["committed_bytes"])

    def test_create_limits(self):
        cases = [("video/avi", 10, "ab" * 32), ("text/plain", 10, "ab" * 32),
                 ("video/mp4", 0, "ab" * 32), ("video/mp4", u.UP["max_file_bytes"] + 1, "ab" * 32),
                 ("video/mp4", True, "ab" * 32), ("video/mp4", 10.0, "ab" * 32),
                 ("video/mp4", 10, "AB" * 32), ("video/mp4", 10, "ab" * 31)]
        for args in cases:
            self.raises("INVALID_INPUT", self.svc.create, "alice", *args)
        top = self.svc.create("alice", "video/webm", u.UP["max_file_bytes"], "ab" * 32)
        self.assertEqual([], errors(top))

    def test_content_type_sniff_rejects_session(self):
        s = self.svc.create("alice", "video/webm", len(BODY), sha(BODY))  # mp4 bytes declared webm
        self.assertEqual("rejected", self.raises("INVALID_INPUT", self.svc.put_chunk, "alice", s["upload_id"], 0, BODY[:CH]).decision)
        sess = self.svc.get("alice", s["upload_id"])
        self.assertEqual(("rejected", 0), (sess["status"], sess["committed_bytes"]))
        self.assertEqual([], errors(sess))
        self.assertEqual("reject_closed", self.raises("INVALID_INPUT", self.svc.put_chunk, "alice", s["upload_id"], 0, BODY[:CH]).decision)
        webm = b"\x1a\x45\xdf\xa3" + b"\x00" * 8
        w = self.svc.create("alice", "video/webm", len(webm), sha(webm))
        self.svc.put_chunk("alice", w["upload_id"], 0, webm)
        self.assertEqual("complete", self.svc.complete("alice", w["upload_id"])["status"])

    def test_whole_file_hash_mismatch_rejects(self):
        s = self.svc.create("alice", "video/mp4", len(MP4), "ab" * 32)
        self.svc.put_chunk("alice", s["upload_id"], 0, MP4)
        self.raises("INVALID_INPUT", self.svc.complete, "alice", s["upload_id"])
        sess = self.svc.get("alice", s["upload_id"])
        self.assertEqual(("rejected", None), (sess["status"], sess["job_id"]))
        self.assertEqual([], errors(sess))

    def test_expired_session_cannot_resume(self):
        self.svc.put_chunk("alice", self.id, 0, BODY[:CH])
        self.clock.t += timedelta(seconds=u.UP["session_ttl_s"])
        self.assertEqual("expired", self.svc.get("alice", self.id)["status"])
        self.assertEqual("reject_closed", self.raises("INVALID_INPUT", self.svc.put_chunk, "alice", self.id, CH, BODY[CH:]).decision)
        meta = json.loads((self.svc.root / self.id / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual("expired", meta["session"]["status"])


if __name__ == "__main__":
    unittest.main()
