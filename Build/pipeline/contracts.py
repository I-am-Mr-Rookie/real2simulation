"""S13a job contracts: DTO validation, upload chunk rule, stage-event sequence check.

Pure functions over contracts/jobs; no network, bucket, queue or GPU access.
"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "contracts" / "jobs"
SCHEMA = json.loads((CONTRACTS / "jobs.schema.json").read_text(encoding="utf-8"))
POLICY = json.loads((CONTRACTS / "policy.json").read_text(encoding="utf-8"))
STAGES = [s["name"] for s in POLICY["stages"]]
MAX_ATTEMPTS = {s["name"]: s["max_attempts"] for s in POLICY["stages"]}
NEVER_RETRY = set(POLICY["retry"]["never_retry"])
_VALIDATOR = Draft202012Validator(SCHEMA)


def errors(doc):
    """Schema errors for one upload_session / chunk_ack / stage_event document."""
    return [e.message for e in _VALIDATOR.iter_errors(doc)]


def chunk_decision(session, offset, length, chunk_sha256, stored_sha256=None):
    """Server rule for one chunk PUT. stored_sha256 = hash already committed at offset, if any.

    accept | duplicate (idempotent re-send, no write) | reject_closed | reject_misaligned
    | reject_gap (client resumes from committed_bytes) | reject_conflict | reject_length
    """
    if session["status"] != "open":
        return "reject_closed"
    size, step, done = session["size_bytes"], session["chunk_bytes"], session["committed_bytes"]
    if offset % step or offset >= size:
        return "reject_misaligned"
    if length != min(step, size - offset):
        return "reject_length"
    if offset < done:
        return "duplicate" if stored_sha256 == chunk_sha256 else "reject_conflict"
    return "accept" if offset == done else "reject_gap"


def _retry_allowed(event):
    err = event["error"]
    return (err["retryable"] and err["code"] not in NEVER_RETRY
            and event["attempt"] < MAX_ATTEMPTS[event["stage"]])


def check_events(events):
    """Ordering/retry violations for one job's stage events (empty list = valid)."""
    problems = []
    last, keys = None, {}
    for i, ev in enumerate(events):
        bad = errors(ev) or ([] if ev["kind"] == "stage_event" else ["not a stage_event"])
        if bad:
            problems += [f"event {i}: {m}" for m in bad]
            return problems
        tag = f"event {i}"
        if ev["job_id"] != events[0]["job_id"]:
            problems.append(f"{tag}: job_id changed")
        if ev["revision"] != i + 1:
            problems.append(f"{tag}: revision must be {i + 1}")
        if ev["attempt"] > MAX_ATTEMPTS[ev["stage"]]:
            problems.append(f"{tag}: attempt exceeds max_attempts")
        if not ev["idempotency_key"].startswith(ev["stage"] + ":"):
            problems.append(f"{tag}: idempotency_key prefix must be the stage")
        if keys.setdefault(ev["stage"], ev["idempotency_key"]) != ev["idempotency_key"]:
            problems.append(f"{tag}: idempotency_key changed across attempts")
        if ev["error"] and ev["error"]["retryable"] and ev["error"]["code"] in NEVER_RETRY:
            problems.append(f"{tag}: {ev['error']['code']} cannot be retryable")
        if ev["status"] == "started":
            if last is None:
                ok = ev["stage"] == STAGES[0] and ev["attempt"] == 1
            elif last["status"] == "succeeded":
                ok = (ev["attempt"] == 1 and last["stage"] != STAGES[-1]
                      and STAGES.index(ev["stage"]) == STAGES.index(last["stage"]) + 1)
            elif last["status"] == "failed":
                ok = (_retry_allowed(last) and ev["stage"] == last["stage"]
                      and ev["attempt"] == last["attempt"] + 1)
            else:
                ok = False
        else:
            ok = (last is not None and last["status"] == "started"
                  and (last["stage"], last["attempt"]) == (ev["stage"], ev["attempt"]))
        if not ok:
            problems.append(f"{tag}: illegal transition to {ev['stage']}/{ev['status']}#{ev['attempt']}")
        last = ev
    return problems


def job_snapshot(job_id, events, scene=None):
    """Project valid stage events onto the S04g shell job DTO (contract 1.0.0).

    scene: shell scene object, required once package succeeded. Cancellation is not a stage event.
    """
    problems = check_events(events)  # explicit raise, not assert: must survive python -O
    if problems:
        raise ValueError(problems)
    snap = {"contract_version": "1.0.0", "kind": "job", "job_id": job_id,
            "revision": events[-1]["revision"] if events else 0,
            "status": "queued" if not events else "running", "result": None, "error": None}
    last = events[-1] if events else None
    if last and last["status"] == "succeeded" and last["stage"] == STAGES[-1]:
        if scene is None:
            raise ValueError("ready job needs its scene")
        snap.update(status="ready", result=scene)
    elif last and last["status"] == "failed" and not _retry_allowed(last):
        snap.update(status="failed", error={k: last["error"][k] for k in ("code", "message")})
    return snap
