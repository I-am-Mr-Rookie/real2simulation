"""N4 regressions: temporary synthetic state only; no cloud/provider clients."""
import hashlib
import json
import tempfile
import os
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from Build.guardrails.admission import ReconstructionPaused, require_reconstruction
from Build.guardrails.durable import read_json, write_json
from Build.guardrails.reservations import claim_gpu, project, reserve_gpu
from Build.guardrails import standalone
from Build.guardrails.settlement import settle_gpu


def billing_row(cost=".1", app="ap-synthetic"):
    return {"object_id": app, "resource": "GPU", "cost": cost,
            "environment": "main", "interval_start": "2026-10-30T06:00:00"}


class Settlement(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.runtime = self.root / "evidence/S20/runtime"
        self.runtime.mkdir(parents=True)
        self.receipt = {"schema": "reconstruction-admission/1", "as_of": datetime.now(timezone.utc).isoformat(),
                        "paused": False, "coverage_verified": True, "credit_verified": True,
                        "sources": ["SYNTHETIC isolated settlement"],
                        "Meta Model API": {"historical_usd": "0", "requests": [], "credit_headroom_usd": "150"},
                        "Modal": {"historical_usd": "0", "requests": [], "credit_headroom_usd": "30"}}
        write_json(self.runtime / "receipt.json", self.receipt)
        write_json(self.runtime / "reservations.json", {"schema": "gpu-reservations/1", "requests": [], "ledgers": []})
        self.ledger = self.root / "calls.jsonl"
        self.first = self.reserve("first")
        self.second = self.reserve("second")
        with self.ledger.open("a") as stream:
            stream.write(json.dumps({"request_id": self.first, "app_id": "ap-synthetic", "provider": "Modal"}) + "\n")
        self.log = self.root / "cost.json"
        self.bill = self.root / "billing.json"
        write_json(self.log, {"app_id": "ap-synthetic", "cost": {"billed": {"status": "billed", "total_usd": ".1"}}})
        write_json(self.bill, [billing_row()])
        now = datetime.now(timezone.utc).isoformat()
        self.proof = {"schema": "modal-settlement/1", "request_id": self.first, "app_id": "ap-synthetic",
                      "status": "completed", "containers": [], "billing_final_verified": True,
                      "reviewed_by": "SYNTHETIC reviewer", "completed_at": now, "billing_read_at": now,
                      "scene_log": "cost.json", "billing_report": "billing.json"}
        self.proof_path = self.root / "settlement.json"
        self.save_proof()

    def reserve(self, key, amount=".5"):
        return reserve_gpu(self.root, self.ledger, "reconstruct", key, amount, max_jobs=2, cap_usd="1")

    def save_proof(self):
        for name, path in (("scene_log", self.log), ("billing_report", self.bill)):
            self.proof[name + "_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        write_json(self.proof_path, self.proof)

    def settle(self):
        return settle_gpu(self.root, self.first, self.proof_path)

    def state(self):
        return project(self.root, self.receipt, read_json(self.runtime / "reservations.json"))[0]

    def test_releases_slot_and_bound_not_monthly_spend_or_replay(self):
        with self.assertRaises(ReconstructionPaused):
            self.reserve("third")
        self.assertEqual(str(self.settle()), "0.10000000")
        self.reserve("third")  # SAME ledger; old reservation no longer consumes an active slot.
        state = self.state()
        write_json(self.runtime / "snapshot.json", state)
        result = require_reconstruction(self.runtime / "snapshot.json", candidate_modal_usd=".1")
        self.assertEqual(str(result["modal_committed_usd"]), "1.10000000")
        journal = read_json(self.runtime / "reservations.json")
        self.assertEqual(len(journal["requests"]), 3)
        with self.assertRaises(ReconstructionPaused):
            self.reserve("first", ".01")

    def test_missing_unknown_or_nonfinal_proof_cannot_release(self):
        original = read_json(self.runtime / "reservations.json")
        for key, value in (("containers", ["live"]), ("containers", None), ("billing_final_verified", False),
                           ("reviewed_by", ""), ("status", "running"), ("request_id", self.second),
                           ("app_id", "ap-other"), ("billing_read_at", "2099-01-01T00:00:00+00:00")):
            with self.subTest(key=key, value=value):
                old = self.proof[key]
                self.proof[key] = value
                self.save_proof()
                with self.assertRaises(ReconstructionPaused):
                    self.settle()
                self.proof[key] = old
                self.assertEqual(read_json(self.runtime / "reservations.json"), original)

    def test_missing_duplicate_negative_and_disagreeing_bills_fail_closed(self):
        for rows in ([], [billing_row(app="ap-other")], [billing_row("-.1")], [billing_row(".2")],
                     [billing_row()] * 2, [billing_row(), billing_row(".2")]):
            with self.subTest(rows=rows):
                write_json(self.bill, rows)
                self.save_proof()
                with self.assertRaises(ReconstructionPaused):
                    self.settle()

    def test_missing_or_changed_evidence_pauses_new_jobs(self):
        self.settle()
        self.bill.unlink()
        with self.assertRaises(ReconstructionPaused):
            self.reserve("third")

    def test_changed_receipt_and_duplicate_settlement_rejected(self):
        self.settle()
        with self.assertRaises(ReconstructionPaused):
            self.settle()
        self.proof["reviewed_by"] = "changed"
        self.save_proof()
        with self.assertRaises(ReconstructionPaused):
            self.reserve("third")

    def test_monthly_cap_still_counts_settled_actual_and_overrun(self):
        self.settle()
        self.receipt["Modal"]["historical_usd"] = "29"
        write_json(self.runtime / "receipt.json", self.receipt)
        with self.assertRaises(ReconstructionPaused):
            self.reserve("third")

    def test_final_overrun_is_not_clamped_to_reservation(self):
        write_json(self.log, {"app_id": "ap-synthetic", "cost": {"billed": {"status": "billed", "total_usd": ".8"}}})
        write_json(self.bill, [billing_row(".8")])
        self.save_proof()
        self.assertEqual(str(self.settle()), "0.80000000")
        self.reserve("third")
        state = self.state()
        write_json(self.runtime / "snapshot.json", state)
        result = require_reconstruction(self.runtime / "snapshot.json", candidate_modal_usd=".1")
        self.assertEqual(str(result["modal_committed_usd"]), "1.80000000")

    def test_lower_final_than_observed_bill_rejected(self):
        with self.ledger.open("a") as stream:
            stream.write(json.dumps({"request_id": self.first, "provider": "Modal", "billed_usd": ".2"}) + "\n")
        with self.assertRaises(ReconstructionPaused):
            self.settle()

    def test_unbound_or_ambiguous_app_cannot_settle(self):
        with self.ledger.open("a") as stream:
            stream.write(json.dumps({"request_id": self.second, "app_id": "ap-synthetic", "provider": "Modal"}) + "\n")
        with self.assertRaises(ReconstructionPaused):
            self.settle()

    def test_failed_durable_write_keeps_both_slots(self):
        with patch("Build.guardrails.settlement.write_json", side_effect=OSError("synthetic disk error")):
            with self.assertRaises(ReconstructionPaused):
                self.settle()
        with self.assertRaises(ReconstructionPaused):
            self.reserve("third")

    def test_pipeline_child_claims_once_without_second_reservation_or_amount_env(self):
        with patch.object(standalone, "ROOT", self.root), patch.dict(os.environ, {"S20_MODAL_REQUEST_ID": self.first}):
            self.assertEqual(standalone.admit_standalone("scene-job:synthetic"), self.first)
            with self.assertRaises(ReconstructionPaused):
                standalone.admit_standalone("scene-job:synthetic")
        self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 2)

    def test_claim_rejects_missing_foreign_stage_stale_and_settled(self):
        for key, operation in (("missing", "scene-job:x"), (self.first, "modal-track:x")):
            with self.assertRaises(ReconstructionPaused):
                claim_gpu(self.root, key, operation)
        self.settle()
        with self.assertRaises(ReconstructionPaused):
            claim_gpu(self.root, self.first, "scene-job:x")
        self.receipt["as_of"] = "2000-01-01T00:00:00+00:00"
        write_json(self.runtime / "receipt.json", self.receipt)
        with self.assertRaises(ReconstructionPaused):
            claim_gpu(self.root, self.second, "scene-job:x")

    def void(self, request_id, apps=(), rows=()):
        """S13n: modal-void/1 for a never-dispatched reservation; returns settle_gpu's amount."""
        now = datetime.now(timezone.utc)
        hour = now.strftime("%Y-%m-%dT%H:00:00")
        write_json(self.root / "apps.json", [{"app_id": a, "created_at": now.isoformat()} for a in apps])
        write_json(self.root / "void-bill.json", [billing_row(app=a) | {"interval_start": hour} for a in rows])
        proof = {"schema": "modal-void/1", "request_id": request_id, "reviewed_by": "SYNTHETIC reviewer",
                 "read_at": now.isoformat(), "app_list": "apps.json", "billing_report": "void-bill.json"}
        for name in ("app_list", "billing_report"):
            proof[name + "_sha256"] = hashlib.sha256((self.root / proof[name]).read_bytes()).hexdigest()
        write_json(self.root / "void.json", proof)
        return settle_gpu(self.root, request_id, self.root / "void.json")

    def test_void_settles_unbound_reservation_at_zero_idempotently(self):
        # Apps/bills seen since the reservation are all bound to another request (first).
        self.assertEqual(self.void(self.second, ["ap-synthetic"], ["ap-synthetic"]), 0)
        journal = read_json(self.runtime / "reservations.json")
        self.assertEqual(settle_gpu(self.root, self.second, self.root / "void.json"), 0)  # replay: no-op
        self.assertEqual(read_json(self.runtime / "reservations.json"), journal)
        row = next(r for r in self.state()["Modal"]["requests"] if r["request_id"] == self.second)
        self.assertEqual((row["settled"], row["billed_usd"], row["app_id"]), (True, "0", None))
        self.reserve("third")  # Slot released.

    def test_void_rejects_app_bound_billed_dispatched_or_unexplained_apps(self):
        original = read_json(self.runtime / "reservations.json")
        for request_id, apps, rows in ((self.first, [], []), (self.second, ["ap-unknown"], []),
                                       (self.second, [], ["ap-unknown"])):
            with self.subTest(request_id=request_id, apps=apps, rows=rows), self.assertRaises(ReconstructionPaused):
                self.void(request_id, apps, rows)
            self.assertEqual(read_json(self.runtime / "reservations.json"), original)
        with self.ledger.open("a") as stream:
            stream.write(json.dumps({"request_id": self.second, "provider": "Modal", "billed_usd": ".01"}) + "\n")
        with self.assertRaises(ReconstructionPaused):
            self.void(self.second)

    def test_dispatched_reservation_cannot_be_voided(self):
        self.assertEqual(claim_gpu(self.root, self.second, "scene-job:x"), self.second)
        with self.assertRaises(ReconstructionPaused):
            self.void(self.second)  # Dispatched: needs real billing settlement, never a void.

    def test_app_bound_after_void_pauses_admission(self):
        self.void(self.second)
        with self.ledger.open("a") as stream:
            stream.write(json.dumps({"request_id": self.second, "app_id": "ap-late", "provider": "Modal"}) + "\n")
        with self.assertRaises(ReconstructionPaused):
            self.reserve("third")


if __name__ == "__main__":
    unittest.main()
