"""Offline regression for both DEV domains; no credentials or network."""
import io
import json
from pathlib import Path
import runpy
import unittest
from contextlib import ExitStack, redirect_stdout
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "infra/railway/dev/verify.py"
HOSTS = ("real2simulation.up.railway.app", "real2simulation.rookiecoders.tech")
CONTENT = {
    "/": "Real2Simulation", "/lab": "Test a motion model", "/library": "Demo library",
    "/sign-in": "Sign in to Real2Simulation", "/workspace/private-check": "Private workspaces require sign-in",
}
fixtures = runpy.run_path(str(VERIFIER.with_name("test_verify.py")))


def verify(broken=None):
    responses = fixtures["baseline"]()
    output = io.StringIO()
    with ExitStack() as resources:
        def transport(url, timeout):
            parsed = urlsplit(url)
            host, path = parsed.hostname, parsed.path
            if host in HOSTS:
                if broken == (host, path):
                    raise URLError("synthetic unavailable host/path")
                status = 404 if path.startswith("/workspace/") else 200
                body = "Real2Simulation " + CONTENT[path]
            else:
                assert host in ("api-dev-6091.up.railway.app", "worker-dev-984d.up.railway.app"), host
                status, data = responses[(host.split("-dev-")[0], path)]
                body = json.dumps(data)
            stream = io.BytesIO(body.encode())
            if status >= 400:
                raise resources.enter_context(HTTPError(url, status, "synthetic", {}, stream))
            stream.status = status
            return resources.enter_context(stream)

        with patch("urllib.request.urlopen", side_effect=transport), redirect_stdout(output):
            try:
                runpy.run_path(str(VERIFIER), run_name="__main__")
            except SystemExit as error:
                code = error.code
    return code, json.loads(output.getvalue())["checks"]


class DomainVerifierTests(unittest.TestCase):
    def test_both_hosts_all_paths_and_existing_service_checks(self):
        code, checks = verify()
        self.assertEqual(code, 0)
        self.assertEqual(len(checks), 17)
        self.assertTrue(all(c["pass"] for c in checks))
        self.assertEqual({c["url"] for c in checks if c["service"] == "web"},
                         {f"https://{host}{path}" for host in HOSTS for path in CONTENT})

    def test_either_host_failure_is_fatal(self):
        for host in HOSTS:
            for path in CONTENT:
                with self.subTest(host=host, path=path):
                    code, checks = verify((host, path))
                    self.assertEqual(code, 1)
                    self.assertEqual([c["url"] for c in checks if not c["pass"]], [f"https://{host}{path}"])


if __name__ == "__main__":
    unittest.main()
