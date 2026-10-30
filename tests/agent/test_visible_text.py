"""S14g-fix product regressions (R-A F1/F2): every adversarial corpus case through validate_response,
safe_reply and the trial check loop; the visible run, prompts, chips and rationales are all checked."""
import json
import unittest
from pathlib import Path

from Build.agent import trial
from Build.agent.tools import safe_reply
from contracts.agent.validate import AgentContractError, validate_response

CASES = json.loads((Path(__file__).with_name("fixtures") / "adversarial-visible-text.json").read_text("utf-8"))["cases"]
SCENE = "scene-x"
OUT = {"schema_version": "agent-tool-output/1.0.0", "id": "t-fit", "tool": "fitter", "status": "ok",
       "quantities": {"gravity": {"value": 9.7, "unit": "m/s^2", "uncertainty": 0.1,
                                  "source": {"label": "measured", "evidence": "SYNTHETIC test fit"}}}}
NUM = {"type": "number", "ref": {"tool_output_id": "t-fit", "quantity": "gravity"}}


def segs(parts):
    return [NUM if p is None else {"type": "text", "text": p} for p in parts]


def reply(segments, questions=(), candidates=None):
    r = {"schema_version": "agent-response/1.0.0", "scene_id": SCENE, "segments": segments, "questions": list(questions)}
    return r if candidates is None else dict(r, candidates=candidates)


def body(r):
    return {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(r)}]}]}


class VisibleText(unittest.TestCase):
    def test_reply_text(self):
        for cid, parts, bad in CASES:
            with self.subTest(cid=cid):
                shown, blocked = safe_reply(reply(segs(parts + [None])), [OUT], SCENE)
                self.assertEqual(bool(blocked), bad, blocked)

    def test_prompts_chips_rationales(self):
        for cid, parts, bad in CASES:
            for where in ("prompt", "chip", "rationale"):
                q = {"id": "q", "kind": "chips_and_free_text", "prompt": [{"type": "text", "text": "Pick."}],
                     "chips": [{"id": "c", "label": [{"type": "text", "text": "Ball"}]}]}
                cands = [{"id": "k", "template": "free_fall", "rationale": [{"type": "text", "text": "Falls."}]}]
                field = segs(parts)
                if where == "prompt":
                    q["prompt"] = field
                elif where == "chip":
                    q["chips"][0]["label"] = field
                else:
                    cands[0]["rationale"] = field
                with self.subTest(cid=cid, where=where):
                    try:
                        validate_response(reply([{"type": "text", "text": "Ok."}], [q], cands), [OUT], SCENE)
                        self.assertFalse(bad)
                    except AgentContractError:
                        self.assertTrue(bad)

    def test_trial_loop_never_shows_probe(self):
        for cid, parts, bad in CASES:
            if bad:
                with self.subTest(cid=cid):
                    sent = iter([body(reply(segs(parts + [None])))] * 4)
                    response, rejected = trial.check_trial({"scene_id": SCENE, "tool_outputs": [OUT]}, lambda _r: next(sent))
                    self.assertEqual(len(rejected), 4)
                    self.assertTrue(response["segments"][0]["text"].startswith("The automatic trial check"))


if __name__ == "__main__":
    unittest.main()

