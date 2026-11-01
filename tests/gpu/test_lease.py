"""N35: a crashed GPU job loses its lease, frees the queue, and its daily_cap reservation is settled exactly once."""
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from Build.api import gpu
from Build.guardrails import daily_cap as dc

T = datetime(2026, 11, 1, 6, 0, tzinfo=timezone.utc)  # 12:00 Dhaka


@pytest.fixture
def quiet(monkeypatch):
    """No heartbeat thread beats during the test: a runner that was killed. Lease = the real 90 s."""
    monkeypatch.setattr(gpu, "BEAT_S", 1000.0)
    yield
    for stop in list(gpu._beats.values()):
        stop.set()


def sec(n):
    return T + timedelta(seconds=n)


def test_killed_job_frees_queue_after_lease_and_never_runs_again(tmp_path, quiet):
    db = tmp_path / "j.db"
    a = gpu.enqueue("u1", "reconstruct", db, T)
    gpu.start(a, db, now=T)
    b = gpu.enqueue("u2", "track", db, sec(1))
    c = gpu.enqueue("u3", "track", db, sec(2))
    gpu.heartbeat(b, db, now=sec(60))  # b and c wait; a's runner is dead
    gpu.heartbeat(c, db, now=sec(60))
    with pytest.raises(TimeoutError):  # 89 s without beat: still inside the lease
        gpu.start(b, db, now=sec(89), timeout=0)
    gpu.heartbeat(c, db, now=sec(89))
    gpu.start(b, db, now=sec(91), timeout=0)  # a expired: b starts
    with pytest.raises(TimeoutError):  # one at a time: c waits for b
        gpu.start(c, db, now=sec(92), timeout=0)
    with pytest.raises(gpu.JobStopped, match="GPU job stopped responding"):
        gpu.heartbeat(a, db, now=sec(92))
    with pytest.raises(gpu.JobStopped):  # a cannot be started a second time
        gpu.start(a, db, now=sec(92), timeout=0)
    with pytest.raises(ValueError):
        gpu.finish(a, db)
    con = sqlite3.connect(db)
    assert con.execute("SELECT count(*) FROM gpu_jobs WHERE started_at IS NOT NULL AND finished_at IS NULL").fetchone()[0] == 1
    assert gpu.status("u1", None, db, now=sec(92))["queue_length"] == 2  # b running, c waiting


def test_status_reaps_with_nobody_waiting(tmp_path, quiet):
    db = tmp_path / "j.db"
    a = gpu.enqueue("u1", "track", db, T)
    gpu.start(a, db, now=T)
    assert gpu.status("u1", None, db, now=sec(60))["queue_length"] == 1
    assert gpu.status("u1", None, db, now=sec(91))["queue_length"] == 0


@pytest.mark.parametrize("renewal", ["start", "heartbeat"])
def test_status_serializes_with_concurrent_renewal_before_expiry(tmp_path, quiet, monkeypatch, renewal):
    """Hold a real renewal's write lock while status tries to reap the old, expired snapshot."""
    from concurrent.futures import ThreadPoolExecutor
    db, cap = tmp_path / "j.db", tmp_path / "s.db"
    rid = reserve(cap)
    jid = gpu.enqueue("u1", "reconstruct", db, T, reservation=rid, cap_db=cap)
    if renewal == "heartbeat":
        gpu.start(jid, db, now=T)
    connected, written, reading, commit = (threading.Event() for _ in range(4))
    connect = gpu._connect

    class Connection:
        def __init__(self, con, status):
            self.con, self.status = con, status

        def execute(self, sql, *args):
            if self.status and sql == "BEGIN IMMEDIATE":
                reading.set()  # fixed path blocks here until the renewal commits
            if not self.status and renewal == "heartbeat" and sql.startswith("UPDATE gpu_jobs SET heartbeat_at"):
                self.con.execute("BEGIN IMMEDIATE")
                cursor = self.con.execute(sql, *args)
                written.set()
                assert commit.wait(5)
                self.con.execute("COMMIT")
                return cursor
            if not self.status and sql == "COMMIT":
                written.set()
                assert commit.wait(5)
            cursor = self.con.execute(sql, *args)
            if self.status and sql.startswith("SELECT id, started_at"):
                reading.set()  # old autocommit path reads the stale row before renewal commits
            return cursor

        def close(self):
            self.con.close()

    def wrapped_connect(path=None):
        con = connect(path)
        status = threading.current_thread().name.startswith("status")
        if status:
            connected.set()
            assert written.wait(5)
        return Connection(con, status)

    monkeypatch.setattr(gpu, "_connect", wrapped_connect)
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="status") as statuses, \
            ThreadPoolExecutor(max_workers=1, thread_name_prefix="renewal") as renewals:
        status = statuses.submit(gpu.status, "u1", None, db, sec(91))
        try:
            assert connected.wait(5)
            renew = renewals.submit(getattr(gpu, renewal), jid, db, now=sec(89))
            assert written.wait(5) and reading.wait(5)
        finally:
            commit.set()
        renew.result(timeout=5)
        assert status.result(timeout=5)["queue_length"] == 1
    with sqlite3.connect(db) as con:
        started, beat, finished = con.execute(
            "SELECT started_at, heartbeat_at, finished_at FROM gpu_jobs WHERE id = ?", (jid,)).fetchone()
    assert started is not None and beat == sec(89).isoformat() and finished is None
    with sqlite3.connect(cap) as con:
        assert con.execute("SELECT actual FROM spend WHERE id = ?", (rid,)).fetchone() == (None,)
    gpu.finish(jid, db, now=sec(92))


