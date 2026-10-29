"""S14d: bounded validator-retry loop. Recorded Muse replies replayed offline; SYNTHETIC mutations marked."""
import copy
import json
import unittest
from pathlib import Path

from Build.agent import interview, muse
from contracts.agent.validate import TEMPLATES, AgentContractError, validate_response

FIX = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (Path(__file__).parent / "fixtures" / "muse").glob("*.json")}
CONTEXT = FIX["live-room-v1-d"]["context"]
REJECTED = FIX["live-room-v1-a"]  # recorded incomplete reply (validator rejects)
VALID = FIX["live-room-v1-d"]


def body(fixture, text=None):
    output = copy.deepcopy(fixture["output"])
    if text is not None:  # SYNTHETIC mutation of a recorded reply
        output[0]["content"][0]["text"] = text
    return {"status": fixture["status"], "output": output}


class Poster:
    """Replays bodies in order and records every request; raises if called more often than scripted."""
    def __init__(self, *bodies):
        self.bodies, self.requests = list(bodies), []

    def __call__(self, request):
        self.requests.append(request)
        reply = self.bodies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


def valid_text(mutate):
    resp = json.loads(VALID["output"][0]["content"][0]["text"])
    mutate(resp)
    return json.dumps(resp)


class Retry(unittest.TestCase):
    def assert_asks_user(self, response):
        validate_response(response, (), CONTEXT["scene_id"])
        self.assertEqual(response["candidates"], [])
        (question,) = response["questions"]
        self.assertEqual([c["id"] for c in question["chips"]], sorted(TEMPLATES))
        for chip in question["chips"]:  # every choice leads straight into the S14c interview
            interview.questions(CONTEXT["scene_id"], chip["id"])
        self.assertNotIn('"number"', json.dumps(response))

    def test_first_valid_reply_needs_no_retry(self):
        post = Poster(body(VALID))
        response, rejected = muse.understand_with_retry(CONTEXT, post)
        self.assertEqual((len(post.requests), rejected), (1, []))
        self.assertEqual(response, muse.understand(CONTEXT, lambda _: body(VALID)))
        self.assertEqual(post.requests[0], muse.build_request(CONTEXT))

    def test_rejected_then_valid_retries_with_validator_issues(self):
        post = Poster(body(REJECTED), body(VALID))
        response, rejected = muse.understand_with_retry(CONTEXT, post)
        self.assertEqual(len(post.requests), 2)
        self.assertEqual(rejected, [REJECTED["issues"]])
        self.assertTrue(response["candidates"])
        retry = post.requests[1]
        self.assertIn(REJECTED["issues"][0], retry["instructions"])
        self.assertEqual({k: v for k, v in retry.items() if k != "instructions"},
                         {k: v for k, v in post.requests[0].items() if k != "instructions"})

    def test_max_three_retries_then_asks_user(self):
        bad = [body(REJECTED), body(VALID, "not json"), body(VALID, valid_text(
            lambda r: r["segments"].__setitem__(0, {"type": "text", "text": "The table is two metres high."}))),
            body(VALID, valid_text(lambda r: r.__setitem__("scene_id", "other-scene")))]
        post = Poster(*bad, body(VALID))  # a fifth (valid) reply exists but must never be requested
        response, rejected = muse.understand_with_retry(CONTEXT, post)
        self.assertEqual(muse.MAX_RETRIES, 3)
        self.assertEqual((len(post.requests), len(rejected)), (1 + muse.MAX_RETRIES, 1 + muse.MAX_RETRIES))
        self.assertEqual(len(post.bodies), 1)
        for request, issues in zip(post.requests[1:], rejected):  # each retry carries the previous issues
            self.assertIn(issues[0][:muse.FEEDBACK_CHARS], request["instructions"])
        self.assert_asks_user(response)

    def test_valid_reply_without_candidates_asks_user_not_retry(self):
        post = Poster(body(VALID, valid_text(lambda r: r.__setitem__("candidates", []))))
        response, rejected = muse.understand_with_retry(CONTEXT, post)
        self.assertEqual((len(post.requests), rejected), (1, []))
        self.assert_asks_user(response)

    def test_transport_error_propagates_without_retry(self):
        post = Poster(OSError("network down"), body(VALID))
        with self.assertRaises(OSError):
            muse.understand_with_retry(CONTEXT, post)
        self.assertEqual(len(post.requests), 1)

    def test_feedback_is_bounded(self):
        issues = ["x" * 1000] * 50
        extra = len(muse.build_request(CONTEXT, feedback=issues)["instructions"]) - len(muse.INSTRUCTIONS)
        self.assertLess(extra, muse.FEEDBACK_ISSUES * (muse.FEEDBACK_CHARS + 2) + 200)
        self.assertEqual(muse.build_request(CONTEXT, feedback=())["instructions"], muse.INSTRUCTIONS)

    def test_ask_user_rejects_bad_scene_id(self):
        with self.assertRaises(AgentContractError):
            muse.ask_user("bad scene id")


if __name__ == "__main__":
    unittest.main()

