"""S14j: owner Q16=A spec path for the RECORDED RM04 scene (no authoritative bundle). Offline; no model, GPU or paid call.

base_spec/scene_context are the recorded S14g-fix3 RM04 understanding (jobs.load_understanding); answers are SYNTHETIC.
"""
import os
import unittest
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.agent import interview
from Build.api.workspace import jobs
from Build.api.workspace.analysis import Q16_LABEL, create_router
from contracts.agent.validate import AgentContractError

from test_analysis import ANSWERS, AUTH, SCENE, TOKEN, resolver as synthetic_resolver

RM04_SHA = "8231fbca041d030f2fc39bd4281af6112e476bf811f548fc9019db53f7cb87ec"
RM04 = "job_" + "0" * 32


def resolver(owner, scene_id):
    if scene_id == RM04 and owner == AUTH["x-workspace-owner"]:
        found = jobs.load_understanding(RM04_SHA)
        return found[0]["spec"], found[0]["scene_context"], jobs.ROOT
    return synthetic_resolver(owner, scene_id)


class Q16SpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = FastAPI()
        app.include_router(create_router(resolver))
        cls.client = TestClient(app)

    def setUp(self):
        patcher = mock.patch.dict(os.environ, {"WORKSPACE_INTERNAL_TOKEN": TOKEN})
        patcher.start()
        self.addCleanup(patcher.stop)

    def post(self, scene, answers):
        return self.client.post(f"/internal/workspace/scenes/{scene}/spec", headers=AUTH, json={"answers": answers})

    def test_rm04_production_path_is_bundle_only_failure(self):  # precondition: why Q16 applies
        spec, scene, root = resolver(AUTH["x-workspace-owner"], RM04)
        with self.assertRaises(AgentContractError) as ctx:
            interview.answers_to_spec(spec, scene, root, ANSWERS)
        self.assertTrue(all(i.startswith("$.scene: invalid authoritative bundle:") for i in ctx.exception.issues))

    def test_rm04_valid_answers_200_labelled_never_setup_validated(self):
        r = self.post(RM04, ANSWERS)
        self.assertEqual(r.status_code, 200, r.text)
        body = r.json()
        self.assertEqual(body["label"], "scale unverified, not setup-validated")
        self.assertIs(body["setup_validated"], False)
        self.assertEqual(body["spec"], body["validated_setup"])
        params = body["spec"]["parameters"]
        self.assertEqual(params["drop_height"]["value"], 1.5)  # the user's number, not a default
        self.assertEqual(params["drop_height"]["source"]["label"], "assumed")
        self.assertNotIn("MET", str(body))

    def test_rm04_invalid_answers_422(self):
        for answers in ({}, {"drop_height": {"text": "-2 m"}, "initial_vertical_velocity": {"chip": "at-rest"}},
                        {"drop_height": {"text": "abc"}, "initial_vertical_velocity": {"chip": "at-rest"}},
                        {**ANSWERS, "extra": {"text": "1"}}):
            with self.subTest(answers=answers):
                r = self.post(RM04, answers)
                self.assertEqual(r.status_code, 422, r.text)
                self.assertEqual(r.json()["detail"]["code"], "INVALID_INPUT")

    def test_authoritative_scene_unchanged(self):
        r = self.post(SCENE, ANSWERS)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(set(r.json()), {"ok", "spec", "validated_setup"})
        self.assertEqual(r.json()["validated_setup"], interview.answers_to_spec(*synthetic_resolver(AUTH["x-workspace-owner"], SCENE), ANSWERS))


if __name__ == "__main__":
    unittest.main()