def test_slow_but_alive_job_is_not_killed(tmp_path, monkeypatch):
    monkeypatch.setattr(gpu, "LEASE_S", 0.3)
    monkeypatch.setattr(gpu, "BEAT_S", 0.05)
    db = tmp_path / "j.db"
    a = gpu.enqueue("u1", "reconstruct", db)
    gpu.start(a, db)
    b = gpu.enqueue("u2", "track", db)
    t = threading.Thread(target=gpu.start, args=(b, db), kwargs={"timeout": 5, "poll": 0.02})
    t.start()
    time.sleep(1.0)  # > 3 leases of silence from the main thread (a long remote call)
    assert t.is_alive()  # b still waits: a kept its lease through the heartbeat thread
    gpu.heartbeat(a, db)
    gpu.finish(a, db)
    t.join(5)
    assert not t.is_alive()
    gpu.finish(b, db)
    assert a not in gpu._beats and b not in gpu._beats


def test_heartbeat_thread_stops_with_finish(tmp_path, monkeypatch):
    monkeypatch.setattr(gpu, "BEAT_S", 0.02)
    db = tmp_path / "j.db"
    a = gpu.enqueue("u1", "track", db)
    gpu.start(a, db)
    gpu.finish(a, db)
    with pytest.raises(gpu.JobStopped):
        gpu.heartbeat(a, db)


def reserve(cap, usd="1.50"):
    return dc.reserve("Modal", usd, "N35", path=cap, now=T)


def spent(cap):
    return dc.today(path=cap, now=T)["spent_usd"]


def test_cap_reservation_of_started_job_is_kept_once(tmp_path, quiet):
    db, cap = tmp_path / "j.db", tmp_path / "s.db"
    rid = reserve(cap)
    a = gpu.enqueue("u1", "reconstruct", db, T, reservation=rid, cap_db=cap)
    gpu.start(a, db, now=T)
    b = gpu.enqueue("u2", "track", db, sec(80))
    gpu.start(b, db, now=sec(100), timeout=0)
    assert spent(cap) == Decimal("1.5")  # may have run: no free run
    row = sqlite3.connect(cap).execute("SELECT actual, settled_at FROM spend WHERE id = ?", (rid,)).fetchone()
    assert row[0] == 150000000 and row[1]  # settled, not left open
    with pytest.raises(ValueError):  # a late runner cannot charge again
        dc.settle(rid, "1.50", path=cap, now=T)
    assert spent(cap) == Decimal("1.5")


def test_cap_reservation_of_never_started_job_is_released(tmp_path, quiet):
    db, cap = tmp_path / "j.db", tmp_path / "s.db"
    rid = reserve(cap)
    dead = gpu.enqueue("u1", "reconstruct", db, T, reservation=rid, cap_db=cap)  # process died while waiting
    b = gpu.enqueue("u2", "track", db, sec(80))
    gpu.start(b, db, now=sec(100), timeout=0)
    assert spent(cap) == 0
    with pytest.raises(gpu.JobStopped):
        gpu.start(dead, db, now=sec(101), timeout=0)


def test_runner_settle_before_reap_is_not_charged_twice(tmp_path, quiet):
    db, cap = tmp_path / "j.db", tmp_path / "s.db"
    rid = reserve(cap)
    a = gpu.enqueue("u1", "reconstruct", db, T, reservation=rid, cap_db=cap)
    gpu.start(a, db, now=T)
    dc.settle(rid, "0.40", path=cap, now=T)  # runner settled, then stalled before finish()
    assert gpu.status("u1", None, db, now=sec(100))["queue_length"] == 0
    assert spent(cap) == Decimal("0.4")


def test_old_database_gets_lease_columns(tmp_path):
    db = tmp_path / "old.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE gpu_jobs (id TEXT PRIMARY KEY, owner TEXT NOT NULL, kind TEXT NOT NULL,"
                " queued_at TEXT NOT NULL, started_at TEXT, finished_at TEXT)")
    con.execute("INSERT INTO gpu_jobs VALUES ('old', 'u', 'track', ?, ?, NULL)", (T.isoformat(), T.isoformat()))
    con.commit()
    con.close()
    j = gpu.enqueue("u2", "track", db)
    gpu.start(j, db, timeout=0)  # the pre-lease row has no heartbeat: expired, queue moves
    gpu.finish(j, db)
