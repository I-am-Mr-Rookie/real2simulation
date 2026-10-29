"""S13a contract tests on SYNTHETIC fixtures; not upload, queue, GPU or scene evidence."""
import copy
import json
import unittest

from jsonschema import Draft202012Validator

from Build.pipeline import contracts as c

SHELL = json.loads((c.ROOT / "Build/web/src/shell/integration.schema.json").read_text(encoding="utf-8"))
SHELL_V = Draft202012Validator(SHELL)
H = "ab" * 32
SCENE = {"scene_id": "synthetic-room-v1", "scene_version": "1.0.0", "access": "private", "evidence": "synthetic"}


def ev(rev, stage, status, attempt=1, error=None):
    return {"contract_version": "1.0.0", "kind": "stage_event", "job_id": "synthetic-job-v1",
            "revision": rev, "stage": stage, "status": status, "attempt": attempt,
            "idempotency_key": f"{stage}:{H}", "at": "2026-10-29T12:00:00Z",
            "output_sha256": H if status == "succeeded" else None, "error": error}


def happy():
    out = []
    for stage in c.STAGES:
        out += [ev(len(out) + 1, stage, "started"), ev(len(out) + 2, stage, "succeeded")]
    return out


def err(code, retryable):
    return {"code": code, "message": "SYNTHETIC failure", "retryable": retryable}


class SchemaTests(unittest.TestCase):
    def test_examples_validate_and_schema_is_valid(self):
        Draft202012Validator.check_schema(c.SCHEMA)
        for doc in json.loads((c.CONTRACTS / "examples.json").read_text(encoding="utf-8")):
            self.assertEqual([], c.errors(doc), doc["kind"])

    def test_versioned_and_limits_match_policy(self):
        self.assertEqual("urn:real2simulation:jobs:1.0.0", c.SCHEMA["$id"])
        self.assertEqual("1.0.0", c.POLICY["contract_version"])
        up, d = c.POLICY["upload"], c.SCHEMA["$defs"]
        s = d["upload_session"]["properties"]
        self.assertEqual(up["max_file_bytes"], s["size_bytes"]["maximum"])
        self.assertEqual(up["chunk_bytes"], s["chunk_bytes"]["const"])
        self.assertEqual(up["chunk_bytes"], d["chunk_ack"]["properties"]["offset"]["multipleOf"])
        self.assertEqual(up["media_types"], s["media_type"]["enum"])
        self.assertEqual(c.STAGES, d["stage"]["enum"])
        self.assertEqual(max(c.MAX_ATTEMPTS.values()), d["stage_event"]["properties"]["attempt"]["maximum"])
        # error codes are the S04g shell set, so failures project without translation
        self.assertEqual(SHELL["$defs"]["error"]["properties"]["code"]["enum"], d["error"]["properties"]["code"]["enum"])
        reconstruct = next(s for s in c.POLICY["stages"] if s["name"] == "reconstruct")
        self.assertEqual("S06a-gpu-image/v1", reconstruct["runtime_contract"])

    def test_invalid_documents_rejected(self):
        session = json.loads((c.CONTRACTS / "examples.json").read_text(encoding="utf-8"))[0]
        for field, value in [("size_bytes", c.POLICY["upload"]["max_file_bytes"] + 1),
                             ("media_type", "video/x-msvideo"), ("chunk_bytes", 1024),
                             ("job_id", "early-job"), ("extra", 1)]:
            bad = dict(session, **{field: value})
            self.assertTrue(c.errors(bad), field)
        self.assertTrue(c.errors(dict(ev(1, "validate", "succeeded"), output_sha256=None)))
        self.assertTrue(c.errors(ev(1, "validate", "failed")))
        self.assertTrue(c.errors(dict(ev(1, "validate", "started"), error=err("PROCESSING_FAILED", True))))
        self.assertTrue(c.errors(dict(ev(1, "validate", "started"), at="2026-10-29 12:00")))


class UploadTests(unittest.TestCase):
    S = {"status": "open", "size_bytes": 20000000, "chunk_bytes": 8388608, "committed_bytes": 8388608}

    def test_resume_duplicate_conflict_gap(self):
        cb = 8388608
        self.assertEqual("accept", c.chunk_decision(self.S, cb, cb, H))
        self.assertEqual("duplicate", c.chunk_decision(self.S, 0, cb, H, stored_sha256=H))
        self.assertEqual("reject_conflict", c.chunk_decision(self.S, 0, cb, H, stored_sha256="cd" * 32))
        self.assertEqual("reject_gap", c.chunk_decision(self.S, 2 * cb, 20000000 - 2 * cb, H))
        self.assertEqual("reject_misaligned", c.chunk_decision(self.S, 100, cb, H))
        self.assertEqual("reject_misaligned", c.chunk_decision(self.S, 3 * cb, 1, H))
        self.assertEqual("reject_length", c.chunk_decision(self.S, cb, cb - 1, H))
        self.assertEqual("accept", c.chunk_decision(dict(self.S, committed_bytes=2 * cb), 2 * cb, 20000000 - 2 * cb, H))
        self.assertEqual("reject_closed", c.chunk_decision(dict(self.S, status="expired"), cb, cb, H))


