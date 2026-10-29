"""S13g job progress feed: project S13d stage events onto a display-safe `job_progress` doc (contract 1.0.0).

The shell host polls this and dispatches {type: 'JOB_UPDATE', job: doc['job']} to the existing S15a reducer;
doc['events'] are display rows (no idempotency keys, hashes, absolute paths or secrets). No UI code here.
CLI: python -m Build.pipeline.progress EVENTS.jsonl [AFTER_REVISION]
(one stage_event JSON per line: the same append-only form as the job:<id>:events list).
"""
import json
import re
import sys

from Build.pipeline.contracts import MAX_ATTEMPTS, _retry_allowed, errors, job_snapshot

MAX_MESSAGE = 240
_REDACT = [
    (re.compile(r"(?i)\b(bearer|basic)\s+\S+"), r"\1 <redacted>"),
    (re.compile(r"(?i)\b(api[_-]?key|token|secret|password|authorization|credential)s?(\s*[=:]\s*)\S+"), r"\1\2<redacted>"),
    (re.compile(r"\b(sk|hf|ak|ghp|gho)[-_][A-Za-z0-9_-]{8,}"), "<redacted>"),
    (re.compile(r"\b[A-Za-z]:[\\/]\S*"), "<path>"),  # Windows absolute
    (re.compile(r"(?<![\w.])~?/(?!/)[^\s/]+/\S*"), "<path>"),  # POSIX absolute / home
    (re.compile(r"(?<![\w/])\.env\b\S*"), "<path>"),
]


def readable(text):
    """One display line: control chars removed, secrets/absolute paths redacted, length capped."""
    text = " ".join(re.sub(r"[\x00-\x1f\x7f]", " ", text or "").split())
    for pattern, repl in _REDACT:
        text = pattern.sub(repl, text)
    return text[:MAX_MESSAGE - 1] + "…" if len(text) > MAX_MESSAGE else text


def _row(ev):
    stage, n, cap = ev["stage"], ev["attempt"], MAX_ATTEMPTS[ev["stage"]]
    title = stage.capitalize() + (f" (attempt {n}/{cap})" if n > 1 else "")
    retryable = None
    if ev["status"] == "started":
        msg = f"{title} started"
    elif ev["status"] == "succeeded":
        msg = f"{title} finished"
    else:
        retryable = _retry_allowed(ev)
        err = ev["error"]
        msg = f"{title} failed: {err['code']}: {err['message']}" + (" Retrying." if retryable else " Not retried.")
    return {"revision": ev["revision"], "stage": stage, "status": ev["status"], "attempt": n,
            "ts": ev["at"], "retryable": retryable, "message": readable(msg)}


def progress(job_id, events, after=0, scene=None):
    """job_progress: display rows with revision > after (in order) + the shell job snapshot.

    Validates the whole event sequence first (job_snapshot raises ValueError on any ordering/schema problem).
    """
    job = job_snapshot(job_id, events, scene)
    if job["error"]:
        job["error"] = {**job["error"], "message": readable(job["error"]["message"])}
    doc = {"contract_version": "1.0.0", "kind": "job_progress", "job_id": job_id, "after_revision": after,
           "events": [_row(e) for e in events if e["revision"] > after], "job": job}
    problems = errors(doc)  # explicit raise: must survive python -O
    if problems:
        raise ValueError(problems)
    return doc


def main(argv):
    if len(argv) not in (1, 2):
        print("usage: python -m Build.pipeline.progress EVENTS.jsonl [AFTER_REVISION]", file=sys.stderr)
        return 2
    with open(argv[0], encoding="utf-8") as f:
        events = [json.loads(line) for line in f if line.strip()]
    if not events:
        print("no events", file=sys.stderr)
        return 1
    try:
        doc = progress(events[0]["job_id"], events, int(argv[1]) if len(argv) == 2 else 0)
    except (ValueError, KeyError) as e:
        print(f"invalid events: {e}", file=sys.stderr)
        return 1
    print(json.dumps(doc, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
