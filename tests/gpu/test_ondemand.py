"""N04: GPU status from real state (job table + Modal stats) and the on-demand Modal settings."""
import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.api import gpu

T0 = datetime.now(timezone.utc)  # real time: status()/start() reap jobs whose heartbeat is older than the lease


def test_status_states_and_positions(tmp_path):
    db = tmp_path / "j.db"
    assert gpu.status("u1", (0, 0), db) == {"state": "red", "queue_length": 0, "your_position": None,
                                             "source": "modal+jobs"}
    a = gpu.enqueue("u1", "reconstruct", db, T0)
    b = gpu.enqueue("u2", "track", db, T0 + timedelta(seconds=1))
    gpu.enqueue("u1", "track", db, T0 + timedelta(seconds=2))
    assert gpu.status("u2", (0, 0), db)["state"] == "yellow"  # queued, container still booting
    assert gpu.status("u2", (1, 3), db)["state"] == "yellow"  # booting container already counts as a runner
    gpu.start(a, db)
    s = gpu.status("u2", (1, 2), db)
    assert (s["state"], s["queue_length"], s["your_position"]) == ("green", 3, 2)
    assert gpu.status("u1", (1, 2), db)["your_position"] == 1
    gpu.finish(a, db)
    gpu.start(b, db)
    gpu.finish(b, db)
    assert gpu.status("u2", (1, 0), db)["your_position"] is None
    assert gpu.status("u1", (1, 0), db)["your_position"] == 1
    assert gpu.status("u3", (1, 0), db)["state"] == "green"  # idle warm container before scale-down
    assert gpu.status("u3", (0, 4), db)["queue_length"] == 4  # Modal backlog from other callers counts
    assert gpu.status("u3", (1, 1), db)["state"] == "yellow"  # outside call waiting, none of ours running


def test_without_modal_stats_falls_back_to_jobs(tmp_path):
    db = tmp_path / "j.db"
    assert gpu.status("u1", None, db)["state"] == "red"
    gpu.enqueue("u1", "track", db, T0)
    assert gpu.status("u1", None, db) == {"state": "yellow", "queue_length": 1, "your_position": 1,
                                           "source": "jobs"}


def test_job_table_rejects_bad_transitions(tmp_path):
    db = tmp_path / "j.db"
    with pytest.raises(ValueError):
        gpu.enqueue("u1", "mine-bitcoin", db)
    j = gpu.enqueue("u1", "track", db)
    gpu.start(j, db)
    with pytest.raises(ValueError):
        gpu.start(j, db)
    with pytest.raises(ValueError):
        gpu.finish("nope", db)


def test_route_requires_internal_token(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_INTERNAL_TOKEN", "t")
    app = FastAPI()
    app.include_router(gpu.create_router(tmp_path / "j.db", stats=lambda: (0, 0)))
    c = TestClient(app)
    assert c.get("/internal/workspace/gpu/status").status_code == 401
    r = c.get("/internal/workspace/gpu/status", headers={"x-workspace-token": "t", "x-workspace-owner": "user_1"})
    assert r.status_code == 200 and r.json()["state"] == "red"


def test_health_app_mounts_gpu_status(monkeypatch):
    monkeypatch.setenv("WORKSPACE_INTERNAL_TOKEN", "t")
    from Build.api.health.app import create_app
    paths = {r.path for r in create_app().routes}
    assert "/internal/workspace/gpu/status" in paths


def test_ondemand_settings():
    """Static check (no Modal client needed): both GPU functions scale to zero after 900 s, one container each."""
    tree = ast.parse((Path(__file__).resolve().parents[2] / "Build/gpu/ondemand.py").read_text(encoding="utf-8"))
    kw = next(n.value for n in ast.walk(tree) if isinstance(n, ast.Assign) and n.targets[0].id == "ONDEMAND")
    od = ast.literal_eval(kw)
    assert od["min_containers"] == 0 and od["max_containers"] == 1 and od["scaledown_window"] == 900
    fns = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert fns == list(gpu.FUNCTIONS)
