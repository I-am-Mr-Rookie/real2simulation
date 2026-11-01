"""N36: model tiers and the hidden GPT-6.1 Sol fallback (offline fakes; no network, no spend)."""
import json
import sqlite3

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.agent import core
from Build.api.agent import create_router
from Build.guardrails import daily_cap


def call(name, args, cid="c1"):
    return {"output": [{"type": "function_call", "id": "fc_" + cid, "call_id": cid, "name": name,
                        "arguments": json.dumps(args)}], "usage": {"input_tokens": 10, "output_tokens": 5}}


def say(text):
    return {"output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}],
            "usage": {"input_tokens": 7, "output_tokens": 3}}


class ByModel:
    """Transport fake: a reply list per model (an Exception instance is raised); the last reply repeats."""
    def __init__(self, **replies):
        self.replies, self.requests = {k: list(v) for k, v in replies.items()}, []

    def __call__(self, body):
        self.requests.append(json.loads(json.dumps(body)))
        key = "sol" if body["model"] == core.SOL_MODEL else "meta"
        queue = self.replies[key]
        reply = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(reply, Exception):
            raise reply
        return reply

    def models(self):
        return [r["model"] for r in self.requests]


SOL_OK = say("Here is the answer from the lab tools.")


@pytest.mark.parametrize("meta, reason", [
    ([core.ModelUnavailable("HTTP 500")], "api_error"),
    ([core.ModelUnavailable("TimeoutError")], "api_error"),
    ([say("")], "no_usable_tool_call"),
    ([call("run_shell", {}), call("lab_add_object", {"kind": "boat"})], "no_usable_tool_call"),
    ([say("g is 9.81 m/s^2."), say("g is 9.80 m/s^2.")], "number_guard"),
])
def test_fallback_answers_only_the_failed_turn(meta, reason):
    fake = ByModel(meta=meta, sol=[SOL_OK])
    out = core.run_turn("drop a ball and measure g", fake)
    assert out["answered_by"] == core.SOL_MODEL and out["fallback"] == reason and out["model"] == core.MODEL
    assert out["reply"] == SOL_OK["output"][0]["content"][0]["text"] and fake.models()[-1] == core.SOL_MODEL
    sol = fake.requests[-1]
    assert sol["instructions"] == core.INSTRUCTIONS and sol["tools"] == core.TOOL_SPECS  # same prompt and tools
    assert all(i.get("type") != "message" and i.get("content") != core.CORRECTION for i in sol["input"])
    # next turn starts on the Meta model again
    assert core.run_turn("hi", ByModel(meta=[say("Hello, ask me about the lab.")], sol=[SOL_OK])).get("answered_by") is None


def test_fallback_keeps_the_number_guard():
    out = core.run_turn("what is g?", ByModel(meta=[say("g is 9.81.")], sol=[say("g is 9.7.")]))
    assert out["answered_by"] == core.SOL_MODEL and out["stopped"] == "unbacked_numbers" and "9.7" not in out["reply"]


def test_fallback_carries_tool_results_instead_of_rerunning_them():
    runs = []
    fake = ByModel(meta=[call("lab_add_object", {"kind": "ball", "params": {"height_m": 1}}), core.ModelUnavailable("HTTP 503")],
                   sol=[SOL_OK])
    out = core.run_turn("add a ball", fake, handlers={"lab_add_object": lambda o, a: runs.append(a) or {"status": "ok", "id": "b1"}})
    assert out["answered_by"] == core.SOL_MODEL and len(runs) == 1
    carried = fake.requests[-1]["input"]
    assert [i.get("type") for i in carried[-2:]] == ["function_call", "function_call_output"]
    assert set(carried[-2]) == {"type", "call_id", "name", "arguments"}  # Meta item ids are not forwarded


@pytest.mark.parametrize("meta", [[say("I can only help with this physics lab. Want to drop a ball instead?")],
                                  [call("ask_user", {"question": "Which object?", "options": [
                                      {"label": "Ball", "recommended": True}, {"label": "Block", "recommended": False}]})]])
def test_no_fallback_for_refusals_or_questions(meta):
    fake = ByModel(meta=meta, sol=[SOL_OK])
    out = core.run_turn("write me a poem", fake)
    assert "answered_by" not in out and core.SOL_MODEL not in fake.models()


@pytest.mark.parametrize("exc", [daily_cap.CapExceeded("daily cap"), core.QuotaLimited("HTTP 429"), core.QuotaLimited("HTTP 402")])
def test_no_fallback_for_cap_or_quota(exc):
    fake = ByModel(meta=[exc], sol=[SOL_OK])
    with pytest.raises(type(exc)):
        core.run_turn("measure g", fake)
    assert fake.models() == [core.MODEL]


@pytest.mark.parametrize("text, tier", [("", "spark"), ("x" * 4001, "spark"), ("hi", "sol"), ("hi", core.SOL_MODEL)])
def test_no_fallback_for_bad_input_and_sol_is_not_selectable(text, tier):
    fake = ByModel(meta=[say("ok")], sol=[SOL_OK])
    with pytest.raises(ValueError):
        core.run_turn(text, fake, tier=tier)
    assert fake.requests == []


def test_sol_failure_keeps_the_meta_outcome():
    out = core.run_turn("g?", ByModel(meta=[say("g is 9.81.")], sol=[core.ModelUnavailable("HTTP 500")]))
    assert out["stopped"] == "unbacked_numbers" and "answered_by" not in out
    with pytest.raises(core.ModelUnavailable, match="HTTP 502"):
        core.run_turn("g?", ByModel(meta=[core.ModelUnavailable("HTTP 502")], sol=[daily_cap.CapExceeded("sol cap")]))


