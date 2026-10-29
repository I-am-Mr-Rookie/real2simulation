"""Read-only Gate A review probes. No live provider, source mutation or original evidence writes."""
import copy
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.agent.tools import safe_reply, quantity_text, BLOCKED
from contracts.agent.validate import AgentContractError, validate_response, numeric_issue

spec = importlib.util.spec_from_file_location("gate_a_reviewed", ROOT / "evidence/S14/S14g_gate_a.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def no_live(*args, **kwargs):
    raise AssertionError("Live provider calls forbidden in R-A")


gate.live_post = no_live
original = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "evidence/S14").glob("*") if p.is_file()}
start = gate.BRIDGE.handle({"action": "start", "template": "free_fall"})
fit = gate.BRIDGE.handle({"action": "fit", "observations": start["observations"]})
outputs = gate.trial.trial_outputs("ra-review", start, fit)
ref = {"type": "number", "ref": {"tool_output_id": "ra-review-fit", "quantity": "gravity"}}
text = lambda value: {"type": "text", "text": value}


def response(parts, questions=None):
    return {"schema_version": "agent-response/1.0.0", "scene_id": gate.SCENE_ID,
            "segments": parts, "questions": questions or []}


rows = []
phrases = ["Gravity is one metre per second squared.", "Gravity is double the fitted value.",
           "Distance is a couple of metres.", "Gravity is nine point eight.", "Distance is two to three metres.",
           "Distance is 2-3 m.", "Gravity is twice the fitted value.", "Distance is half a metre.",
           "Gravity is ٩٫٨.", "Distance is ½ metre.", "Gravity is Ⅸ.", "Gravity is 三.",
           "Gravity is 9.81 m/s².", "Gravity is nine\u200bpoint\u200beight."]
for phrase in phrases:
    shown, blocked = safe_reply(response([text(phrase), ref]), outputs, gate.SCENE_ID)
    rows.append({"input": phrase, "blocked": bool(blocked), "shown": shown,
                 "gate_scan": gate.invented(shown, outputs)})
split = response([text("Gravity is ni"), text("ne point ei"), text("ght metres per second squared. "), ref])
shown, blocked = safe_reply(split, outputs, gate.SCENE_ID)
rows.append({"input": "split segments: ni + ne point ei + ght", "blocked": bool(blocked),
             "shown": shown, "gate_scan": gate.invented(shown, outputs)})
assert not rows[0]["blocked"] and rows[0]["gate_scan"] is None
assert not rows[1]["blocked"] and rows[1]["gate_scan"] is None
assert not rows[-1]["blocked"] and rows[-1]["gate_scan"] is not None
assert all(row["blocked"] for row in rows[3:13])

end_to_end = []
for i, parts in enumerate(([text(phrases[0])], [text(phrases[1])],
                           [text("Gravity is ni"), text("ne point ei"), text("ght metres per second squared.")])):
    cited = {"type": "number", "ref": {"tool_output_id": f"gate-a-t{i:02d}-fit", "quantity": "gravity"}}
    payload = gate.body(json.dumps(response([*parts, cited])))
    row = gate.turn(i, lambda _request, payload=payload: payload)
    assert row["attempts"] == 1 and not row["blocked"] and row["model_reply_shown"]
    assert (row["invented"] is None) == (i < 2)
    end_to_end.append(row)

unknown = response([text("Unknown citation "), {"type": "number", "ref": {
    "tool_output_id": "not-a-tool", "quantity": "gravity"}}])
fallback, issues = safe_reply(unknown, outputs, gate.SCENE_ID)
assert issues and fallback.startswith(BLOCKED) and gate.invented(fallback, outputs) is None
assert all(quantity_text(q) in fallback for out in outputs for q in out["quantities"].values())
empty, empty_issues = safe_reply(unknown, [], gate.SCENE_ID)
assert empty_issues and empty == BLOCKED + "."
try:
    safe_reply(unknown, [{**outputs[0], "status": "error"}], gate.SCENE_ID)
except AgentContractError:
    invalid_tools_raise = True
else:
    raise AssertionError("Invalid trusted tools must fail closed")

