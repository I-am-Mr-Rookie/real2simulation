"""N48: finished room jobs beat stale Modal backlog; warm-idle is timed, not a stuck queue."""
from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from Build.api import gpu
from Build.reconstruction import live_room

T = datetime(2026, 11, 2, 4, 40, tzinfo=timezone.utc)


def test_cold_start_running_finish_idle_sleep_and_stale_backlog(tmp_path):
    db = tmp_path / 'gpu.db'
    jid = gpu.enqueue('owner', 'reconstruct', db, T)
    gpu.start(jid, db, now=T)
    assert gpu.status('owner', (1, 1), db, now=T)['state'] == 'yellow'
    assert gpu.status('owner', (1, 0), db, now=T)['state'] == 'green'
    done = T + timedelta(seconds=300)  # a 5-minute cold start/result, with a live runner heartbeat
    gpu.finish(jid, db, now=done)
    for seconds in (0, 1, 60, 899):
        s = gpu.status('owner', (1, 1), db, now=done + timedelta(seconds=seconds))
        assert s == {'state': 'green', 'queue_length': 0, 'your_position': None,
                     'source': 'modal+jobs', 'idle_seconds_remaining': 900 - seconds}
    assert gpu.status('owner', (0, 0), db, now=done + timedelta(seconds=900))['state'] == 'red'
    assert gpu.status('owner', (0, 1), db, now=done + timedelta(seconds=901))['state'] == 'red'
    # With no stats, the job clock is explicitly an estimate; never stay warm forever.
    assert gpu.status('owner', None, db, now=done)['idle_seconds_remaining'] == 900
    assert gpu.status('owner', None, db, now=done + timedelta(seconds=900))['state'] == 'red'
    # Positive runner telemetry wins over the estimated sleep deadline.
    assert gpu.status('owner', (1, 0), db, now=done + timedelta(seconds=901))['idle_seconds_remaining'] == 0


def test_last_finished_job_resets_idle_clock_but_duplicate_finish_does_not(tmp_path):
    db = tmp_path / 'gpu.db'
    for seconds in (0, 100):
        now = T + timedelta(seconds=seconds)
        jid = gpu.enqueue('owner', 'track', db, now)
        gpu.start(jid, db, now=now)
        gpu.finish(jid, db, now=now)
    gpu.finish(jid, db, now=T + timedelta(seconds=150))
    assert gpu.status('owner', (1, 0), db, now=T + timedelta(seconds=160))['idle_seconds_remaining'] == 840


def test_lease_cleanup_then_late_finish_does_not_mask_runner_error(tmp_path):
    db = tmp_path / 'gpu.db'
    jid = gpu.enqueue('owner', 'reconstruct', db, T)
    gpu.start(jid, db, now=T)
    gpu.status('owner', (1, 1), db, now=T + timedelta(seconds=100))
    gpu.finish(jid, db, now=T + timedelta(seconds=110))
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT finished_at, failed_reason FROM gpu_jobs WHERE id = ?', (jid,)).fetchone() == (
            (T + timedelta(seconds=100)).isoformat(), gpu.REASON)
    assert jid not in gpu._beats


@pytest.mark.parametrize('failure', [None, 'queue', 'remote', 'settle', 'postprocess'])
def test_room_always_finishes_shared_gpu_job(tmp_path, monkeypatch, failure):
    db, cap = tmp_path / 'gpu.db', tmp_path / 'cap.db'
    job = tmp_path / 'room'
    job.mkdir()
    monkeypatch.setattr(live_room, 'sample_frames', lambda *a: [b'frame'])
    monkeypatch.setattr(live_room, 'scene_log', lambda *a: {
        'cost': {'upper_bound': {'total_usd': 0}}, 'timing_s': {}, 'gpu': 'L4'})

    def fail(*args, **kwargs):
        raise RuntimeError('offline injected failure')

    if failure == 'queue':
        monkeypatch.setattr(live_room.gpu_jobs, 'start', fail)
    if failure == 'settle':
        monkeypatch.setattr(live_room.daily_cap, 'settle', fail)
    monkeypatch.setattr(live_room, 'finish', fail if failure == 'postprocess' else lambda *a: {
        'room': {'scale': {'status': 'MODEL-ESTIMATED'}, 'gravity': {'status': 'MODEL-ESTIMATED'}}})
    remote = fail if failure == 'remote' else lambda frames: {'npz': b'offline fixture'}
    live_room.run_job(job, 'unused.mp4', 30, 'owner', remote=remote, gpu_db=db, cap_db=cap)
    with sqlite3.connect(db) as con:
        rows = con.execute('SELECT id, finished_at FROM gpu_jobs').fetchall()
    assert len(rows) == 1 and rows[0][1]
    assert rows[0][0] not in gpu._beats
    assert gpu.status('owner', (1, 1), db)['queue_length'] == 0
