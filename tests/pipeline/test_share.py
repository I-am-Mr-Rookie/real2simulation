"""N16 Guess the Gravity share API: offline, no spend."""
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.api import experiment
from Build.api.experiment import share
from Build.api.storage.files import Store
from Build.pipeline import live_experiment as le
from tests.pipeline.test_live_experiment import fall_track as _clean

H = {"x-workspace-token": "t", "x-workspace-owner": "alice"}
EX = "/internal/workspace/experiments"


def fall_track():  # a noiseless fit gives -inf AIC, which JSON cannot store; add small deterministic jitter
    t = _clean()
    for k, f in enumerate(t["frames"]):
        f[3] += 0.4 * ((-1) ** k) * (k % 3)
        f[2] += 0.3 * ((-1) ** (k // 2)) * (k % 4)
    return t


def setup(tmp_path, monkeypatch, known_size="5 cm"):
    monkeypatch.setenv("WORKSPACE_INTERNAL_TOKEN", "t")
    store = Store(tmp_path)
    src = tmp_path / "u.mp4"
    src.write_bytes(b"\x00" * 64)
    f = store.add("alice", "private-name.mp4", "video/mp4", src, 1.0)
    run = lambda path, text, point, size: {**le.analyse(fall_track(), size), "track": fall_track()}
    app = FastAPI()
    app.include_router(experiment.create_router(store, run=run, submit=lambda fn, *a: fn(*a)))
    app.include_router(share.create_router(store))
    c = TestClient(app)
    body = {"file_id": f["id"], "point": {"x": 1, "y": 2}, "known_size": known_size}
    return c, c.post(EX, headers=H, json=body).json()["experiment"]["id"]


def test_share_view_hides_answer_then_reveal_and_revoke(tmp_path, monkeypatch):
    c, eid = setup(tmp_path, monkeypatch)
    tok = c.post(f"{EX}/{eid}/share", headers=H).json()["token"]
    assert c.post(f"{EX}/{eid}/share", headers=H).json()["token"] == tok  # idempotent while active
    v = c.get(f"/public/guess/{tok}")  # no auth headers
    assert v.status_code == 200 and v.json()["title"] == "Guess the Gravity"
    blob = json.dumps(v.json())
    assert "quantity" not in blob and "alice" not in blob and "private-name" not in blob and "file_id" not in blob
    r = c.post(f"/public/guess/{tok}/reveal", json={"guess": 10}).json()
    assert abs(r["quantity"]["value"] - 9.81) < 0.2 and r["quantity"]["label"].startswith("MEASURED")
    assert abs(r["difference"] - (10 - r["quantity"]["value"])) < 1e-9
    for bad in ("x", None, -1, 1e9, True):
        assert c.post(f"/public/guess/{tok}/reveal", json={"guess": bad}).status_code == 422
    assert c.delete(f"{EX}/{eid}/share", headers=H).json() == {"revoked": 1}
    assert c.get(f"/public/guess/{tok}").status_code == 404
    assert c.post(f"/public/guess/{tok}/reveal", json={"guess": 1}).status_code == 404


def test_owner_only_and_shareable_only(tmp_path, monkeypatch):
    c, eid = setup(tmp_path, monkeypatch)
    assert c.post(f"{EX}/{eid}/share").status_code == 401
    assert c.post(f"{EX}/{eid}/share", headers={**H, "x-workspace-owner": "bob"}).status_code == 404
    assert c.delete(f"{EX}/{eid}/share", headers={**H, "x-workspace-owner": "bob"}).status_code == 404
    assert c.get("/public/guess/" + "z" * 32).status_code == 404
    (tmp_path / "n").mkdir()
    c2, eid2 = setup(tmp_path / "n", monkeypatch, known_size=None)
    assert c2.post(f"{EX}/{eid2}/share", headers=H).status_code == 422  # px only: no scale, nothing to guess
