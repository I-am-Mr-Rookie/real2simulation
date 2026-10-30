"""S14i: /internal/workspace analysis routes via TestClient. Offline; no model, GPU or paid call.

Scenes/specs are the visibly SYNTHETIC S08 fixtures; fits come from seeded SYNTHETIC simulated instruments.
Not real-scene, Gate A or physical evidence.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.agent import interview
from Build.api.workspace.analysis import WHAT_IF_LABEL, create_router
from Build.fitter.api import handle
from Build.reports.render import _fmt
from Build.instruments.synthetic import ruler_observation, stopwatch_observation

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests/spec"))
from test_setup_validation import BUNDLE, setup  # noqa: E402  (S08 synthetic fixture builder)

TOKEN, OWNER, SCENE = "synthetic-test-token", "user_synthA", "synthetic-room-v1"
AUTH = {"x-workspace-token": TOKEN, "x-workspace-owner": OWNER}
FIT_REQUEST = {  # same seeded SYNTHETIC simulated observations as tests/reports/fixture.py
    "times": [stopwatch_observation(i * 0.1, seed=i, bias_s=0, noise_std_s=0.001, resolution_s=1e-3, uncertainty_s=1e-3)
              for i in range(8)],
    "positions": [ruler_observation(1 + 0.04 * i + 4.905 * (i * 0.1) ** 2, resolution_m=1e-3, uncertainty_m=1e-3, bias_m=0)
                  for i in range(8)],
    "degree": 2, "select_model": True}
ANSWERS = {"drop_height": {"text": "1.5 m"}, "initial_vertical_velocity": {"chip": "at-rest"}}  # SYNTHETIC


def resolver(owner, scene_id):
    if owner == OWNER and scene_id == SCENE:
        spec, scene = setup("free_fall")
        return spec, scene, BUNDLE
    return None


class AnalysisRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = FastAPI()
        app.include_router(create_router(resolver))
        cls.client = TestClient(app)
        cls.fit = handle(FIT_REQUEST)

    def setUp(self):
        patcher = mock.patch.dict(os.environ, {"WORKSPACE_INTERNAL_TOKEN": TOKEN})
        patcher.start()
        self.addCleanup(patcher.stop)

    def get_q(self, headers=AUTH, scene=SCENE):
        return self.client.get(f"/internal/workspace/scenes/{scene}/questions", headers=headers)

    def code(self, response, status):
        self.assertEqual(response.status_code, status, response.text)
        return response.json()["detail"]["code"]

    def test_auth_rejects_missing_bad_token_and_owner(self):
        bad = [{}, {"x-workspace-owner": OWNER}, {**AUTH, "x-workspace-token": "wrong"},
               {"x-workspace-token": TOKEN},
               {**AUTH, "x-workspace-owner": "user/../other"}]
        for headers in bad:
            with self.subTest(headers=headers):
                self.assertEqual(self.code(self.get_q(headers), 401), "UNAUTHORIZED")
        for path in ("fit", "report"):  # every route is behind the router-level gate
            self.assertEqual(self.code(self.client.post(f"/internal/workspace/{path}", json={}), 401), "UNAUTHORIZED")
        with mock.patch.dict(os.environ, {"WORKSPACE_INTERNAL_TOKEN": ""}):  # unset server token fails closed
            self.assertEqual(self.code(self.get_q(), 401), "UNAUTHORIZED")

    def test_questions_owner_scoped_and_from_interview(self):
        r = self.get_q()
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json(), interview.questions(SCENE, "free_fall"))
        self.assertEqual(self.code(self.get_q({**AUTH, "x-workspace-owner": "user_other"}), 404), "NOT_FOUND")
        self.assertEqual(self.code(self.get_q(scene="bad%20id"), 404), "NOT_FOUND")

    def test_spec_validates_via_interview_and_never_defaults(self):
        url = f"/internal/workspace/scenes/{SCENE}/spec"
        r = self.client.post(url, headers=AUTH, json={"answers": ANSWERS})
        self.assertEqual(r.status_code, 200, r.text)
        spec, scene = setup("free_fall")
        expected = interview.answers_to_spec(spec, scene, BUNDLE, ANSWERS)
        artifact = {"artifact_version": "s10-validated-setup-v1", "validation": "validate_setup",
                    "producer": "contracts/experiment/validate_experiment.py", "spec": expected, "scene": scene}
        self.assertEqual(r.json(), {"ok": True, "spec": expected, "validated_setup": artifact})
        for answers in ({"drop_height": {"text": "tall"}}, {}, ["x"]):
            with self.subTest(answers=answers):
                r = self.client.post(url, headers=AUTH, json={"answers": answers})
                self.assertEqual(self.code(r, 422), "INVALID_INPUT")
                detail = r.json()["detail"]
                self.assertIs(detail["ok"], False)
                self.assertTrue(detail["errors"])
                self.assertNotIn("spec", detail)  # no default-number spec on failure

    def test_fit_is_fitter_handle(self):
        r = self.client.post("/internal/workspace/fit", headers=AUTH, json=FIT_REQUEST)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json(), self.fit)
        bad = self.client.post("/internal/workspace/fit", headers=AUTH, json={"times": [], "bogus": 1})
        self.assertEqual(self.code(bad, 422), "INVALID_INPUT")
        self.assertEqual(bad.json()["detail"]["error"], handle({"times": [], "bogus": 1})["error"])

    def test_report_html_fallback_labelled_simulated(self):
        r = self.client.post("/internal/workspace/report", headers=AUTH, json={"spec": {"template": "free_fall"}, "fit": self.fit})
        self.assertEqual(r.status_code, 200, r.text)
        out = r.json()
        self.assertEqual(out["status"], "html-print-fallback")
        self.assertEqual(out["labels"], ["simulated"])
        self.assertIn(_fmt(self.fit["gravity"]["value"]), out["html"])  # number copied from the fit, not authored
        self.assertIn("Content-Security-Policy", out["html"])
        self.assertNotIn("what_if_label", out)
        r = self.client.post("/internal/workspace/report", headers=AUTH,
                             json={"spec": {"template": "free_fall"}, "fit": self.fit, "label": WHAT_IF_LABEL})
        self.assertEqual(r.status_code, 200, r.text)  # S15r: Q20 label passed through into the report
        self.assertEqual(r.json()["what_if_label"], WHAT_IF_LABEL)
        self.assertIn(WHAT_IF_LABEL, r.json()["html"])
        r = self.client.post("/internal/workspace/report", headers=AUTH,
                             json={"spec": {"template": "free_fall"}, "fit": self.fit, "label": "measured"})
        self.assertEqual(self.code(r, 422), "INVALID_INPUT")
        for body in ({"spec": {"template": "nope"}, "fit": self.fit}, {"spec": {"template": "free_fall"}},
                     {"spec": {"template": "free_fall"}, "fit": {"status": "error"}}, ["x"]):
            with self.subTest(body=body):
                self.assertEqual(self.code(self.client.post("/internal/workspace/report", headers=AUTH, json=body), 422), "INVALID_INPUT")

    def test_report_degree_one_fit_rejected_not_invented(self):
        linear = handle({**FIT_REQUEST, "degree": 1, "select_model": False})
        self.assertEqual(linear["status"], "ok", linear)
        r = self.client.post("/internal/workspace/report", headers=AUTH, json={"spec": {"template": "ramp"}, "fit": linear})
        self.assertEqual(self.code(r, 422), "INVALID_INPUT")  # no gravity in fit -> no report, never a filler number
        self.assertIn("gravity", r.json()["detail"]["errors"][0])

    def test_no_paid_client_imported(self):
        self.get_q()
        self.assertNotIn("modal", sys.modules)


if __name__ == "__main__":
    unittest.main()
