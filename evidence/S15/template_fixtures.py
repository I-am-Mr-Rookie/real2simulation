"""S15e: build/check tests/workspace/fixtures/template-cases.json from the REAL Python contract: Build/agent/interview.py
(QUESTIONS/UNITS/_parse) and answers_to_spec -> S08 validate_setup. JS tests replay these recorded verdicts; no model calls.
Usage (repo root): python evidence/S15/template_fixtures.py [--check]"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests/spec")]
from Build.agent import interview as iv  # noqa: E402
from contracts.agent.validate import AgentContractError  # noqa: E402
from test_setup_validation import BUNDLE, setup  # noqa: E402

OUT = ROOT / "tests/workspace/fixtures/template-cases.json"
VALID = {  # SYNTHETIC inputs; the validator, not this table, decides acceptance
    "free_fall": ["2", "0"], "projectile": ["2", "1.5"], "ramp": ["30 deg", "0.1", "0"], "pendulum": ["1", "3 deg", "0"],
}
BAD = {"free_fall": [["-1", "0"], ["2 ft", "0"], ["abc", "0"], ["1e999", "0"]], "ramp": [["30", "0.1", "0"], ["1.5 rad", "0.1", "0"]],
       "pendulum": [["1", "2 rad", "0"]], "projectile": [["", "1"]]}


def verdict(template, texts):
    params = [q[0] for q in iv.QUESTIONS[template]]
    answers = {p: {"text": t} for p, t in zip(params, texts)}
    spec, scene = setup(template)
    try:
        return {"template": template, "answers": answers, "ok": True, "spec": iv.answers_to_spec(spec, scene, BUNDLE, answers)}
    except AgentContractError as e:
        return {"template": template, "answers": answers, "ok": False, "errors": [str(i) for i in e.issues]}


def build():
    fields = {t: [{"param": q[0], "unit": q[3], "units": sorted(iv.UNITS[q[3]])} for q in qs] for t, qs in iv.QUESTIONS.items()}
    verdicts = [verdict(t, v) for t, vs in VALID.items() for v in [vs]] + [verdict(t, v) for t, vs in BAD.items() for v in vs]
    return {"provenance": "SYNTHETIC inputs; verdicts recorded from Build/agent/interview.py answers_to_spec -> S08 validate_setup. Not Gate P/A, real-scene or physical evidence.",
            "fields": fields, "verdicts": verdicts}


if __name__ == "__main__":
    text = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        sys.exit(0 if OUT.read_text(encoding="utf-8") == text else "template fixtures drifted: rerun without --check")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    d = json.loads(text)["verdicts"]
    print("wrote", OUT.relative_to(ROOT), "verdicts:", len(d), "ok:", sum(v["ok"] for v in d))

