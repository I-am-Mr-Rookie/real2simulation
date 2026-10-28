"""Health contracts only: no database, model, credentials or real worker loop."""

import importlib
import json
import os
import socket
import threading
import time
import unittest
from unittest.mock import patch
from urllib.request import urlopen

import uvicorn
from fastapi.testclient import TestClient


MODULES = ("Build.api.health.app", "Build.worker.health.app")


class HealthTests(unittest.TestCase):
    def applications(self):
        for module in MODULES:
            yield importlib.import_module(module)

    def test_liveness_is_200_without_downstream_configuration(self):
        with patch.dict(os.environ, {}, clear=True):
            for module in self.applications():
                with self.subTest(service=module.SERVICE), TestClient(module.create_app()) as client:
                    response = client.get("/health/live")
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json(), {
                        "service": module.SERVICE, "status": "ok", "revision": "unknown",
                    })

    def test_readiness_cannot_claim_missing_integrations_are_healthy(self):
        expected = {
            "api": {"postgres": "not-configured", "redis": "not-configured", "bucket": "not-configured"},
            "worker": {"redis": "not-configured", "bucket": "not-configured", "heartbeat": "unavailable"},
        }
        with patch.dict(os.environ, {}, clear=True):
            for module in self.applications():
                with self.subTest(service=module.SERVICE), TestClient(module.create_app()) as client:
                    response = client.get("/health/ready")
                    self.assertEqual(response.status_code, 503)
                    self.assertEqual(response.json(), {
                        "service": module.SERVICE, "status": "unavailable",
                        "revision": "unknown", "dependencies": expected[module.SERVICE],
                    })

    def test_config_presence_cannot_fabricate_dependency_or_worker_success(self):
        with patch.dict(os.environ, {"DATABASE_URL": "secret-canary", "REDIS_URL": "secret-canary",
                                     "BUCKET_URL": "secret-canary"}, clear=True):
            for module in self.applications():
                with self.subTest(service=module.SERVICE), TestClient(module.create_app()) as client:
                    response = client.get("/health/ready")
                    self.assertEqual(response.status_code, 503)
                    self.assertNotIn("secret-canary", response.text)
                    self.assertNotIn("ok", response.json()["dependencies"].values())

    def test_version_only_publishes_valid_revision_not_raw_environment(self):
        for revision, want in (("a" * 40, "a" * 40), ("A" * 40, "a" * 40),
                               ("short", "unknown"), ("secret-canary\n", "unknown")):
            with patch.dict(os.environ, {"RAILWAY_GIT_COMMIT_SHA": revision}, clear=True):
                for module in self.applications():
                    with self.subTest(service=module.SERVICE, revision=revision), TestClient(module.create_app()) as client:
                        self.assertEqual(client.get("/api/version").json(), {
                            "service": module.SERVICE, "revision": want,
                        })
                        self.assertEqual(client.get("/health/live").json()["revision"], want)

    def test_health_has_no_scene_or_job_api(self):
        for module in self.applications():
            with self.subTest(service=module.SERVICE), TestClient(module.create_app()) as client:
                self.assertEqual(client.get("/scenes/private").status_code, 404)
                self.assertEqual(client.post("/jobs", json={}).status_code, 404)

    def test_both_services_respond_over_real_loopback_http(self):
        for module in self.applications():
            with self.subTest(service=module.SERVICE), socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
                server = uvicorn.Server(uvicorn.Config(module.create_app(), log_level="error"))
                thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
                thread.start()
                try:
                    deadline = time.monotonic() + 5
                    while not server.started and thread.is_alive() and time.monotonic() < deadline:
                        time.sleep(0.01)
                    self.assertTrue(server.started, "health server failed to start within 5s")
                    with urlopen(f"http://127.0.0.1:{port}/health/live", timeout=2) as response:
                        self.assertEqual(response.status, 200)
                        self.assertEqual(json.load(response)["service"], module.SERVICE)
                finally:
                    server.should_exit = True
                    thread.join(timeout=5)
                self.assertFalse(thread.is_alive(), "health server leaked after shutdown")


if __name__ == "__main__":
    unittest.main()
