"""Synthetic accounting cases, plus read-only compatibility with existing receipt shapes. No spend."""
import json
import unittest
from decimal import Decimal
from pathlib import Path

from Build.guardrails.accounting import (
    META_ALLOCATION_USD, META_DEMO_RESERVE_USD, META_ROUTINE_STOP_USD,
    liability_usd, meta_snapshot, usd,
)

ROOT = Path(__file__).resolve().parents[2]


def request(key="req-1", **costs):
    return {"request_id": key, "provider": "Meta Model API", "reserved_usd": "1", **costs}


class Accounting(unittest.TestCase):
    def test_allocation_preserves_demo_reserve(self):
        self.assertEqual(META_ROUTINE_STOP_USD + META_DEMO_RESERVE_USD, META_ALLOCATION_USD)
        self.assertEqual((META_ROUTINE_STOP_USD, META_DEMO_RESERVE_USD), (Decimal(120), Decimal(30)))

    def test_history_pending_and_conservative_estimates_all_count(self):
        rows = [request("pending", reserved_usd="2"),
                request("estimated", reserved_usd="1", est_usd="3"),
                request("final", billed_usd="4", settled=True)]
        result = meta_snapshot("110", rows, "1")
        self.assertEqual(result["requests_usd"], Decimal(9))
        self.assertEqual(result["committed_usd"], Decimal(119))
        self.assertEqual(result["projected_usd"], Decimal(120))
        self.assertFalse(result["routine_cap_allows"])
        self.assertEqual(result["demo_reserve_usd"], Decimal(30))

    def test_routine_threshold_is_strict_including_candidate(self):
        for history, candidate, allowed in [("119.99", "0", True), ("119.99", ".01", False),
                                             ("120", "0", False), ("149", "0", False)]:
            with self.subTest(history=history, candidate=candidate):
                self.assertEqual(meta_snapshot(history, [], candidate)["routine_cap_allows"], allowed)

    def test_unsettled_bill_and_lower_estimate_never_release_reserve(self):
        self.assertEqual(liability_usd(request(reserved_usd="2", est_usd=".1", billed_usd=".05")), 2)

    def test_higher_estimate_or_provisional_bill_counts(self):
        self.assertEqual(liability_usd(request(est_usd="3")), 3)
        self.assertEqual(liability_usd(request(est_usd="3", billed_usd="4")), 4)

    def test_final_reconciliation_replaces_reserve_without_double_counting(self):
        self.assertEqual(liability_usd(request(reserved_usd="5", est_usd="2", billed_usd="1", settled=True)), 1)
        self.assertEqual(liability_usd(request(billed_usd=0, settled=True)), 0)
        self.assertEqual(liability_usd(request(billed_usd="9", settled=True)), 9)  # overrun is not clamped

    def test_no_bill_cannot_be_final_and_no_bound_cannot_be_pending(self):
        for row in [request(settled=True), request(reserved_usd=None, est_usd=1),
                    request(reserved_usd=None, billed_usd=0), request(settled="true")]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                liability_usd(row)

    def test_unknown_history_or_candidate_is_not_zero(self):
        for value in [None, "unknown", "", True]:
            with self.subTest(history=value), self.assertRaises(ValueError):
                meta_snapshot(value, [])
            with self.subTest(candidate=value), self.assertRaises(ValueError):
                meta_snapshot(0, [], value)

    def test_invalid_money_refused_at_every_present_cost_field(self):
        for value in [-1, "-.000000001", float("nan"), float("inf"), "-Infinity", "NaN", True, {}, []]:
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                usd(value)
            for key in ["reserved_usd", "est_usd", "billed_usd"]:
                with self.subTest(value=repr(value), key=key), self.assertRaises(ValueError):
                    liability_usd(request(**{key: value}))

    def test_settled_does_not_mask_malformed_unused_fields(self):
        with self.assertRaises(ValueError):
            liability_usd(request(reserved_usd=-1, billed_usd=0, settled=True))

    def test_decimal_arithmetic_and_rounding_cannot_hide_cap(self):
        self.assertEqual(usd(.1) + usd(.2), Decimal(".3"))
        self.assertEqual(usd(".000000001"), Decimal(".00000001"))
        self.assertFalse(meta_snapshot("119.999999999", [])["routine_cap_allows"])
        self.assertFalse(meta_snapshot("119.99999999", [], ".000000001")["routine_cap_allows"])

    def test_breached_headroom_never_negative(self):
        result = meta_snapshot(121, [])
        self.assertEqual(result["routine_headroom_usd"], 0)
        self.assertFalse(result["routine_cap_allows"])

    def test_duplicate_missing_or_empty_request_ids_refused(self):
        for rows in [[request(), request()], [request(request_id=None)], [request(request_id=" ")]]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                meta_snapshot(0, rows)

    def test_provider_envelopes_cannot_be_mixed(self):
        for provider in [None, "Modal", "AWS", "Baseten"]:
            with self.subTest(provider=provider), self.assertRaises(ValueError):
                meta_snapshot(0, [request(provider=provider)])

    def test_malformed_collections_cannot_look_like_empty_history(self):
        for rows in [None, {}, "", 0]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                meta_snapshot(0, rows)
        for row in [None, [], "", 0]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                meta_snapshot(0, [row])
            with self.subTest(cost=row), self.assertRaises(ValueError):
                liability_usd(row)

    def test_existing_meta_ledger_fields_project_without_importing_live_recorder(self):
        path = ROOT / "evidence/S14/S14b-ledger.jsonl"
        row = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
        projected = {**row, "request_id": "evidence/S14/S14b-ledger.jsonl#L1"}
        result = meta_snapshot(0, [projected])  # synthetic history, NOT a current global balance
        self.assertEqual(result["requests_usd"], max(usd(row["reserved_usd"]), usd(row["est_usd"])))
        self.assertIsNone(row["billed_usd"])

    def test_existing_scene_receipt_provisional_bill_retains_envelope(self):
        # Same projection as CONTRACT.md; do not import a runtime or touch source receipts.
        path = ROOT / "evidence/S06/S06f/RM04-scene-log.json"
        cost = json.loads(path.read_text(encoding="utf-8"))["cost"]
        row = {"reserved_usd": ".50", "est_usd": cost["upper_bound"]["total_usd"],
               "billed_usd": cost["billed"]["total_usd"]}
        self.assertEqual(liability_usd(row), Decimal(".50"))
        self.assertEqual(liability_usd({**row, "settled": True}), usd(row["billed_usd"]))


if __name__ == "__main__":
    unittest.main()
