"""Record live Muse Wonder scene-understanding replies as sanitized offline fixtures (S14b).

Usage: python -m Build.agent.record_muse <fixture-name> [scene-dir]
Key by NAME only (MODEL_API_KEY / MODEL_API_BASE_URL from the canonical .env); never printed or stored.
Budget guard: <=20 calls and <=$1 conservative total per the S14b contract, ledgered before and after.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx
from dotenv import dotenv_values

from Build.agent import muse
from Build.agent.tools import scene_context
from contracts.agent.validate import AgentContractError
from Build.guardrails.accounting import liability_usd, usd
from Build.guardrails.admission import ReconstructionPaused
from Build.guardrails.reservations import reserve_meta, project_ledger

ROOT = Path(__file__).parents[2]
ENV = Path(r"C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.env")
LEDGER = ROOT / "evidence" / "S14" / "S14b-ledger.jsonl"
FIXTURES = ROOT / "tests" / "agent" / "fixtures" / "muse"
MAX_CALLS, MAX_USD = 20, 1.0
# shortcut: concept-note list price for Wonder ($4 in / $20 out per Mtok, dev.meta.ai, Oct27) x1.5 margin;
# replace with billed usage once Meta billing is reconciled.
IN_USD, OUT_USD = 4e-6 * 1.5, 20e-6 * 1.5


def ledger() -> list[dict]:
    return [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines()] if LEDGER.exists() else []


def reserve(body: dict) -> float:
    """Worst-case USD for one call; refuse if it would break the call or dollar cap."""
    worst = (len(json.dumps(body)) // 2) * IN_USD + muse.MAX_OUTPUT_TOKENS * OUT_USD  # chars/2 over-counts tokens
    try:
        rows = project_ledger(LEDGER, str(LEDGER.resolve())) if LEDGER.exists() else []
        spent = sum(liability_usd(r) for r in rows)
    except (OSError, ValueError, KeyError, TypeError):
        raise SystemExit("SPEND_PAUSED: invalid Meta ledger") from None
    if len(rows) >= MAX_CALLS or spent + usd(worst) > usd(MAX_USD):
        raise SystemExit(f"SPEND_PAUSED: budget guard: {len(rows)} calls, ${spent:.4f} spent, next worst ${worst:.4f}")
    return worst


def main(name: str, scene_dir: str = "test-data/synthetic/scene/room-v1") -> None:
    root = ROOT / scene_dir
    context = scene_context(json.loads((root / "scene.json").read_text(encoding="utf-8")), root)
    body = muse.build_request(context)
    try:
        worst = reserve(body)
        request_id = reserve_meta(ROOT, LEDGER, "record_muse", uuid4().hex, worst,
                                  max_calls=MAX_CALLS, cap_usd=MAX_USD)
    except (ReconstructionPaused, OSError, ValueError, KeyError, TypeError):
        raise SystemExit("SPEND_PAUSED: Meta admission unavailable or budget paused") from None
    env = dotenv_values(ENV)
    started = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    try:
        r = httpx.post(env["MODEL_API_BASE_URL"].rstrip("/") + "/responses", json=body, timeout=120,
                       headers={"Authorization": "Bearer " + env["MODEL_API_KEY"]})
        reply = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    except httpx.HTTPError as exc:
        r, reply = None, {"error": type(exc).__name__}
    usage = reply.get("usage") or {}
    tin, tout = usage.get("input_tokens"), usage.get("output_tokens")
    est = tin * IN_USD + tout * OUT_USD if tin is not None and tout is not None else worst  # unknown usage -> keep worst case
    row = {"request_id": request_id, "stage": "record_muse", "utc": started, "rid": "S14b-orch16", "fixture": name, "provider": "Meta Model API",
           "model": reply.get("model", body["model"]), "http": r.status_code if r is not None else None,
           "input_tokens": tin, "output_tokens": tout,
           "reasoning_tokens": (usage.get("output_tokens_details") or {}).get("reasoning_tokens"),
           "reserved_usd": round(worst, 6), "est_usd": round(est, 6), "billed_usd": None}
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    fixture = {"provenance": f"RECORDED live Meta Model API {row['model']} {started} by S14b-orch16; sanitized "
                             "(response ids/headers dropped); input = synthetic scene context only",
               "scene_dir": scene_dir, "context": context, "http": row["http"], "status": reply.get("status"),
               "usage": {"input_tokens": tin, "output_tokens": tout},
               "error": reply.get("error"),
               "output": [{"type": i.get("type"), "content": [{"type": p.get("type"), "text": p.get("text")}
                                                              for p in i.get("content") or ()]}
                          for i in reply.get("output") or () if i.get("type") == "message"]}
    try:
        muse.understand(context, lambda _: {"status": fixture["status"], "output": fixture["output"]})
        fixture["expect"] = "valid"
    except AgentContractError as exc:
        fixture["expect"], fixture["issues"] = "rejected", list(exc.issues)
    FIXTURES.mkdir(parents=True, exist_ok=True)
    (FIXTURES / f"{name}.json").write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(name, row["http"], fixture["status"], fixture["expect"], fixture.get("issues", "")[:3] if fixture.get("issues") else "",
          f"in={tin} out={tout} est=${est:.4f}")


if __name__ == "__main__":
    main(*sys.argv[1:])
