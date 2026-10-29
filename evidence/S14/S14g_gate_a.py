"""S14g Gate A: ten understand -> interview -> spec cases and thirty Spark trial-check turns.

Usage (from the repo root): python evidence/S14/S14g_gate_a.py offline|live
- valid spec: understand_with_retry offers a candidate; its template's interview questions are answered with the
  hand-written SYNTHETIC S14c answers; answers_to_spec passes the S08 validator.
- invented numeric claim: any numeric character/number word left in the SHOWN reply text after removing the
  rendered tool-output quantities (independent scan of the displayed string, not the validator's verdict).
offline replays RECORDED S14b Muse fixtures and SYNTHETIC Spark replies (incl. invented numbers);
live calls Meta (Wonder for understanding, Spark for trial checks) on the SYNTHETIC room-v1 scene and S10
simulator/fitter outputs, with a per-call ledger and a hard dollar cap.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests/spec"), str(ROOT / "tests/agent")]
from Build.agent import muse, trial  # noqa: E402
from Build.agent.interview import answers_to_spec, questions, template_of  # noqa: E402
from Build.agent.record_muse import ENV, IN_USD, OUT_USD  # noqa: E402
from Build.agent.tools import quantity_text, safe_reply  # noqa: E402
from contracts.agent.validate import AgentContractError, numeric_issue  # noqa: E402
from test_interview import SYNTHETIC_ANSWERS  # noqa: E402
from test_setup_validation import BUNDLE, setup  # noqa: E402

SPECS, TURNS, SPEC_PASS = 10, 30, 9
CAP_USD = 3.00  # S14g contract cap for this run's Meta spend (estimated, list price x1.5)
LEDGER = ROOT / "evidence/S14/S14g-ledger.jsonl"
FIX = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "tests/agent/fixtures/muse").glob("*.json")}
CONTEXT = FIX["live-room-v1-d"]["context"]  # tools.scene_context of SYNTHETIC room-v1 (number-free)
SCENE_ID = CONTEXT["scene_id"]
_spec = importlib.util.spec_from_file_location("s10_session_bridge", ROOT / "Build/lab/session-bridge.py")
BRIDGE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BRIDGE)


def invented(shown: str, outputs) -> str | None:
    rest = shown
    for output in outputs:
        for q in output["quantities"].values():
            rest = rest.replace(quantity_text(q), " ")
    return numeric_issue(rest)


def texts(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from [v] if k == "text" and isinstance(v, str) else texts(v)
    elif isinstance(node, list):
        for v in node:
            yield from texts(v)


def model_numbers(bodies) -> int:
    """Model replies (before any guard) whose text fields state a number - the attempts the guard must catch."""
    n = 0
    for b in bodies:
        try:
            reply = json.loads(muse.output_text(b))
        except (AgentContractError, ValueError):
            continue
        n += any(numeric_issue(t) for t in texts(reply))
    return n


def recording(post):
    seen = []
    def wrapped(request):
        seen.append(post(request))
        return seen[-1]
    return wrapped, seen


def spec_case(post) -> dict:
    post, seen = recording(post)
    response, rejected = muse.understand_with_retry(CONTEXT, post)
    row = {"attempts": len(seen), "rejected": rejected, "model_number_attempts": model_numbers(seen)}
    if not response.get("candidates"):
        return dict(row, valid=False, why="no candidate -> ask_user")
    template = template_of(response, response["candidates"][0]["id"])
    asked = [q["id"] for q in questions(SCENE_ID, template)["questions"]]
    answers = {k: v for k, v in SYNTHETIC_ANSWERS[template].items() if k in asked}
    try:
        answers_to_spec(*setup(template), BUNDLE, answers)
        return dict(row, valid=True, template=template)
    except AgentContractError as error:
        return dict(row, valid=False, template=template, why=list(error.issues))


def turn(i: int, post) -> dict:
    template, mystery = [("free_fall", False), ("projectile", False), ("free_fall", True), ("projectile", True)][i % 4]
    start = BRIDGE.handle({"action": "start", "template": template, "mystery": mystery})  # actual simulator
    fit = BRIDGE.handle({"action": "fit", "observations": start["observations"]})  # actual fitter
    outputs = trial.trial_outputs(f"gate-a-t{i:02d}", start, fit)
    post, seen = recording(post)
    response, rejected = trial.check_trial(trial.trial_context(SCENE_ID, f"gate-a-t{i:02d}", start, outputs), post)
    shown, blocked = safe_reply(response, outputs, SCENE_ID)
    return {"turn": i, "template": template, "mystery": mystery, "attempts": len(seen),
            "model_reply_shown": not response["segments"][0]["text"].startswith("The automatic trial check"),
            "model_number_attempts": model_numbers(seen),
            "rejected": rejected, "blocked": blocked, "invented": invented(shown, outputs), "shown": shown}


# ---- offline: recorded / SYNTHETIC replies -------------------------------------------------------------
def body(text: str) -> dict:
    return {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}]}


def synthetic_turns():
    """SYNTHETIC Spark replies: per turn a scripted sequence; bad ones state numbers in text."""
    def reply(i, *segs):
        return body(json.dumps({"schema_version": "agent-response/1.0.0", "scene_id": SCENE_ID, "questions": [],
                                "segments": [s if isinstance(s, dict) else {"type": "text", "text": s} for s in segs]}))
    num = lambda i, out, q: {"type": "number", "ref": {"tool_output_id": f"gate-a-t{i:02d}-{out}", "quantity": q}}
    good = lambda i: reply(i, "Simulated check: the fitter gives gravity ", num(i, "fit", "gravity"),
                           ", consistent with the run; simulated, not physical evidence.")
    bad = [lambda i: reply(i, "Gravity is about 9.81 here."), lambda i: reply(i, "Gravity is nine point eight."),
           lambda i: reply(i, "Roughly twice the drop.", num(i, "sim", "drop")), lambda i: reply(i, "No values cited.")]
    for i in range(TURNS):
        k = i % 5  # 0: good first try; 1-3: bad then good; 4: four bad -> tool_only fallback
        yield [good(i)] if k == 0 else [bad[k - 1](i), good(i)] if k < 4 else [b(i) for b in bad]


def offline() -> dict:
    order = ["live-room-v1-a", "live-room-v1-b", "live-room-v1-c", "live-room-v1-d"]
    specs = []
    for i in range(SPECS):
        replay = itertools.cycle(FIX[n] for n in order[i % 4:] + order[:i % 4])
        specs.append(spec_case(lambda _req: (lambda f: {"status": f["status"], "output": f["output"]})(next(replay))))
    turns = []
    for i, script in enumerate(synthetic_turns()):
        turns.append(turn(i, lambda _req, s=script: s.pop(0)))
    out = turns[0]["shown"]  # self-check: the detector sees a planted number and clears rendered quantities
    assert invented(out + " about 9.81", []) and invented(out, []) and invented("one point five", []), "detector"
    return {"specs": specs, "turns": turns}


# ---- live: Meta Model API, per-call ledger, hard cap ----------------------------------------------------
class Budget(Exception):
    pass


def live_post(label: str):
    import httpx
    from dotenv import dotenv_values
    env = dotenv_values(ENV)

    def post(request: dict) -> dict:
        rows = [json.loads(x) for x in LEDGER.read_text(encoding="utf-8").splitlines()] if LEDGER.exists() else []
        spent = sum(r["est_usd"] for r in rows)
        worst = (len(json.dumps(request)) // 2) * IN_USD + request["max_output_tokens"] * OUT_USD
        if spent + worst > CAP_USD:
            raise Budget(f"cap: {len(rows)} calls, ${spent:.4f} spent, next worst ${worst:.4f}")
        started = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        try:
            r = httpx.post(env["MODEL_API_BASE_URL"].rstrip("/") + "/responses", json=request, timeout=120,
                           headers={"Authorization": "Bearer " + env["MODEL_API_KEY"]})
            reply = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        except httpx.HTTPError as exc:
            r, reply = None, {"error": type(exc).__name__}
        usage = reply.get("usage") or {}
        tin, tout = usage.get("input_tokens"), usage.get("output_tokens")
        est = tin * IN_USD + tout * OUT_USD if tin is not None and tout is not None else worst
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"utc": started, "rid": "S14g-orch47", "call": label, "provider": "Meta Model API",
                                 "model": reply.get("model", request["model"]), "http": r.status_code if r is not None else None,
                                 "input_tokens": tin, "output_tokens": tout, "reserved_usd": round(worst, 6),
                                 "est_usd": round(est, 6), "billed_usd": None}) + "\n")
        if r is None or r.status_code != 200:
            raise RuntimeError(f"transport: http {r.status_code if r is not None else None} {reply.get('error')}")
        return reply
    return post


def live() -> dict:
    specs, turns, stop = [], [], None
    try:
        for i in range(SPECS):
            specs.append(spec_case(live_post(f"spec-{i:02d}")))
        for i in range(TURNS):
            turns.append(turn(i, live_post(f"turn-{i:02d}")))
    except (Budget, RuntimeError) as error:
        stop = str(error)
    return {"specs": specs, "turns": turns, "stopped": stop}


def summary(result: dict) -> dict:
    specs, turns = result["specs"], result["turns"]
    valid = sum(s["valid"] for s in specs)
    invented_n = sum(t["invented"] is not None for t in turns)
    met = len(specs) == SPECS and len(turns) == TURNS and valid >= SPEC_PASS and invented_n == 0
    return {"valid_specs": f"{valid}/{len(specs)}", "turns": len(turns), "invented_shown": invented_n,
            "model_replies_shown": sum(t["model_reply_shown"] for t in turns),
            "tool_only_fallbacks": sum(not t["model_reply_shown"] for t in turns),
            "model_number_attempts_caught": sum(t["model_number_attempts"] for t in turns + specs),
            "spark_calls": sum(t["attempts"] for t in turns), "wonder_calls": sum(s["attempts"] for s in specs),
            "stopped": result.get("stopped"), "gate_a": "MET" if met else "NOT_MET"}


if __name__ == "__main__":
    mode = sys.argv[1]
    result = offline() if mode == "offline" else live()
    result["summary"] = summary(result)
    out = ROOT / f"evidence/S14/S14g-{mode}.json"
    out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=1))

