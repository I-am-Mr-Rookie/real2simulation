"""Offline synthetic admission + read-only public-library regression. No paid transports."""
import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from Build.guardrails.admission import ReconstructionPaused, require_reconstruction

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 10, 29, 22, 10, tzinfo=timezone.utc)


def snapshot():
    return {"schema": "reconstruction-admission/1", "as_of": NOW.isoformat(),
            "paused": False, "coverage_verified": True, "credit_verified": True,
            "sources": ["SYNTHETIC history receipt", "SYNTHETIC pending ledger"],
            "Meta Model API": {"historical_usd": "110", "requests": [], "credit_headroom_usd": "40"},
            "Modal": {"historical_usd": "1", "requests": [], "credit_headroom_usd": "29"}}


def row(provider="Modal", **costs):
    return {"request_id": "synthetic-attempt-1", "provider": provider,
            "reserved_usd": "1", "billed_usd": None, **costs}


class Admission(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "state.json"
        self.state = snapshot()

    def save(self):
        self.path.write_text(json.dumps(self.state), encoding="utf-8")

    def admit(self, modal="0.50", meta="0"):
        return require_reconstruction(self.path, candidate_modal_usd=modal,
                                      candidate_meta_usd=meta, now=NOW)

    def paused(self):
        with self.assertRaises(ReconstructionPaused) as caught:
            self.admit()
        self.assertEqual((caught.exception.code, caught.exception.retryable), ("SPEND_PAUSED", False))

    def test_below_caps_allows_without_writing_or_dispatching(self):
        self.state["Modal"]["requests"] = [row(est_usd="2", billed_usd=".01")]
        self.save()
        before = self.path.read_bytes()
        result = self.admit()
        self.assertEqual(result["modal_projected_usd"], Decimal("3.5"))
        self.assertTrue(result["meta"]["routine_cap_allows"])
        self.assertEqual(self.path.read_bytes(), before)

    def test_meta_history_pending_estimate_and_candidate_reach_cap(self):
        self.state["Meta Model API"]["requests"] = [row("Meta Model API", reserved_usd="2", est_usd="9")]
        self.save()
        self.assertEqual(self.admit(meta=".99")["meta"]["projected_usd"], Decimal("119.99"))
        for candidate in ("1", "1.01"):
            with self.subTest(candidate=candidate), self.assertRaises(ReconstructionPaused):
                self.admit(meta=candidate)

    def test_existing_meta_cap_blocks_even_zero_new_meta_cost(self):
        for history in ("120", "121"):
            self.state["Meta Model API"]["historical_usd"] = history
            self.save()
            self.paused()

    def test_modal_authorized_ceiling_is_not_promotional_credit(self):
        self.state["Modal"].update(historical_usd="30", credit_headroom_usd="130")
        self.save()
        self.paused()

    def test_five_dollar_floor_counts_candidate_and_credit(self):
        for field, allowed, denied in (("historical_usd", "24.5", "24.50000001"),
                                      ("credit_headroom_usd", "5.5", "5.49999999")):
            self.state = snapshot()
            self.state["Modal"][field] = allowed
            self.save()
            self.admit()
            self.state["Modal"][field] = denied
            self.save()
            self.paused()

    def test_meta_credit_shortfall_blocks_below_routine_cap(self):
        self.state["Meta Model API"]["credit_headroom_usd"] = ".49"
        self.save()
        with self.assertRaises(ReconstructionPaused):
            self.admit(meta=".50")

    def test_missing_corrupt_wrong_encoding_and_unreadable_state_pause(self):
        self.paused()
        for contents in (b'{', b'null', b'[]', b'{}', b'\xff'):
            with self.subTest(contents=contents):
                self.path.write_bytes(contents)
                self.paused()
        with patch.object(Path, "read_text", side_effect=PermissionError("synthetic private detail")):
            with self.assertRaises(ReconstructionPaused) as caught:
                self.admit()
            self.assertNotIn("private detail", str(caught.exception))

    def test_every_required_field_missing_pauses(self):
        base = snapshot()
        for key in base:
            with self.subTest(key=key):
                self.state = copy.deepcopy(base)
                del self.state[key]
                self.save()
                self.paused()
        for provider in ("Meta Model API", "Modal"):
            for key in base[provider]:
                with self.subTest(provider=provider, key=key):
                    self.state = copy.deepcopy(base)
                    del self.state[provider][key]
                    self.save()
                    self.paused()

    def test_duplicate_json_fields_cannot_hide_spend(self):
        source = json.dumps(snapshot())
        self.path.write_text(source.replace('"historical_usd": "110"',
                                            '"historical_usd": "120", "historical_usd": "0"'))
        self.paused()

    def test_corrupt_provider_money_fields_pause(self):
        for provider in ("Meta Model API", "Modal"):
            for field in ("historical_usd", "credit_headroom_usd"):
                for value in (None, False, "NaN", "-1", "unknown"):
                    with self.subTest(provider=provider, field=field, value=value):
                        self.state = snapshot()
                        self.state[provider][field] = value
                        self.save()
                        self.paused()

    def test_unverified_kill_switch_inventory_and_schema_pause(self):
        for key, value in (("paused", True), ("paused", 0), ("credit_verified", False),
                           ("coverage_verified", 1), ("sources", []), ("sources", ["x", "x"]),
                           ("sources", [None]), ("schema", "unknown")):
            with self.subTest(key=key, value=value):
                self.state = snapshot()
                self.state[key] = value
                self.save()
                self.paused()

    def test_stale_future_or_naive_clock_pause(self):
        for stamp in ((NOW - timedelta(minutes=5, microseconds=1)).isoformat(),
                      (NOW + timedelta(microseconds=1)).isoformat(), NOW.replace(tzinfo=None).isoformat(), "bad"):
            self.state["as_of"] = stamp
            self.save()
            self.paused()
        self.state = snapshot()
        self.save()
        with self.assertRaises(ReconstructionPaused):
            require_reconstruction(self.path, candidate_modal_usd=".5", now=NOW.replace(tzinfo=None))

    def test_invalid_money_and_unbounded_candidate_pause(self):
        self.save()
        for bad in (None, True, "NaN", "Infinity", "-1", {}, "1e1000"):
            with self.subTest(bad=bad), self.assertRaises(ReconstructionPaused):
                self.admit(modal=bad)
            with self.subTest(meta=bad), self.assertRaises(ReconstructionPaused):
                self.admit(meta=bad)
        with self.assertRaises(ReconstructionPaused):
            self.admit(modal=0)

    def test_invalid_rows_or_duplicate_identity_pause(self):
        for provider in ("Meta Model API", "Modal"):
            for rows in ([row(provider), row(provider)], [row("other")], [None], [{}],
                         [row(provider, reserved_usd=None)], [row(provider, billed_usd="NaN")],
                         [row(provider, settled=True, billed_usd=".01")]):
                with self.subTest(provider=provider, rows=rows):
                    self.state = snapshot()
                    self.state[provider]["requests"] = rows
                    self.save()
                    self.paused()

    def test_final_reconciliation_only_releases_its_own_reservation(self):
        self.state["Modal"]["requests"] = [row(reserved_usd="25", est_usd="24", billed_usd=".01")]
        self.save()
        self.paused()
        self.state["Modal"]["requests"][0].update(settled=True, reconciliation_ref="SYNTHETIC final receipt")
        self.save()
        self.assertEqual(self.admit()["modal_projected_usd"], Decimal("1.51"))

    def test_guard_can_precede_existing_upload_store_and_reservation(self):
        # Integration harness only: production callers remain unchanged by contract.
        from Build.pipeline.gpu_stages import reserve
        from Build.pipeline.uploads import UploadService

        store = self.path.parent / "uploads"
        service = UploadService(store, now=lambda: NOW)
        ledger = self.path.parent / "gpu-ledger.jsonl"
        self.save()
        self.admit()
        session = service.create("synthetic-owner", "video/mp4", 12, "0" * 64)
        runtime = self.path.parent / "evidence/S20/runtime"
        runtime.mkdir(parents=True)
        state = copy.deepcopy(self.state)
        state["as_of"] = datetime.now(timezone.utc).isoformat()
        (runtime / "receipt.json").write_text(json.dumps(state), encoding="utf-8")
        (runtime / "reservations.json").write_text(json.dumps(
            {"schema": "gpu-reservations/1", "requests": [], "ledgers": []}), encoding="utf-8")
        with patch("Build.guardrails.reservations.repository_root", return_value=self.path.parent):
            reserve(ledger, "reconstruct", "synthetic-attempt", .5)
        self.assertEqual(service.get("synthetic-owner", session["upload_id"])["status"], "open")
        files = sorted(p.relative_to(store) for p in store.rglob("*"))
        before = ledger.read_bytes()
        self.state["Meta Model API"]["historical_usd"] = "120"
        self.save()
        with self.assertRaises(ReconstructionPaused):
            self.admit()
            service.create("synthetic-owner", "video/mp4", 12, "0" * 64)
            reserve(ledger, "reconstruct", "synthetic-attempt-2", .5)
        self.assertEqual(ledger.read_bytes(), before)
        self.assertEqual(sorted(p.relative_to(store) for p in store.rglob("*")), files)

    def test_guest_precomputed_fixture_read_does_not_consult_admission(self):
        # Read-only existing public-library contract + synthetic asset, NOT HTTP/playback evidence.
        shell = ROOT / "Build/web/src/shell"
        for state in ("missing", "corrupt", "breached"):
            with self.subTest(state=state):
                if state == "corrupt":
                    self.path.write_text("{", encoding="utf-8")
                elif state == "breached":
                    self.state["Meta Model API"]["historical_usd"] = "120"
                    self.save()
                self.paused()
                with patch("Build.guardrails.admission.require_reconstruction", side_effect=AssertionError("library consulted guard")):
                    example = next(x for x in json.loads((shell / "examples.json").read_text()) if x["kind"] == "library")
                    mount = json.loads((shell / "fixture-mounts.json").read_text())["mounts"][0]
                    manifest = json.loads((ROOT / mount["repository_manifest"]).read_text())
                    self.assertEqual(example["scene"]["access"], "public-library")
                    self.assertEqual(example["scene"]["scene_id"], manifest["id"])
                    self.assertTrue(manifest["synthetic"])
        page = (ROOT / "Build/web/src/app/(public)/library/page.jsx").read_text()
        self.assertIn("Guest browsing needs no account", page)
        self.assertNotRegex(page, r"\b(import|require|fetch|SPEND_PAUSED|require_reconstruction)\b")


if __name__ == "__main__":
    unittest.main()
