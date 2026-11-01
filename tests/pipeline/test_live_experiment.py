"""N07 Mode B live pipeline: offline tests (recorded hosted SAM 3.1 response, fake trackers; no network, no spend)."""
import json
import math
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.api import experiment
from Build.api.storage.files import Store
from Build.guardrails import daily_cap
from Build.measurement import hosted_sam
from Build.pipeline import live_experiment as le

ROOT = Path(__file__).resolve().parents[2]
APPLE = ROOT / "evidence/N02/resp-apple.json"  # recorded N02 ST03 response (Pexels License clip, masks stripped)


def apple_track():
    tr = hosted_sam.result(json.loads(APPLE.read_text(encoding="utf-8")))
    return le.track_record(tr, [k / 29.97 for k in range(tr["frame_count"])])


def fall_track(g=9.81, mpp=0.001, n_rest=5, n_fall=20):
    """Synthetic drop: rest, then y_px grows as g t^2 / 2 / mpp; 50 px box so '5 cm' gives mpp 0.001."""
    frames = [[k, k / 30, 300.0, 100.0, 50, 50] for k in range(n_rest)]
    for i in range(1, n_fall + 1):
        t = i / 30
        frames.append([n_rest - 1 + i, (n_rest - 1 + i) / 30, 300.0, 100.0 + 0.5 * g * t * t / mpp, 50, 50])
    return {"frames": frames}


def test_recorded_apple_segment_and_labels():
    track = apple_track()
    px = le.analyse(track)
    assert px["segment"]["first_frame"] == 56 and px["segment"]["last_frame"] == 77
    assert px["motion"] in ("free_fall", "projectile") and px["units"] == "px"
    q = px["quantity"]
    assert q["unit"] == "px/s^2" and q["value"] > 0 and q["uncertainty"] > 0 and "scale unverified" in q["label"]
    m = le.analyse(track, "apple width 8 cm")
    assert m["quantity"]["unit"] == "m/s^2" and m["quantity"]["label"] == "MEASURED"
    assert m["scale"]["status"] == "declared" and m["quantity"]["uncertainty"] > 0
    assert len(m["trajectory"]["t_s"]) == m["segment"]["frames"] and m["trajectory"]["unit"] == "m"


def test_synthetic_drop_recovers_g_and_skips_rest_frames():
    r = le.analyse(fall_track(), "ball diameter 5 cm")
    assert r["motion"] == "free_fall" and r["segment"]["first_frame"] >= 4
    assert r["quantity"]["value"] == pytest.approx(9.81, rel=1e-6)


def test_no_scale_basis_abstains_on_metric_values():
    r = le.analyse(fall_track(), "no idea")
    assert r["units"] == "px" and r["scale"]["status"] == "abstain" and r["quantity"]["unit"] == "px/s^2"


def test_pendulum_like_reports_no_number_and_short_tracks_abstain():
    frames = [[k, k / 30, 300 + 80 * math.sin(k / 5), 200 + 10 * math.cos(k / 2.5), 30, 30] for k in range(90)]
    r = le.analyse({"frames": frames})
    assert r["motion"].startswith("periodic") and "quantity" not in r and r["fit"] is None
    assert le.analyse({"frames": frames[:3]})["status"] == "abstain"


def test_run_uses_injected_tracker_and_checks_frame_count(monkeypatch):
    tr = hosted_sam.result(json.loads(APPLE.read_text(encoding="utf-8")))
    monkeypatch.setattr(le, "probe", lambda p: (720, 1366, [k / 29.97 for k in range(543)]))
    out = le.run("clip.mp4", "apple", tracker=lambda *a: tr)
    assert out["track"]["source"].startswith("hosted") and out["cost_usd"] == pytest.approx(0.1086)
    backup = le.run("clip.mp4", "apple", tracker=lambda *a: 1 / 0, backup=lambda *a: tr)
    assert backup["track"]["source"].startswith("Modal")
    monkeypatch.setattr(le, "probe", lambda p: (720, 1366, [0.0] * 10))
    with pytest.raises(ValueError, match="543 frames"):
        le.run("clip.mp4", "apple", tracker=lambda *a: tr)


