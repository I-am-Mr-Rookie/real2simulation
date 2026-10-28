"""Independent process deadline for the one RM02 client. No Modal import here."""
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

from rm02_deadline import TOTAL_SECONDS, CLEANUP_SECONDS, STOP_SECONDS, ResourceIncident


def atomic_json(path, state):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def supervise(command, directory, *, total_seconds=TOTAL_SECONDS,
              reserve_seconds=CLEANUP_SECONDS, cli=None):
    """Test seam accepts isolated local children; production entry uses only RM02."""
    if not (math.isfinite(total_seconds) and math.isfinite(reserve_seconds)
            and total_seconds > reserve_seconds > 0):
        raise ValueError("Need a finite positive child budget and independent reserve")
    started = time.monotonic()
    deadline = started + total_seconds
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)  # Never trust a previous run's ID.
    worker_path = directory / "worker.json"
    phase_path = directory / "lifecycle-phase.json"
    phase_token = uuid.uuid4().hex
    receipt_path = directory / "watchdog.json"
    state = {"total_budget_s": total_seconds, "independent_reserve_s": reserve_seconds,
             "child_deadline_monotonic": deadline - reserve_seconds,
             "watchdog_fired": False, "stop_attempted": False,
             "stop_process_started": False, "stop_dispatched": "NOT_VERIFIED",
             "stop_acknowledged": False, "independent_stop_confirmed": False,
             "resource_incident": True, "preflight_validation_failed": False,
             "no_remote_creation_confirmed": False, "phase_token": phase_token,
             "phase_receipt": "NOT_VERIFIED", "errors": []}
    atomic_json(receipt_path, state)  # Storage must work before any setup can start.

    def emit():
        try:
            atomic_json(receipt_path, state)
        except OSError as exc:
            state["errors"].append("evidence:" + type(exc).__name__)

    env = dict(os.environ, RM02_WATCHDOG_RECEIPT=str(worker_path.resolve()),
               RM02_PHASE_RECEIPT=str(phase_path.resolve()),
               RM02_PHASE_TOKEN=phase_token,
               RM02_CHILD_BUDGET=str(total_seconds - reserve_seconds),
               RM02_CHILD_DEADLINE=str(deadline - reserve_seconds))
    child = None
    preflight_validation_failure = False
    try:
        with (directory / "client.log").open("wb") as log:
            child = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
            state["child_pid"] = child.pid
            emit()
            try:
                child.wait(timeout=max(.001, deadline - reserve_seconds - time.monotonic()))
            except subprocess.TimeoutExpired:
                state["watchdog_fired"] = True
                child.kill()
                child.wait(timeout=min(2, reserve_seconds / 10))
            state["child_returncode"] = child.returncode
    except (OSError, subprocess.SubprocessError) as exc:
        state["errors"].append("child:" + type(exc).__name__)
    finally:
        if child is not None and child.poll() is None:
            try:
                child.kill()
                child.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired) as exc:
                state["errors"].append("child:kill_not_confirmed:" + type(exc).__name__)
        # Independent fresh processes, not the blocked event loop/client connection.
        preflight_candidate = False
        phase_invalid = False
        try:
            phase = json.loads(phase_path.read_text(encoding="utf-8"))
            if (phase.get("version") != 1 or phase.get("token") != phase_token
                    or phase.get("pid") != child.pid
                    or type(phase.get("remote_creation_started")) is not bool
                    or phase.get("phase") not in ("preflight_failed", "preflight_validated",
                                                   "remote_creation_started")
                    or not isinstance(phase.get("history"), list)):
                raise ValueError("Invalid lifecycle phase receipt")
            expected = {
                "preflight_failed": (["preflight_failed"], False),
                "preflight_validated": (["preflight_validated"], False),
                "remote_creation_started": (["preflight_validated", "remote_creation_started"], True),
            }[phase["phase"]]
            if phase["history"] != expected[0] or phase["remote_creation_started"] is not expected[1]:
                raise ValueError("Invalid lifecycle phase history")
            state["phase_receipt"] = "VALID_" + phase["phase"].upper()
            preflight_candidate = phase["phase"] == "preflight_failed"
        except (OSError, ValueError, AttributeError, TypeError, json.JSONDecodeError) as exc:
            if isinstance(exc, OSError) and not phase_path.exists():
                state["phase_receipt"] = "NOT_VERIFIED"
            else:
                phase_invalid = True
                state["errors"].append("phase:unknown_remote_state:" + type(exc).__name__)
                state["phase_receipt"] = "INVALID_OR_MISSING"
        try:
            worker = json.loads(worker_path.read_text(encoding="utf-8"))
            app_id = worker["app_id"]
            if not isinstance(app_id, str) or not re.fullmatch(r"ap-[a-zA-Z0-9]{22}", app_id):
                raise ValueError("Missing exact SDK-format own app ID")
            state["app_id"] = app_id
        except (OSError, ValueError, KeyError, TypeError) as exc:
            if not preflight_candidate:
                state["errors"].append("app_id:unknown_remote_state:" + type(exc).__name__)
        else:
            cli = cli if cli is not None else [sys.executable, "-m", "modal"]

            def invoke(name, args, allowance):
                remaining = min(allowance, deadline - time.monotonic() - min(2, reserve_seconds / 10))
                if remaining <= 0:
                    raise TimeoutError("Independent reserve exhausted")
                with (directory / (name + ".stdout")).open("wb") as out, \
                     (directory / (name + ".stderr")).open("wb") as err:
                    if name == "stop":
                        state["stop_attempted"] = True
                        emit()
                    process = subprocess.Popen([*cli, *args], stdout=out, stderr=err,
                                               env=dict(os.environ, PYTHONIOENCODING="utf-8"))
                    if name == "stop":
                        state["stop_process_started"] = True
                    try:
                        process.wait(timeout=remaining)
                    except BaseException:
                        process.kill()
                        process.wait(timeout=1)
                        raise
                state[name + "_returncode"] = process.returncode
                return process.returncode

            try:
                if invoke("stop", ["app", "stop", app_id, "--yes"],
                          min(STOP_SECONDS, reserve_seconds / 3)) == 0:
                    state.update(stop_dispatched=True, stop_acknowledged=True)
            except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
                state["errors"].append("stop:" + type(exc).__name__)
            # Even a failed/lost stop response must not skip the independent check.
            try:
                state["verification_attempts"] = 0
                while True:
                    info_code = invoke("info", ["app", "info", app_id, "--json"],
                                       min(15, reserve_seconds / 3))
                    containers_code = invoke("containers", ["container", "list", "--app-id", app_id,
                                                            "--json"], min(15, reserve_seconds / 3))
                    info = json.loads((directory / "info.stdout").read_text(encoding="utf-8"))
                    containers = json.loads((directory / "containers.stdout").read_text(encoding="utf-8"))
                    state["verification_attempts"] += 1
                    state["independent_stop_confirmed"] = (
                        info_code == containers_code == 0 and info.get("app_id") == app_id
                        and info.get("lifecycle", {}).get("state") == "stopped"
                        and containers == [])
                    emit()
                    if state["independent_stop_confirmed"]:
                        break
                    # Provider state may lag; never extend the original parent reserve.
                    time.sleep(min(1, max(0, deadline - time.monotonic()
                                          - min(2, reserve_seconds / 10))))
            except (OSError, subprocess.SubprocessError, TimeoutError, ValueError, AttributeError) as exc:
                state["errors"].append("verification:" + type(exc).__name__)
        if (preflight_candidate and state.get("child_returncode") != 0
                and not state["watchdog_fired"] and "app_id" not in state
                and "function_call_id" not in state and not state["errors"]):
            state["preflight_validation_failed"] = True
            state["no_remote_creation_confirmed"] = True
            state["resource_incident"] = False
            preflight_validation_failure = True
        if preflight_validation_failure:
            state["resource_incident"] = False
        else:
            state["resource_incident"] = not state["independent_stop_confirmed"]
        if phase_invalid:
            state["independent_stop_confirmed"] = False
            state["resource_incident"] = True
        state["elapsed_s"] = time.monotonic() - started
        emit()
    if preflight_validation_failure:
        state["resource_incident"] = False
        state["independent_stop_confirmed"] = False
        emit()
        raise RuntimeError("Preflight validation failed; no remote creation admitted; inspect " + str(receipt_path))
    if state["resource_incident"]:
        raise ResourceIncident("Independent stop unconfirmed; inspect " + str(receipt_path))
    if state["errors"]:
        raise OSError("Cleanup confirmed but watchdog errors; inspect " + str(receipt_path))
    if state["watchdog_fired"] or state.get("child_returncode") != 0:
        raise RuntimeError("Client failed; independent stop confirmed; inspect " + str(receipt_path))
    return state


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    directory = root / "evidence/S05/S05b/recovery8" / ("attempt-" + uuid.uuid4().hex)
    supervise([sys.executable, str(Path(__file__).with_name("modal_rm02.py"))], directory)