class StageEventTests(unittest.TestCase):
    def test_happy_path_projects_to_ready_shell_job(self):
        events = happy()
        self.assertEqual([], c.check_events(events))
        snap = c.job_snapshot("synthetic-job-v1", events, SCENE)
        self.assertEqual(("ready", len(events)), (snap["status"], snap["revision"]))
        self.assertEqual([], [e.message for e in SHELL_V.iter_errors(snap)])
        queued = c.job_snapshot("synthetic-job-v1", [])
        self.assertEqual(("queued", 0), (queued["status"], queued["revision"]))
        self.assertEqual([], [e.message for e in SHELL_V.iter_errors(queued)])

    def test_retryable_failure_retries_with_same_key(self):
        events = [ev(1, "validate", "started"), ev(2, "validate", "succeeded"),
                  ev(3, "keyframes", "started"), ev(4, "keyframes", "failed", 1, err("DEPENDENCY_UNAVAILABLE", True))]
        self.assertEqual("running", c.job_snapshot("synthetic-job-v1", events)["status"])
        events += [ev(5, "keyframes", "started", 2), ev(6, "keyframes", "succeeded", 2)]
        self.assertEqual([], c.check_events(events))
        changed = copy.deepcopy(events)
        changed[4]["idempotency_key"] = "keyframes:" + "cd" * 32
        changed[5]["idempotency_key"] = changed[4]["idempotency_key"]
        self.assertTrue(any("idempotency_key changed" in p for p in c.check_events(changed)))

    def test_terminal_failures_project_to_failed_and_block_retry(self):
        base = [ev(1, "validate", "started"), ev(2, "validate", "succeeded"),
                ev(3, "keyframes", "started"), ev(4, "keyframes", "succeeded"),
                ev(5, "understand", "started")]
        cases = [
            base + [ev(6, "understand", "failed", 1, err("SPEND_PAUSED", False))],
            base + [ev(6, "understand", "failed", 1, err("PROCESSING_FAILED", True)),
                    ev(7, "understand", "started", 2), ev(8, "understand", "failed", 2, err("PROCESSING_FAILED", True))],
        ]
        for events in cases:
            self.assertEqual([], c.check_events(events))
            snap = c.job_snapshot("synthetic-job-v1", events)
            self.assertEqual("failed", snap["status"])
            self.assertEqual([], [e.message for e in SHELL_V.iter_errors(snap)])
            retry = ev(len(events) + 1, "understand", "started", events[-1]["attempt"] + 1)
            self.assertTrue(c.check_events(events + [retry]))

    def test_sequence_violations(self):
        h = happy()
        never = [ev(1, "validate", "started"), ev(2, "validate", "failed", 1, err("UNAUTHORIZED", True))]
        bad = {
            "illegal transition to understand": [h[0], h[1], ev(3, "understand", "started")],
            "revision must be 2": [h[0], dict(h[1], revision=3)],
            "illegal transition to validate/succeeded": [ev(1, "validate", "succeeded")],
            "illegal transition to package/started#2": h + [ev(len(h) + 1, "package", "started", 2)],
            "UNAUTHORIZED cannot be retryable": never,
            "attempt exceeds max_attempts": [ev(1, "validate", "started"),
                                             ev(2, "validate", "failed", 1, err("PROCESSING_FAILED", True)),
                                             ev(3, "validate", "started", 2)],
            "job_id changed": [h[0], dict(h[1], job_id="other-job")],
            "prefix must be the stage": [dict(h[0], idempotency_key=f"package:{H}")],
            "not a stage_event": json.loads((c.CONTRACTS / "examples.json").read_text(encoding="utf-8"))[:1],
        }
        for reason, events in bad.items():
            self.assertTrue(any(reason in p for p in c.check_events(events)), reason)
        with self.assertRaises(ValueError):
            c.job_snapshot("synthetic-job-v1", never)
        with self.assertRaises(ValueError):
            c.job_snapshot("synthetic-job-v1", h)  # ready without scene


if __name__ == "__main__":
    unittest.main()
