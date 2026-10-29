"""S14a: agent text cannot carry untraced numbers. All fixtures are visibly SYNTHETIC."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from Build.agent.tools import fit_tool_output, render, scene_context
from Build.fitter.api import handle
from Build.instruments.synthetic import ruler_observation, stopwatch_observation
from contracts.agent.validate import (
    TOOL_OUTPUT_VERSION, AgentContractError, numeric_issue, validate_response, validate_tool_output,
)

ROOT = Path(__file__).resolve().parents[2]
SCENE_DIR = ROOT / "test-data/synthetic/scene/room-v1"
SCHEMA = json.loads((ROOT / "contracts/agent/response.schema.json").read_text(encoding="utf-8"))
SCENE_ID = "synthetic-room-v1"


def synthetic_fit():
    times, positions = [], []
    for i in range(6):
        t = i * 0.1
        times.append(stopwatch_observation(t, seed=i, bias_s=0, noise_std_s=0, resolution_s=1e-6, uncertainty_s=1e-6))
        positions.append(ruler_observation(1.0 + 0.4 * t + 4.905 * t * t, resolution_m=1e-6,
                                           uncertainty_m=1e-6, bias_m=0))
    return fit_tool_output("fit-synthetic", handle({"times": times, "positions": positions, "degree": 2}))


def text(t):
    return {"type": "text", "text": t}


NUM = {"type": "number", "ref": {"tool_output_id": "fit-synthetic", "quantity": "gravity"}}


def response(segments=None, questions=None):
    return {"schema_version": "agent-response/1.0.0", "scene_id": SCENE_ID,
            "segments": segments or [text("The synthetic fit gives "), NUM, text(".")],
            "questions": questions if questions is not None else [
                {"id": "q-object", "kind": "chips_and_free_text", "prompt": [text("Which object falls?")],
                 "chips": [{"id": "ball", "label": [text("The ball")]}]}]}


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fit = synthetic_fit()
        cls.tools = [cls.fit]

    def rejected(self, resp, needle, tools=None):
        with self.assertRaises(AgentContractError) as ctx:
            validate_response(resp, self.tools if tools is None else tools, SCENE_ID)
        self.assertIn(needle, str(ctx.exception))
        return ctx.exception

    def test_schema_is_valid_and_traced_reply_renders_labelled(self):
        Draft202012Validator.check_schema(SCHEMA)
        out = render(response(), self.tools, SCENE_ID)
        g = self.fit["quantities"]["gravity"]
        self.assertEqual(g["source"]["label"], "simulated")
        self.assertIn(f"{g['value']:.6g} ± ", out)
        self.assertTrue(out.endswith("m/s^2 (simulated)."), out)
        self.assertAlmostEqual(g["value"], 9.81, places=3)  # fitter output, not authored

    def test_schema_alone_rejects_ascii_digits(self):
        bad = response([text("g is 9.81 m/s^2")])
        self.assertTrue(list(Draft202012Validator(SCHEMA).iter_errors(bad)))
        self.rejected(bad, "not valid under any")

    def test_untraced_numbers_rejected_everywhere(self):
        for where in ("segments", "prompt", "chip", "candidate"):
            resp = response()
            if where == "segments":
                resp["segments"] = [text("about ten metres per second squared")]
            elif where == "prompt":
                resp["questions"][0]["prompt"] = [text("Drop from two metres?")]
            elif where == "chip":
                resp["questions"][0]["chips"][0]["label"] = [text("Ball, half a metre up")]
            else:
                resp["candidates"] = [{"id": "c", "template": "drop", "rationale": [text("Height ¾ m")]}]
            with self.subTest(where=where):
                self.rejected(resp, "untraced_")

    def test_unicode_and_word_numbers(self):
        for t in ("g≈٩٫٨", "Ⅷ trials", "½ metre", "nine point eight", "Twenty percent", "三"):
            with self.subTest(t=t):
                self.assertIsNotNone(numeric_issue(t))
        for t in ("Which one falls first?", "The ball rolls off the table.", "Gravity is hidden."):
            with self.subTest(t=t):
                self.assertIsNone(numeric_issue(t))

    def test_number_refs_must_resolve_to_tool_outputs(self):
        missing_out = response([{"type": "number", "ref": {"tool_output_id": "llm-guess", "quantity": "gravity"}}])
        self.rejected(missing_out, "unknown tool_output_id")
        missing_q = response([{"type": "number", "ref": {"tool_output_id": "fit-synthetic", "quantity": "rmse"}}])
        self.rejected(missing_q, "no quantity")
        self.rejected(response(), "unknown tool_output_id", tools=[])

    def test_inline_value_or_unknown_fields_rejected(self):
        smuggled = response([{"type": "number", "value": 9.81,
                              "ref": {"tool_output_id": "fit-synthetic", "quantity": "gravity"}}])
        self.rejected(smuggled, "response/segments/0")
        extra = response()
        extra["confidence"] = "high"
        self.rejected(extra, "Additional properties")

    def test_tool_output_label_tool_and_provenance_enforced(self):
        for mutate, needle in (
            (lambda o: o["quantities"]["gravity"]["source"].update(label="estimated"), "measured or simulated"),
            (lambda o: o["quantities"]["gravity"]["source"].update(evidence=" "), "evidence"),
            (lambda o: o["quantities"]["gravity"].update(value=float("nan")), "finite"),
            (lambda o: o["quantities"]["gravity"].update(unit="bananas"), "unit"),
            (lambda o: o.update(tool="llm"), "tool"),
            (lambda o: o.update(status="error"), "status"),
            (lambda o: o.update(note="x"), "unknown fields"),
        ):
            bad = copy.deepcopy(self.fit)
            mutate(bad)
            with self.subTest(needle=needle), self.assertRaises(AgentContractError) as ctx:
                validate_tool_output(bad)
            self.assertIn(needle, str(ctx.exception))
        measured = copy.deepcopy(self.fit)
        measured["quantities"]["gravity"]["source"]["label"] = "measured"
        self.assertEqual(validate_tool_output(measured)["quantities"]["gravity"]["source"]["label"], "measured")
        self.assertEqual(self.fit["schema_version"], TOOL_OUTPUT_VERSION)
        self.rejected(response(), "duplicate id", tools=[self.fit, self.fit])

    def test_failed_fit_cannot_back_numbers(self):
        with self.assertRaises(AgentContractError):
            fit_tool_output("fit-bad", handle({"times": [], "positions": []}))

    def test_question_contract(self):
        q = response()["questions"][0]
        self.rejected(response(questions=[dict(q, id=f"q{i}") for i in "abcd"]), "is too long")
        self.rejected(response(questions=[dict(q, kind="free_text")]), "free_text has no chips")
        self.rejected(response(questions=[dict(q, kind="chips", chips=[])]), "chip kinds need")
        validate_response(response(questions=[dict(q, kind="free_text", chips=[])]), self.tools, SCENE_ID)

    def test_scene_binding_and_strict_json(self):
        self.rejected(dict(response(), scene_id="other-scene"), "scene_id")
        raw = json.dumps(response())
        self.assertEqual(validate_response(raw, self.tools, SCENE_ID)["scene_id"], SCENE_ID)
        self.rejected(raw[:-1] + ', "scene_id": "synthetic-room-v1"}', "response:")
        self.rejected('{"segments": NaN}', "response:")

    def test_scene_context_has_no_numbers(self):
        ctx = scene_context(json.loads((SCENE_DIR / "scene.json").read_text(encoding="utf-8")), SCENE_DIR)
        self.assertEqual(ctx["scene_id"], SCENE_ID)
        self.assertTrue(ctx["synthetic"])

        def walk(v):
            if isinstance(v, dict):
                return [x for c in v.values() for x in walk(c)]
            if isinstance(v, list):
                return [x for c in v for x in walk(c)]
            return [v]
        self.assertFalse([v for v in walk(ctx) if isinstance(v, (int, float)) and not isinstance(v, bool)])


if __name__ == "__main__":
    unittest.main()
