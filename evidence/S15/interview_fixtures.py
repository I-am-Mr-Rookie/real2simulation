"""S15d: build/check tests/workspace/fixtures/interview-responses.json. Every response is validated by
contracts/agent/validate.py (S14a) before it is written; --check fails on drift. No model calls.
Usage (repo root): python evidence/S15/interview_fixtures.py [--check]"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from contracts.agent.validate import validate_response, validate_tool_output  # noqa: E402

OUT = ROOT / "tests/workspace/fixtures/interview-responses.json"
SCENE = "synthetic-room-v1"
t = lambda s: {"type": "text", "text": s}  # noqa: E731
TOOL = {"schema_version": "agent-tool-output/1.0.0", "id": "fit-synthetic", "tool": "fitter", "status": "ok",
        "quantities": {"gravity": {"value": 9.8, "uncertainty": 0.1, "unit": "m/s^2",
                                   "source": {"label": "simulated", "evidence": "SYNTHETIC placeholder, not a fit"}}}}
NUM = {"type": "number", "ref": {"tool_output_id": "fit-synthetic", "quantity": "gravity"}}
chip = lambda i, s: {"id": i, "label": [t(s)]}  # noqa: E731
AUTHORED = {
    "authored-three-kinds": {"schema_version": "agent-response/1.0.0", "scene_id": SCENE, "segments": [t("SYNTHETIC interview fixture.")],
        "questions": [
            {"id": "q-object", "kind": "chips", "prompt": [t("Which object falls?")], "chips": [chip("ball", "Ball"), chip("block", "Block")]},
            {"id": "q-notes", "kind": "free_text", "prompt": [t("Describe the release in your own words.")], "chips": []},
            {"id": "q-height", "kind": "chips_and_free_text", "prompt": [t("Release surface?")],
             "chips": [chip("table", "Table"), {"id": "ref-g", "label": [t("Compare with "), NUM]}]}]},
    "authored-no-questions": {"schema_version": "agent-response/1.0.0", "scene_id": SCENE, "segments": [t("Nothing to ask.")], "questions": []},
}


def build():
    tools = [validate_tool_output(TOOL)]
    responses = {}
    for p in sorted((ROOT / "tests/agent/fixtures/muse").glob("*.json")):
        f = json.loads(p.read_text(encoding="utf-8"))
        if f["expect"] == "valid":
            responses["muse-" + p.stem.rsplit("-", 1)[1]] = json.loads(f["output"][0]["content"][0]["text"])
    responses.update(AUTHORED)
    for name, r in responses.items():
        validate_response(r, tools, SCENE)
    return {"provenance": "SYNTHETIC. muse-* = recorded S14b replies (synthetic scene context); authored-* = hand-written. All validated by contracts/agent/validate.py::validate_response. Not Gate A, real-scene or physical evidence.",
            "scene_id": SCENE, "tool_outputs": tools, "responses": responses}


if __name__ == "__main__":
    text = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        sys.exit(0 if OUT.read_text(encoding="utf-8") == text else "interview fixtures drifted: rerun without --check")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT), "responses:", len(json.loads(text)["responses"]))