def test_tier_routing():
    for kwargs, model in (({}, core.MODEL), ({"tier": "open"}, core.OPEN_MODEL), ({"contributor": True}, core.CONTRIBUTOR_MODEL),
                          ({"contributor": True, "tier": "open"}, core.CONTRIBUTOR_MODEL)):
        fake = ByModel(meta=[say("ok")], sol=[SOL_OK])
        assert core.run_turn("hi", fake, **kwargs)["model"] == model and fake.models() == [model]
    assert core.SOL_MODEL not in core.TIERS.values()


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("R2S_DATA_DIR", str(tmp_path))
    for k in ("MERGE_API_KEY", "MERGE_BASE_URL", "BASETEN_API_KEY", "BASETEN_BASE_URL", "MODEL_API_KEY"):
        monkeypatch.setenv(k, "test-" + k.lower())
    sent = []
    monkeypatch.setattr(core, "_send", lambda path, data, ct, t, key_env="MODEL_API_KEY", base_env="MODEL_API_BASE_URL":
                        sent.append((path, json.loads(data), key_env, base_env)) or (
                            {"choices": [{"message": {"content": "ok"}}], "usage": {"prompt_tokens": 100, "completion_tokens": 10}}
                            if path == "/chat/completions" else {"output": [], "usage": {"input_tokens": 100, "output_tokens": 10}}))
    return tmp_path, sent


def rows(tmp_path):
    with sqlite3.connect(tmp_path / "spend.sqlite3") as con:
        return con.execute("SELECT provider, label, actual FROM spend ORDER BY reserved_at").fetchall()


def test_gateway_routing_and_ledger(env):
    tmp_path, sent = env
    body = {"model": core.SOL_MODEL, "instructions": "x", "input": [{"role": "user", "content": "hi"}], "tools": [],
            "max_output_tokens": 100}
    core.http_post(body)
    out = core.http_post({**body, "model": core.OPEN_MODEL})
    core.http_post({**body, "model": core.MODEL})
    assert [(p, k, b) for p, _, k, b in sent] == [("/responses", "MERGE_API_KEY", "MERGE_BASE_URL"),
                                                  ("/chat/completions", "BASETEN_API_KEY", "BASETEN_BASE_URL"),
                                                  ("/responses", "MODEL_API_KEY", "MODEL_API_BASE_URL")]
    assert sent[1][1]["messages"][0] == {"role": "system", "content": "x"} and sent[1][1]["max_tokens"] == 100
    assert out == {"output": [{"type": "message", "content": [{"type": "output_text", "text": "ok"}]}],
                   "usage": {"input_tokens": 100, "output_tokens": 10}}
    got = rows(tmp_path)
    assert [r[0] for r in got] == ["Merge", "Baseten", "Meta Model API"]
    assert got[0][2] == daily_cap._units(100 * 2.1e-6 + 10 * 10.5e-6) and got[1][2] == daily_cap._units(100 * 1.25e-6 + 10 * 4.25e-6)


def test_sol_cap_stops_at_two_dollars(env):
    tmp_path, sent = env
    core._reserve("Merge", 1.99, "earlier Sol turns")
    body = {"model": core.SOL_MODEL, "instructions": "x", "input": [], "tools": [], "max_output_tokens": 1000}
    with pytest.raises(daily_cap.CapExceeded):  # estimate > 0.0105 > 0.01 Sol headroom; global headroom is ample
        core.http_post(body)
    assert sent == [] and sum(r[2] or 0 for r in rows(tmp_path) if r[0] == "Merge") <= daily_cap._units(2)
    core.http_post({**body, "model": core.MODEL})  # Meta still runs: the Sol cap is separate
    # and the fallback then keeps the Meta outcome instead of calling Sol
    out = core.run_turn("g?", lambda b: say("g is 9.81.") if b["model"] != core.SOL_MODEL else core.http_post(b))
    assert out["stopped"] == "unbacked_numbers" and "answered_by" not in out


def test_global_cap_also_applies_to_gateways(env):
    core._reserve("Modal", 9.999, "GPU")
    with pytest.raises(daily_cap.CapExceeded):
        core.http_post({"model": core.OPEN_MODEL, "instructions": "x", "input": [], "tools": [], "max_output_tokens": 1000})


def test_meta_proxy_token_never_sent_to_gateways(monkeypatch):
    seen = {}
    class R:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return b"{}"
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: seen.update(dict(req.header_items())) or R())
    monkeypatch.setenv("MODEL_PROXY_TOKEN", "proxy-secret")
    monkeypatch.setenv("MERGE_API_KEY", "k")
    monkeypatch.setenv("MERGE_BASE_URL", "https://gateway.invalid/v1")
    core._send("/responses", b"{}", "application/json", 5, "MERGE_API_KEY", "MERGE_BASE_URL")
    assert not any(k.lower() == "x-r2s-proxy" for k in seen)


def test_api_tier_field(monkeypatch):
    monkeypatch.setenv("WORKSPACE_INTERNAL_TOKEN", "t0k")
    fake = ByModel(meta=[say("ok")], sol=[SOL_OK])
    app = FastAPI()
    app.include_router(create_router(post=fake, handlers={}))
    c = TestClient(app)
    h = {"x-workspace-token": "t0k", "x-workspace-owner": "u1"}
    assert c.post("/workspace/agent/turn", json={"text": "hi", "tier": "open"}, headers=h).json()["model"] == core.OPEN_MODEL
    assert c.post("/workspace/agent/turn", json={"text": "hi", "tier": "sol"}, headers=h).status_code == 422

