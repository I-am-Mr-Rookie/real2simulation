"""Real isolated local child/CLI doubles; never import or invoke Modal."""
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import rm02_watchdog as watchdog


APP_ID = "ap-" + "A" * 22
CHILD = '''
import json, os, pathlib, signal, sys, time
mode = sys.argv[1]
path = pathlib.Path(os.environ["RM02_WATCHDOG_RECEIPT"])
path.with_name("child-clock.json").write_text(json.dumps({
    "deadline": float(os.environ["RM02_CHILD_DEADLINE"]), "observed": time.monotonic()}))
if mode == "preflight_fail":
    sys.exit(9)
if mode not in ("lost", "hang_lost"):
    path.write_text(json.dumps({"app_id": sys.argv[2]}))
if mode == "result_hang":
    path.with_name("gpu-result.json").write_text('{"synthetic": true}')
if mode in ("hang", "hang_lost", "result_hang"):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    while True:
        pass  # Deliberately blocks all asyncio/cooperative cancellation.
if mode == "fail":
    sys.exit(7)
'''
CLI = '''
import json, pathlib, sys, time
mode, command, action = sys.argv[1:4]
with pathlib.Path(__file__).with_name("calls.jsonl").open("a") as out:
    out.write(json.dumps(sys.argv[2:]) + "\\n")
calls = pathlib.Path(__file__).with_name("calls.jsonl").read_text().splitlines()
rounds = sum(json.loads(line)[1] == "info" for line in calls)
if action == "stop":
    if mode == "stop_hang":
        time.sleep(10)
    sys.exit(1 if mode in ("stop_fail_running", "already_stopped") else 0)
if action == "info":
    if mode == "info_fail":
        sys.exit(4)
    if mode == "bad_json":
        print("not json")
    else:
        print(json.dumps({"app_id": sys.argv[4] if mode != "wrong_id" else "ap-wrong",
                          "description": chr(955),
                          "lifecycle": {"state": "stopping..." if mode == "transition" and rounds == 1
                                        else "running" if mode in ("running", "stop_fail_running")
                                        else "stopped"}}, ensure_ascii=False))
else:
    print(json.dumps([{"app_id": sys.argv[5]}] if mode == "containers" or
                     (mode == "containers_transition" and rounds == 1) else []))
'''


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.child = self.root / "child.py"
        self.cli = self.root / "cli.py"
        self.child.write_text(CHILD)
        self.cli.write_text(CLI)
        self.directory = self.root / "attempt"

    def run_guard(self, child="ok", cli="ok", app_id=APP_ID):
        return watchdog.supervise([sys.executable, str(self.child), child, app_id], self.directory,
                                  total_seconds=3.5, reserve_seconds=3,
                                  cli=[sys.executable, str(self.cli), cli])

    def receipt(self):
        return json.loads((self.directory / "watchdog.json").read_text())

    def test_success_fresh_exact_id_stop_and_independent_verification(self):
        state = self.run_guard()
        self.assertTrue(state["independent_stop_confirmed"])
        self.assertTrue(state["stop_acknowledged"])
        clock = json.loads((self.directory / "child-clock.json").read_text())
        self.assertGreater(clock["deadline"], clock["observed"])
        self.assertLess(clock["deadline"] - clock["observed"], .5)
        calls = [json.loads(line) for line in (self.root / "calls.jsonl").read_text().splitlines()]
        self.assertEqual(calls, [["app", "stop", APP_ID, "--yes"],
                                 ["app", "info", APP_ID, "--json"],
                                 ["container", "list", "--app-id", APP_ID, "--json"]])

    def test_noncooperative_child_killed_but_not_mistaken_for_remote_stop(self):
        started = time.monotonic()
        with self.assertRaisesRegex(RuntimeError, "Client failed"):
            self.run_guard(child="hang")
        state = self.receipt()
        self.assertTrue(state["watchdog_fired"])
        self.assertNotEqual(state["child_returncode"], 0)
        self.assertTrue(state["independent_stop_confirmed"])
        self.assertLess(time.monotonic() - started, 3.5)

    def test_transient_state_and_containers_are_polled_on_exact_same_app(self):
        for mode in ("transition", "containers_transition"):
            with self.subTest(mode=mode):
                self.directory = self.root / mode
                calls_path = self.root / "calls.jsonl"
                if calls_path.exists():
                    calls_path.unlink()
                state = self.run_guard(cli=mode)
                self.assertTrue(state["independent_stop_confirmed"])
                self.assertEqual(state["verification_attempts"], 2)
                calls = [json.loads(line) for line in calls_path.read_text().splitlines()]
                self.assertEqual(calls, [["app", "stop", APP_ID, "--yes"]] +
                                 [["app", "info", APP_ID, "--json"],
                                  ["container", "list", "--app-id", APP_ID, "--json"]] * 2)

    def test_persistent_running_state_exhausts_original_reserve_as_incident(self):
        started = time.monotonic()
        with self.assertRaises(watchdog.ResourceIncident):
            self.run_guard(cli="running")
        state = self.receipt()
        self.assertGreaterEqual(state["verification_attempts"], 2)
        self.assertTrue(state["resource_incident"])
        self.assertTrue(state["stop_acknowledged"])
        self.assertFalse(state["independent_stop_confirmed"])
        # Expiry may occur before Popen or during its bounded wait on Windows.
        self.assertTrue(set(state["errors"]) & {
            "verification:TimeoutError", "verification:TimeoutExpired"})
        self.assertLess(time.monotonic() - started, 3.5)

    def test_cli_json_uses_utf8_even_with_cp1252_parent_environment(self):
        with patch.dict(watchdog.os.environ, PYTHONIOENCODING="cp1252"):
            self.run_guard()
        info = json.loads((self.directory / "info.stdout").read_text(encoding="utf-8"))
        self.assertEqual(info["description"], chr(955))

    def test_late_result_file_cannot_turn_killed_client_into_success(self):
        with self.assertRaisesRegex(RuntimeError, "Client failed"):
            self.run_guard(child="result_hang")
        self.assertTrue((self.directory / "gpu-result.json").exists())
        self.assertTrue(self.receipt()["watchdog_fired"])
        self.assertTrue(self.receipt()["independent_stop_confirmed"])

    def test_preflight_failure_without_id_remains_unknown_not_shutdown_success(self):
        with self.assertRaises(watchdog.ResourceIncident):
            self.run_guard(child="preflight_fail")
        state = self.receipt()
        self.assertEqual(state["child_returncode"], 9)
        self.assertTrue(state["resource_incident"])
        self.assertFalse(state["stop_attempted"])
        self.assertFalse((self.root / "calls.jsonl").exists())

    def test_missing_app_id_durable_incident_no_name_or_account_guess(self):
        with self.assertRaises(watchdog.ResourceIncident):
            self.run_guard(child="lost")
        self.assertTrue(self.receipt()["resource_incident"])
        self.assertFalse((self.root / "calls.jsonl").exists())

    def test_hung_child_lost_id_stays_incident_after_kill(self):
        with self.assertRaises(watchdog.ResourceIncident):
            self.run_guard(child="hang_lost")
        self.assertTrue(self.receipt()["watchdog_fired"])
        self.assertTrue(self.receipt()["resource_incident"])
        self.assertFalse(self.receipt()["independent_stop_confirmed"])
        self.assertFalse((self.root / "calls.jsonl").exists())

    def test_actual_guard_preserves_payload_when_cleanup_blocks_until_parent_kill(self):
        source = f'''
import asyncio, hashlib, json, os, pathlib, sys
sys.path.insert(0, {str(Path(__file__).parent.resolve())!r})
import rm02_deadline as guard
from rm02_watchdog import atomic_json
from rm02_result import persist_result
from test_rm02_deadline import Fake
guard.STARTUP_SECONDS = .05
guard.EXECUTION_SECONDS = .05
guard.CLEANUP_SECONDS = .1
guard.STOP_SECONDS = .05
guard.EXIT_SECONDS = .02
async def enter(self):
    self.app_id = {APP_ID!r}
    return self
async def blocked_exit(self, *args):
    while True:
        pass
Fake.__aenter__ = enter
Fake.__aexit__ = blocked_exit
f = Fake()
data = b"synthetic-preserved-payload"
f.result = ({{"output_bytes": len(data), "output_sha256": hashlib.sha256(data).hexdigest()}}, data)
path = pathlib.Path(os.environ["RM02_WATCHDOG_RECEIPT"])
asyncio.run(guard.guarded_probe(f, f, (), lambda state: atomic_json(path, state),
    total_seconds=float(os.environ["RM02_CHILD_BUDGET"]),
    deadline=float(os.environ["RM02_CHILD_DEADLINE"]) - .02,
    save_result=lambda result: persist_result(path.parent, result)))
'''
        self.child.write_text(source, encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Client failed"):
            # Importing the real test fake is slower than the tiny child double.
            watchdog.supervise([sys.executable, str(self.child)], self.directory,
                               total_seconds=5, reserve_seconds=3,
                               cli=[sys.executable, str(self.cli), "ok"])
        self.assertEqual((self.directory / "local/RM02-mapanything.npz").read_bytes(),
                         b"synthetic-preserved-payload")
        pending = json.loads((self.directory / "result-received.json").read_text())
        self.assertEqual(pending["remote_cleanup_status"], "PENDING")
        self.assertFalse((self.directory / "gpu-result.json").exists())
        self.assertTrue(self.receipt()["independent_stop_confirmed"])
        self.assertTrue(self.receipt()["watchdog_fired"])

    def test_invalid_id_cannot_fall_back_to_name_resolution(self):
        with self.assertRaises(watchdog.ResourceIncident):
            self.run_guard(app_id="ap-fake")
        self.assertFalse((self.root / "calls.jsonl").exists())

    def test_stop_failure_does_not_skip_fresh_verification(self):
        with self.assertRaises(watchdog.ResourceIncident):
            self.run_guard(cli="stop_fail_running")
        self.assertFalse(self.receipt()["stop_acknowledged"])
        self.assertEqual(self.receipt()["info_returncode"], 0)
        self.assertFalse(self.receipt()["independent_stop_confirmed"])

    def test_stop_nonzero_can_still_be_independently_confirmed(self):
        state = self.run_guard(cli="already_stopped")
        self.assertFalse(state["stop_acknowledged"])
        self.assertEqual(state["stop_dispatched"], "NOT_VERIFIED")
        self.assertTrue(state["independent_stop_confirmed"])

    def test_hung_stop_is_bounded_and_fresh_checks_still_run(self):
        with self.assertRaises(OSError):
            self.run_guard(cli="stop_hang")
        self.assertTrue(self.receipt()["independent_stop_confirmed"])
        self.assertFalse(self.receipt()["stop_acknowledged"])
        self.assertLess(self.receipt()["elapsed_s"], 3.5)

    def test_confirmation_failure_variants_are_incidents(self):
        for mode in ("wrong_id", "containers", "info_fail", "bad_json"):
            with self.subTest(mode=mode):
                self.directory = self.root / mode
                with self.assertRaises(watchdog.ResourceIncident):
                    self.run_guard(cli=mode)
                self.assertTrue(self.receipt()["resource_incident"])

    def test_client_failure_preserved_after_confirmed_independent_cleanup(self):
        with self.assertRaisesRegex(RuntimeError, "Client failed"):
            self.run_guard(child="fail")
        self.assertEqual(self.receipt()["child_returncode"], 7)
        self.assertTrue(self.receipt()["independent_stop_confirmed"])

    def test_broken_preflight_evidence_never_launches_client(self):
        with patch.object(watchdog, "atomic_json", side_effect=OSError("disk")), \
             patch.object(watchdog.subprocess, "Popen") as popen:
            with self.assertRaises(OSError):
                self.run_guard()
        popen.assert_not_called()

    def test_broken_later_evidence_still_runs_independent_stop(self):
        original = watchdog.atomic_json
        calls = 0
        def fail_later(path, state):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("disk")
            original(path, state)
        with patch.object(watchdog, "atomic_json", side_effect=fail_later):
            with self.assertRaises(OSError):
                self.run_guard()
        self.assertTrue(self.receipt()["independent_stop_confirmed"])
        self.assertTrue(self.receipt()["stop_process_started"])

    def test_stale_directory_rejected_before_client_launch(self):
        self.directory.mkdir()
        with patch.object(watchdog.subprocess, "Popen") as popen:
            with self.assertRaises(FileExistsError):
                self.run_guard()
        popen.assert_not_called()

    def test_nonfinite_or_impossible_budget_rejected(self):
        for total, reserve in ((0, 0), (3, 4), (float("inf"), 1), (4, float("nan"))):
            with self.assertRaises(ValueError):
                watchdog.supervise([], self.directory, total_seconds=total, reserve_seconds=reserve)

    def test_exhausted_independent_reserve_never_fakes_stop_attempt(self):
        with patch.object(watchdog.time, "monotonic", side_effect=[0, 0, 100, 100, 100]):
            with self.assertRaises(watchdog.ResourceIncident):
                self.run_guard()
        self.assertFalse(self.receipt()["stop_attempted"])
        self.assertFalse(self.receipt()["stop_process_started"])
        self.assertFalse((self.root / "calls.jsonl").exists())

    def test_atomic_replace_failure_preserves_previous_receipt(self):
        path = self.root / "atomic.json"
        watchdog.atomic_json(path, {"resource_incident": True})
        with patch.object(watchdog.os, "replace", side_effect=OSError("replace")):
            with self.assertRaises(OSError):
                watchdog.atomic_json(path, {"resource_incident": False})
        self.assertTrue(json.loads(path.read_text())["resource_incident"])


if __name__ == "__main__":
    unittest.main()
