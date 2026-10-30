"""Actual local synthetic rebuilds plus admission, provenance and retry boundaries."""
import copy
import hashlib
from importlib import import_module
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from threading import Event, Thread
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests/spec"))
from test_setup_validation import BUNDLE, setup
from Build.agent.tools import render, tool_backed
from contracts.agent.validate import AgentContractError, validate_response, validate_tool_output

r = import_module("Build.sidebar-tools.rebuild")
c = r.contracts
INSTRUMENTS = dict(time_resolution_s=1e-6, time_uncertainty_s=2e-6, time_bias_s=0,
                   distance_resolution_m=1e-6, distance_uncertainty_m=3e-6, distance_bias_m=0)


class RebuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.base, self.scene = setup()
        self.scene_path = self.folder / "scene.json"
        self.scene_path.write_text(json.dumps(self.scene), encoding="utf-8")
        shutil.copyfile(BUNDLE / "points.ply", self.folder / "points.ply")
        self.session = self.make_session()

    def make_session(self):
        return r.RebuildSession(self.base, scene_path=self.scene_path,
                               instruments=INSTRUMENTS, scratch_dir=self.folder)

    def patch_call(self, **simulation):
        spec = self.session.current_spec
        return {"schema_version": c.VERSION, "id": "patch_one", "tool": "spec.patch",
                "scene_id": spec["scene"]["scene_id"], "arguments": {
                    "base_spec_sha256": c.spec_sha256(spec), "patch": {
                        "simulation": {**copy.deepcopy(spec["simulation"]), "seed": 12, **simulation}}}}

    def rebuild_call(self, spec=None, call_id="rebuild_one"):
        spec = self.session.current_spec if spec is None else copy.deepcopy(spec)
        return {"schema_version": c.VERSION, "id": call_id, "tool": "scene.rebuild",
                "scene_id": spec["scene"]["scene_id"], "arguments": {
                    "spec": spec, "spec_sha256": c.spec_sha256(spec)}}

    def admit(self):
        return self.session.handle(self.patch_call())

    def assert_error(self, result, code):
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["payload"]["code"], code)
        self.assertEqual(result["tool_outputs"], [])

    def test_no_patch_or_invalid_patch_cannot_run(self):
        with patch.object(r, "run_lab") as execute:
            self.assert_error(self.session.handle(self.rebuild_call()), "not_ready")
            bad = self.patch_call()
            bad["arguments"]["patch"]["simulation"]["duration"]["value"] = -1
            with self.assertRaises(c.SidebarContractError):
                self.session.handle(bad)
            self.assert_error(self.session.handle(self.rebuild_call()), "not_ready")
            execute.assert_not_called()
        self.assertEqual(self.session.current_spec, self.base)

    def test_stale_revision_and_forged_valid_spec_do_not_run(self):
        old = self.rebuild_call()
        self.admit()
        forged = self.session.current_spec
        forged["simulation"]["seed"] = 29
        with patch.object(r, "run_lab") as execute:
            self.assert_error(self.session.handle(old), "stale_spec")
            self.assert_error(self.session.handle(self.rebuild_call(forged)), "stale_spec")
            bad = self.rebuild_call()
            bad["arguments"]["spec_sha256"] = "0" * 64
            with self.assertRaises(c.SidebarContractError):
                self.session.handle(bad)
            execute.assert_not_called()

    def test_scene_and_asset_drift_rechecked_before_execution(self):
        self.admit()
        with patch.object(r, "run_lab") as execute:
            altered = copy.deepcopy(self.scene)
            altered["label"] = "Changed trusted scene"
            self.scene_path.write_text(json.dumps(altered), encoding="utf-8")
            self.assert_error(self.session.handle(self.rebuild_call()), "stale_spec")
            self.scene_path.write_text(json.dumps(self.scene), encoding="utf-8")
            (self.folder / "points.ply").write_text("tampered", encoding="utf-8")
            self.assert_error(self.session.handle(self.rebuild_call()), "not_ready")
            execute.assert_not_called()

    def test_actual_ballistic_pipeline_hashes_and_agent_citations(self):
        for template in ("free_fall", "projectile"):
            with self.subTest(template=template):
                self.base, self.scene = setup(template)
                self.scene_path.write_text(json.dumps(self.scene), encoding="utf-8")
                self.session = self.make_session()
                before = copy.deepcopy((self.base, self.scene, INSTRUMENTS))
                accepted = self.admit()
                request = self.rebuild_call(call_id="r" * 64)
                result = self.session.handle(request)
                self.assertEqual(result["status"], "ok", result)
                self.assertEqual(result["payload"]["state"], "completed")
                self.assertEqual(result["payload"]["spec_sha256"], accepted["payload"]["spec_sha256"])
                self.assertEqual([out["tool"] for out in result["tool_outputs"]], ["simulator", "fitter"])
                for output in result["tool_outputs"]:
                    self.assertEqual(validate_tool_output(output), output)
                    raw = json.dumps(output, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")
                    self.assertEqual(result["payload"]["output_sha256"][output["id"]], hashlib.sha256(raw).hexdigest())
                    for quantity in output["quantities"].values():
                        self.assertEqual(quantity["source"]["label"], "simulated")
                        self.assertIn(accepted["payload"]["spec_sha256"], quantity["source"]["evidence"])
                quantities = result["tool_outputs"][0]["quantities"]
                self.assertEqual(quantities["duration"]["uncertainty"], INSTRUMENTS["time_uncertainty_s"])
                self.assertEqual(quantities["drop"]["uncertainty"], INSTRUMENTS["distance_uncertainty_m"])
                response = tool_backed(request["scene_id"], result["tool_outputs"])
                self.assertIn("simulated", render(response, result["tool_outputs"], request["scene_id"]))
                response["segments"].append({"type": "text", "text": "Gravity is 9.81"})
                with self.assertRaises(AgentContractError):
                    validate_response(response, result["tool_outputs"], request["scene_id"])
                self.assertEqual((self.base, self.scene, INSTRUMENTS), before)
                self.assertFalse(list(self.folder.glob("sidebar-rebuild-*")))

    def test_failure_is_sanitized_and_retry_runs_then_caches(self):
        self.admit()
        call = self.rebuild_call()
        for error in (ValueError("private detail"), OSError("private detail"),
                      subprocess.TimeoutExpired("private command", 30)):
            with patch.object(r, "run_lab", side_effect=error) as execute:
                result = self.session.handle(call)
                self.assert_error(result, "internal_error")
                self.assertNotIn("private", json.dumps(result))
                execute.assert_called_once()
        with patch.object(r, "run_lab", wraps=r.run_lab) as execute:
            result = self.session.handle(call)
            self.assertEqual(result["status"], "ok", result)
            snapshot = copy.deepcopy(result)
            result["tool_outputs"][0]["quantities"].clear()
            again = self.session.handle(call)
            self.assertEqual(again, snapshot)
            retry = self.session.handle(self.rebuild_call(call_id="retry_two"))
            self.assertEqual(retry["payload"], snapshot["payload"])
            self.assertEqual(retry["call_id"], "retry_two")
            execute.assert_called_once()

    def test_new_patch_invalidates_completed_cache(self):
        self.admit()
        old_call = self.rebuild_call()
        self.assertEqual(self.session.handle(old_call)["status"], "ok")
        self.session.handle(self.patch_call(seed=13))
        with patch.object(r, "run_lab", wraps=r.run_lab) as execute:
            self.assert_error(self.session.handle(old_call), "stale_spec")
            self.assertEqual(self.session.handle(self.rebuild_call())["status"], "ok")
            execute.assert_called_once()

    def test_changed_duration_reaches_simulator_and_changes_receipts(self):
        self.admit()
        first = self.session.handle(self.rebuild_call())
        duration = copy.deepcopy(self.session.current_spec["simulation"]["duration"])
        # Stop-plane crossing can end a long configured run early; shorten the actual run.
        duration["value"] = first["tool_outputs"][0]["quantities"]["duration"]["value"] / 2
        self.session.handle(self.patch_call(duration=duration))
        second = self.session.handle(self.rebuild_call(call_id="shorter_run"))
        self.assertEqual(second["status"], "ok", second)
        self.assertLess(second["tool_outputs"][0]["quantities"]["duration"]["value"],
                        first["tool_outputs"][0]["quantities"]["duration"]["value"])
        self.assertNotEqual(second["payload"]["spec_sha256"], first["payload"]["spec_sha256"])
        self.assertNotEqual(second["payload"]["output_sha256"], first["payload"]["output_sha256"])

    def test_rejected_patch_does_not_invalidate_completed_receipt(self):
        self.admit()
        call = self.rebuild_call()
        completed = self.session.handle(call)
        stale = self.patch_call()
        stale["arguments"]["base_spec_sha256"] = "0" * 64
        with self.assertRaises(c.SidebarContractError):
            self.session.handle(stale)
        with patch.object(r, "run_lab") as execute:
            self.assertEqual(self.session.handle(call), completed)
            execute.assert_not_called()

    def test_missing_scene_file_and_bad_instruments_return_safe_errors(self):
        self.admit()
        self.scene_path.unlink()
        self.assert_error(self.session.handle(self.rebuild_call()), "not_ready")
        self.scene_path.write_text(json.dumps(self.scene), encoding="utf-8")
        self.session = r.RebuildSession(self.base, scene_path=self.scene_path,
                                       instruments={}, scratch_dir=self.folder)
        self.admit()
        self.assert_error(self.session.handle(self.rebuild_call()), "internal_error")
        self.assertFalse(list(self.folder.glob("sidebar-rebuild-*")))

    def test_library_search_is_not_silently_dispatched(self):
        call = {"schema_version": c.VERSION, "id": "search_one", "tool": "library.search",
                "scene_id": self.base["scene"]["scene_id"], "arguments": {
                    "query": "fall", "limit": 1, "templates": [], "licenses": []}}
        with patch.object(r, "run_lab") as execute:
            self.assert_error(self.session.handle(call), "not_ready")
            execute.assert_not_called()

    def test_returned_patch_and_current_snapshot_are_defensive_copies(self):
        accepted = self.admit()
        accepted["payload"]["spec"]["simulation"]["seed"] = 99
        snapshot = self.session.current_spec
        snapshot["simulation"]["seed"] = 88
        self.assertEqual(self.session.current_spec["simulation"]["seed"], 12)

    def test_unsupported_template_never_dispatches(self):
        self.base, self.scene = setup("ramp")
        self.session = self.make_session()
        self.admit()
        with patch.object(r, "run_lab") as execute:
            self.assert_error(self.session.handle(self.rebuild_call()), "not_ready")
            execute.assert_not_called()

    def test_non_synthetic_metadata_cannot_admit_a_physical_job(self):
        # Negative schema fixture only: these strings are NOT rights/approval evidence.
        self.scene["synthetic"] = False
        self.scene["provenance"].update(method="planes-boxes", sources=[{
            "clip_id": "negative_fixture", "source_url": "https://example.org/not-footage",
            "license": "Public-Domain", "attribution": "NEGATIVE TEST ONLY",
            "approval_evidence": "NEGATIVE TEST ONLY; NO APPROVAL"}])
        self.scene_path.write_text(json.dumps(self.scene), encoding="utf-8")
        self.session = self.make_session()
        self.admit()
        with patch.object(r, "run_lab") as execute:
            self.assert_error(self.session.handle(self.rebuild_call()), "not_ready")
            execute.assert_not_called()

    def test_incompatible_lab_output_publishes_no_numbers(self):
        self.admit()
        with patch.object(r, "run_lab", return_value={"source": "measured", "inputProvenance": "synthetic"}):
            self.assert_error(self.session.handle(self.rebuild_call()), "internal_error")

    def test_fitter_abstention_publishes_no_partial_simulator_numbers(self):
        self.admit()
        actual = r.run_lab

        def abstain(*args, **kwargs):
            result = actual(*args, **kwargs)
            result["fit"] = {"status": "error", "error": {"code": "no_fit"}}
            return result

        with patch.object(r, "run_lab", side_effect=abstain):
            self.assert_error(self.session.handle(self.rebuild_call()), "internal_error")

    def test_synthetic_fitter_cannot_be_relabelled_measured(self):
        self.admit()
        actual = r.run_lab

        def relabel(*args, **kwargs):
            result = actual(*args, **kwargs)
            result["fit"]["gravity"]["source"]["label"] = "measured"
            return result

        with patch.object(r, "run_lab", side_effect=relabel):
            self.assert_error(self.session.handle(self.rebuild_call()), "internal_error")

    def test_completed_contract_rejects_tampered_numbers_hash_or_empty_outputs(self):
        self.admit()
        call = self.rebuild_call()
        result = self.session.handle(call)
        self.assertEqual(result["status"], "ok", result)
        for change in ("value", "digest", "missing", "empty"):
            bad = copy.deepcopy(result)
            if change == "value":
                bad["tool_outputs"][0]["quantities"]["duration"]["value"] += 1
            elif change == "digest":
                key = next(iter(bad["payload"]["output_sha256"]))
                bad["payload"]["output_sha256"][key] = "0" * 64
            elif change == "missing":
                del bad["payload"]["output_sha256"]
            else:
                bad["tool_outputs"] = []
                bad["payload"]["output_sha256"] = {}
            with self.subTest(change=change), self.assertRaises(c.SidebarContractError):
                c.validate_result(bad, call)

    def test_patch_waits_for_rebuild_receipt_publication(self):
        self.admit()
        next_patch = self.patch_call(seed=13)
        entered, release, patch_started, patch_done = Event(), Event(), Event(), Event()
        results = []
        actual = r.run_lab

        def run(*args, **kwargs):
            entered.set()
            if not release.wait(10):
                raise ValueError("test synchronization timeout")
            return actual(*args, **kwargs)

        def edit():
            patch_started.set()
            results.append(self.session.handle(next_patch))
            patch_done.set()

        with patch.object(r, "run_lab", side_effect=run):
            rebuild = Thread(target=lambda: results.append(self.session.handle(self.rebuild_call())))
            rebuild.start()
            self.assertTrue(entered.wait(10))
            editor = Thread(target=edit)
            editor.start()
            self.assertTrue(patch_started.wait(10))
            try:
                self.assertFalse(patch_done.wait(0.1))
            finally:
                release.set()
                rebuild.join(20)
                editor.join(20)
            self.assertFalse(rebuild.is_alive() or editor.is_alive())
        self.assertEqual(len(results), 2)
        self.assertTrue(all(result["status"] == "ok" for result in results), results)
        self.assertEqual(self.session.current_spec["simulation"]["seed"], 13)


if __name__ == "__main__":
    unittest.main()
