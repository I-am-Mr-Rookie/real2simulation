"""N19 offline adversarial probes. No real network, credentials, GPU, or source edits."""
import asyncio
import io
import json
import os
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from Build.agent import core
from Build.api.agent import create_router as agent_router
from Build.api.storage.files import Store, MAX_USER, create_router as storage_router
from Build.guardrails import daily_cap as dc
from Build.measurement import hosted_sam


def spend_bypass(root):
    os.environ['R2S_DATA_DIR'] = str(root)
    dc.reserve('Modal', '10')
    assert dc.today()['headroom_usd'] == 0
    response = io.BytesIO(b'{"text":"mock","output":[]}')
    with patch.dict(os.environ, {'MODEL_API_KEY': 'synthetic-not-a-secret'}):
        with patch('urllib.request.urlopen', return_value=response) as send:
            core.http_post({'model': core.MODEL})
            assert send.call_count == 1
        with patch('urllib.request.urlopen', return_value=io.BytesIO(b'{"text":"mock"}')) as send:
            core.http_post_file(b'mock')
            assert send.call_count == 1
        with patch.object(hosted_sam.requests, 'post') as send:
            send.return_value.json.return_value = {'output': []}
            hosted_sam.track('mock-file', 'ball')
            assert send.call_count == 1
    assert dc.today()['spent_usd'] == 10
    print('CAP_BYPASS: full $10 ledger still allowed 3 mocked live transports; ledger unchanged')


def quota_race(root, storage=False):
    stores = [Store(root), Store(root)]
    day = stores[0]._day()
    count = 1 if storage else 19
    for n in range(count):
        stores[0].db.execute('INSERT INTO files (id,user,name,media_type,size,created,dhaka_day) VALUES (?,?,?,?,?,?,?)',
                            (str(n), 'u', 'seed', 'video/mp4', MAX_USER - 10 if storage else 0, 'now', day))
    barrier = threading.Barrier(2)
    for store in stores:
        quota = store.quota
        counter = [0]

        def wrapped(user, quota=quota, counter=counter):
            result = quota(user)
            counter[0] += 1
            if counter[0] == 2:  # both final quota snapshots precede either insert
                barrier.wait(timeout=10)
            return result

        store.quota = wrapped
    def add(pair):
        n, store = pair
        tmp = root / 'tmp' / str(n)
        tmp.write_bytes(b'12345678')
        return store.add('u', 'clip.mp4', 'video/mp4', tmp, 1)
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert len(list(pool.map(add, enumerate(stores)))) == 2
    quota = Store.quota(stores[0], 'u')
    if storage:
        assert quota['storage_bytes_used'] == MAX_USER + 6
        print('STORAGE_RACE: 2 Store connections admitted 8 bytes each with 10 remaining; exceeded cap by 6')
    else:
        assert quota['uploads_today'] == 21
        print('DAILY_RACE: 2 Store connections admitted uploads 20 and 21; cap is 20')
    for store in stores:
        store.db.close()


def number_guard():
    assert core.unbacked_numbers('MEASURED acceleration +9.81', ['{"acceleration": -9.81}']) == []
    assert core.unbacked_numbers('MEASURED mass 9.81 kg', ['{"duration_s": 9.81}']) == []
    body = {'output': [{'type': 'function_call', 'name': 'ask_user', 'call_id': 'x',
                       'arguments': json.dumps({'question': 'MEASURED gravity is 12345 m/s2. Continue?',
                                                'options': [{'label': 'Yes', 'recommended': True},
                                                            {'label': 'No', 'recommended': False}]})}]}
    result = core.run_turn('Track my experiment', lambda request: body)
    assert result['stopped'] == 'ask_user' and '12345' in result['reply']
    print('NUMBER_GUARD: sign/unit substitution accepted; ask_user bypass returns invented 12345')


def auth_and_paths():
    app = FastAPI()
    app.include_router(agent_router(post=lambda request: {'output': []}))
    with patch.dict(os.environ, {'WORKSPACE_INTERNAL_TOKEN': 'synthetic-test-token'}):
        with TestClient(app) as client:
            payload = {'text': 'help with physics'}
            assert client.post('/workspace/agent/turn', json=payload).status_code == 401
            headers = {'x-workspace-token': 'synthetic-test-token', 'x-workspace-owner': 'user_test'}
            assert client.post('/workspace/agent/turn', json=payload, headers=headers).status_code == 200
            assert client.post('/internal/workspace/agent/turn', json=payload, headers=headers).status_code == 404
    print('ROUTING: agent auth fails closed, but BFF upstream /internal/workspace/agent/turn returns 404')


def missing_media_probe(root):
    store = Store(root)
    app = FastAPI()
    app.include_router(storage_router(store))
    with patch.dict(os.environ, {'WORKSPACE_INTERNAL_TOKEN': 'synthetic-test-token'}):
        with patch('Build.api.storage.files.shutil.which', return_value=None):
            with TestClient(app) as client:
                headers = {'x-workspace-token': 'synthetic-test-token', 'x-workspace-owner': 'user_test'}
                result = client.post('/internal/workspace/files', headers=headers,
                                     files={'file': ('spoof.mp4', b'\x00\x00\x00\x18ftypmp42garbage', 'text/html')})
    assert result.status_code == 201 and result.json()['file']['duration_s'] is None
    assert result.json()['file']['media_type'] == 'video/mp4'
    store.db.close()
    print('MEDIA_PROBE: missing ffprobe accepts corrupt MP4 magic as video/mp4 with no duration enforcement')


async def transcription_read_limit():
    # Drive the ASGI endpoint directly: observe bytes consumed before validation, not just declared length.
    app = FastAPI()
    app.include_router(agent_router(post_file=lambda audio: {'text': 'mock'}))
    endpoint = next(r.endpoint for r in app.routes if getattr(r, 'path', '') == '/workspace/agent/transcribe')
    reads = 0
    async def receive():
        nonlocal reads
        reads += 1
        return {'type': 'http.request', 'body': b'x' * 1_000_000, 'more_body': reads < 6}
    request = Request({'type': 'http', 'method': 'POST', 'path': '/', 'headers': []}, receive)
    try:
        await endpoint(request, owner='user_test')
    except Exception as exc:
        assert exc.status_code == 422
    assert reads == 6
    print('TRANSCRIPTION: consumed all 6 MB before rejecting 4 MB input cap')


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='r2s-n19-') as tmp:
        root = Path(tmp)
        spend_bypass(root / 'spend')
        quota_race(root / 'daily')
        quota_race(root / 'storage', storage=True)
        missing_media_probe(root / 'media')
    number_guard()
    auth_and_paths()
    asyncio.run(transcription_read_limit())
