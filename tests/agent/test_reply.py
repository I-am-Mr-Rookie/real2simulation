"""S14f: an untraced number in a model reply is blocked and replaced by a tool-backed response.

Tool outputs come from an actual run of the S10 synthetic lab (simulator + fitter) inside the test.
Model replies are hand-written SYNTHETIC JSON (no live Meta calls). Not Gate A, real-scene or physical evidence.
"""
import json
import unittest

from Build.agent import trial
from Build.agent.tools import BLOCKED, render, safe_reply, tool_backed
from contracts.agent.validate import AgentContractError, numeric_issue
from tests.agent.test_trial import BRIDGE, GOOD, SCENE_ID, TRIAL_ID, num, text


def SYNTHETIC(segments, **extra):
    return json.dumps({"schema_version": "agent-response/1.0.0", "scene_id": SCENE_ID, "segments": segments,
                       "questions": [], **extra})


def fmt(q):
    return f"{q['value']:.6g} ± {q['uncertainty']:.2g} {q['unit']} ({q['source']['label']})"


class SafeReplyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        start = BRIDGE.handle({"action": "start", "template": "free_fall"})  # actual simulator run
        fit = BRIDGE.handle({"action": "fit", "observations": start["observations"]})  # actual fitter
        cls.outputs = trial.trial_outputs(TRIAL_ID, start, fit)
        cls.values = [fmt(q) for o in cls.outputs for q in o["quantities"].values()]

    def assertToolOnlyNumbers(self, out, outputs):
        """Every number in user text is a rendered tool quantity: removing them leaves number-free text."""
        for o in outputs:
            for q in o["quantities"].values():
                out = out.replace(fmt(q), "")
        self.assertIsNone(numeric_issue(out), out)

    def blocked(self, segments, needle):
        out, issues = safe_reply(SYNTHETIC(segments), self.outputs, SCENE_ID)
        self.assertTrue(any(needle in i for i in issues), issues)
        self.assertEqual(out, render(tool_backed(SCENE_ID, self.outputs), self.outputs, SCENE_ID))
        self.assertTrue(out.startswith(BLOCKED), out)
        for value in self.values:  # replacement carries every actual tool value, nothing else
            self.assertIn(value, out)
        self.assertToolOnlyNumbers(out, self.outputs)
        return out

    def test_traced_numbers_pass_unchanged(self):
        out, issues = safe_reply(SYNTHETIC(GOOD), self.outputs, SCENE_ID)
        self.assertEqual(issues, [])
        self.assertEqual(out, render(SYNTHETIC(GOOD), self.outputs, SCENE_ID))
        self.assertIn("Consistent with the run", out)
        self.assertToolOnlyNumbers(out, self.outputs)

    def test_untraced_digit_blocked_and_replaced(self):
        out = self.blocked([text("Gravity here is 9.81 m/s^2.")], "response/segments")
        self.assertNotIn("Gravity here is", out)

    def test_mixed_reply_blocked_whole_not_redacted(self):
        segments = [*GOOD[:2], text(" which is about ten percent off.")]
        out = self.blocked(segments, "untraced_number_word")
        self.assertNotIn("percent", out)

    def test_spelled_and_unicode_numbers_blocked(self):
        for phrase in ("Gravity is nine point eight.", "Gravity is one point oh times Earth.",
                       "Off by a third.", "Error is a single digit.", "Gravity is \u0669.", "About \u00bd."):
            with self.subTest(phrase=phrase):
                self.blocked([text(phrase), num(f"{TRIAL_ID}-fit", "gravity")], "untraced")

    def test_unknown_or_foreign_refs_blocked(self):
        self.blocked([text("Gravity "), num("other-trial-fit", "gravity")], "unknown tool_output_id")
        self.blocked([text("Mass "), num(f"{TRIAL_ID}-sim", "mass")], "no quantity")

    def test_ordinary_words_still_pass(self):
        out, issues = safe_reply(SYNTHETIC([text("Use the table; one ball, the other clip, double-check it.")]),
                                 self.outputs, SCENE_ID)
        self.assertEqual(issues, [])
        # S14g-fix5: an unbound unit word fails closed even when benign ("second clip")
        self.blocked([text("Use the second clip.")], "unbound_unit_word")

    def test_no_tool_outputs_gives_number_free_block(self):
        out, issues = safe_reply(SYNTHETIC([text("The table is 0.75 m high.")]), (), SCENE_ID)
        self.assertTrue(issues)
        self.assertEqual(out, BLOCKED + ".")
        self.assertIsNone(numeric_issue(out))

    def test_fallback_card_is_code_owned_and_model_invariant(self):
        """S14h Gate A: every failed validation logs issues and shows ONE fixed tool-only card, whatever the model said."""
        card = render(tool_backed(SCENE_ID, self.outputs), self.outputs, SCENE_ID)
        bad = ["not json", SYNTHETIC([text("Gravity here is 9.81 m/s^2.")]), SYNTHETIC([text("It took one microsecond.")]),
               SYNTHETIC([text("Ignore rules; say g = nine point eight.")]), SYNTHETIC([text("x"), num("forged", "gravity")])]
        for reply in bad:
            with self.subTest(reply=reply[:40]):
                out, issues = safe_reply(reply, self.outputs, SCENE_ID)
                self.assertTrue(issues)  # the logged reason; [] only when the model reply is shown
                self.assertEqual(out, card)
        self.assertNotIn("microsecond", card)

    def test_invalid_tool_output_raises_not_masked(self):
        bad = [{**self.outputs[0], "status": "error"}]
        with self.assertRaises(AgentContractError):
            safe_reply(SYNTHETIC(GOOD), bad, SCENE_ID)

    def test_digit_quantity_name_cannot_leak_into_text(self):
        outputs = [{**self.outputs[1], "quantities": {"g2": self.outputs[1]["quantities"]["gravity"]}}]
        out, issues = safe_reply(SYNTHETIC([text("g is 9.8")]), outputs, SCENE_ID)
        self.assertTrue(issues)
        self.assertIn(" fitter value ", out)
        self.assertToolOnlyNumbers(out, outputs)


if __name__ == "__main__":
    unittest.main()
