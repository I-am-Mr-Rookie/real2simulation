"""N04 GPU status for the private workspace: GET /internal/workspace/gpu/status (browser: /api/workspace/gpu/status).

state: red sleeping (no GPU container, nothing queued), yellow starting (work queued, no container has picked it
up yet), green running (a container is up and working or warm-idle). Modal counts a booting container in
num_total_runners (seen live in evidence/N04), so "picked up" = Modal backlog below our unfinished job count.
Real state = Modal Function.get_current_stats() of the deployed
r2s-ondemand functions + our own job table (queued/started/finished timestamps, SQLite in R2S_DATA_DIR).
queue_length = unfinished jobs (running + waiting); your_position = 1-based place of the caller's oldest
unfinished job (1 = running or next), null when the caller has none.

N35 lease: every unfinished job has heartbeat_at. A waiting job refreshes it on each start() poll, a running job from a
daemon thread started by start() (every BEAT_S, stopped by finish()). Not refreshed for LEASE_S (a crashed process)
= failed with REASON, queue moves on, and its daily_cap reservation (if enqueue got one) is settled once: at the
reserved amount if the job had started (the GPU may have run: no free run), at 0 if it never started.
"""
import os
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends

from Build.api.workspace.auth import require_owner
from Build.guardrails import daily_cap

APP_NAME = "r2s-ondemand"
FUNCTIONS = ("reconstruct", "track")  # Build/gpu/ondemand.py
LEASE_S, BEAT_S = 90.0, 20.0
REASON = "GPU job stopped responding"
_NEW_COLUMNS = ("heartbeat_at", "failed_reason", "reservation", "cap_db")  # added after the first release
_beats = {}  # job id -> stop Event of this process's heartbeat thread


class JobStopped(RuntimeError):
    """The job's lease ran out and it was failed; it must not run."""


def default_path():
    return Path(os.environ.get("R2S_DATA_DIR", "data")) / "gpu_jobs.sqlite3"


