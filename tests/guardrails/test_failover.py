"""Synthetic offline receipts only; never authorize or launch real AWS work."""
import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from Build.gpu import aws_adapter
from Build.guardrails.admission import ReconstructionPaused
from Build.guardrails.failover import select_provider

NOW = datetime(2026, 10, 29, 22, 20, tzinfo=timezone.utc)
ON = {aws_adapter.ENV_FLAG: "1"}


class Failover(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.state_path, self.quota_path, self.budget_path = (
            root / name for name in ("state.json", "quota.json", "budget.json"))
        self.state = {"schema": "reconstruction-admission/1", "as_of": NOW.isoformat(),
                      "paused": False, "coverage_verified": True, "credit_verified": True,
                      "sources": ["SYNTHETIC shared ledger"],
                      "Meta Model API": {"historical_usd": "110", "requests": [],
                                         "credit_headroom_usd": "40"},
                      "Modal": {"historical_usd": "1", "requests": [], "credit_headroom_usd": "29"}}
        self.state["AWS"] = {"historical_usd": "0", "requests": [], "credit_headroom_usd": "50"}
        runtime = root / "evidence/S20/runtime"
        runtime.mkdir(parents=True)
        self.journal_path = runtime / "reservations.json"
        self.journal_path.write_text(json.dumps(
            {"schema": "gpu-reservations/1", "requests": [], "ledgers": []}), encoding="utf-8")
        root_patch = patch("Build.guardrails.failover.ROOT", root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        self.quota = {"schema": "aws-quota-receipt/1", "as_of": NOW.isoformat(),
                      "owner_approved": True, "region": "us-east-2", "market": "spot",
                      "quota_code": aws_adapter.SPOT_QUOTA_CODE, "spot_quota_vcpu": 8}
        self.budget = {"schema": "aws-budget-receipt/1", "as_of": NOW.isoformat(),
                       "owner_approved": True, "region": "us-east-2",
                       "budget": {**copy.deepcopy(aws_adapter.OWNER_GATES["budget"]),
                                  "currency": "USD", "period": "MONTHLY", "gross": True},
                       "coverage_verified": True, "credit_verified": True,
                       "remaining_gross_usd": "10", "credit_headroom_usd": "9"}
        self.save()

    def save(self):
        for path, data in ((self.state_path, self.state), (self.quota_path, self.quota),
                           (self.budget_path, self.budget)):
            path.write_text(json.dumps(data), encoding="utf-8")

    def select(self, **overrides):
        kwargs = {"candidate_modal_usd": "1", "candidate_aws_usd": "2",
                  "quota_receipt_path": self.quota_path, "budget_receipt_path": self.budget_path,
                  "max_session_seconds": 600, "env": ON, "now": NOW}
        return select_provider(self.state_path, **{**kwargs, **overrides})

    def refused(self, **overrides):
        with self.assertRaises(ReconstructionPaused) as caught:
            self.select(**overrides)
        self.assertEqual(caught.exception.code, "SPEND_PAUSED")
        self.assertFalse(caught.exception.retryable)

    def test_default_off_ignores_aws_receipts_but_keeps_admission(self):
        self.quota_path.unlink()
        self.budget_path.unlink()
        with patch.dict("os.environ", {}, clear=True):
            result = select_provider(self.state_path, candidate_modal_usd="1", now=NOW)
        self.assertEqual(result["provider"], "Modal")
        self.assertFalse(result["launched"])
        self.assertIsNone(result["aws"])
        for flag in (None, "0", "true", "yes", " 1", 1, True):
            self.assertEqual(self.select(env={aws_adapter.ENV_FLAG: flag})["provider"], "Modal")
        self.state["paused"] = True
        self.save()
        self.refused(env={})

    def test_explicit_switch_reuses_adapter_and_admission(self):
        with patch("Build.guardrails.failover.aws_adapter.activate",
                   wraps=aws_adapter.activate) as adapter:
            result = self.select()
        adapter.assert_called_once()
        self.assertEqual(result["provider"], "AWS")
        self.assertFalse(result["launched"])
        self.assertEqual(result["aws"]["region"], "us-east-2")
        self.assertEqual(result["aws"]["market"], "spot")
        self.assertEqual(result["aws"]["instance"], "g6e.xlarge")
        self.assertEqual(result["aws"]["all_in_usd"], Decimal("2"))
        self.assertEqual(result["aws"]["max_session_seconds"], 600)
        self.assertTrue(result["aws"]["stop_on_exit"])
        self.assertEqual(result["admission"]["meta"]["projected_usd"], Decimal("110"))

    def test_missing_paths_and_unreadable_or_malformed_receipts_refuse(self):
        self.refused(quota_receipt_path=None)
        self.refused(budget_receipt_path=None)
        for path in (self.quota_path, self.budget_path):
            for contents in (b"{", b"null", b"[]", b"{}", b"\xff",
                             b'{"schema":"a","schema":"b"}'):
                with self.subTest(path=path.name, contents=contents):
                    self.save()
                    path.write_bytes(contents)
                    self.refused()
            self.save()
            path.unlink()
            self.refused()
            self.save()
        with patch.object(Path, "read_text", side_effect=PermissionError("private detail")):
            self.refused()

    def test_each_required_receipt_field_refuses_when_absent(self):
        for name in ("quota", "budget"):
            original = copy.deepcopy(getattr(self, name))
            for key in original:
                with self.subTest(receipt=name, missing=key):
                    setattr(self, name, {k: v for k, v in original.items() if k != key})
                    self.save()
                    self.refused()
            setattr(self, name, original)
        original = copy.deepcopy(self.budget["budget"])
        for key in original:
            self.budget["budget"] = {k: v for k, v in original.items() if k != key}
            self.save()
            self.refused()

    def test_bad_quota_region_market_schema_or_approval_refuses(self):
        original = copy.deepcopy(self.quota)
        for key, value in (("region", "us-east-1"), ("market", "on-demand"),
                           ("market", None), ("quota_code", "L-DB2E81BA"),
                           ("owner_approved", False), ("owner_approved", 1),
                           ("schema", "unknown"), ("spot_quota_vcpu", 3),
                           ("spot_quota_vcpu", True), ("spot_quota_vcpu", "8"),
                           ("spot_quota_vcpu", float("nan")), ("spot_quota_vcpu", float("inf"))):
            with self.subTest(key=key, value=value):
                self.quota = {**original, key: value}
                self.save()
                self.refused()

    def test_budget_must_be_exact_gross_monthly_fifty_usd_with_ec2_alerts(self):
        original = copy.deepcopy(self.budget["budget"])
        for key, value in (("name", "other"), ("amount_usd", 25), ("amount_usd", 51),
                           ("amount_usd", True), ("amount_usd", "NaN"),
                           ("currency", "EUR"), ("period", "DAILY"), ("gross", False),
                           ("services", []), ("services", "EC2 - Other"),
                           ("alerts", []), ("alerts", ["actual:100"]), ("alerts", {})):
            with self.subTest(key=key, value=value):
                self.budget["budget"] = {**original, key: value}
                self.save()
                self.refused()

    def test_budget_headroom_and_verification_fail_closed(self):
        original = copy.deepcopy(self.budget)
        for key, value in (("region", "us-west-2"), ("owner_approved", False),
                           ("schema", "unknown"), ("coverage_verified", False),
                           ("credit_verified", "true"), ("remaining_gross_usd", "1.99"),
                           ("remaining_gross_usd", "51"), ("credit_headroom_usd", "1.99"),
                           ("credit_headroom_usd", "NaN"), ("credit_headroom_usd", -1),
                           ("credit_headroom_usd", True)):
            with self.subTest(key=key, value=value):
                self.budget = {**original, key: value}
                self.save()
                self.refused()

    def test_stale_future_naive_and_invalid_receipt_timestamps_refuse(self):
        for receipt in (self.quota, self.budget):
            for value in ((NOW - timedelta(minutes=5, microseconds=1)).isoformat(),
                          (NOW + timedelta(microseconds=1)).isoformat(),
                          NOW.replace(tzinfo=None).isoformat(), "invalid", None):
                receipt["as_of"] = value
                self.save()
                self.refused()
            receipt["as_of"] = (NOW - timedelta(minutes=5)).isoformat()
            self.save()
            self.select()
            receipt["as_of"] = NOW.isoformat()
        self.refused(now=NOW.replace(tzinfo=None))

    def test_positive_all_in_bound_and_bounded_session_required(self):
        for value in (None, 0, -1, True, "NaN", "Infinity", "10"):
            self.refused(candidate_aws_usd=value)
        for value in (None, 0, -1, True, "600", 0.5, 3601):
            self.refused(max_session_seconds=value)
        self.select(candidate_aws_usd="9", max_session_seconds=3600)

    def test_switch_never_bypasses_s20b_caps_credit_or_pause(self):
        for provider, field, value in (("Meta Model API", "historical_usd", "120"),
                                       ("Modal", "historical_usd", "25"),
                                       ("Modal", "credit_headroom_usd", "1")):
            original = copy.deepcopy(self.state)
            self.state[provider][field] = value
            self.save()
            self.refused()
            self.state = original
        self.state["paused"] = True
        self.save()
        self.refused()

    def test_failed_aws_does_not_silently_fallback(self):
        self.quota["market"] = "on-demand"
        self.save()
        self.refused()

    def test_headroom_is_not_rounded_up_and_cost_is_rounded_up(self):
        self.budget["credit_headroom_usd"] = "1.999999999"
        self.save()
        self.refused()
        self.budget["credit_headroom_usd"] = "2"
        self.save()
        self.refused(candidate_aws_usd="2.000000001")
        self.assertEqual(self.select(candidate_aws_usd="1.000000001")["aws"]["all_in_usd"],
                         Decimal("1.00000001"))

    def test_receipts_stay_read_only_but_aws_selection_durably_reserves(self):
        paths = (self.state_path, self.quota_path, self.budget_path)
        before = [path.read_bytes() for path in paths]
        env = dict(ON)
        self.select(env=env)
        self.assertEqual(env, ON)
        self.assertEqual([path.read_bytes() for path in paths], before)
        self.assertEqual(len(json.loads(self.journal_path.read_text())["requests"]), 1)
        self.state["paused"] = True
        self.save()
        with patch("Build.guardrails.failover.aws_adapter.activate") as adapter:
            self.refused()
        adapter.assert_not_called()

    def test_A15_repeated_admissions_cannot_reuse_same_aws_headroom(self):
        self.select(candidate_aws_usd="6")
        self.refused(candidate_aws_usd="6")
        self.assertEqual(len(json.loads(self.journal_path.read_text())["requests"]), 1)

    def test_aws_requires_bucket_and_existing_global_journal(self):
        del self.state["AWS"]
        self.save()
        self.refused()
        self.state["AWS"] = {"historical_usd": "0", "requests": [], "credit_headroom_usd": "50"}
        self.save()
        self.journal_path.unlink()
        self.refused()

    def test_aws_also_reserves_meta_candidate_before_returning_plan(self):
        self.state["Meta Model API"]["historical_usd"] = "119"
        self.save()
        self.select(candidate_meta_usd=".5")
        self.refused(candidate_meta_usd=".5")
        rows = json.loads(self.journal_path.read_text())["requests"]
        self.assertEqual({r["provider"] for r in rows}, {"AWS", "Meta Model API"})
        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
