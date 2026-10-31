import os
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Build.api.lab import create_router

app = FastAPI(); app.include_router(create_router()); client = TestClient(app)
URL, TOKEN = "/internal/lab/bridge", "t" * 32


class ApiLabBridgeTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict(os.environ, {"WORKSPACE_INTERNAL_TOKEN": TOKEN}); patcher.start(); self.addCleanup(patcher.stop)

    def post(self, body, token=TOKEN):
        return client.post(URL, content=body, headers={"x-workspace-token": token} if token else {})

    def test_token_required_and_fail_closed_when_unset(self):
        self.assertEqual(self.post(b"{}", token=None).status_code, 401)
        self.assertEqual(self.post(b"{}", token="wrong").status_code, 401)
        with patch.dict(os.environ, {"WORKSPACE_INTERNAL_TOKEN": ""}):
            self.assertEqual(self.post(b"{}").status_code, 401)

    def test_schema_size_and_json_guards(self):
        self.assertEqual(self.post(b"{bad").json()["error"]["code"], "invalid_json")
        self.assertEqual(self.post(b" " * 1_000_001).json()["error"]["code"], "request_too_large")
        self.assertEqual(self.post(b'{"action":"start","template":"free_fall","extra":1}').json()["error"]["code"], "invalid_start_request")
        self.assertEqual(self.post(b'{"action":"start","template":"orbit"}').json()["error"]["code"], "unsupported_template")
        self.assertEqual(self.post(b'{"action":"read_file"}').json()["error"]["code"], "unsupported_action")

    def test_real_start_and_fit(self):
        start = self.post(b'{"action":"start","template":"free_fall","mystery":false}').json()
        self.assertEqual(start["status"], "ok"); self.assertEqual(start["source"], "simulated")
        import json
        fit = self.post(json.dumps({"action": "fit", "observations": start["observations"]}).encode()).json()
        self.assertEqual(fit["status"], "ok")


if __name__ == "__main__":
    unittest.main()
