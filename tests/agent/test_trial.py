"""S14e: Muse Spark trial-check claims must reference the ACTUAL simulator/fitter outputs of the trial.

The trial is a real run of the S10 synthetic lab (node simulator + Python fitter) inside the test.
Spark replies are hand-written SYNTHETIC Responses-API bodies (no live Meta calls: billing hold).
Not Gate A, real-scene, calibration or physical evidence.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

from Build.agent import trial
from Build.agent.tools import render
from contracts.agent.validate import AgentContractError

ROOT = Path(__file__).resolve().parents[2]
SCENE_ID = "synthetic-room-v1"
TRIAL_ID = "synthetic-trial-ff"
_spec = importlib.util.spec_from_file_location("s10_session_bridge", ROOT / "Build/lab/session-bridge.py")
BRIDGE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BRIDGE)


def text(t):
    return {"type": "text", "text": t}


def num(output_id, quantity):
    return {"type": "number", "ref": {"tool_output_id": output_id, "quantity": quantity}}


def SYNTHETIC_reply(segments, **extra):
    """Hand-written SYNTHETIC Spark reply, wrapped as a Responses-API body."""
    reply = {"schema_version": "agent-response/1.0.0", "scene_id": SCENE_ID, "segments": segments,
             "questions": [], **extra}
    return {"status": "completed", "output": [{"type": "message", "content": [
        {"type": "output_text", "text": json.dumps(reply)}]}]}


GOOD = [text("Simulated trial: the fitter gives gravity "), num(f"{TRIAL_ID}-fit", "gravity"),
        text(" from a simulated drop of "), num(f"{TRIAL_ID}-sim", "drop"), text(" over "),
        num(f"{TRIAL_ID}-sim", "duration"), text(". Consistent with the run; simulated, not physical evidence.")]


def reply_text(body):
    return body["output"][0]["content"][0]["text"]


class Post:
    def __init__(self, *bodies):
        self.bodies, self.requests = list(bodies), []

    def __call__(self, request):
        self.requests.append(copy.deepcopy(request))
        return self.bodies.pop(0)


class TrialCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start = BRIDGE.handle({"action": "start", "template": "free_fall"})  # actual simulator run
        assert cls.start["status"] == "ok", cls.start
        cls.fit = BRIDGE.handle({"action": "fit", "observations": cls.start["observations"]})  # actual fitter
        assert cls.fit["status"] == "ok", cls.fit
        cls.outputs = trial.trial_outputs(TRIAL_ID, cls.start, cls.fit)
        cls.context = trial.trial_context(SCENE_ID, TRIAL_ID, cls.start, cls.outputs)

    def rejected(self, segments, needle, outputs=None, **extra):
        with self.assertRaises(AgentContractError) as ctx:
            trial.validate_check(reply_text(SYNTHETIC_reply(segments, **extra)),
                                 self.outputs if outputs is None else outputs, SCENE_ID)
        self.assertIn(needle, str(ctx.exception))

    def test_tool_outputs_are_the_actual_simulator_and_fitter_values(self):
        sim, fit = self.outputs
        last = self.start["observations"][-1]
        self.assertEqual((sim["id"], sim["tool"], fit["id"], fit["tool"]),
                         (f"{TRIAL_ID}-sim", "simulator", f"{TRIAL_ID}-fit", "fitter"))
        self.assertEqual(sim["quantities"]["duration"]["value"], last["time_s"])
        self.assertEqual(sim["quantities"]["drop"]["value"], last["position_m"])
        self.assertEqual(fit["quantities"]["gravity"]["value"], self.fit["gravity"]["value"])
        self.assertEqual({q["source"]["label"] for o in self.outputs for q in o["quantities"].values()}, {"simulated"})
        self.assertAlmostEqual(fit["quantities"]["gravity"]["value"], 9.81, places=3)  # fitter output, not authored

    def test_valid_claims_render_exactly_the_tool_values(self):
        response = trial.validate_check(reply_text(SYNTHETIC_reply(GOOD)), self.outputs, SCENE_ID)
        out = render(response, self.outputs, SCENE_ID)
        sim, fit = (o["quantities"] for o in self.outputs)
        for q in (fit["gravity"], sim["drop"], sim["duration"]):
            self.assertIn(f"{q['value']:.6g} ± {q['uncertainty']:.2g} {q['unit']} (simulated)", out)

    def test_untraced_numbers_are_rejected(self):
        self.rejected([text("Gravity is 9.81 here.")], "response/segments")
        self.rejected([text("Gravity is nine point eight "), num(f"{TRIAL_ID}-fit", "gravity")], "untraced_number_word")
        self.rejected([text("Roughly ٩ metres "), num(f"{TRIAL_ID}-fit", "gravity")], "response.segments[0].text")

    def test_refs_must_name_this_trials_outputs(self):
        self.rejected([text("g "), num(f"{TRIAL_ID}-fit", "velocity")], "no quantity 'velocity'")
        self.rejected([text("g "), num("synthetic-trial-other-fit", "gravity")], "unknown tool_output_id")
        other = trial.trial_outputs("synthetic-trial-other", self.start, self.fit)
        self.rejected(GOOD, "unknown tool_output_id", outputs=other)  # stale reply vs another trial

    def test_claim_must_cite_and_carry_no_questions_or_candidates(self):
        self.rejected([text("The trial looks consistent.")], "must cite at least one")
        self.rejected(GOOD, "questions and candidates must be empty",
                      candidates=[{"id": "c", "template": "free_fall", "rationale": [text("Drop.")]}])

    def test_retry_then_valid_and_request_carries_actual_outputs(self):
        post = Post(SYNTHETIC_reply([text("Gravity is about ten.")]), SYNTHETIC_reply([text("Fine.")]),
                    SYNTHETIC_reply(GOOD))
        response, rejected = trial.check_trial(self.context, post)
        self.assertEqual(response["segments"], GOOD)
        self.assertEqual(len(post.requests), 3)
        self.assertEqual(len(rejected), 2)
        first = post.requests[0]
        self.assertEqual(first["model"], "muse-spark-1.3")
        self.assertEqual(json.loads(first["input"])["tool_outputs"], self.outputs)
        self.assertTrue(first["instructions"].startswith(trial.INSTRUCTIONS[:40]))
        self.assertIn(rejected[1][0][:60], post.requests[2]["instructions"])

    def test_four_rejects_fall_back_to_tool_only_without_model_claims(self):
        post = Post(*[SYNTHETIC_reply([text("About ten.")])] * 4)
        response, rejected = trial.check_trial(self.context, post)
        self.assertEqual((len(post.requests), len(rejected)), (4, 4))
        refs = [s["ref"] for s in response["segments"] if s["type"] == "number"]
        self.assertEqual(refs, [{"tool_output_id": o["id"], "quantity": q} for o in self.outputs for q in o["quantities"]])
        self.assertIn("tool results only", render(response, self.outputs, SCENE_ID))

    def test_transport_errors_propagate_without_retry(self):
        def post(request):
            raise TimeoutError("synthetic transport failure")
        with self.assertRaises(TimeoutError):
            trial.check_trial(self.context, post)

    def test_failed_trials_produce_no_tool_outputs(self):
        with self.assertRaises(AgentContractError):
            trial.trial_outputs(TRIAL_ID, {"status": "error", "error": {"code": "x"}}, self.fit)
        with self.assertRaises(AgentContractError):
            trial.trial_outputs(TRIAL_ID, self.start, {"status": "error"})

    def test_scene_request_unchanged_by_instructions_parameter(self):
        from Build.agent import muse
        ctx = {"scene_id": SCENE_ID}
        self.assertEqual(muse.build_request(ctx)["instructions"], muse.INSTRUCTIONS)
        self.assertEqual(muse.build_request(ctx)["model"], "muse-wonder-1.0")


if __name__ == "__main__":
    unittest.main()
