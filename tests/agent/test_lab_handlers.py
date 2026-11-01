"""N12 offline tests: lab tools on a per-owner scene, server RK4 run, fitter measurement, report, fake agent transport."""
import json
import math

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.agent import core
from Build.api.agent import lab_handlers as h
from Build.api.workspace.auth import require_owner


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("R2S_DATA_DIR", str(tmp_path))


def test_ball_drop_measures_scene_gravity_with_uncertainty():
    assert h.lab_add_object("u1", {"kind": "ball", "params": {"radius_m": 0.025, "height_m": 1.2}})["status"] == "ok"
    out = h.lab_run("u1", {})
    r = out["results"][0]
    assert out["label"] == r["label"] == "SIMULATED" and r["ended"] == "floor_contact"
    g = r["g"]
    assert 0 < g["uncertainty"] < 0.1 and abs(g["value"] - 9.81) < 3 * g["uncertainty"]


def test_pendulum_period_matches_large_angle_theory():
    h.lab_add_object("u1", {"kind": "pendulum", "params": {"length_m": 0.8, "angle_deg": 30}})
    r = h.lab_run("u1", {})["results"][0]
    T, theory = r["period"], r["large_angle_period_s"]["value"]
    assert T["uncertainty"] > 0 and abs(T["value"] - theory) / theory < 2e-3
    assert abs(theory - 2 * math.pi * math.sqrt(0.8 / 9.81)) > 0.02  # 30 degrees is visibly non-small-angle


def test_bad_inputs_are_errors_not_crashes():
    assert h.lab_add_object("u1", {"kind": "flywheel", "params": {}})["status"] == "error"
    assert "unknown params" in h.lab_add_object("u1", {"kind": "ball", "params": {"speed": 3}})["error"]["detail"]
    assert "size" in h.lab_add_object("u1", {"kind": "ball", "params": {"radius_m": -1}})["error"]["detail"]
    assert h.lab_run("u1", {})["error"]["code"] == "EMPTY_SCENE"
    assert h.write_report("u1", {})["error"]["code"] == "NO_RUN"
    assert h.load_scene("u2")["objects"] == []  # owners are isolated


def test_update_and_remove_by_id_or_kind():
    h.lab_add_object("u1", {"kind": "ball", "params": {"diameter_m": 0.05, "height_m": 1.2}})
    h.lab_add_object("u1", {"kind": "ramp", "params": {}})
    ball = h.lab_update_object("u1", {"id": "ball", "params": {"dx_m": -0.3, "diameter_m": 0.1, "yaw_deg": 90}})["object"]
    assert ball["id"] == "ball-1" and ball["size"] == [0.1] * 3
    assert abs(ball["position"][0] + 0.3) < 1e-9 and abs(ball["position"][1] - 1.2) < 1e-9
    assert abs(ball["rotation"][1] - math.sin(math.pi / 4)) < 1e-6  # quarter turn about +y
    ramp = h.lab_update_object("u1", {"id": "ramp-1", "params": {"angle_deg": 30, "length_m": 2}})["object"]
    assert ramp["size"][0] == 2 and abs(ramp["rotation"][2] - math.sin(math.radians(15))) < 1e-6
    bad = h.lab_update_object("u1", {"id": "ball", "params": {"speed": 3}})
    assert "unknown" in bad["error"]["detail"]
    assert "objects in the scene: ball-1 (ball), ramp-1 (ramp)" in h.lab_remove_object("u1", {"id": "spring"})["error"]["detail"]
    assert "size" in h.lab_update_object("u1", {"id": "ball", "params": {"diameter_m": -1}})["error"]["detail"]  # editor validateScene
    assert "objects in the scene" in h.lab_remove_object("u1", {})["error"]["detail"]
    args, issues = core.validate_call("lab_remove_object", json.dumps({"kind": "ramp"}))  # live run 2 shape
    assert issues == [] and h.lab_remove_object("u1", args)["objects"] == [{"id": "ball-1", "kind": "ball"}]
    assert [o["id"] for o in h.load_scene("u1")["objects"]] == ["ball-1"]


