"""Deterministic offline coverage observations; no product writes or live transport."""
import ast
from concurrent.futures import Future
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import URLError
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
observations = []


def observe(name, **details):
    observations.append(dict(name=name, **details))


spec = importlib.util.spec_from_file_location("review_dependency_health", ROOT / "Build/api/health/dependencies.py")
deps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deps)
now = [0.0]
answers = iter((True, False, True))
calls = []
def submit(fn, name, env):
    calls.append(name)
    future = Future()
    future.set_result("ok" if next(answers) else "unavailable")
    return future

with patch.object(deps, "_POOL", SimpleNamespace(submit=submit)), patch.object(deps.time, "monotonic", lambda: now[0]):
    health = deps.DependencyHealth({"R2S_ENVIRONMENT": "development", "RAILWAY_ENVIRONMENT_NAME": "dev",
                                  "REDIS_URL": "redis://synthetic.invalid"}, ("redis",))
    states = []
    for instant in (0, 4.999, 5, 9.999, 10):
        now[0] = instant
        states.append(health.check()["redis"])
    assert states == ["ok", "ok", "unavailable", "unavailable", "ok"], states
    assert calls == ["redis"] * 3, calls
    observe("cache-expiry-failure-recovery", times=[0, 4.999, 5, 9.999, 10], states=states, submissions=len(calls))

for answer in (1, "ok", {}, None, True, False):
    with patch.object(deps, "probe", return_value=answer):
        state = deps._safe_probe("redis", {})
        assert state == ("ok" if answer is True else "unavailable")
        observe("strict-probe-success", synthetic_type=type(answer).__name__, result=state)

test_spec = importlib.util.spec_from_file_location("review_verify_helpers", ROOT / "infra/railway/dev/test_verify.py")
helpers = importlib.util.module_from_spec(test_spec)
test_spec.loader.exec_module(helpers)
code, checks = helpers.verify(helpers.baseline())
assert code == 0 and len(checks) == 10
observe("current-hardened-verifier-baseline", exit=code, checks=len(checks))
for value in (None, [], "ok", 1, True):
    responses = helpers.baseline()
    responses[("api", "/health/live")] = (200, value)
    code, checks = helpers.verify(responses)
    failures = [c for c in checks if not c["pass"]]
    assert code == 1 and len(checks) == 10 and len(failures) == 1
    observe("non-object-json", synthetic_type=type(value).__name__, exit=code, failures=len(failures))

for exception in (URLError("synthetic transport failure"), TimeoutError("synthetic timeout"),
                  UnicodeDecodeError("utf8", b"\xff", 0, 1, "synthetic")):
    output = io.StringIO()
    with patch("urllib.request.urlopen", side_effect=exception), redirect_stdout(output):
        try:
            runpy.run_path(str(ROOT / "infra/railway/dev/verify.py"), run_name="__main__")
        except SystemExit as result:
            code = result.code
    checks = json.loads(output.getvalue())["checks"]
    assert code == 1 and len(checks) == 10 and all(not c["pass"] for c in checks)
    assert all(c["error_type"] == type(exception).__name__ for c in checks)
    observe("transport-exception-isolation", error_type=type(exception).__name__, failed_checks=len(checks))

for case in ("malformed-json", "invalid-utf8", "web-missing-title", "web-wrong-content", "private-wrong-status"):
    def transport(url, timeout):
        assert timeout == 20
        parsed = urlsplit(url)
        service = parsed.hostname.split("-dev-")[0]
        status = 200
        if service != "web":
            status, body = helpers.baseline()[(service, parsed.path)]
            body = json.dumps(body).encode()
            if service == "api" and parsed.path == "/health/live":
                if case == "malformed-json": body = b"{not-json"
                if case == "invalid-utf8": body = b"\xff"
        else:
            status = 404 if parsed.path.startswith("/workspace/") else 200
            body = "Real2Simulation " + {
                "/": "", "/library": "No demos are published yet",
                "/sign-in": "Sign-in unavailable",
                "/workspace/private-check": "Private workspaces remain unavailable",
            }[parsed.path]
            if parsed.path == "/library":
                if case == "web-missing-title": body = "No demos are published yet"
                if case == "web-wrong-content": body = "Real2Simulation unrelated page"
            if case == "private-wrong-status" and parsed.path.startswith("/workspace/"):
                status = 200
            body = body.encode()
        response = io.BytesIO(body)
        response.status = status
        return response
    output = io.StringIO()
    with patch("urllib.request.urlopen", side_effect=transport), redirect_stdout(output):
        try:
            runpy.run_path(str(ROOT / "infra/railway/dev/verify.py"), run_name="__main__")
        except SystemExit as result:
            code = result.code
    checks = json.loads(output.getvalue())["checks"]
    failures = [c for c in checks if not c["pass"]]
    assert code == 1 and len(checks) == 10 and len(failures) == 1, case
    observe(case, exit=code, failed_service=failures[0]["service"],
            error_type=failures[0].get("error_type"), checks=len(checks))

sources = [
    "Build/web/src/auth/access.mjs", "Build/web/src/auth/config.mjs",
    "Build/web/src/auth/access.test.mjs", "Build/web/src/auth/config.test.mjs",
    "Build/web/src/auth/server-access.js", "Build/web/src/auth/server-config.js",
    "Build/api/health/dependencies.py", "Build/api/health/app.py",
    "Build/worker/health/app.py", "Build/api/health/test_dependencies.py",
    "Build/api/health/test_health.py", "infra/railway/dev/verify.py",
    "infra/railway/dev/test_verify.py", "infra/railway/dev/stage.py",
]
manifest = {path: hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest() for path in sources}
test_map = {}
for path in sources:
    if path.endswith(".py") and "/test_" in path:
        tree = ast.parse((ROOT / path).read_text())
        test_map[path] = [{"name": node.name, "line": node.lineno} for node in ast.walk(tree)
                          if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
result = dict(observations=observations, source_hashes_lf_normalized=manifest,
              existing_python_tests=test_map, live_transport_calls=0, product_writes=0)
(HERE / "observations.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(f"PASS {len(observations)} offline observations; source hashes and test map saved")