def _connect(path=None):
    path = Path(path or default_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=30, isolation_level=None)
    con.execute("CREATE TABLE IF NOT EXISTS gpu_jobs (id TEXT PRIMARY KEY, owner TEXT NOT NULL, kind TEXT NOT NULL,"
                " queued_at TEXT NOT NULL, started_at TEXT, finished_at TEXT)")
    have = {r[1] for r in con.execute("PRAGMA table_info(gpu_jobs)")}
    for col in _NEW_COLUMNS:
        if col not in have:
            try:
                con.execute(f"ALTER TABLE gpu_jobs ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError:  # another process added it first
                pass
    return con


def _now(now):
    return (now or datetime.now(timezone.utc)).isoformat()


def enqueue(owner, kind, path=None, now=None, reservation=None, cap_db=None):
    """reservation/cap_db: the daily_cap reservation id (and its db path, None = default) to settle if the job dies."""
    if kind not in FUNCTIONS:
        raise ValueError("unknown GPU job kind")
    jid = uuid.uuid4().hex
    con = _connect(path)
    try:
        con.execute("INSERT INTO gpu_jobs (id, owner, kind, queued_at, heartbeat_at, reservation, cap_db)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (jid, owner, kind, _now(now), _now(now), reservation, str(cap_db) if cap_db else None))
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


def _reap(con, now):
    """Fail unfinished jobs whose lease ran out. Returns [(reservation, cap_db, started)] to pass to _settle after commit."""
    t = now or datetime.now(timezone.utc)
    dead = []
    for jid, started, rid, cap_db, beat in con.execute(
            "SELECT id, started_at, reservation, cap_db, heartbeat_at FROM gpu_jobs WHERE finished_at IS NULL").fetchall():
        if beat and (t - datetime.fromisoformat(beat)).total_seconds() <= LEASE_S:
            continue  # no heartbeat at all = row from before N35: expired
        if con.execute("UPDATE gpu_jobs SET finished_at = ?, failed_reason = ? WHERE id = ? AND finished_at IS NULL",
                       (_now(now), REASON, jid)).rowcount == 1:
            dead.append((rid, cap_db, started is not None))
    return dead


def _settle(dead):
    for rid, cap_db, started in dead:
        if not rid:
            continue
        try:
            amount = 0
            if started:  # may have run on the GPU: keep the full reservation, as an unsettled row would
                con = daily_cap._connect(cap_db or daily_cap.default_path())
                try:
                    row = con.execute("SELECT reserved FROM spend WHERE id = ?", (rid,)).fetchone()
                finally:
                    con.close()
                amount = Decimal(row[0]) * daily_cap.UNIT if row else 0
            daily_cap.settle(rid, amount, path=cap_db)
        except ValueError:  # unknown or already settled by the runner: never charge twice
            pass


def heartbeat(jid, path=None, now=None):
    """Refresh the lease. Raises JobStopped when the job was failed or finished (the runner must stop)."""
    con = _connect(path)
    try:
        if con.execute("UPDATE gpu_jobs SET heartbeat_at = ? WHERE id = ? AND finished_at IS NULL",
                       (_now(now), jid)).rowcount != 1:
            row = con.execute("SELECT failed_reason FROM gpu_jobs WHERE id = ?", (jid,)).fetchone()
            raise JobStopped((row and row[0]) or "GPU job is not running")
    finally:
        con.close()


def _run_beats(jid, path, stop):
    while not stop.wait(BEAT_S):
        try:
            heartbeat(jid, path)
        except RuntimeError:  # JobStopped
            return
        except sqlite3.Error:  # transient lock: the lease tolerates several misses
            pass


def start(jid, path=None, now=None, timeout=1800.0, poll=1.0):
    """Block until jid is the oldest unfinished job of ANY kind, then mark it started: one GPU queue for
    reconstruct and track (two Modal functions, but never two jobs dispatched at once). TimeoutError when stuck,
    JobStopped if this job's own lease ran out while waiting. Starts the heartbeat thread; finish() stops it."""
    deadline = time.monotonic() + timeout
    while True:
        con = _connect(path)
        try:
            con.execute("BEGIN IMMEDIATE")
            dead = _reap(con, now)
            con.execute("UPDATE gpu_jobs SET heartbeat_at = ? WHERE id = ? AND finished_at IS NULL AND started_at IS NULL",
                        (_now(now), jid))  # a waiting job holds its place by polling
            head = con.execute("SELECT id FROM gpu_jobs WHERE finished_at IS NULL ORDER BY queued_at, rowid"
                               " LIMIT 1").fetchone()
            ok = head is not None and head[0] == jid and con.execute(
                "UPDATE gpu_jobs SET started_at = ? WHERE id = ? AND started_at IS NULL", (_now(now), jid)).rowcount == 1
            con.execute("COMMIT")
            row = con.execute("SELECT started_at, failed_reason FROM gpu_jobs WHERE id = ?", (jid,)).fetchone()
        finally:
            con.close()
        _settle(dead)
        if ok:
            _beats[jid] = stop = threading.Event()
            threading.Thread(target=_run_beats, args=(jid, path, stop), daemon=True).start()
            return
        if row and row[1]:
            raise JobStopped(row[1])
        if not row or row[0]:
            raise ValueError("unknown job or started_at already set")
        if time.monotonic() >= deadline:
            raise TimeoutError("GPU queue busy; job not started")
        time.sleep(poll)


def finish(jid, path=None, now=None):
    stop = _beats.pop(jid, None)
    if stop:
        stop.set()
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


def status(owner, stats, path=None, now=None):
    con = _connect(path)
    try:
        dead = _reap(con, now)  # a dead job must not show as queue length
        active = con.execute("SELECT owner FROM gpu_jobs WHERE finished_at IS NULL ORDER BY queued_at, rowid").fetchall()
    finally:
        con.close()
    _settle(dead)
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