def test_report_has_sections_labels_and_no_em_dash():
    h.lab_add_object("u1", {"kind": "ball", "params": {"radius_m": 0.025, "height_m": 1.2}})
    h.lab_run("u1", {})
    out = h.write_report("u1", {})
    md = (h._dir("u1") / "report.md").read_text("utf-8")
    for s in ("## Aim", "## Setup", "## Data", "## Fit with uncertainty", "## Conclusion", "SIMULATED", "±"):
        assert s in md
    assert "\u2014" not in md and "consistent" in out["conclusion"]
    assert "<table>" in (h._dir("u1") / "report.html").read_text("utf-8")


def _call(name, args, cid):
    return {"output": [{"type": "function_call", "id": "fc_" + cid, "call_id": cid, "name": name, "arguments": json.dumps(args)}]}


class FakeLedger:
    def __init__(self, cap=False):
        self.cap, self.settled = cap, []

    def reserve(self, provider, usd, label):
        if self.cap:
            raise RuntimeError("cap")
        return "r1"

    def settle(self, rid, usd):
        self.settled.append(usd)


def test_illustration_is_optional_costed_and_never_raises(monkeypatch):
    from Build.reports import lab_report
    ok = lambda path, data, ctype, timeout: {"data": [{"b64_json": "UklGRg=="}]}
    ledger = FakeLedger()
    assert lab_report.illustrate("Lab report: x", send=ok, ledger=ledger) == "UklGRg==" and ledger.settled == [0.01]
    def boom(*a):
        raise OSError("down")
    ledger = FakeLedger()
    assert lab_report.illustrate("t", send=boom, ledger=ledger) is None and ledger.settled == [0]
    assert lab_report.illustrate("t", send=ok, ledger=FakeLedger(cap=True)) is None
    bad = lambda *a: {"data": [{"b64_json": '"><script>'}]}
    assert lab_report.illustrate("t", send=bad, ledger=FakeLedger()) is None
    monkeypatch.setenv("R2S_LAB_REPORT_IMAGE", "1")
    monkeypatch.setattr(lab_report, "illustrate", lambda title: "UklGRg==")
    h.lab_add_object("u1", {"kind": "ball", "params": {}})
    h.lab_run("u1", {})
    assert h.write_report("u1", {})["illustration"] is True
    assert "data:image/webp;base64,UklGRg==" in (h._dir("u1") / "report.html").read_text("utf-8")
    assert (h._dir("u1") / "report.webp").read_bytes() == b"RIFF"


def test_agent_turn_with_fake_transport_runs_the_experiment():
    script = iter([_call("lab_add_object", {"kind": "ball", "params": {"radius_m": 0.025, "height_m": 1.2}}, "c1"),
                   _call("lab_run", {}, "c2"), _call("write_report", {}, "c3")])
    seen = []

    def post(body):
        seen.append(body)
        nxt = next(script, None)
        if nxt:
            return nxt
        g = json.loads(json.loads(body["input"][-1]["output"])["untrusted_data"])["conclusion"]
        return {"output": [{"type": "message", "content": [{"type": "output_text", "text": "Done. " + g}]}]}

    res = core.run_turn("Drop a 5 cm ball from 1.2 m and measure g", post, owner="u1", handlers=h.HANDLERS)
    assert res["stopped"] == "final" and [c["name"] for c in res["tool_calls"]] == ["lab_add_object", "lab_run", "write_report"]
    assert "SIMULATED" in res["reply"]


def test_router_scene_roundtrip_and_validation():
    app = FastAPI()
    app.include_router(h.create_router())
    app.dependency_overrides[require_owner] = lambda: "u1"
    c = TestClient(app)
    assert c.get("/workspace/agent/lab/scene").json()["scene"]["objects"] == []
    scene = {"version": "lab-scene-v1", "objects": [{"id": "b", "kind": "ball", "position": [0, 2, 0]}]}
    assert c.post("/workspace/agent/lab/scene", json=scene).json()["scene"]["label"] == "SIMULATED"
    assert c.post("/workspace/agent/lab/scene", json={"version": "bad"}).status_code == 422
    assert c.get("/workspace/agent/lab/scene", params={"project": "../x"}).status_code == 422
    assert c.get("/workspace/agent/lab/report").status_code == 404