def test_hosted_track_reserves_and_settles_daily_cap(monkeypatch, tmp_path):
    cap = tmp_path / "spend.sqlite3"
    resp = json.loads(APPLE.read_text(encoding="utf-8"))
    calls = []
    monkeypatch.setattr(hosted_sam, "_post", lambda *a: calls.append(a) or resp)
    hosted_sam.track("file-1", "apple", max_frames=600, cap_path=cap)
    assert float(daily_cap.today(cap)["spent_usd"]) == pytest.approx(543 * hosted_sam.USD_PER_FRAME)
    with pytest.raises(daily_cap.CapExceeded):
        hosted_sam.track("file-1", "apple", max_frames=10**9, cap_path=cap)
    assert len(calls) == 1  # refused before any network call


def client(tmp_path, monkeypatch, run):
    monkeypatch.setenv("WORKSPACE_INTERNAL_TOKEN", "t")
    store = Store(tmp_path)
    src = tmp_path / "upload.mp4"
    src.write_bytes(b"\x00" * 64)
    f = store.add("alice", "drop.mp4", "video/mp4", src, 1.0)
    app = FastAPI()
    app.include_router(experiment.create_router(store, run=run, submit=lambda fn, *a: fn(*a)))
    return TestClient(app), store, f


H = {"x-workspace-token": "t", "x-workspace-owner": "alice"}


def test_api_start_poll_attach_and_validate(tmp_path, monkeypatch):
    seen = []
    def run(path, text, point, size):
        seen.append((Path(path).name, text, point, size))
        return {"status": "ok", "track": fall_track(), "cost_usd": 0.0}
    c, store, f = client(tmp_path, monkeypatch, run)
    r = c.post("/internal/workspace/experiments", headers=H, json={"file_id": f["id"], "point": {"x": 10, "y": 20},
                                                                   "known_size": "5 cm"})
    assert r.status_code == 202
    e = r.json()["experiment"]
    assert seen == [(f["id"], None, (10, 20), "5 cm")]
    got = c.get(f"/internal/workspace/experiments/{e['id']}", headers=H).json()["experiment"]
    assert got["status"] == "done" and got["result"]["status"] == "ok"
    assert store.project("alice", got["project_id"])["mode"] == "experiment"
    listed = c.get(f"/internal/workspace/experiments?project_id={got['project_id']}", headers=H).json()["experiments"]
    assert [x["id"] for x in listed] == [e["id"]]
    refit = experiment.refit(store, "alice", e["id"])
    assert refit["quantity"]["value"] == pytest.approx(9.81, rel=1e-6) and "trajectory" not in refit
    for bad in ({"file_id": f["id"]}, {"file_id": f["id"], "target_text": "ball", "point": {"x": 1, "y": 1}},
                {"file_id": f["id"], "target_text": "x" * 81}, {"file_id": f["id"], "point": {"x": -1, "y": 1}}):
        assert c.post("/internal/workspace/experiments", headers=H, json=bad).status_code == 422
    assert c.post("/internal/workspace/experiments", headers={**H, "x-workspace-owner": "bob"},
                  json={"file_id": f["id"], "target_text": "ball"}).status_code == 404
    assert c.get(f"/internal/workspace/experiments/{e['id']}",
                 headers={**H, "x-workspace-owner": "bob"}).status_code == 404
    assert c.get(f"/internal/workspace/experiments/{e['id']}", headers={"x-workspace-owner": "alice"}).status_code == 401


def test_job_failures_are_recorded_not_raised(tmp_path, monkeypatch):
    def capped(*a):
        raise daily_cap.CapExceeded("cap")
    c, store, f = client(tmp_path, monkeypatch, capped)
    e = c.post("/internal/workspace/experiments", headers=H, json={"file_id": f["id"], "target_text": "ball"}).json()
    got = experiment.get(store, "alice", e["experiment"]["id"])["experiment"]
    assert got["status"] == "failed" and got["error"]["code"] == "CAP_EXCEEDED"

