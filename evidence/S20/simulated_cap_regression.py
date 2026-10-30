"""Gate C SIMULATED ONLY: real local guards, temporary ledgers, no provider launches.

Run from the repository root: python -B evidence/S20/simulated_cap_regression.py
"""
import ast
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
from contextlib import ExitStack
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Build.guardrails import admission, failover, reservations, settlement, standalone
from Build.guardrails.accounting import liability_usd
from Build.guardrails.admission import ReconstructionPaused
from Build.guardrails.durable import read_json, write_json

NOW = datetime(2026, 10, 30, 9, 0, tzinfo=timezone.utc)
MAINS = ("Build/gpu/runtime.py", "Build/gpu/scene_job.py",
         "Build/measurement/runtime/modal_track.py", "Build/reconstruction/spike/modal_rm02.py",
         "Build/reconstruction/spike/modal_scenes.py")


class Clock(datetime):
    @classmethod
    def now(cls, tz=None):
        return NOW if tz is not None else NOW.replace(tzinfo=None)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def run_regression():
    """Return deterministic evidence; no actual state, environment or credential reads."""
    events = []
    library_checks = []
    with ExitStack() as stack:
        base = Path(stack.enter_context(tempfile.TemporaryDirectory()))
        for module in (admission, reservations, settlement):
            stack.enter_context(patch.object(module, "datetime", Clock))
        stack.enter_context(patch.dict(os.environ, {}, clear=True))
        network = stack.enter_context(patch.object(socket.socket, "connect", side_effect=AssertionError("network forbidden")))
        processes = stack.enter_context(patch.object(subprocess, "Popen", side_effect=AssertionError("launch forbidden")))
        aws = stack.enter_context(patch.object(failover.aws_adapter, "activate", side_effect=AssertionError("AWS must stay OFF")))

        def fixture(name, *, meta="0", modal="0", credit="30"):
            root = base / name
            runtime = root / "evidence/S20/runtime"
            runtime.mkdir(parents=True)
            receipt = {"schema": "reconstruction-admission/1", "as_of": NOW.isoformat(),
                       "paused": False, "coverage_verified": True, "credit_verified": True,
                       "sources": ["SIMULATED fixture; NOT verified provider balances"],
                       "Meta Model API": {"historical_usd": meta, "requests": [],
                                          "credit_headroom_usd": str(Decimal("150") - Decimal(meta))},
                       "Modal": {"historical_usd": modal, "requests": [], "credit_headroom_usd": credit}}
            write_json(runtime / "receipt.json", receipt)
            write_json(runtime / "reservations.json", {"schema": "gpu-reservations/1", "requests": [], "ledgers": []})
            return root, runtime, receipt

        def totals(root, runtime):
            journal = read_json(runtime / "reservations.json")
            state, _ = reservations.project(root, read_json(runtime / "receipt.json"), journal)
            result = {}
            for provider in ("Meta Model API", "Modal"):
                bucket = state[provider]
                total = Decimal(bucket["historical_usd"]) + sum(
                    (liability_usd(row) for row in bucket["requests"]), Decimal(0))
                result[provider] = format(total, ".8f")
            result["journal_rows"] = len(journal["requests"])
            result["active_modal_jobs"] = sum(r["provider"] == "Modal" and not r.get("settled", False)
                                              for r in journal["requests"])
            return result

        def event(root, runtime, scene, action, provider, amount, operation, *, paused=False):
            before = read_json(runtime / "reservations.json")
            try:
                value = operation()
            except ReconstructionPaused as exc:
                check(paused, scene + ": unexpected refusal")
                check(exc.code == "SPEND_PAUSED" and exc.retryable is False, "wrong pause contract")
                check(read_json(runtime / "reservations.json") == before, "refusal mutated journal")
                outcome, value = "SPEND_PAUSED", None
            else:
                check(not paused, scene + ": unexpectedly admitted")
                outcome = "PASS"
            events.append({"scene": scene, "action": action, "provider": provider,
                           "cost_kind": "SIMULATED", "simulated_usd": format(Decimal(amount), ".8f"),
                           "outcome": outcome, "after": totals(root, runtime)})
            return value

        def library_read(reason):
            # Existing public DTO/manifest reads only; not HTTP, rendered UI or playback.
            with patch.object(admission, "require_reconstruction", side_effect=AssertionError("library called admission")):
                shell = REPO / "Build/web/src/shell"
                example = next(row for row in read_json(shell / "examples.json") if row["kind"] == "library")
                mount = read_json(shell / "fixture-mounts.json")["mounts"][0]
                manifest = read_json(REPO / mount["repository_manifest"])
                check(example["scene"]["access"] == "public-library" and manifest["synthetic"] is True
                      and example["scene"]["scene_id"] == manifest["id"], "public library fixture unavailable")
            library_checks.append({"admission_state": reason, "read": "existing public DTO + synthetic manifest",
                                   "outcome": "PASS", "cost_kind": "SIMULATED", "simulated_usd": "0.00000000"})

        # Distinct ledgers/stages and a linked worktree must share one Meta envelope.
        root, runtime, receipt = fixture("meta", meta="119.7")
        common = root / ".git"
        gitdir = common / "worktrees/linked"
        gitdir.mkdir(parents=True)
        (gitdir / "commondir").write_text("../..", encoding="utf-8")
        linked = root / "linked"
        linked.mkdir()
        (linked / ".git").write_text("gitdir: " + str(gitdir), encoding="utf-8")
        check(reservations.repository_root(linked) == root, "linked worktree escaped canonical state")
        for i, amount in enumerate((".05", ".1", ".14999999", ".00000001", ".00000002")):
            stage = "understand" if i % 2 == 0 else "record_muse"
            event(root, runtime, f"SIM-meta-{i+1}", "reserve_meta", "Meta Model API", amount,
                  lambda i=i, amount=amount, stage=stage: reservations.reserve_meta(
                      linked, linked / f"scene-{i}/meta-ledger.jsonl", stage, f"scene-{i}", amount,
                      max_calls=10, cap_usd="1"), paused=i >= 3)
        check(totals(root, runtime)["Meta Model API"] == "119.99999999", "global Meta stop failed")
        demo = Decimal("150") - Decimal(totals(root, runtime)["Meta Model API"])
        check(demo >= 30, "demo reserve consumed")
        library_read("Meta candidate reaches/exceeds routine cap")

        # Two parent jobs, one-use child claim, hash-bound settlement, third scene.
        root, runtime, receipt = fixture("modal", modal="24")
        ledger = root / "scenes/gpu-ledger.jsonl"
        def reserve(key, amount=".5"):
            return reservations.reserve_gpu(root, ledger, "reconstruct", key, amount, max_jobs=2, cap_usd="1")
        first = event(root, runtime, "SIM-modal-1", "parent_reserve", "Modal", ".5", lambda: reserve("one"))
        event(root, runtime, "SIM-modal-2", "parent_reserve", "Modal", ".5", lambda: reserve("two"))
        event(root, runtime, "SIM-modal-3-before-settle", "third_job_refused", "Modal", ".01",
              lambda: reserve("three"), paused=True)
        with patch.object(standalone, "ROOT", root), patch.dict(os.environ, {"S20_MODAL_REQUEST_ID": first}):
            event(root, runtime, "SIM-modal-1-child", "one_use_handoff", "Modal", "0",
                  lambda: standalone.admit_standalone("scene-job:SIM-modal-1"))
            event(root, runtime, "SIM-modal-1-replay", "handoff_replay", "Modal", "0",
                  lambda: standalone.admit_standalone("scene-job:SIM-modal-1"), paused=True)
        check(totals(root, runtime)["journal_rows"] == 2, "handoff double-reserved")
        with ledger.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"request_id": first, "provider": "Modal", "app_id": "ap-SIMULATED-one"}) + "\n")
        log, bill, proof_path = (root / name for name in ("cost.json", "billing.json", "proof.json"))
        write_json(log, {"app_id": "ap-SIMULATED-one", "cost": {"billed": {"status": "billed", "total_usd": ".1"}}})
        write_json(bill, [{"object_id": "ap-SIMULATED-one", "resource": "GPU", "cost": ".1",
                           "environment": "SIMULATED", "interval_start": NOW.isoformat()}])
        proof = {"schema": "modal-settlement/1", "request_id": first, "app_id": "ap-SIMULATED-one",
                 "status": "completed", "containers": [], "billing_final_verified": True,
                 "reviewed_by": "SIMULATED operator; NOT provider evidence", "completed_at": NOW.isoformat(),
                 "billing_read_at": NOW.isoformat(), "scene_log": log.name, "billing_report": bill.name}
        for name, path in (("scene_log", log), ("billing_report", bill)):
            proof[name + "_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        write_json(proof_path, proof)
        event(root, runtime, "SIM-modal-1-settle", "simulated_final_bill", "Modal", ".1",
              lambda: settlement.settle_gpu(root, first, proof_path))
        event(root, runtime, "SIM-modal-3", "slot_reused_history_retained", "Modal", ".4", lambda: reserve("three", ".4"))
        check(totals(root, runtime)["Modal"] == "25.00000000", "settled liability lost or double counted")
        event(root, runtime, "SIM-modal-settle-replay", "settlement_replay", "Modal", "0",
              lambda: settlement.settle_gpu(root, first, proof_path), paused=True)
        def tampered_attempt():
            original = bill.read_bytes()
            bill.write_text("[]", encoding="utf-8")
            try:
                return reserve("changed-proof")
            finally:
                bill.write_bytes(original)
        event(root, runtime, "SIM-modal-tampered-proof", "tampered_proof_refused_then_restored", "Modal", ".5",
              tampered_attempt, paused=True)

        # Direct preflight exercises the tight floor and outer cap without the two-job cap masking them.
        cases = (("monthly-floor-exact", "24", "30", "1", False),
                 ("monthly-floor-below", "24", "30", "1.00000001", True),
                 ("monthly-cap-exact", "29", "30", "1", True),
                 ("monthly-cap-above", "29", "30", "1.00000001", True),
                 ("credit-floor-exact", "0", "5.5", ".5", False),
                 ("credit-floor-below", "0", "5.5", ".50000001", True))
        for name, history, credit, amount, paused in cases:
            root, runtime, receipt = fixture(name, modal=history, credit=credit)
            event(root, runtime, "SIM-" + name, "select_provider_AWS_unset", "Modal", amount,
                  lambda: failover.select_provider(runtime / "receipt.json", candidate_modal_usd=amount, now=NOW),
                  paused=paused)

        root, runtime, receipt = fixture("standalone")
        with patch.object(standalone, "ROOT", root):
            event(root, runtime, "SIM-no-bound", "standalone_missing_bound", "Modal", "0",
                  lambda: standalone.admit_standalone("scene-job:SIM"), paused=True)
            with patch.dict(os.environ, {"S20_MODAL_RESERVATION_USD": ".5"}):
                event(root, runtime, "SIM-standalone-1", "standalone_reserve_and_claim", "Modal", ".5",
                      lambda: standalone.admit_standalone("scene-job:SIM-one"))
                event(root, runtime, "SIM-pipeline-with-standalone", "same_global_envelope", "Modal", ".5",
                      lambda: reservations.reserve_gpu(root, root / "pipeline/gpu-ledger.jsonl", "segment",
                                                       "SIM-two", ".5", max_jobs=2, cap_usd="1"))
                event(root, runtime, "SIM-standalone-3", "shared_job_cap", "Modal", ".5",
                      lambda: standalone.admit_standalone("scene-job:SIM-three"), paused=True)

        root, runtime, receipt = fixture("active-dollar-cap")
        for scene, amount, paused in (("one", ".6", False), ("over", ".40000001", True), ("exact", ".4", False)):
            event(root, runtime, "SIM-active-cap-" + scene, "global_one_dollar_active_bound", "Modal", amount,
                  lambda scene=scene, amount=amount: reservations.reserve_gpu(
                      root, root / scene / "gpu-ledger.jsonl", "reconstruct", scene, amount, max_jobs=2, cap_usd="1"),
                  paused=paused)

        root, runtime, receipt = fixture("pause")
        receipt["paused"] = True
        write_json(runtime / "receipt.json", receipt)
        event(root, runtime, "SIM-paused-meta", "explicit_pause", "Meta Model API", ".1",
              lambda: reservations.reserve_meta(root, root / "meta.jsonl", "understand", "paused", ".1",
                                                max_calls=6, cap_usd="1"), paused=True)
        event(root, runtime, "SIM-paused-failover", "no_auto_AWS_on_pause", "Modal", ".1",
              lambda: failover.select_provider(runtime / "receipt.json", candidate_modal_usd=".1", now=NOW), paused=True)
        library_read("explicit SPEND_PAUSED")
        original = (runtime / "receipt.json").read_bytes()
        (runtime / "receipt.json").unlink()
        try:
            try:
                failover.select_provider(runtime / "receipt.json", candidate_modal_usd=".1", now=NOW)
            except ReconstructionPaused as exc:
                check(exc.code == "SPEND_PAUSED" and exc.retryable is False, "missing ledger not paused")
                library_read("missing admission receipt")
            else:
                raise AssertionError("unknown accounting state admitted")
        finally:
            (runtime / "receipt.json").write_bytes(original)
        with patch.object(standalone, "ROOT", root), patch.dict(os.environ, {"S20_MODAL_RESERVATION_USD": ".1"}):
            for file in MAINS:
                tree = ast.parse((REPO / file).read_text(encoding="utf-8"))
                main = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "main")
                start = next(i for i, n in enumerate(main.body) if isinstance(n, ast.ImportFrom)
                             and n.module == "Build.guardrails.standalone")
                tail = ast.fix_missing_locations(ast.Module(body=main.body[start:], type_ignores=[]))
                event(root, runtime, "SIM-main:" + file, "real_launch_tail_refused", "Modal", ".1",
                      lambda tail=tail, file=file: exec(compile(tail, file, "exec"), {"scene": "SIM", "clip": "SIM"}),
                      paused=True)
        root, runtime, receipt = fixture("AWS-off")
        plan = event(root, runtime, "SIM-AWS-default", "AWS_flag_unset", "Modal", ".1",
                     lambda: failover.select_provider(runtime / "receipt.json", candidate_modal_usd=".1", now=NOW))
        check(plan["provider"] == "Modal" and plan["aws"] is None and plan["launched"] is False, "AWS selected by default")
        for name, mock in (("network", network), ("process", processes), ("AWS activation", aws)):
            check(mock.call_count == 0, name + " attempted")
        check("R2S_ENABLE_AWS" not in os.environ, "AWS enabled during regression")

    return {"schema": "gate-c-simulated-regression/1", "status": "PASS", "mode": "SIMULATED_ONLY",
            "scope": "S20d local simulated-cap regression; NOT full runtime Gate C",
            "cost_semantics": "Per-event candidate bounds or simulated final bills; NOT additive spend. See after liabilities.",
            "provider_calls": 0, "actual_spend_usd": "0.00000000", "clock": NOW.isoformat(),
            "meta_routine_stop_usd": "120", "meta_demo_reserve_usd": "30",
            "meta_demo_remaining_simulated_usd": str(demo), "modal_cap_usd": "30", "modal_floor_usd": "5",
            "aws_flag": "UNSET", "aws_activation_calls": 0, "events": events, "public_library_checks": library_checks,
            "limitations": ["Offline local guards only; NOT live enforcement, measured costs or physical gate evidence.",
                            "Modal $5 floor makes $25 the effective routine monthly ceiling; outer $30 cap also refuses.",
                            "R-C R2-1..4 remain: operator settlement trust, bearer IDs, entrypoint-only guard, removed-worktree pause.",
                            "Upload HTTP integration/durable daily user quota remain unimplemented per ADMISSION.md; no exhausted-quota claim.",
                            "Library check reads existing public DTO + synthetic manifest, NOT live HTTP, rendered UI or playback."]}


if __name__ == "__main__":
    result = run_regression()
    target = REPO / "evidence/S20/S20d-regression.json"
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"PASS SIMULATED_ONLY: {len(result['events'])} checks; provider calls=0; spend=$0; {target.name}")