normalization = []
for kind in ("free_text", "chips", "chips_and_free_text"):
    for chips in ([], [{"id": "ball", "label": [text("The ball")]}]):
        question = {"id": "q", "kind": kind, "prompt": [text("Choose the object.")], "chips": chips}
        item = response([text("Choose.")], [question])
        before = copy.deepcopy(item)
        checked = validate_response(item, outputs, gate.SCENE_ID)
        assert item == before
        for where in ("prompt", "chip"):
            bad = copy.deepcopy(item)
            if where == "prompt":
                bad["questions"][0]["prompt"] = [text("Drop two metres?")]
            else:
                bad["questions"][0]["chips"] = [{"id": "ball", "label": [text("Half a metre")]}]
            try:
                validate_response(bad, outputs, gate.SCENE_ID)
            except AgentContractError:
                pass
            else:
                raise AssertionError((kind, chips, where))
        normalization.append({"kind": kind, "chips": bool(chips), "normalized": checked["questions"][0]["kind"],
                              "input_unchanged": True, "prompt_and_chip_numbers_rejected": True})

offline = gate.offline()
offline["summary"] = gate.summary(offline)
saved_offline = json.loads((ROOT / "evidence/S14/S14g-offline.json").read_text(encoding="utf-8"))
assert offline["summary"] == saved_offline["summary"]
(Path(__file__).with_name("offline-rerun.json")).write_text(json.dumps(offline, indent=2) + "\n", encoding="utf-8")
live = json.loads((ROOT / "evidence/S14/S14g-live.json").read_text(encoding="utf-8"))
ledger = [json.loads(line) for line in (ROOT / "evidence/S14/S14g-ledger.jsonl").read_text().splitlines()]
expected = Counter({f"spec-{i:02d}": row["attempts"] for i, row in enumerate(live["specs"])})
expected.update({f"turn-{i:02d}": row["attempts"] for i, row in enumerate(live["turns"])})
assert Counter(row["call"] for row in ledger) == expected
assert all(row["http"] == 200 for row in ledger)
assert live["summary"] == gate.summary(live)
assert len(live["specs"]) == 10 and len(live["turns"]) == 30
assert all(row["valid"] for row in live["specs"])
assert all(row["invented"] is None for row in live["turns"])
assert all(abs(row["est_usd"] - (row["input_tokens"] * gate.IN_USD + row["output_tokens"] * gate.OUT_USD)) < 0.0000011 for row in ledger)

# Independent of numeric_issue: explicitly look for common numeric tokens after stripping only tool formats.
independent = re.compile(r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|double|twice|half|quarter)\b", re.I)
live_scan = []
for row in live["turns"]:
    i = row["turn"]
    rest = row["shown"]
    if not row["mystery"]:
        s = gate.BRIDGE.handle({"action": "start", "template": row["template"], "mystery": False})
        f = gate.BRIDGE.handle({"action": "fit", "observations": s["observations"]})
        tools = gate.trial.trial_outputs(f"gate-a-t{i:02d}", s, f)
        for out in tools:
            for q in out["quantities"].values():
                # Separate formatting to avoid trusting the exact implementation under review.
                rest = rest.replace(f"{q['value']:.6g} ± {q['uncertainty']:.2g} {q['unit']} ({q['source']['label']})", " ")
        provenance = "reproduced deterministic simulator/fitter output"
    else:
        # Historical random Mystery-g outputs/seeds were not saved: format scan is NOT provenance proof.
        rest = re.sub(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)? ± [\d.e+-]+ (?:m/s\^2|m/s|s|m|px) \((?:simulated|measured)\)", " ", rest)
        provenance = "UNVERIFIABLE: historical tool outputs and random seed absent; format-only scan"
    assert not any(c.isnumeric() for c in rest) and not independent.search(rest), (i, rest)
    live_scan.append({"turn": i, "residual": rest, "common_numeric_tokens": False, "provenance": provenance})

assert original == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in original}
result = {"baseline": "ca34cbff8a3aaae6b3a4b07c4dda83d73e6b9821", "probes": rows,
          "end_to_end_gate_turns": end_to_end,
          "unknown_ref_blocked": True, "fallback_tool_quantities_present": True,
          "no_outputs_fallback_safe": True, "invalid_tools_raise": invalid_tools_raise,
          "normalization": normalization, "offline_summary": offline["summary"],
          "stored_live_summary": live["summary"], "ledger_rows": len(ledger),
          "ledger_labels_reconcile": True, "estimated_usd": round(sum(r["est_usd"] for r in ledger), 6),
          "model_counts": dict(Counter(r["model"] for r in ledger)),
          "billed_unknown": all(r["billed_usd"] is None for r in ledger),
          "live_independent_residual_scan": live_scan, "original_S14_evidence_unchanged": True,
          "original_S14_sha256": {str(p.relative_to(ROOT)): digest for p, digest in original.items()}}
Path(__file__).with_name("probe-results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k not in ("probes", "live_independent_residual_scan", "end_to_end_gate_turns", "original_S14_sha256")}, indent=2))
