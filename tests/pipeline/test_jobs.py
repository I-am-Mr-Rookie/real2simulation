"""S13d lifecycle/retry tests on SYNTHETIC workers; no Redis server, queue, GPU or spend."""
import hashlib
import unittest
from collections import Counter

from Build.pipeline import contracts as c
from Build.pipeline.jobs import Busy, JobRunner, MemoryStore, StageError

IN = "cd" * 32
SCENE = {"scene_id": "synthetic-room-v1", "scene_version": "1.0.0", "access": "private", "evidence": "synthetic"}


class Clock:
    t = 0.0

    def __call__(self):
        return self.t


def fixture(fail=None):
    """Workers counting dispatches; fail: {stage: [exception or None per call]}."""
    calls, fail = Counter(), fail or {}

    def make(stage):
        def work(key):
            calls[stage] += 1
            plan = fail.get(stage, [])
            if len(plan) >= calls[stage] and plan[calls[stage] - 1]:
                raise plan[calls[stage] - 1]
            return hashlib.sha256(key.encode()).hexdigest()
        return work
    return calls, {s: make(s) for s in c.STAGES}


def runner(store, workers, sleeps):
    return JobRunner(store, workers, sleep=sleeps.append, now=lambda: "2026-10-29T12:00:00Z")


def paid(calls):
    return {s: calls[s] for s in ("understand", "segment", "reconstruct")}


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.store, self.sleeps = MemoryStore(self.clock), []

    def test_happy_path_dispatches_each_stage_once(self):
        calls, w = fixture()
        r = runner(self.store, w, self.sleeps)
        self.assertEqual("ready", r.run("job-a", IN, SCENE)["status"])
        self.assertEqual({s: 1 for s in c.STAGES}, dict(calls))
        self.assertEqual([], c.check_events(r.events("job-a")))
        self.assertEqual([], [k for k in self.store.kv if k.startswith("claim:")])  # leases released

    def test_retryable_paid_failure_retries_once_with_backoff(self):
        calls, w = fixture({"segment": [StageError("DEPENDENCY_UNAVAILABLE", "SYNTHETIC 503", True)]})
        snap = runner(self.store, w, self.sleeps).run("job-a", IN, SCENE)
        self.assertEqual("ready", snap["status"])
        self.assertEqual({"understand": 1, "segment": 2, "reconstruct": 1}, paid(calls))
        self.assertEqual([5], self.sleeps)

    def test_paid_stage_retries_bounded_at_two(self):
        boom = StageError("DEPENDENCY_UNAVAILABLE", "SYNTHETIC down", True)
        calls, w = fixture({"reconstruct": [boom] * 9})
        snap = runner(self.store, w, self.sleeps).run("job-a", IN)
        self.assertEqual("failed", snap["status"])
        self.assertEqual(2, calls["reconstruct"])
        self.assertEqual(0, calls["package"])

    def test_retries_are_bounded_then_terminal_and_frozen(self):
        boom = StageError("DEPENDENCY_UNAVAILABLE", "SYNTHETIC down", True)
        calls, w = fixture({"keyframes": [boom] * 9})
        r = runner(self.store, w, self.sleeps)
        snap = r.run("job-a", IN)
        self.assertEqual(("failed", "DEPENDENCY_UNAVAILABLE"), (snap["status"], snap["error"]["code"]))
        self.assertEqual(3, calls["keyframes"])
        self.assertEqual([5, 30], self.sleeps)
        self.assertEqual(snap, r.run("job-a", IN))  # terminal job never transitions
        self.assertEqual(3, calls["keyframes"])

    def test_never_retry_code_is_terminal_even_if_flagged_retryable(self):
        calls, w = fixture({"understand": [StageError("SPEND_PAUSED", "SYNTHETIC cap", True)]})
        snap = runner(self.store, w, self.sleeps).run("job-a", IN)
        self.assertEqual(("failed", "SPEND_PAUSED"), (snap["status"], snap["error"]["code"]))
        self.assertEqual(1, calls["understand"])
        self.assertEqual(0, calls["segment"])

    def test_user_retry_new_job_reuses_outputs_without_paid_redispatch(self):
        calls, w = fixture({"reconstruct": [StageError("PROCESSING_FAILED", "SYNTHETIC bad mesh", False)]})
        r = runner(self.store, w, self.sleeps)
        self.assertEqual("failed", r.run("job-a", IN)["status"])
        self.assertEqual("ready", r.run("job-b", IN, SCENE)["status"])  # new job id, same input
        self.assertEqual({"understand": 1, "segment": 1, "reconstruct": 2}, paid(calls))
        self.assertEqual(1, calls["package"])
        outs = [k for k in self.store.kv if k.startswith("out:")]
        self.assertEqual(len(c.STAGES), len(outs))  # one artifact record per key, none duplicated
        a = [e for e in r.events("job-a") if e["status"] == "succeeded"]
        b = {e["stage"]: e["output_sha256"] for e in r.events("job-b") if e["status"] == "succeeded"}
        self.assertTrue(all(b[e["stage"]] == e["output_sha256"] for e in a))

    def test_crash_mid_stage_resumes_with_one_bounded_retry(self):
        calls, w = fixture({"understand": [RuntimeError("SYNTHETIC crash")]})
        r = runner(self.store, w, self.sleeps)
        with self.assertRaises(RuntimeError):
            r.run("job-a", IN)
        self.assertEqual("ready", r.run("job-a", IN, SCENE)["status"])
        self.assertEqual(2, calls["understand"])
        lost = [e for e in r.events("job-a") if e["status"] == "failed"]
        self.assertEqual(["understand"], [e["stage"] for e in lost])

    def test_crash_with_recorded_output_reuses_it(self):
        calls, w = fixture({"segment": [RuntimeError("SYNTHETIC crash")]})
        r = runner(self.store, w, self.sleeps)
        with self.assertRaises(RuntimeError):
            r.run("job-a", IN)
        key = r.events("job-a")[-1]["idempotency_key"]
        self.store.set(f"out:{key}", "ef" * 32)  # e.g. a concurrent job finished this key
        self.assertEqual("ready", r.run("job-a", IN, SCENE)["status"])
        self.assertEqual(1, calls["segment"])

    def test_live_lease_blocks_duplicate_paid_dispatch(self):
        calls, w = fixture()
        r = runner(self.store, w, self.sleeps)
        seen = {}

        def segment(key):  # while job-a holds the segment lease, job-b reaches the same key
            calls["segment"] += 1
            with self.assertRaises(Busy):
                r.run("job-b", IN)
            seen["during"] = paid(calls)
            return "ab" * 32
        w["segment"] = segment
        r.run("job-a", IN, SCENE)
        self.assertEqual({"understand": 1, "segment": 1, "reconstruct": 0}, seen["during"])
        self.assertEqual("ready", r.run("job-b", IN, SCENE)["status"])
        self.assertEqual({"understand": 1, "segment": 1, "reconstruct": 1}, paid(calls))

    def test_crashed_worker_lease_expires(self):
        calls, w = fixture()
        r = runner(self.store, w, self.sleeps)
        self.store.set(f"claim:validate:{IN}", "dead-worker", nx=True, ex=r.lease_s)
        with self.assertRaises(Busy):
            r.run("job-a", IN)
        self.assertEqual(0, calls["validate"])
        self.clock.t += r.lease_s
        self.assertEqual("ready", r.run("job-a", IN, SCENE)["status"])


if __name__ == "__main__":
    unittest.main()
