"""Wonder admission, Dhaka boundaries and Spark fallbacks, all offline."""
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.agent import core
from Build.api.agent import create_router
from Build.guardrails import daily_cap as dc


def say(text="Ready for lab work."):
    return {"output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}],
            "usage": {"input_tokens": 100, "output_tokens": 10}}


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("R2S_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MODEL_API_KEY", "offline-test")
    return tmp_path


@pytest.mark.parametrize("utc, turns, cap", [
    ("2026-11-04T17:59:59+00:00", 10, 3),
    ("2026-11-04T18:00:00+00:00", 20, 6),
    ("2026-11-08T17:59:59+00:00", 20, 6),
    ("2026-11-08T18:00:00+00:00", 10, 3),
])
def test_dhaka_window_and_exact_turn_limit(env, monkeypatch, utc, turns, cap):
    day = dc.dhaka_day(datetime.fromisoformat(utc))
    assert core.wonder_limits(day) == (turns, cap)
    monkeypatch.setattr(dc, "dhaka_day", lambda now=None: day)
    assert all(core._claim_wonder_turn("user-one") for _ in range(turns))
    assert not core._claim_wonder_turn("user-one")
    assert core._claim_wonder_turn("user-two")


def test_admission_is_atomic_and_survives_day_reset(env, monkeypatch):
    monkeypatch.setattr(dc, "dhaka_day", lambda now=None: date(2026, 11, 3))
    with ThreadPoolExecutor(max_workers=12) as pool:
        admitted = list(pool.map(lambda _: core._claim_wonder_turn("same-user"), range(24)))
    assert sum(admitted) == 10
    with sqlite3.connect(dc.default_path()) as con:
        assert con.execute("SELECT turns FROM wonder_turns").fetchone() == (10,)
    monkeypatch.setattr(dc, "dhaka_day", lambda now=None: date(2026, 11, 4))
    assert core._claim_wonder_turn("same-user")


def test_user_limit_falls_back_to_standard_spark_with_notice(env):
    seen = []
    post = lambda body: seen.append(body["model"]) or say()
    for _ in range(10):
        out = core.run_turn("Help with the lab", post, tier="wonder", owner="u1")
        assert out["model"] == core.WONDER_MODEL and "notice" not in out
    out = core.run_turn("Help with the lab", post, tier="wonder", owner="u1")
    assert out["model"] == core.MODEL and out["notice"] == core.WONDER_LIMIT_NOTE
    assert seen == [core.WONDER_MODEL] * 10 + [core.MODEL]
    assert core.SOL_MODEL not in core.TIERS.values()
    assert core.run_turn("Help", post, tier="wonder", owner="u2")["model"] == core.WONDER_MODEL


def test_tool_steps_count_as_one_turn_and_contributor_does_not_count(env):
    replies = iter([
        {"output": [{"type": "function_call", "name": "list_files", "call_id": "c1", "arguments": "{}"}]},
        say(),
    ])
    core.run_turn("List my files", lambda _: next(replies), tier="wonder", owner="u1",
                  handlers={"list_files": lambda owner, args: {"files": []}})
    core.run_turn("Help", lambda _: say(), tier="wonder", contributor=True, owner="u1")
    with sqlite3.connect(dc.default_path()) as con:
        assert con.execute("SELECT owner, turns FROM wonder_turns").fetchall() == [("u1", 1)]


@pytest.mark.parametrize("day, cap", [(date(2026, 11, 4), 3), (date(2026, 11, 5), 6),
                                      (date(2026, 11, 8), 6), (date(2026, 11, 9), 3)])
def test_cap_reservation_falls_back_and_counts_only_wonder_meta_rows(env, monkeypatch, day, cap):
    monkeypatch.setattr(dc, "dhaka_day", lambda now=None: day)
    dc.reserve("Meta Model API", 1, core.MODEL)  # Spark spend must not use Wonder's own cap.
    core._reserve("Meta Model API", cap - 0.001, core.WONDER_MODEL)
    sent = []

    def send(path, data, *args):
        sent.append(json.loads(data)["model"])
        return say()

    monkeypatch.setattr(core, "_send", send)
    out = core.run_turn("Help with the lab", core.http_post, tier="wonder", owner="u1")
    assert out["model"] == core.MODEL and out["notice"] == core.WONDER_LIMIT_NOTE
    assert sent == [core.MODEL]  # reservation denied before any Wonder network call
    with sqlite3.connect(dc.default_path()) as con:
        assert con.execute("SELECT COUNT(*) FROM spend WHERE label = ?", (core.WONDER_MODEL,)).fetchone() == (1,)


