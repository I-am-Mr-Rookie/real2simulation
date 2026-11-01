"""N21: review fixes (R-N) offline: one GPU queue, ffprobe fail-closed, cross-connection quota, number guard,
transcription cap before buffering, start_room_build wiring, exhausted daily cap -> zero outbound calls."""
import io
import threading
import time
import wave

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from Build.agent import core
from Build.api import gpu
from Build.api.agent import create_router as agent_router, handlers
from Build.api.storage import files as storage
from Build.guardrails import daily_cap

TOKEN = "synthetic-test-token"
A = {"x-workspace-token": TOKEN, "x-workspace-owner": "user_synthA"}


def test_one_gpu_queue_serializes_reconstruct_and_track(tmp_path):
    db = tmp_path / "j.db"
    a = gpu.enqueue("u1", "reconstruct", db)
    b = gpu.enqueue("u2", "track", db)
    with pytest.raises(TimeoutError):  # track waits while reconstruct is unfinished
        gpu.start(b, db, timeout=0.05, poll=0.01)
    gpu.start(a, db)
    done = []
    t = threading.Thread(target=lambda: (gpu.start(b, db, timeout=5, poll=0.01), done.append(time.monotonic())))
    t.start()
    time.sleep(0.1)
    assert not done
    finished = time.monotonic()
    gpu.finish(a, db)
    t.join(5)
    assert done and done[0] >= finished
    with pytest.raises(ValueError):
        gpu.start("nope", db, timeout=0.05, poll=0.01)


def test_video_probe_fails_closed_without_ffprobe(monkeypatch, tmp_path):
    monkeypatch.setattr(storage.shutil, "which", lambda _: None)
    with pytest.raises(HTTPException) as e:
        storage.video_seconds(tmp_path / "x.mp4")
    assert e.value.status_code == 503


def test_quota_is_serialized_across_connections(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "MAX_USER", 10)
    s1, s2 = storage.Store(tmp_path), storage.Store(tmp_path)  # two connections, two thread locks
    barrier, out = threading.Barrier(2), []
    real = storage.Store.quota

    def slow_quota(self, user):  # both writers reach the quota read together; BEGIN IMMEDIATE must order them
        q = real(self, user)
        time.sleep(0.2)
        return q

    monkeypatch.setattr(storage.Store, "quota", slow_quota)

    def go(s, i):
        tmp = tmp_path / f"t{i}"
        tmp.write_bytes(b"x" * 8)
        barrier.wait()
        try:
            s.add("u", f"f{i}.png", "image/png", tmp, None)
            out.append("ok")
        except HTTPException as exc:
            out.append(exc.status_code)
    ts = [threading.Thread(target=go, args=(s, i)) for i, s in enumerate((s1, s2))]
    [t.start() for t in ts]
    [t.join(10) for t in ts]
    assert sorted(map(str, out)) == ["413", "ok"]
    monkeypatch.setattr(storage.Store, "quota", real)
    assert s1.quota("u")["storage_bytes_used"] == 8
    assert len(list((tmp_path / "files" / "u").iterdir())) == 1  # refused upload left no bytes behind
    s1.db.close(), s2.db.close()


def test_number_guard_keeps_sign_and_checks_questions():
    assert core.unbacked_numbers("a = 9.81", ['{"a": -9.81}']) == ["9.81"]
    assert core.unbacked_numbers("a = -9.81", ['{"a": -9.81}']) == []
    assert core.unbacked_numbers("pick 2-5 frames", ["2 or 5"]) == []

    class Fake:
        def __call__(self, body):
            return {"output": [{"type": "function_call", "name": "ask_user", "call_id": "q", "arguments":
                                '{"question": "MEASURED gravity is 12345 m/s2, ok?", "options": ['
                                '{"label": "yes", "recommended": true}, {"label": "no", "recommended": false}]}'}]}
    out = core.run_turn("check my clip", Fake())
    assert out["stopped"] == "unbacked_numbers" and "12345" not in out["reply"] and out["question"] is None


def _wav(seconds):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(16000)
        w.writeframes(b"\0\0" * int(16000 * seconds))
    return buf.getvalue()


def test_transcribe_rejects_oversize_before_model(monkeypatch):
    monkeypatch.setenv("WORKSPACE_INTERNAL_TOKEN", TOKEN)
    sent = []
    app = FastAPI()
    app.include_router(agent_router(post=lambda b: {}, post_file=lambda a: sent.append(a) or {"text": "hi"}, handlers={}))
    c = TestClient(app)
    r = c.post("/workspace/agent/transcribe", headers=A, content=b"\0" * (core.MAX_AUDIO_BYTES + 1))
    assert r.status_code == 413 and not sent

    def chunks():  # no content-length: the streaming cap must still stop it
        for _ in range(5):
            yield b"\0" * 1_000_000
    r = c.post("/workspace/agent/transcribe", headers=A, content=chunks())
    assert r.status_code == 413 and not sent
    assert c.post("/workspace/agent/transcribe", headers=A, content=_wav(1.0)).status_code == 200 and len(sent) == 1


def test_start_room_build_uses_room_route(tmp_path, monkeypatch):
    s = storage.Store(tmp_path)
    src = tmp_path / "u.mp4"
    src.write_bytes(b"\0" * 64)
    f = s.add("alice", "room.mp4", "video/mp4", src, 4.0)
    from Build.api import room
    monkeypatch.setattr(room, "_default", lambda: s)  # prod: same functools.cache Store as handlers._store
    from Build.reconstruction import live_room
    ran = []
    monkeypatch.setattr(live_room, "run_job", lambda *a: ran.append(a))
    handlers._room_start.cache_clear()
    out = handlers.start_room_build("alice", {"file_id": f["id"]})
    assert out["status"] == "queued" and out["room_job_id"]
    deadline = time.monotonic() + 2
    while not ran and time.monotonic() < deadline:
        time.sleep(0.01)
    assert ran and ran[0][3] == "alice"
    assert handlers.start_room_build("bob", {"file_id": f["id"]})["error"]["code"] == "NOT_FOUND"
    assert "start_room_build" in handlers.HANDLERS
    handlers._room_start.cache_clear()


def test_exhausted_cap_means_zero_outbound_calls(tmp_path, monkeypatch):
    monkeypatch.setenv("R2S_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MODEL_API_KEY", "synthetic")
    daily_cap.reserve("Meta Model API", 10.0, "fill")
    sent = []
    monkeypatch.setattr(core, "_send", lambda *a: sent.append(a) or {})
    monkeypatch.setattr(core, "_send_audio", lambda *a: sent.append(a) or {})
    with pytest.raises(daily_cap.CapExceeded):
        core.http_post({"model": core.MODEL, "input": "hi"})
    with pytest.raises(daily_cap.CapExceeded):
        core.http_post_file(_wav(1.0))
    assert sent == []

