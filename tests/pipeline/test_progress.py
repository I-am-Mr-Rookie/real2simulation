"""S13g job_progress feed tests on SYNTHETIC workers; no Redis server, GPU, Modal or Meta calls."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from Build.pipeline import contracts as c
from Build.pipeline import progress as p
from Build.pipeline.jobs import MemoryStore, StageError
from tests.pipeline.test_jobs import IN, SCENE, fixture, runner


def run(fail=None):
    _, w = fixture(fail)
    r = runner(MemoryStore(), w, [])
    snap = r.run("job-a", IN, SCENE)
    return r, snap


class ProgressTests(unittest.TestCase):
    def test_success_rows_ordered_and_job_ready(self):
        r, snap = run()
        doc = r.progress("job-a", scene=SCENE)
        self.assertEqual([], c.errors(doc))
        self.assertEqual(snap, doc["job"])  # host dispatches {type:'JOB_UPDATE', job: doc['job']}
        rows = doc["events"]
        self.assertEqual(list(range(1, 2 * len(c.STAGES) + 1)), [e["revision"] for e in rows])
        self.assertEqual([s for s in c.STAGES for _ in (0, 1)], [e["stage"] for e in rows])
        self.assertEqual(["started", "succeeded"] * len(c.STAGES), [e["status"] for e in rows])
        self.assertTrue(all(e["retryable"] is None and e["ts"] == "2026-10-29T12:00:00Z" for e in rows))
        self.assertEqual("Package finished", rows[-1]["message"])

    def test_retryable_failure_marked_then_retry_attempt_shown(self):
        r, snap = run({"segment": [StageError("DEPENDENCY_UNAVAILABLE", "SYNTHETIC 503", True)]})
        self.assertEqual("ready", snap["status"])
        rows = [e for e in r.progress("job-a", scene=SCENE)["events"] if e["stage"] == "segment"]
        self.assertEqual([("started", 1, None), ("failed", 1, True), ("started", 2, None), ("succeeded", 2, None)],
                         [(e["status"], e["attempt"], e["retryable"]) for e in rows])
        self.assertEqual("Segment failed: DEPENDENCY_UNAVAILABLE: SYNTHETIC 503 Retrying.", rows[1]["message"])
        self.assertEqual("Segment (attempt 2/2) started", rows[2]["message"])

    def test_retryable_error_out_of_attempts_is_not_retried(self):
        r, snap = run({"segment": [StageError("PROCESSING_FAILED", "SYNTHETIC crash", True)] * 2})
        self.assertEqual("failed", snap["status"])
        last = r.progress("job-a")["events"][-1]
        self.assertEqual((2, False), (last["attempt"], last["retryable"]))
        self.assertTrue(last["message"].endswith("Not retried."))

    def test_never_retry_failure_is_terminal_and_redacted(self):
        msg = r"clip not approved: C:\Users\HP\secret\clip.mp4 token=abc123 see evidence/S13/x.json"
        r, snap = run({"keyframes": [StageError("INVALID_INPUT", msg, True)]})
        doc = r.progress("job-a")
        self.assertEqual(("failed", "INVALID_INPUT"), (doc["job"]["status"], doc["job"]["error"]["code"]))
        last = doc["events"][-1]
        self.assertEqual(("keyframes", "failed", 1, False), (last["stage"], last["status"], last["attempt"], last["retryable"]))
        text = json.dumps(doc)
        for leak in ("C:\\", "Users", "abc123", "idempotency_key", IN):
            self.assertNotIn(leak, text)
        self.assertIn("evidence/S13/x.json", last["message"])  # relative evidence pointers stay readable
        self.assertNotIn("abc123", doc["job"]["error"]["message"])

    def test_after_revision_returns_only_new_rows_and_bad_sequence_raises(self):
        r, _ = run()
        evs = r.events("job-a")
        self.assertEqual([11, 12], [e["revision"] for e in p.progress("job-a", evs, 10, SCENE)["events"]])
        self.assertEqual([], p.progress("job-a", evs, 12, SCENE)["events"])
        self.assertEqual("queued", p.progress("job-a", [])["job"]["status"])
        with self.assertRaises(ValueError):
            p.progress("job-a", [evs[1], evs[0]])  # out of order
        with self.assertRaises(ValueError):
            p.progress("job-a", [{**evs[0], "status": "done"}])  # schema-invalid event

    def test_schema_rejects_unsafe_or_malformed_rows(self):
        r, _ = run()
        doc = r.progress("job-a", scene=SCENE)
        row = doc["events"][0]
        for bad in ({**row, "idempotency_key": "x"}, {**row, "retryable": True}, {**row, "message": ""},
                    {**row, "message": "x" * 241}, {**row, "ts": "yesterday"}):
            self.assertTrue(c.errors({**doc, "events": [bad]}), bad)
        long = p.readable("y" * 500)
        self.assertEqual(240, len(long))

    def test_cli_reads_append_only_jsonl(self):
        r, _ = run({"keyframes": [StageError("INVALID_INPUT", "SYNTHETIC bad clip", False)]})
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "events.jsonl"
            f.write_text("".join(json.dumps(e) + "\n" for e in r.events("job-a")), encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(0, p.main([str(f), "2"]))
            doc = json.loads(out.getvalue())
            self.assertEqual(([3, 4], "failed"), ([e["revision"] for e in doc["events"]], doc["job"]["status"]))
            f.write_text(json.dumps({**r.events("job-a")[0], "revision": 5}) + "\n", encoding="utf-8")
            self.assertEqual(1, p.main([str(f)]))


if __name__ == "__main__":
    unittest.main()
