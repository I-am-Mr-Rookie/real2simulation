"""S14c: interview chips and free text map into S08-validated spec inputs. Offline, no model calls.

All scenes/specs are the visibly SYNTHETIC S08 test fixtures; answers are hand-written SYNTHETIC user input.
The template choice replays a RECORDED S14b Muse fixture. Not Gate A, real-scene or physical evidence.
"""
import json
import math
import sys
import unittest
from pathlib import Path

from Build.agent import interview
from Build.agent.muse import understand
from contracts.agent.validate import AgentContractError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests/spec"))
from test_setup_validation import BUNDLE, setup  # noqa: E402  (S08 synthetic fixture builder)

MUSE = ROOT / "tests/agent/fixtures/muse/live-room-v1-d.json"
SYNTHETIC_ANSWERS = {  # hand-written SYNTHETIC user answers, one valid set per template
    "free_fall": {"drop_height": {"text": "1.5 m"}, "initial_vertical_velocity": {"chip": "at-rest"}},
    "projectile": {"launch_height": {"text": "0.8"}, "horizontal_speed": {"text": "2 m/s"}},
    "ramp": {"incline_angle": {"text": "30 deg"}, "friction_coefficient": {"chip": "frictionless"},
             "initial_speed": {"text": "0.5"}},
    "pendulum": {"length": {"text": "0.75 m"}, "release_angle": {"text": "0.1 rad"},
                 "initial_angular_velocity": {"chip": "at-rest"}},
}


def problems(base, answers):
    spec, scene = setup(base)
    with unittest.TestCase().assertRaises(AgentContractError) as caught:
        interview.answers_to_spec(spec, scene, BUNDLE, answers)
    return caught.exception.issues


class InterviewTests(unittest.TestCase):
    def test_questions_are_one_to_three_and_number_free(self):
        for template in interview.QUESTIONS:
            with self.subTest(template):
                response = interview.questions("synthetic-room-v1", template)
                self.assertTrue(1 <= len(response["questions"]) <= 3)
                for q in response["questions"]:
                    self.assertIn(q["id"], setup(template)[0]["parameters"])
                    self.assertEqual(bool(q["chips"]), q["kind"] != "free_text")

    def test_chips_and_free_text_map_into_validated_spec(self):
        for template, answers in SYNTHETIC_ANSWERS.items():
            with self.subTest(template):
                spec, scene = setup(template)
                out = interview.answers_to_spec(spec, scene, BUNDLE, answers)
                for param, answer in answers.items():
                    q = out["parameters"][param]
                    self.assertEqual(q["source"]["label"], "assumed")
                    self.assertTrue(q["source"]["evidence"].startswith(f"user-input:{param}:"))
                    self.assertIsNone(q["uncertainty"])
                    if "chip" in answer:
                        self.assertEqual(q["value"], 0.0)
                self.assertEqual(out["environment"], spec["environment"])  # untouched inputs keep provenance
        out = interview.answers_to_spec(*setup("ramp"), BUNDLE, SYNTHETIC_ANSWERS["ramp"])
        self.assertAlmostEqual(out["parameters"]["incline_angle"]["value"], math.pi / 6)
        self.assertEqual(out["parameters"]["initial_speed"]["value"], 0.5)

    def test_recorded_muse_candidate_selects_template(self):
        f = json.loads(MUSE.read_text(encoding="utf-8"))
        response = understand(f["context"], lambda _: {"status": f["status"], "output": f["output"]})
        self.assertEqual(interview.template_of(response, "drop-from-table"), "free_fall")
        self.assertRaises(AgentContractError, interview.template_of, response, "no-such-candidate")

    def test_bad_answers_are_rejected_with_reasons(self):
        good = SYNTHETIC_ANSWERS["free_fall"]
        cases = {
            "missing": {"drop_height": good["drop_height"]},
            "extra": {**good, "mass": {"text": "1"}},
            "unknown chip": {**good, "initial_vertical_velocity": {"chip": "thrown"}},
            "chip on free text": {**good, "drop_height": {"chip": "at-rest"}},
            "both": {**good, "drop_height": {"text": "1", "chip": "at-rest"}},
            "word": {**good, "drop_height": {"text": "two metres"}},
            "wrong unit": {**good, "drop_height": {"text": "1.5 ft"}},
            "unicode digit": {**good, "drop_height": {"text": "\u0661"}},
            "overflow": {**good, "drop_height": {"text": "1e999"}},
            "non-string": {**good, "drop_height": {"text": 1.5}},
            "S08 range": {**good, "drop_height": {"text": "-1"}},
            "S08 bounds": {**good, "drop_height": {"text": "500"}},
        }
        for name, answers in cases.items():
            with self.subTest(name):
                self.assertTrue(problems("free_fall", answers))
        # angles need an explicit unit: a bare number is ambiguous between deg and rad
        self.assertTrue(problems("pendulum", {**SYNTHETIC_ANSWERS["pendulum"], "release_angle": {"text": "0.1"}}))

    def test_base_spec_not_mutated_and_unknown_template_rejected(self):
        spec, scene = setup("free_fall")
        before = json.dumps(spec, sort_keys=True)
        interview.answers_to_spec(spec, scene, BUNDLE, SYNTHETIC_ANSWERS["free_fall"])
        self.assertEqual(json.dumps(spec, sort_keys=True), before)
        self.assertRaises(AgentContractError, interview.questions, "synthetic-room-v1", "orbit")


if __name__ == "__main__":
    unittest.main()
