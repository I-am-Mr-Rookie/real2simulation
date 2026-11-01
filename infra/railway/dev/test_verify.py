"""Offline synthetic transport regression for the real CLI verifier (no network)."""
import copy
import io
import json
from pathlib import Path
import runpy
import unittest
from contextlib import ExitStack, redirect_stdout
from urllib.error import HTTPError
from urllib.parse import urlsplit
from unittest.mock import patch

REVISION = "300cd2096f9e32bcdf3433520b36b67f709df0d5"
API_REVISION = "db6060d2a994f8f1f36f2507a64b07ecdf7a0c72"
PATHS = ("/health/live", "/health/ready", "/api/version")
ENDPOINTS = [(service, path) for service in ("api", "worker") for path in PATHS]
INTERNAL = ("api", "/internal/workspace/jobs/job_" + "0" * 32)


def baseline():
    responses = {}
    for service, path in ENDPOINTS:
        data = {"service": service, "revision": API_REVISION if service == "api" else REVISION}
        status = 200
        if path != "/api/version":
            data["status"] = "ok"
        if path == "/health/ready":
            data["dependencies"] = {"redis": "ok", "bucket": "ok"}
            if service == "api":
                data["dependencies"]["postgres"] = "ok"
            else:
                data["dependencies"]["heartbeat"] = "unavailable"
                data["status"] = "unavailable"
                status = 503
        responses[(service, path)] = (status, data)
    responses[INTERNAL] = (401, {"detail": {"code": "UNAUTHORIZED", "message": "synthetic"}})
    return responses


def verify(responses):
    resources = ExitStack()

    def transport(url, timeout):
        parsed = urlsplit(url)
        service = parsed.hostname.split("-dev-")[0]
        if service == "web":
            status = 404 if parsed.path.startswith("/workspace/") else 200
            body = "Real2Simulation " + {
                "/": "", "/library": "Demo library",
                "/sign-in": "Sign in to Real2Simulation",
                "/workspace/private-check": "Private workspaces require sign-in",
            }[parsed.path]
        else:
            status, data = responses[(service, parsed.path)]
            body = json.dumps(data)
        stream = io.BytesIO(body.encode())
        if status >= 400:
            raise resources.enter_context(HTTPError(url, status, "synthetic", {}, stream))
        stream.status = status
        return resources.enter_context(stream)

    output = io.StringIO()
    with resources, patch("urllib.request.urlopen", side_effect=transport), redirect_stdout(output):
        try:
            runpy.run_path(str(Path(__file__).with_name("verify.py")), run_name="__main__")
        except SystemExit as error:
            code = error.code
        else:
            raise AssertionError("verifier did not exit")
    return code, json.loads(output.getvalue())["checks"]


class VerifyTests(unittest.TestCase):
    def assert_rejected(self, endpoint, mutate):
        responses = copy.deepcopy(baseline())
        status, data = responses[endpoint]
        responses[endpoint] = mutate(status, data)
        code, checks = verify(responses)
        self.assertEqual(code, 1)
        failures = [c for c in checks if not c["pass"]]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["service"], endpoint[0])
        self.assertTrue(failures[0]["url"].endswith(endpoint[1]))

    def test_baseline_including_statusless_version_and_worker_503(self):
        code, checks = verify(baseline())
        self.assertEqual(code, 0)
        self.assertEqual(len(checks), 11)
        self.assertTrue(all(c["pass"] for c in checks))

    def test_internal_workspace_route_must_reject_missing_token(self):
        for status, data in ((200, {"job": {}}), (404, {"detail": {"code": "NOT_FOUND"}}), (401, {"detail": "other"})):
            with self.subTest(status=status):
                self.assert_rejected(INTERNAL, lambda *_: (status, data))

    def test_wrong_or_missing_service(self):
        for endpoint in ENDPOINTS:
            for value in ("WRONG-SERVICE", None):
                with self.subTest(endpoint=endpoint, value=value):
                    def mutate(status, data):
                        if value is None:
                            data.pop("service")
                        else:
                            data["service"] = value
                        return status, data
                    self.assert_rejected(endpoint, mutate)

    def test_wrong_or_missing_health_status(self):
        for endpoint in [e for e in ENDPOINTS if e[1] != "/api/version"]:
            opposite = "ok" if endpoint == ("worker", "/health/ready") else "unavailable"
            for value in ("WRONG-STATUS", None, "OK", opposite):
                with self.subTest(endpoint=endpoint, value=value):
                    def mutate(status, data):
                        if value is None:
                            data.pop("status")
                        else:
                            data["status"] = value
                        return status, data
                    self.assert_rejected(endpoint, mutate)

    def test_wrong_or_missing_revision(self):
        for endpoint in ENDPOINTS:
            for value in ("0" * 40, None):
                with self.subTest(endpoint=endpoint, value=value):
                    def mutate(status, data):
                        if value is None:
                            data.pop("revision")
                        else:
                            data["revision"] = value
                        return status, data
                    self.assert_rejected(endpoint, mutate)

    def test_http_codes_remain_exact(self):
        for endpoint in ENDPOINTS:
            with self.subTest(endpoint=endpoint):
                self.assert_rejected(endpoint, lambda status, data: (200 if status == 503 else 503, data))

    def test_readiness_dependencies_remain_exact(self):
        for service in ("api", "worker"):
            endpoint = service, "/health/ready"
            names = baseline()[endpoint][1]["dependencies"]
            for name in names:
                for missing in (False, True):
                    with self.subTest(service=service, name=name, missing=missing):
                        def mutate(status, data):
                            if missing:
                                data["dependencies"].pop(name)
                            else:
                                data["dependencies"][name] = "ok" if name == "heartbeat" else "unavailable"
                            return status, data
                        self.assert_rejected(endpoint, mutate)
            for value in (None, {}, {**names, "unexpected": "ok"}):
                with self.subTest(service=service, dependencies=value):
                    def mutate(status, data):
                        if value is None:
                            data.pop("dependencies")
                        else:
                            data["dependencies"] = value
                        return status, data
                    self.assert_rejected(endpoint, mutate)

    def test_non_object_json_fails_closed(self):
        for value in (None, [], "ok"):
            with self.subTest(value=value):
                self.assert_rejected(("api", "/health/live"), lambda status, data: (status, value))


if __name__ == "__main__":
    unittest.main()
