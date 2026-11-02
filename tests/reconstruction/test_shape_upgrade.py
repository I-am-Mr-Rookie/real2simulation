import json
import sqlite3
from functools import partial

from Build.api import gpu
from Build.gpu import sf3d
from Build.guardrails import daily_cap
from Build.reconstruction import live_room, shape_upgrade as upgrades
from unittest.mock import patch


def read(d, name):
    return json.loads((d / name).read_text())


def room(tmp_path, n=2):
    d = tmp_path / ('a' * 32)
    d.mkdir()
    (d / 'objects').mkdir()
    objects = [{'id': f'room-object-{i}', 'kind': 'block', 'size': [2, 1, 2], 'position': [0, .5, 0],
                'rotation': [0, 0, 0, 1], 'shape': {'type': 'box', 'fallback_reason': 'pending'}} for i in range(n)]
    live_room._write(d / 'scene.json', {'objects': objects})
    live_room._write(d / 'room.json', {'shell': {'kept': [{'id': o['id'], 'upgrade': {'state': 'pending'}} for o in objects]}})
    live_room._write(d / 'status.json', {'state': 'done'})
    upgrades.prepare(d, [{'id': o['id'], 'category': 'chair', 'png': b'rgba',
                         'proxy': {**o, 'camera': [0, 1, 3]}} for o in objects])
    return d


