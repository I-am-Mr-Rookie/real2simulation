"""N07 agent handlers + daily-cap hook in the agent transport (offline; no network, no spend)."""
import json

import pytest

from Build.agent import core
from Build.api import experiment
from Build.api.agent import handlers
from Build.api.storage.files import Store
from Build.guardrails import daily_cap
from Build.pipeline import live_experiment


@pytest.fixture
def store(tmp_path, monkeypatch):
    s = Store(tmp_path)
    src = tmp_path / "u.mp4"
    src.write_bytes(b"\x00" * 64)
    s.add("alice", "drop.mp4", "video/mp4", src, 1.0)
    monkeypatch.setattr(handlers, "_store", lambda: s)
    monkeypatch.setattr(experiment, "_submit", lambda fn, *a: fn(*a))
    frames = [[k, k / 30, 300.0, 100.0 + 0.5 * 9.81 * (k / 30) ** 2 / 0.001, 50, 50] for k in range(1, 20)]
    monkeypatch.setattr(live_experiment, "run", lambda *a: {"status": "ok", "track": {"frames": frames}})
    return s


def test_list_start_and_fit_by_trajectory_id(store):
    files = handlers.list_files("alice", {})["files"]
    assert [f["name"] for f in files] == ["drop.mp4"] and handlers.list_files("bob", {})["files"] == []
    started = handlers.start_experiment_track("alice", {"file_id": files[0]["id"], "target": "ball"})
    assert started["status"] == "done" and started["trajectory_id"]  # inline submit in tests; live returns queued
    out = handlers.fit("alice", {"trajectory_id": started["trajectory_id"]})
    assert out["motion"] == "free_fall" and out["units"] == "px" and "trajectory" not in out
    assert handlers.fit("bob", {"trajectory_id": started["trajectory_id"]})["error"]["code"] == "NOT_FOUND"
    assert handlers.start_experiment_track("alice", {"file_id": "0" * 32, "target": "ball"})["error"]["code"] == "NOT_FOUND"


def test_fit_schema_accepts_trajectory_id_and_router_uses_real_handlers():
    args, issues = core.validate_call("fit", json.dumps({"trajectory_id": "abc123"}))
    assert not issues and args == {"trajectory_id": "abc123"}
    assert core.DEFAULT_HANDLERS["fit"]("u", {})["status"] == "error"
    assert set(handlers.HANDLERS) == {"list_files", "start_experiment_track", "fit", "start_room_build"}


def test_agent_transport_settles_reported_usage_on_daily_cap(tmp_path, monkeypatch):
    monkeypatch.setenv("R2S_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MODEL_API_KEY", "test-key")
    monkeypatch.setattr(core, "_send", lambda *a: {"usage": {"input_tokens": 1000, "output_tokens": 100}})
    core.http_post({"model": core.MODEL, "input": "hi", "max_output_tokens": 50})
    assert float(daily_cap.today()["spent_usd"]) == pytest.approx(1000 * 1e-6 + 100 * 5e-6)
    monkeypatch.setattr(core, "_send", lambda *a: (_ for _ in ()).throw(core.ModelUnavailable("HTTP 500")))
    with pytest.raises(core.ModelUnavailable):
        core.http_post({"model": core.MODEL, "input": "hi", "max_output_tokens": 50})
    assert float(daily_cap.today()["spent_usd"]) > 1000 * 1e-6 + 100 * 5e-6  # failed call keeps its reservation

