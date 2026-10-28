"""Review probe: local doubles only; never imports or invokes Modal.

Run from Build/reconstruction/spike:  python <this file>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import test_rm02_watchdog as t  # reuse the existing isolated child/CLI doubles

out = {}
for label, app_arg in (("malformed_id", "not-an-app-id"), ("empty_id", "")):
    case = t.WatchdogTests("test_contradictory_app_id_never_allows_preflight_success")
    case.setUp()
    try:
        try:
            case.run_guard(child="preflight_conflict", app_id=app_arg,
                           total_seconds=5, reserve_seconds=3)
            outcome = "returned"
        except Exception as exc:  # record which classification the parent chose
            outcome = type(exc).__name__ + ": " + str(exc).split(";")[0]
        state = case.receipt()
        out[label] = {"outcome": outcome,
                      "worker_json_present": (case.directory / "worker.json").exists(),
                      "preflight_validation_failed": state["preflight_validation_failed"],
                      "no_remote_creation_confirmed": state["no_remote_creation_confirmed"],
                      "resource_incident": state["resource_incident"],
                      "errors": state["errors"]}
    finally:
        case.temp.cleanup()
print(json.dumps(out, indent=2))