def test_wonder_reservation_is_atomic_separate_and_settles_actual_usage(env, monkeypatch):
    monkeypatch.setattr(dc, "dhaka_day", lambda now=None: date(2026, 11, 3))
    dc.reserve("Meta Model API", 4, core.MODEL)
    dc.reserve("Modal", 1, "GPU")
    # Neither existing Meta spend nor GPU spend exhausts Wonder's model-only allowance.
    rid = core._reserve("Meta Model API", 2.9, core.WONDER_MODEL)
    with pytest.raises(dc.CapExceeded):
        core._reserve("Meta Model API", 0.11, core.WONDER_MODEL)
    dc.settle(rid, 0.01)
    sent = []

    def send(path, data, *args):
        with sqlite3.connect(dc.default_path()) as con:
            assert con.execute("SELECT COUNT(*) FROM spend WHERE label = ? AND actual IS NULL",
                               (core.WONDER_MODEL,)).fetchone() == (1,)
        sent.append(json.loads(data)["reasoning"])
        return say()

    monkeypatch.setattr(core, "_send", send)
    core.run_turn("Help with the lab", core.http_post, tier="wonder", owner="u1")
    assert sent == [{"effort": "high"}]
    with sqlite3.connect(dc.default_path()) as con:
        rows = con.execute("SELECT provider, actual FROM spend WHERE label = ? ORDER BY reserved_at",
                           (core.WONDER_MODEL,)).fetchall()
    assert rows == [("Meta Model API", dc._units(0.01)), ("Meta Model API", dc._units(0.0006))]


def test_prefixed_benchmark_spend_also_counts_towards_wonder_cap(env, monkeypatch):
    monkeypatch.setattr(dc, "dhaka_day", lambda now=None: date(2026, 11, 3))
    dc.reserve("Meta Model API", 2.99, "N70 case " + core.WONDER_MODEL)
    with pytest.raises(dc.CapExceeded):
        core._reserve("Meta Model API", 0.02, core.WONDER_MODEL)


def test_concurrent_wonder_spend_reservations_cannot_overrun_cap(env, monkeypatch):
    monkeypatch.setattr(dc, "dhaka_day", lambda now=None: date(2026, 11, 3))

    def reserve(_):
        try:
            core._reserve("Meta Model API", 0.6, core.WONDER_MODEL)
            return True
        except dc.CapExceeded:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(reserve, range(16))) == 5
    assert dc.today()["spent_usd"] == 3


def test_mid_turn_cap_fallback_carries_tools_without_repeating_them(env):
    seen, tools = [], []

    def post(body):
        seen.append(body["model"])
        if len(seen) == 1:
            return {"output": [{"type": "function_call", "name": "list_files", "call_id": "c1", "arguments": "{}"}]}
        if body["model"] == core.WONDER_MODEL:
            raise dc.CapExceeded("Wonder cap")
        assert any(i.get("type") == "function_call_output" for i in body["input"])
        return say()

    out = core.run_turn("List files", post, tier="wonder", owner="u1",
                        handlers={"list_files": lambda o, a: tools.append(o) or {"files": []}})
    assert seen == [core.WONDER_MODEL, core.WONDER_MODEL, core.MODEL] and tools == ["u1"]
    assert out["notice"] == core.WONDER_LIMIT_NOTE and out["tool_calls"][0]["name"] == "list_files"


def test_spark_failure_after_wonder_cap_preserves_tools_for_unchanged_sol_fallback(env):
    seen, tools = [], []

    def post(body):
        seen.append(body["model"])
        if body["model"] == core.WONDER_MODEL:
            raise dc.CapExceeded("Wonder cap")
        if body["model"] == core.MODEL:
            if seen.count(core.MODEL) == 1:
                return {"output": [{"type": "function_call", "name": "list_files", "call_id": "c1", "arguments": "{}"}]}
            raise core.ModelUnavailable("Spark unavailable")
        assert body["model"] == core.SOL_MODEL
        assert any(i.get("type") == "function_call_output" for i in body["input"])
        return say()

    out = core.run_turn("List files", post, tier="wonder", owner="u1",
                        handlers={"list_files": lambda o, a: tools.append(o) or {"files": []}})
    assert seen == [core.WONDER_MODEL, core.MODEL, core.MODEL, core.SOL_MODEL] and tools == ["u1"]
    assert out["answered_by"] == core.SOL_MODEL and out["notice"] == core.WONDER_LIMIT_NOTE


def test_api_uses_authenticated_owner_and_allows_wonder_but_not_sol(env, monkeypatch):
    monkeypatch.setenv("WORKSPACE_INTERNAL_TOKEN", "test-internal")
    app = FastAPI()
    app.include_router(create_router(post=lambda _: say()))
    client = TestClient(app)
    headers = {"x-workspace-token": "test-internal", "x-workspace-owner": "u1"}
    assert client.post("/workspace/agent/turn", json={"text": "Help", "tier": "wonder"}).status_code == 401
    assert client.post("/workspace/agent/turn", headers=headers,
                       json={"text": "Help", "tier": "wonder"}).json()["model"] == core.WONDER_MODEL
    for tier in ("sol", core.SOL_MODEL):
        assert client.post("/workspace/agent/turn", headers=headers,
                           json={"text": "Help", "tier": tier}).status_code == 422
    with sqlite3.connect(dc.default_path()) as con:
        assert con.execute("SELECT owner, turns FROM wonder_turns").fetchall() == [("u1", 1)]
