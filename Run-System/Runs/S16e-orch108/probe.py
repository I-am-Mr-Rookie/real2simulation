"""One-shot live adapter verification; emits only allowlisted evidence, never secrets."""
from datetime import datetime, timezone
from importlib import import_module
import json
from pathlib import Path
import sys
from time import monotonic
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
s = import_module("Build.sidebar-tools.library_search")
OUT = ROOT / "evidence/S16/S16e-orch108-live.json"


def main():
    assert len(sys.argv) == 3 and sys.argv[1] == "--env-file"
    env = {}
    for line in Path(sys.argv[2]).read_text(encoding="utf-8-sig").splitlines():
        key, sep, value = line.strip().removeprefix("export ").partition("=")
        if sep and key.strip() in {"BASETEN_API_KEY", "BASETEN_MODEL", "BASETEN_BASE_URL"}:
            env[key.strip()] = value.strip().strip("\"'")
    assert set(env) == {"BASETEN_API_KEY", "BASETEN_MODEL", "BASETEN_BASE_URL"}
    assert all(env.values())
    assert env["BASETEN_MODEL"] == s.MODEL_ID, "Pinned model configuration mismatch"
    assert env["BASETEN_BASE_URL"].rstrip("/") == s.BASE_URL, "Endpoint configuration mismatch"
    call = {"schema_version": s.contracts.VERSION, "id": "s16e_orch108_live",
            "scene_id": "dev_library", "tool": "library.search",
            "arguments": {"query": "Find a simulated free-fall experiment for the virtual lab",
                          "limit": 2, "templates": ["free_fall"], "licenses": []}}
    # A durable exclusive reservation prevents rerunning this probe from spending again.
    OUT.parent.mkdir(parents=True, exist_ok=True)
    evidence = {"run_id": "S16e-orch108", "model_id": s.MODEL_ID,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "credit": "owner-confirmed organizer-issued $100; restricted model credit",
                "balance": "unobservable", "request_count": 0,
                "cost_usd": None, "cost_basis": "unknown; no verified published pricing",
                "scope": "local dev adapter with real hosted inference; not deployed web routing",
                "status": "reserved"}
    with OUT.open("x", encoding="utf-8") as file:
        json.dump(evidence, file, indent=2)

    def send(request, *, timeout):
        assert evidence["request_count"] == 0, "No retries authorized by this probe"
        body = json.loads(request.data)
        assert body["model"] == s.MODEL_ID and body["max_tokens"] <= 2048
        assert request.full_url == s.BASE_URL + "/chat/completions"
        evidence.update(request_count=1, max_tokens=body["max_tokens"])
        started = monotonic()
        try:
            raw = s.transport(request, timeout=timeout)
            evidence["http_status"] = 200
            response = json.loads(raw)
            evidence["response_model_matches_pin"] = response.get("model") == s.MODEL_ID
            usage = response.get("usage", {})
            evidence["usage_measured"] = {key: usage[key] for key in
                ("prompt_tokens", "completion_tokens", "total_tokens")
                if isinstance(usage.get(key), int) and not isinstance(usage[key], bool)}
            if response.get("choices"):
                reason = response["choices"][0].get("finish_reason")
                evidence["finish_reason"] = reason if reason in {"stop", "length", "tool_calls", "content_filter"} else "other"
            return raw
        except HTTPError as error:
            evidence["http_status"] = error.code
            raise
        finally:
            evidence["latency_seconds_measured"] = round(monotonic() - started, 6)

    try:
        result = s.search(call, environ=env, send=send)
        s.contracts.validate_result(result, call)
        evidence["result"] = result
        evidence["status"] = "usable" if result["status"] == "ok" and result["payload"]["items"] else "unavailable"
        if evidence["status"] == "usable":
            items = result["payload"]["items"]
            catalogue = {item["id"]: item for item in s._catalogue(ROOT / "test-data/library-artifacts/free-fall.json", ROOT)}
            assert all(item == catalogue[item["id"]] for item in items)
            evidence["ranked_ids"] = [item["id"] for item in items]
            evidence["validated_card_mapping"] = True
    finally:
        evidence["completed_at"] = datetime.now(timezone.utc).isoformat()
        OUT.write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({key: evidence.get(key) for key in
                     ("status", "request_count", "http_status", "latency_seconds_measured", "usage_measured", "ranked_ids")}))


if __name__ == "__main__":
    main()
