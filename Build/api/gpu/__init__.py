"""N04 GPU status for the private workspace: GET /internal/workspace/gpu/status (browser: /api/workspace/gpu/status).

state: red sleeping (no GPU container, nothing queued), yellow starting (work queued, no container has picked it
up yet), green running (a container is up and working or warm-idle). Modal counts a booting container in
num_total_runners (seen live in evidence/N04), so "picked up" = Modal backlog below our unfinished job count.
Real state = Modal Function.get_current_stats() of the deployed
r2s-ondemand functions + our own job table (queued/started/finished timestamps, SQLite in R2S_DATA_DIR).
queue_length = unfinished jobs (running + waiting); your_position = 1-based place of the caller's oldest
unfinished job (1 = running or next), null when the caller has none.
"""
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends

from Build.api.workspace.auth import require_owner

APP_NAME = "r2s-ondemand"
FUNCTIONS = ("reconstruct", "track")  # Build/gpu/ondemand.py


def default_path():
    return Path(os.environ.get("R2S_DATA_DIR", "data")) / "gpu_jobs.sqlite3"


def _connect(path=None):
    path = Path(path or default_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=30, isolation_level=None)
    con.execute("CREATE TABLE IF NOT EXISTS gpu_jobs (id TEXT PRIMARY KEY, owner TEXT NOT NULL, kind TEXT NOT NULL,"
                " queued_at TEXT NOT NULL, started_at TEXT, finished_at TEXT)")
    return con


def _now(now):
    return (now or datetime.now(timezone.utc)).isoformat()


def enqueue(owner, kind, path=None, now=None):
    if kind not in FUNCTIONS:
        raise ValueError("unknown GPU job kind")
    jid = uuid.uuid4().hex
    con = _connect(path)
    try:
        con.execute("INSERT INTO gpu_jobs VALUES (?, ?, ?, ?, NULL, NULL)", (jid, owner, kind, _now(now)))
    finally:
        con.close()
    return jid


def _mark(column, jid, path, now):
    con = _connect(path)
    try:
        if con.execute(f"UPDATE gpu_jobs SET {column} = ? WHERE id = ? AND {column} IS NULL",
                       (_now(now), jid)).rowcount != 1:
            raise ValueError(f"unknown job or {column} already set")
    finally:
        con.close()


def start(jid, path=None, now=None):
    _mark("started_at", jid, path, now)


def finish(jid, path=None, now=None):
    _mark("finished_at", jid, path, now)


def modal_stats():
    """(runners, backlog) summed over the deployed functions, or None if Modal is unreachable/not configured."""
    try:
        import modal
        runners = backlog = 0
        for name in FUNCTIONS:
            s = modal.Function.from_name(APP_NAME, name).get_current_stats()
            runners, backlog = runners + s.num_total_runners, backlog + s.backlog
        return runners, backlog
    except Exception:  # missing client/token/deployment: fall back to the job table, labelled source="jobs"
        return None


def status(owner, stats, path=None):
    con = _connect(path)
    try:
        active = con.execute("SELECT owner FROM gpu_jobs WHERE finished_at IS NULL ORDER BY queued_at, id").fetchall()
    finally:
        con.close()
    owners = [o for (o,) in active]
    position = owners.index(owner) + 1 if owner in owners else None
    runners, backlog = stats if stats else (0, 0)
    if runners == 0:
        state = "yellow" if (backlog > 0 or owners) else "red"
    else:  # max_containers=1 and one queue: nothing picked up yet means the container is still starting
        state = "yellow" if backlog > 0 and backlog >= len(owners) else "green"
    return {"state": state, "queue_length": max(len(owners), backlog), "your_position": position,
            "source": "modal+jobs" if stats else "jobs"}


def create_router(path=None, stats=modal_stats) -> APIRouter:
    router = APIRouter(prefix="/internal/workspace", dependencies=[Depends(require_owner)])

    @router.get("/gpu/status")
    def gpu_status(owner: str = Depends(require_owner)):
        # shortcut: one Modal stats round-trip per poll, add a few-second cache if many clients poll
        return status(owner, stats(), path)

    return router
