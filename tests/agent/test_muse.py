"""S14b: recorded Muse Wonder replies validate offline; invalid / untraced-number replies are rejected."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Build.agent import muse, record_muse
from contracts.agent.validate import TEMPLATES, AgentContractError

FIXTURES = sorted((Path(__file__).parent / "fixtures" / "muse").glob("*.json"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def replay(fixture, text=None):
    """Run muse.understand offline against a recorded reply (optionally with replaced output text)."""
    output = copy.deepcopy(fixture["output"])
    if text is not None:
        output[0]["content"][0]["text"] = text
    return muse.understand(fixture["context"], lambda body: {"status": fixture["status"], "output": output})


class RecordedFixtures(unittest.TestCase):
    def test_every_fixture_is_recorded_sanitized_and_replays_as_labelled(self):
        self.assertTrue(FIXTURES)
        for path in FIXTURES:
            with self.subTest(path.name):
                f = load(path)
                self.assertTrue(f["provenance"].startswith("RECORDED live Meta Model API muse-wonder-1.0"))
                self.assertTrue(f["context"]["synthetic"])
                self.assertEqual(set(f), {"provenance", "scene_dir", "context", "http", "status", "usage", "error",
                                          "output", "expect"} | ({"issues"} if f["expect"] == "rejected" else set()))
                self.assertNotIn("Bearer", path.read_text(encoding="utf-8"))
                if f["expect"] == "valid":
                    replay(f)
                else:
                    with self.assertRaises(AgentContractError):
                        replay(f)

    def test_valid_recordings_carry_scene_and_known_candidates(self):
        valid = [load(p) for p in FIXTURES if load(p)["expect"] == "valid"]
        self.assertTrue(valid)
        for f in valid:
            response = replay(f)
            self.assertEqual(response["scene_id"], f["context"]["scene_id"])
            self.assertTrue(response["candidates"])
            self.assertLessEqual({c["template"] for c in response["candidates"]}, TEMPLATES)


class Rejections(unittest.TestCase):
    def setUp(self):
        self.f = next(load(p) for p in FIXTURES if load(p)["expect"] == "valid")
        self.resp = json.loads(self.f["output"][0]["content"][0]["text"])

    def rejected(self, mutate):
        resp = copy.deepcopy(self.resp)
        mutate(resp)
        with self.assertRaises(AgentContractError) as ctx:
            replay(self.f, json.dumps(resp))
        return ctx.exception.issues

    def test_untraced_numbers_rejected(self):
        for name, value in (("digit", "The table is 0.75 m high."), ("word", "There are two surfaces."),
                            ("unicode", "Drop from ¾ of the table.")):
            with self.subTest(name):
                self.rejected(lambda r: r["segments"].__setitem__(0, {"type": "text", "text": value}))
        # no tool outputs exist at scene-understanding time, so any number segment is untraced
        issues = self.rejected(lambda r: r["segments"].append(
            {"type": "number", "ref": {"tool_output_id": "fit", "quantity": "gravity"}}))
        self.assertTrue(any("unknown tool_output_id" in i for i in issues))
        self.rejected(lambda r: r["candidates"][0]["rationale"].__setitem__(0, {"type": "text", "text": "g is 9.8"}))

    def test_invalid_structure_rejected(self):
        self.rejected(lambda r: r["candidates"][0].__setitem__("template", "drop"))
        self.rejected(lambda r: r["candidates"].append(copy.deepcopy(r["candidates"][0])))  # duplicate id
        self.rejected(lambda r: r.__setitem__("scene_id", "other-scene"))
        self.rejected(lambda r: r.__setitem__("gravity_m_s2", None))
        self.rejected(lambda r: r.__delitem__("segments"))
        for text in ("", "not json", '{"a": 1, "a": 2}'):
            with self.subTest(text), self.assertRaises(AgentContractError):
                replay(self.f, text)

    def test_incomplete_or_empty_reply_rejected(self):
        for body in ({"status": "incomplete", "output": self.f["output"]}, {"status": "completed", "output": []}):
            with self.subTest(body["status"]), self.assertRaises(AgentContractError):
                muse.understand(self.f["context"], lambda _: body)


class Request(unittest.TestCase):
    def test_request_carries_schema_bounds_and_only_context(self):
        ctx = load(FIXTURES[0])["context"]
        body = muse.build_request(ctx)
        self.assertEqual(body["model"], "muse-wonder-1.0")
        self.assertEqual(json.loads(body["input"]), ctx)
        self.assertEqual(body["text"]["format"]["schema"]["$id"], "real2sim/agent/response/1.0.0")
        self.assertLessEqual(body["max_output_tokens"], 1500)

    def test_budget_guard_refuses_past_call_or_dollar_cap(self):
        body = muse.build_request(load(FIXTURES[0])["context"])
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            with mock.patch.object(record_muse, "LEDGER", ledger):
                self.assertLess(record_muse.reserve(body), 0.1)
                ledger.write_text(json.dumps({"est_usd": 0.97}) + "\n", encoding="utf-8")
                self.assertRaises(SystemExit, record_muse.reserve, body)
                ledger.write_text((json.dumps({"est_usd": 0}) + "\n") * 20, encoding="utf-8")
                self.assertRaises(SystemExit, record_muse.reserve, body)


if __name__ == "__main__":
    unittest.main()
