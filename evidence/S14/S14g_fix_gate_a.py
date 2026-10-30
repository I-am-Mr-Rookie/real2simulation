"""S14g-fix Gate A rerun (R-A F1-F4). Usage (repo root): python evidence/S14/S14g_fix_gate_a.py offline|live

- Cases are DISTINCT scene bundles with explicit case ids, never repeated to fake diversity. Gate A acceptance is
  9/10 valid specs on >=10 distinct RECORDED (non-synthetic) scenes; summary checks coverage before saying MET.
- Invented-claim counting uses the independent oracle (S14g_fix_oracle.py), not contracts.agent.numeric_issue,
  over every visible string: shown reply, question prompts, chip labels, candidate rationales.
- Provenance (F4): accepted (validated) responses, case/scene ids + scene hash, validated specs, exact trusted tool
  outputs + sha256. No keys, headers or private files. Interview answers are hand-written SYNTHETIC S14c answers.
Historical S14g evidence is untouched; outputs go to S14g-fix-*.json / S14g-fix-ledger.jsonl.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests/spec"), str(ROOT / "tests/agent"), str(HERE)]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


OLD = _load("s14g_gate_a", HERE / "S14g_gate_a.py")  # reuse helpers (simulator bridge, scripted replies)
from S14g_fix_oracle import oracle, self_check, visible  # noqa: E402
from Build.agent import muse, trial  # noqa: E402
from Build.agent.interview import answers_to_spec, questions, template_of  # noqa: E402
from Build.agent.record_muse import ENV, IN_USD, OUT_USD  # noqa: E402
from Build.agent.tools import quantity_text, safe_reply, scene_context  # noqa: E402
from contracts.agent.validate import AgentContractError  # noqa: E402
from test_interview import SYNTHETIC_ANSWERS  # noqa: E402
import test_setup_validation as tsv  # noqa: E402

RID, CAP_USD, META_STOP_USD = "S14g-fix-orch55", 3.00, 120.0 - 30.0  # run cap; $120 hard stop minus $30 reserve
SPECS_REQUIRED, SPEC_PASS, TURNS = 10, 9, 30
LEDGER = HERE / "S14g-fix-ledger.jsonl"
CASES = [  # every scene bundle found in the repo (rg scene.json, 2026-10-29): explicit ids, one case each
    ("room-v1-synthetic", ROOT / "test-data/synthetic/scene/room-v1",
     ["live-room-v1-a", "live-room-v1-b", "live-room-v1-c", "live-room-v1-d"]),  # recorded S14b replies, in order
    ("rm04-mapanything-s06d", ROOT / "evidence/S13/S13h/live/reconstruct/bundle", None),
]
CORPUS = json.loads((ROOT / "tests/agent/fixtures/adversarial-visible-text.json").read_text(encoding="utf-8"))["cases"]
sha = lambda obj: hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def visible_strings(response) -> list[str]:
    """Every user-visible text run of a validated response (cited quantities as a space)."""
    run = lambda segs: "".join(" " if s["type"] == "number" else s["text"] for s in segs)
    out = [run(response["segments"])]
    for q in response.get("questions", ()):
        out += [run(q["prompt"])] + [run(c["label"]) for c in q["chips"]]
    out += [run(c["rationale"]) for c in response.get("candidates", ())]
    return out


def base_spec(template, scene):
    if scene["synthetic"]:
        return tsv.setup(template)  # S14g's synthetic room setup (assumed gravity, synthetic test)
    spec = tsv.fixture(template)  # real scene: no gravity/collider fabrication
    spec["scene"].update(scene_id=scene["id"], scale_status=scene["scale"]["status"])
    if "bounds_m" in scene:
        spec["scene"]["constraints"]["bounds_m"] = scene["bounds_m"]
    return spec, scene


def spec_case(case_id, root, post) -> dict:
    scene = json.loads((root / "scene.json").read_text(encoding="utf-8"))
    row = {"case_id": case_id, "scene_id": scene.get("id"), "synthetic": scene.get("synthetic"),
           "scene_sha256": hashlib.sha256((root / "scene.json").read_bytes()).hexdigest(), "valid": False}
    try:
        context = scene_context(scene, root)
    except Exception as error:  # scene validator rejects the bundle: recorded, not hidden
        return dict(row, why=f"scene_context: {error}")
    post, seen = OLD.recording(post)
    response, rejected = muse.understand_with_retry(context, post)
    row.update(attempts=len(seen), rejected=rejected, model_number_attempts=OLD.model_numbers(seen),
               accepted_response=response, invented=[o for o in map(oracle, visible_strings(response)) if o])
    if not response.get("candidates"):
        return dict(row, why="no candidate -> ask_user")
    template = template_of(response, response["candidates"][0]["id"])
    asked = [q["id"] for q in questions(context["scene_id"], template)["questions"]]
    answers = {k: v for k, v in SYNTHETIC_ANSWERS[template].items() if k in asked}
    try:
        spec, scn = base_spec(template, scene)
        built = answers_to_spec(spec, scn, tsv.BUNDLE if scene["synthetic"] else root, answers)
        return dict(row, valid=True, template=template, answers=answers, spec=built)
    except (AgentContractError, KeyError, ValueError) as error:
        return dict(row, template=template, answers=answers, why=getattr(error, "issues", None) or str(error))


def turn(i, post, scene_id) -> dict:
    template, mystery = [("free_fall", False), ("projectile", False), ("free_fall", True), ("projectile", True)][i % 4]
    start = OLD.BRIDGE.handle({"action": "start", "template": template, "mystery": mystery})  # actual simulator
    fit = OLD.BRIDGE.handle({"action": "fit", "observations": start["observations"]})  # actual fitter
    outputs = trial.trial_outputs(f"gate-a-t{i:02d}", start, fit)
    post, seen = OLD.recording(post)
    response, rejected = trial.check_trial(trial.trial_context(scene_id, f"gate-a-t{i:02d}", start, outputs), post)
    shown, blocked = safe_reply(response, outputs, scene_id)
    rendered = [quantity_text(q) for o in outputs for q in o["quantities"].values()]
    return {"case_id": f"turn-{i:02d}", "scene_id": scene_id, "template": template, "mystery": mystery,
            "attempts": len(seen), "model_reply_shown": not blocked and not response["segments"][0]["text"]
            .startswith("The automatic trial check"), "model_number_attempts": OLD.model_numbers(seen),
            "rejected": rejected, "blocked": blocked, "invented": oracle(visible(shown, rendered)), "shown": shown,
            "accepted_response": response, "tool_outputs": outputs, "tool_outputs_sha256": sha(outputs)}


def adversarial_turns(scene_id) -> list[dict]:
    """Every invented corpus case as a 4x-repeated Spark reply through the real trial loop + display path."""
    rows = []
    for cid, parts, bad in CORPUS:
        if not bad:
            continue
        def post(_req, parts=parts):
            segs = [{"type": "number", "ref": {"tool_output_id": "gate-a-t00-fit", "quantity": "gravity"}} if p is None
                    else {"type": "text", "text": p} for p in parts + [None]]
            return OLD.body(json.dumps({"schema_version": "agent-response/1.0.0", "scene_id": scene_id,
                                        "segments": segs, "questions": []}))
        row = turn(0, post, scene_id)
        rows.append({"case_id": f"adv-{cid}", "attempts": row["attempts"], "model_reply_shown": row["model_reply_shown"],
                     "invented": row["invented"]})
    return rows


def offline() -> dict:
    fix = OLD.FIX
    specs = [spec_case(cid, root, (lambda it: lambda _r: (lambda f: {"status": f["status"], "output": f["output"]})(
                 fix[next(it)]))(iter(names)))
             if names else {"case_id": cid, "valid": False, "why": "no recorded Wonder reply for this scene (offline)"}
             for cid, root, names in CASES]
    turns = [turn(i, lambda _r, s=script: s.pop(0), OLD.SCENE_ID) for i, script in enumerate(OLD.synthetic_turns())]
    return {"specs": specs, "turns": turns, "adversarial": adversarial_turns(OLD.SCENE_ID)}


class Budget(Exception):
    pass


def _spent(path):
    return sum(json.loads(x).get("est_usd") or 0 for x in path.read_text(encoding="utf-8").splitlines()) if path.exists() else 0.0


def live_post(label: str):
    import httpx
    from dotenv import dotenv_values
    env = dotenv_values(ENV)

    def post(request: dict) -> dict:
        run = _spent(LEDGER)
        meta = run + sum(_spent(p) for p in HERE.glob("S14*ledger.jsonl") if p != LEDGER)
        worst = (len(json.dumps(request)) // 2) * IN_USD + request["max_output_tokens"] * OUT_USD
        if run + worst > CAP_USD or meta + worst > META_STOP_USD:
            raise Budget(f"cap: run {run:.4f} USD, recorded S14 Meta {meta:.4f} USD, next worst {worst:.4f} USD")
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
            fh.write(json.dumps({"utc": started, "rid": RID, "call": label, "provider": "Meta Model API",
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
        for cid, root, _ in CASES:
            specs.append(spec_case(cid, root, live_post(f"spec-{cid}")))
        for i in range(TURNS):
            turns.append(turn(i, live_post(f"turn-{i:02d}"), OLD.SCENE_ID))
    except (Budget, RuntimeError) as error:
        stop = str(error)
    return {"specs": specs, "turns": turns, "stopped": stop}


def summary(result: dict) -> dict:
    specs, turns, adv = result["specs"], result["turns"], result.get("adversarial", [])
    recorded = {s["scene_id"] for s in specs if s.get("synthetic") is False and "attempts" in s}
    valid_recorded = sum(s["valid"] for s in specs if s.get("synthetic") is False)
    invented_n = sum(t["invented"] is not None for t in turns + adv) + sum(bool(s.get("invented")) for s in specs)
    coverage_ok = len(recorded) >= SPECS_REQUIRED
    met = coverage_ok and valid_recorded >= SPEC_PASS and len(turns) == TURNS and invented_n == 0
    return {"distinct_recorded_scenes": len(recorded), "required_recorded_scenes": SPECS_REQUIRED,
            "spec_cases": {s["case_id"]: s["valid"] for s in specs}, "valid_recorded_specs": valid_recorded,
            "turns": len(turns), "adversarial_turns": len(adv), "invented_shown_oracle": invented_n,
            "model_replies_shown": sum(t["model_reply_shown"] for t in turns),
            "tool_only_fallbacks": sum(not t["model_reply_shown"] for t in turns),
            "model_number_attempts_caught": sum(t.get("model_number_attempts", 0) for t in turns + specs),
            "spark_calls": sum(t["attempts"] for t in turns), "wonder_calls": sum(s.get("attempts", 0) for s in specs),
            "oracle_self_check": self_check(), "stopped": result.get("stopped"),
            "gate_a": "MET" if met else "NOT_MET",
            "why": None if met else ("coverage: fewer than ten distinct recorded scenes" if not coverage_ok else "counts")}


if __name__ == "__main__":
    mode = sys.argv[1]
    result = offline() if mode == "offline" else live()
    result["summary"] = summary(result)
    (HERE / f"S14g-fix-{mode}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=1))

