"""S13d job lifecycle + retry over a Redis-shaped store (contract 1.0.0).

Idempotency: a stage's output is recorded once under `out:<idempotency_key>` and reused by
every later attempt or job with the same key, so retries never recompute an artifact or re-dispatch
a paid stage that already succeeded. A per-key lease (claim:<key>, SET NX EX) stops two workers
dispatching the same key concurrently. SYNTHETIC tests only; no Redis server, queue, GPU or spend ran.
"""
import datetime
import json
import time

from Build.pipeline.contracts import NEVER_RETRY, POLICY, STAGES, _retry_allowed, check_events, job_snapshot
from Build.pipeline.progress import progress

BACKOFF_S = POLICY["retry"]["backoff_s"]
LOST = {"code": "PROCESSING_FAILED", "message": "worker lost mid-stage; no recorded output", "retryable": True}


class MemoryStore:
    """In-memory stand-in exposing only the redis-py calls used here.

    shortcut: single process, no persistence; pass redis.Redis(decode_responses=True) instead once a
    client is installed (not installed or exercised in S13d).
    """

    def __init__(self, clock=time.monotonic):
        self.clock, self.kv, self.lists = clock, {}, {}

    def _live(self, key):
        item = self.kv.get(key)
        if item and item[1] is not None and item[1] <= self.clock():
            del self.kv[key]
            return None
        return item

    def set(self, key, value, nx=False, ex=None):
        if nx and self._live(key):
            return None
        self.kv[key] = (value, None if ex is None else self.clock() + ex)
        return True

    def get(self, key):
        item = self._live(key)
        return item[0] if item else None

    def delete(self, key):
        return int(self.kv.pop(key, None) is not None)

    def rpush(self, key, value):
        self.lists.setdefault(key, []).append(value)
        return len(self.lists[key])

    def lrange(self, key, start, end):
        items = self.lists.get(key, [])
        return items[start:None if end == -1 else end + 1]


class StageError(Exception):
    """Expected stage failure; code must be a contract error code."""

    def __init__(self, code, message, retryable):
        super().__init__(message)
        self.code, self.message, self.retryable = code, message, retryable


class Busy(Exception):
    """Another worker holds the lease for this idempotency key; do not dispatch it again."""


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class JobRunner:
    """Drive one job through STAGES with bounded retries.

    workers: {stage: fn(idempotency_key) -> output_sha256}; raise StageError for expected failures.
    Paid workers must pass the key on to the provider. lease_s must exceed the longest stage runtime.
    """

    def __init__(self, store, workers, sleep=time.sleep, lease_s=900, now=_now):
        self.store, self.workers, self.sleep, self.lease_s, self.now = store, workers, sleep, lease_s, now

    def events(self, job_id):
        return [json.loads(e) for e in self.store.lrange(f"job:{job_id}:events", 0, -1)]

    def progress(self, job_id, after=0, scene=None):
        """S13g display feed (job_progress) for the shell host; see Build/pipeline/progress.py."""
        return progress(job_id, self.events(job_id), after, scene)

    def _emit(self, job_id, stage, status, attempt, key, output=None, error=None):
        evs = self.events(job_id)
        ev = {"contract_version": "1.0.0", "kind": "stage_event", "job_id": job_id,
              "revision": len(evs) + 1, "stage": stage, "status": status, "attempt": attempt,
              "idempotency_key": key, "at": self.now(), "output_sha256": output, "error": error}
        problems = check_events(evs + [ev])  # explicit raise: must survive python -O
        if problems:
            raise ValueError(problems)
        self.store.rpush(f"job:{job_id}:events", json.dumps(ev))

    def run(self, job_id, input_sha256, scene=None):
        """Run or resume job_id until ready or terminally failed; returns the shell job snapshot.

        Resuming reads the stored events; input_sha256 is used only for a job with no events.
        """
        while True:
            evs = self.events(job_id)
            last = evs[-1] if evs else None
            if last is None:
                stage, attempt, sha = STAGES[0], 1, input_sha256
            elif last["status"] == "succeeded":
                if last["stage"] == STAGES[-1]:
                    return job_snapshot(job_id, evs, scene)
                stage, attempt, sha = STAGES[STAGES.index(last["stage"]) + 1], 1, last["output_sha256"]
            elif last["status"] == "failed":
                if not _retry_allowed(last):
                    return job_snapshot(job_id, evs)  # terminal: never transitions again
                self.sleep(BACKOFF_S[min(last["attempt"], len(BACKOFF_S)) - 1])
                stage, attempt, sha = last["stage"], last["attempt"] + 1, last["idempotency_key"].split(":", 1)[1]
            else:
                self._recover(job_id, last)
                continue
            self._attempt(job_id, stage, attempt, f"{stage}:{sha}")

    def _attempt(self, job_id, stage, attempt, key):
        claim = f"claim:{key}"
        if not self.store.set(claim, job_id, nx=True, ex=self.lease_s):
            raise Busy(key)
        try:
            self._emit(job_id, stage, "started", attempt, key)
            out = self.store.get(f"out:{key}")
            if out is None:
                try:
                    out = self.workers[stage](key)
                except StageError as e:
                    self._emit(job_id, stage, "failed", attempt, key, error={
                        "code": e.code, "message": e.message,
                        "retryable": bool(e.retryable) and e.code not in NEVER_RETRY})
                    return
                self.store.set(f"out:{key}", out)  # under the lease: one writer per key
            self._emit(job_id, stage, "succeeded", attempt, key, output=out)
        finally:
            # shortcut: unconditional delete may drop a lease taken over after expiry; use a token check (Lua) with real Redis
            self.store.delete(claim)

    def _recover(self, job_id, last):
        """A started event with no outcome: a worker crashed. Close it from the store, never by guessing."""
        key = last["idempotency_key"]
        if self.store.get(f"claim:{key}") is not None:
            raise Busy(key)
        out = self.store.get(f"out:{key}")
        if out is not None:
            self._emit(job_id, last["stage"], "succeeded", last["attempt"], key, output=out)
        else:
            self._emit(job_id, last["stage"], "failed", last["attempt"], key, error=dict(LOST))
