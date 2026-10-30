"""Reproduce S16f evidence with fake responses; never invoke a provider transport."""
from datetime import datetime, timezone
from importlib import import_module
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
s = import_module("Build.sidebar-tools.library_search")
MODEL = "accounts/fireworks/models/synthetic-ranker"
ENV = {"BASETEN_API_KEY": "synthetic-offline-only", "BASETEN_BASE_URL": s.BASE_URL,
       "BASETEN_MODEL": s.MODEL_ID, "FIREWORKS_API_KEY": "synthetic-offline-only",
       "FIREWORKS_BASE_URL": s.FIREWORKS_BASE_URL, "FIREWORKS_MODEL": MODEL}


def check(provider, *, fail=False, empty=False):
    call = {"schema_version": s.contracts.VERSION, "id": "offline_search", "scene_id": "offline_scene",
            "tool": "library.search", "arguments": {"query": "synthetic free fall", "limit": 2,
                "templates": ["pendulum"] if empty else [], "licenses": []}}
    attempts = []

    def fake_send(request, *, timeout):
        body = json.loads(request.data)
        attempts.append({"endpoint": request.full_url, "model": body["model"], "timeout": timeout})
        assert request.get_header("Authorization") == "Bearer synthetic-offline-only"
        assert not body["stream"] and body["max_tokens"] == 2048
        if fail:
            raise TimeoutError("synthetic transport failure")
        candidates = json.loads(body["messages"][1]["content"])["candidates"]
        ids = [item["id"] for item in candidates[:2]]
        return json.dumps({"model": body["model"], "choices": [{"finish_reason": "stop",
            "message": {"content": json.dumps({"ids": ids})}}]}).encode()

    result = s.search(call, environ={**ENV, "SIDEBAR_SEARCH_PROVIDER": provider}, send=fake_send)
    assert len(attempts) == (0 if empty else 1)
    assert result["execution"] == {"provider": provider,
        "model": s.MODEL_ID if provider == "baseten" else MODEL,
        "state": "not_requested" if empty else "failed" if fail else "served",
        "meta_bonus_claimed": False}
    assert result["status"] == ("error" if fail else "ok")
    assert result["tool_outputs"] == []
    if not fail:
        assert len(result["payload"]["items"]) == (0 if empty else 2)
        for item in result["payload"]["items"]:
            assert item["synthetic"] and item["provenance"]["numeric_label"] == "synthetic"
            assert not item["scale_verified"] and item["availability"] == "metadata-only"
    if provider == "fireworks":
        assert "muse" not in json.dumps(result).lower()
    assert "synthetic-offline-only" not in json.dumps(result)
    return {"provider": provider, "synthetic_failure": fail, "empty_catalogue": empty,
            "fake_attempts": attempts, "result": result}


if __name__ == "__main__":
    cases = [check(provider, fail=fail) for provider in ("baseten", "fireworks") for fail in (False, True)]
    cases.append(check("fireworks", empty=True))
    proof = {"run": "S16f-orch111", "created_at": datetime.now(timezone.utc).isoformat(),
             "mode": "OFFLINE_SYNTHETIC_FAKE_TRANSPORT", "live_requests": 0,
             "inference_spend_usd": 0, "fireworks_model_availability_verified": False,
             "bonus_claimed": False, "cases": cases}
    output = ROOT / "evidence/S16/S16f-orch111-offline.json"
    output.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print("PASS: 5 synthetic cases; 4 fake requests, zero live requests/spend; " + str(output))
