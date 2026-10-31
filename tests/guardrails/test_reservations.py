"""R-C regressions: synthetic local state, real processes/files, no paid transports."""
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from Build.guardrails.admission import ReconstructionPaused, require_reconstruction
from Build.guardrails.durable import read_json, write_json
from Build.guardrails.reservations import inventory, project, project_ledger, repository_root, reserve_gpu
from Build.pipeline import gpu_stages

REPO = Path(__file__).resolve().parents[2]


class Reservations(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.runtime = self.root / "evidence/S20/runtime"
        self.runtime.mkdir(parents=True)
        self.receipt = {"schema": "reconstruction-admission/1", "as_of": datetime.now(timezone.utc).isoformat(),
                        "paused": False, "coverage_verified": True, "credit_verified": True,
                        "sources": ["SYNTHETIC coverage"],
                        "Meta Model API": {"historical_usd": "0", "requests": [], "credit_headroom_usd": "150"},
                        "Modal": {"historical_usd": "0", "requests": [], "credit_headroom_usd": "30"}}
        self.journal = {"schema": "gpu-reservations/1", "requests": [], "ledgers": []}
        self.save()

    def save(self):
        write_json(self.runtime / "receipt.json", self.receipt)
        write_json(self.runtime / "reservations.json", self.journal)

    def reserve(self, name, amount=".5", **kwargs):
        reserve_gpu(self.root, self.root / name / "gpu-ledger.jsonl", "reconstruct", name, amount,
                    max_jobs=kwargs.get("max_jobs", 2), cap_usd=kwargs.get("cap_usd", "1"))

    def test_G1_three_fresh_directories_cannot_reset_global_cap(self):
        self.reserve("one", "1")
        for name in ("two", "three"):
            with self.assertRaises(ReconstructionPaused):
                self.reserve(name, "1")
        self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 1)
        self.assertFalse((self.root / "two/gpu-ledger.jsonl").exists())

    def test_G3_corrupt_local_ledger_maps_to_nonretryable_stage_error(self):
        ledger = self.root / "bad.jsonl"
        ledger.write_text("{broken\n", encoding="utf-8")
        with patch.object(gpu_stages, "ROOT", self.root):
            with self.assertRaises(gpu_stages.StageError) as caught:
                gpu_stages.reserve(ledger, "segment", "bad", ".5")
        self.assertEqual((caught.exception.code, caught.exception.retryable), ("SPEND_PAUSED", False))
        self.assertEqual(ledger.read_text(), "{broken\n")

    def test_missing_runtime_pauses_before_transport_or_output(self):
        (self.runtime / "receipt.json").unlink()
        calls = []
        with patch.object(gpu_stages, "ROOT", self.root):
            with self.assertRaises(gpu_stages.StageError) as caught:
                gpu_stages.segment("one", lambda: calls.append("paid"), self.root / "output",
                                   self.root / "gpu-ledger.jsonl", "chair", 0)
        self.assertEqual(caught.exception.code, "SPEND_PAUSED")
        self.assertEqual(calls, [])
        self.assertFalse((self.root / "output").exists())

    def test_C1_real_processes_admit_only_one_four_dollar_liability(self):
        self.receipt["Modal"]["historical_usd"] = "20"
        self.save()
        code = """
import sys
from pathlib import Path
from Build.guardrails.reservations import reserve_gpu
from Build.guardrails.admission import ReconstructionPaused
try:
    reserve_gpu(Path(sys.argv[1]), Path(sys.argv[1])/sys.argv[2]/'gpu-ledger.jsonl',
                'reconstruct', sys.argv[2], '4', max_jobs=10, cap_usd='100')
    print('ADMITTED')
except ReconstructionPaused:
    print('SPEND_PAUSED')
"""
        def child(name):
            return subprocess.run([sys.executable, "-c", code, str(self.root), name],
                                  cwd=REPO, capture_output=True, text=True, timeout=30, check=True).stdout.strip()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(child, ("one", "two")))
        self.assertEqual(sorted(results), ["ADMITTED", "SPEND_PAUSED"])
        self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 1)
        with self.assertRaises(ReconstructionPaused):
            self.reserve("retry", "4", max_jobs=10, cap_usd="100")

    def test_X1_unknown_top_level_key_and_excess_aws_liabilities_pause(self):
        self.receipt["unknown-provider"] = {}
        self.save()
        with self.assertRaises(ReconstructionPaused):
            self.reserve("unknown")
        del self.receipt["unknown-provider"]
        self.receipt["AWS"] = {"historical_usd": "51", "requests": [], "credit_headroom_usd": "100"}
        self.save()
        with self.assertRaises(ReconstructionPaused):
            self.reserve("aws-over-cap")

    def test_R1_credit_rounds_down_not_into_admission(self):
        self.receipt["Meta Model API"]["credit_headroom_usd"] = "0.000000001"
        self.save()
        with self.assertRaises(ReconstructionPaused):
            require_reconstruction(self.runtime / "receipt.json", candidate_modal_usd=".5",
                                   candidate_meta_usd="0.00000001")

    def test_missing_corrupt_and_duplicate_journal_and_missing_old_ledger_pause(self):
        for contents in (None, "{", "null", '[]', '{"schema":1,"schema":2}'):
            self.save()
            path = self.runtime / "reservations.json"
            if contents is None:
                path.unlink()
            else:
                path.write_text(contents, encoding="utf-8")
            with self.assertRaises(ReconstructionPaused):
                self.reserve("one")
        self.save()
        self.reserve("one")
        (self.root / "one/gpu-ledger.jsonl").unlink()
        with self.assertRaises(ReconstructionPaused):
            self.reserve("two")

    def test_failed_local_append_retains_global_liability(self):
        ledger = self.root / "blocked/gpu-ledger.jsonl"
        with patch("pathlib.Path.open", autospec=True, side_effect=OSError("disk unavailable")):
            with self.assertRaises(ReconstructionPaused):
                self.reserve("blocked")
        self.assertFalse(ledger.exists())
        # Inject only the append failure: durable replacement still succeeds.
        original = Path.open
        def fail_append(path, mode="r", *args, **kwargs):
            if mode == "a":
                raise OSError("append failed")
            return original(path, mode, *args, **kwargs)
        with patch.object(Path, "open", fail_append):
            with self.assertRaises(ReconstructionPaused):
                self.reserve("blocked")
        self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 1)
        with self.assertRaises(ReconstructionPaused):
            self.reserve("two")

    def test_project_folds_events_and_preserves_worst_cost(self):
        path = self.root / "events.jsonl"
        events = [{"run": "one", "reserved_usd": ".5"},
                  {"run": "one", "app_id": "ap-one", "cost": {"upper_bound": {"total_usd": "2"}}, "billed_usd": ".1"}]
        path.write_text("\n".join(map(json.dumps, events)), encoding="utf-8")
        rows = project_ledger(path, "events.jsonl")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["est_usd"], "2.00000000")
        self.journal["ledgers"] = [str(path)]
        state, paths = project(self.root, self.receipt, self.journal)
        self.assertIn(path, paths)
        self.assertEqual(len(state["Modal"]["requests"]), 1)
        self.assertIn("#sha256=", state["sources"][0])

    def test_duplicate_journal_and_receipt_ids_pause_instead_of_silent_merge(self):
        row = {"request_id": "same", "provider": "Modal", "reserved_usd": "1"}
        self.journal["requests"] = [row, row]
        self.save()
        with self.assertRaises(ReconstructionPaused):
            self.reserve("duplicate-journal")
        self.journal["requests"] = []
        self.receipt["Modal"]["requests"] = [row, row]
        self.save()
        with self.assertRaises(ReconstructionPaused):
            self.reserve("duplicate-receipt")

    def test_scene_log_overrun_is_folded_and_missing_known_source_pauses(self):
        directory = self.root / "evidence/S13/live"
        bundle = directory / "reconstruct/bundle"
        bundle.mkdir(parents=True)
        ledger = directory / "gpu-ledger.jsonl"
        ledger.write_text(json.dumps({"stage": "reconstruct", "idempotency_key": "one", "reserved_usd": ".5"}) + "\n")
        artifact = bundle.parent / "reconstruction.json"
        artifact.write_text(json.dumps({"app_id": "ap-one", "idempotency_key": "one"}))
        log = bundle / "room-scene-log.json"
        log.write_text(json.dumps({"app_id": "ap-one", "cost": {"upper_bound": {"total_usd": "24.6"}}}))
        with self.assertRaises(ReconstructionPaused):
            self.reserve("overrun")  # 24.6 + .5 violates the $5 remaining floor.
        log.write_text(json.dumps({"app_id": "ap-one", "cost": {"upper_bound": {"total_usd": "2"}}}))
        self.reserve("accepted")
        snapshot = read_json(self.runtime / "snapshot.json")
        self.assertEqual(snapshot["Modal"]["requests"][0]["est_usd"], "2.00000000")
        log.unlink()
        with self.assertRaises(ReconstructionPaused):
            self.reserve("missing-known-log")

    def test_journal_row_reusing_recorded_reconstruct_key_does_not_break_projection(self):
        # S13l: a rerun reserves the same manifest key as an older recorded bundle in another directory.
        directory = self.root / "evidence/S13/live"
        bundle = directory / "reconstruct/bundle"
        bundle.mkdir(parents=True)
        (directory / "gpu-ledger.jsonl").write_text(
            json.dumps({"stage": "reconstruct", "idempotency_key": "one", "reserved_usd": ".5"}) + "\n")
        (bundle.parent / "reconstruction.json").write_text(json.dumps({"app_id": "ap-one", "idempotency_key": "one"}))
        (bundle / "room-scene-log.json").write_text(
            json.dumps({"app_id": "ap-one", "cost": {"upper_bound": {"total_usd": ".1"}}}))
        self.reserve("one")  # journal row: stage reconstruct, key "one", no "source"
        self.reserve("two")  # must project, not KeyError -> SPEND_PAUSED
        self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 2)

    def test_json_parent_counts_sum_of_child_worst_costs_not_parent_plus_children(self):
        directory = self.root / "evidence/S06/test"
        directory.mkdir(parents=True)
        log = directory / "room-scene-log.json"
        log.write_text(json.dumps({"app_id": "ap-one", "cost": {"upper_bound": {"total_usd": ".7"}}}))
        ledger = directory / "job-ledger.json"
        ledger.write_text(json.dumps({"new_all_in_reservation_usd": "1", "jobs": [
            {"app_id": "ap-one", "scene_log": "evidence/S06/test/room-scene-log.json", "measured_cost_usd": ".1"},
            {"app_id": "ap-two", "upper_bound_cost_usd": ".6", "measured_cost_usd": ".1"}]}))
        rows = project_ledger(ledger, "evidence/S06/test/job-ledger.json")
        from Build.guardrails.accounting import liability_usd
        self.assertEqual(liability_usd(rows[0]), Decimal("1.3"))
        state, _ = project(self.root, self.receipt, self.journal)
        self.assertEqual(liability_usd(state["Modal"]["requests"][0]), Decimal("1.3"))

    def test_reflected_journal_liability_does_not_reduce_net_credit_twice(self):
        self.reserve("one")
        self.journal = read_json(self.runtime / "reservations.json")
        state, _ = project(self.root, self.receipt, self.journal)
        repeated, _ = project(self.root, state, self.journal)
        self.assertEqual(repeated["Modal"]["credit_headroom_usd"], state["Modal"]["credit_headroom_usd"])

    def test_linked_worktree_resolves_to_same_root(self):
        common = self.root / ".git"
        directory = common / "worktrees/worker"
        directory.mkdir(parents=True)
        (directory / "commondir").write_text("../..")
        worktree = self.root / "worker"
        worktree.mkdir()
        (worktree / ".git").write_text("gitdir: " + str(directory))
        self.assertEqual(repository_root(worktree), self.root)


if __name__ == "__main__":
    unittest.main()