MESH = {'glb': b'glTF', 'vertices': [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
        'faces': [[0, 1, 2], [0, 2, 3], [0, 3, 1], [1, 2, 3]], 'gpu_name': 'NVIDIA L4'}


class Fn:
    def __init__(self, check=lambda: None):
        self.calls = 0
        self.check = check

    def spawn(self, png):
        self.calls += 1
        assert png == b'rgba'
        return self

    def get(self, timeout):
        assert timeout == sf3d.BACKGROUND_BUDGET_S
        self.check()
        return MESH


def test_room_already_ready_reservation_held_until_async_result_and_gpu_activity(tmp_path):
    d, cap, jobs = room(tmp_path), tmp_path / 'cap.db', tmp_path / 'jobs.db'

    def check():
        assert read(d, 'status.json')['state'] == 'done'
        assert any(o['upgrade']['state'] == 'pending' for o in read(d, 'room.json')['shell']['kept'])
        with sqlite3.connect(cap) as con:
            assert con.execute('SELECT actual FROM spend ORDER BY rowid DESC LIMIT 1').fetchone() == (None,)
        assert gpu.status('owner', (1, 0), jobs)['state'] == 'green'

    fn = Fn(check)
    upgrades.run(d, 'owner', cap_db=cap, gpu_db=jobs, generate=partial(sf3d.generate_remote, fn=fn))
    assert fn.calls == 2
    assert all(o['upgrade']['state'] == 'ready' for o in read(d, 'room.json')['shell']['kept'])
    for o in read(d, 'scene.json')['objects']:
        assert o['shape']['collider'] == 'box' and o['size'] == [2, 1, 2]
        assert (d / 'objects' / (o['id'] + '.glb')).read_bytes() == b'glTF'
    with sqlite3.connect(cap) as con:
        assert con.execute('SELECT COUNT(*) FROM spend WHERE actual IS NULL').fetchone() == (0,)
    assert 0 < float(daily_cap.today(cap)['spent_usd']) < 2 * sf3d.ESTIMATE_USD
    assert gpu.status('owner', None, jobs)['idle_seconds_remaining'] == 900
    upgrades.run(d, 'owner', generate=partial(sf3d.generate_remote, fn=fn))
    assert fn.calls == 2  # reopen never repeats a paid attempt


def test_cap_denial_does_not_spawn_or_fail_ready_room(tmp_path):
    d, cap, fn = room(tmp_path), tmp_path / 'cap.db', Fn()
    daily_cap.reserve('Modal', daily_cap.today(cap)['cap_usd'], path=cap)
    upgrades.run(d, 'owner', cap_db=cap, generate=partial(sf3d.generate_remote, fn=fn))
    assert fn.calls == 0 and read(d, 'status.json')['state'] == 'done'
    assert all(o['upgrade']['state'] == 'failed' and 'CapExceeded' in o['upgrade']['reason']
               for o in read(d, 'room.json')['shell']['kept'])
    assert all(o['shape']['type'] == 'box' for o in read(d, 'scene.json')['objects'])


def test_lease_reaper_retains_reservation_and_late_result_cannot_release_it(tmp_path):
    from datetime import datetime, timedelta, timezone
    import pytest
    cap, jobs = tmp_path / 'cap.db', tmp_path / 'jobs.db'

    def reap():
        gpu.status('owner', (1, 0), jobs, now=datetime.now(timezone.utc) + timedelta(seconds=gpu.LEASE_S + 1))

    with pytest.raises(RuntimeError, match=gpu.REASON):
        sf3d.generate_remote(b'rgba', cap_path=cap, gpu_path=jobs, owner='owner', fn=Fn(reap),
                             timeout_s=sf3d.BACKGROUND_BUDGET_S)
    with sqlite3.connect(cap) as con:
        reserved, actual = con.execute('SELECT reserved,actual FROM spend').fetchone()
    assert actual == reserved


def test_partial_failure_and_new_batch_cannot_receive_stale_mesh(tmp_path):
    d = room(tmp_path)
    calls = []

    def generate(png, **kw):
        calls.append(png)
        if len(calls) == 1:
            raise RuntimeError('synthetic GPU failure')
        return MESH

    upgrades.run(d, 'owner', generate=generate)
    kept = read(d, 'room.json')['shell']['kept']
    assert [o['upgrade']['state'] for o in kept] == ['failed', 'ready']
    assert 'synthetic GPU failure' in kept[0]['upgrade']['reason']
    before = read(d, 'scene.json')
    upgrades._update(d, 'replaced-batch', 'room-object-1', {'state': 'failed', 'reason': 'stale'})
    assert read(d, 'scene.json') == before


def test_deferred_shell_selects_largest_and_returns_boxes_without_a_gpu_call():
    import numpy as np
    from Build.reconstruction import room_shell
    from tests.reconstruction.test_object_lift import room_npz
    npz, hit = room_npz()
    _, _, model_room, scene = live_room.analyse(npz)
    rows, cols = np.nonzero(hit)
    box = [int(cols.min()), int(rows.min()), int(cols.max()), int(rows.max())]
    deferred = []
    with patch.object(room_shell, 'MAX_SF3D', 1):
        result, shell, glbs = room_shell.build(npz, model_room, scene,
             lambda png, noun, w, h: [box] if noun in ('table', 'chair') else [], deferred=deferred)
    assert len(deferred) == 1 and not glbs
    kept = shell['kept']
    selected = next(o for o in kept if o['id'] == deferred[0]['id'])
    assert np.prod(selected['size_m']) == max(np.prod(o['size_m']) for o in kept)
    assert selected['upgrade']['state'] == 'pending'
    assert all(o['shape']['type'] == 'box' for o in result['objects'] if o['id'].startswith('room-object-'))
    assert all('upgrade' in o for o in kept)


def test_room_api_exposes_per_object_pending_ready_failed_states(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from Build.api.room import create_router
    parent = tmp_path / 'rooms/owner'
    parent.mkdir(parents=True)
    d = room(parent, 3)
    data = read(d, 'room.json')
    data['shell']['kept'][1]['upgrade'] = {'state': 'ready'}
    data['shell']['kept'][2]['upgrade'] = {'state': 'failed', 'reason': 'cap denied'}
    live_room._write(d / 'room.json', data)
    monkeypatch.setenv('WORKSPACE_INTERNAL_TOKEN', 'test-only-token')
    app = FastAPI()
    app.include_router(create_router(SimpleNamespace(root=tmp_path), remote=lambda *a: None))
    client = TestClient(app)
    headers = {'x-workspace-token': 'test-only-token', 'x-workspace-owner': 'owner'}
    assert client.get(f'/internal/workspace/rooms/{d.name}').status_code == 401
    status = client.get(f'/internal/workspace/rooms/{d.name}', headers=headers).json()['job']
    assert [o['state'] for o in status['shape_upgrades']] == ['pending', 'ready', 'failed']
    result = client.get(f'/internal/workspace/rooms/{d.name}/result', headers=headers).json()
    assert result['room']['shell']['kept'][2]['upgrade']['reason'] == 'cap denied'


def test_rebuilding_a_shell_skips_old_remaining_calls_and_processes_new_batch(tmp_path):
    import threading
    d = room(tmp_path, 3)
    calls, done = [], threading.Event()

    def generate(png, **kw):
        calls.append(png)
        if len(calls) == 1:
            upgrades.prepare(d, [{'id': 'room-object-0', 'category': 'chair', 'png': b'new',
                                 'proxy': {'position': [0, 0, 0], 'rotation': [0, 0, 0, 1], 'camera': [0, 0, 3]}}])
        else:
            done.set()
        return MESH

    upgrades.run(d, 'owner', generate=generate)
    assert done.wait(5)
    # Wait for the replacement supervisor's file commit, not just its synthetic inference.
    import time
    deadline = time.monotonic() + 5
    while str(d) in upgrades._running and time.monotonic() < deadline:
        time.sleep(.01)
    assert calls == [b'rgba', b'new']
    assert read(d, 'room.json')['shell']['kept'][0]['upgrade']['state'] == 'ready'
