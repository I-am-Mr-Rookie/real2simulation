"""No-network regressions for the R-C N1/M3/N2 admission seams."""
import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from Build.agent import record_muse
from Build.guardrails import standalone
from Build.guardrails.admission import ReconstructionPaused
from Build.guardrails.durable import read_json, write_json
from Build.guardrails.reservations import reserve_meta, reserve_gpu
from Build.pipeline import understand
from Build.pipeline.jobs import StageError

REPO = Path(__file__).resolve().parents[2]


class LiveAdmission(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.runtime = self.root / "evidence/S20/runtime"
        self.runtime.mkdir(parents=True)
        self.receipt = {"schema": "reconstruction-admission/1", "as_of": datetime.now(timezone.utc).isoformat(),
                        "paused": False, "coverage_verified": True, "credit_verified": True,
                        "sources": ["SYNTHETIC isolated receipt"],
                        "Meta Model API": {"historical_usd": "0", "requests": [], "credit_headroom_usd": "150"},
                        "Modal": {"historical_usd": "0", "requests": [], "credit_headroom_usd": "30"}}
        self.save()
        write_json(self.runtime / "reservations.json", {"schema": "gpu-reservations/1", "requests": [], "ledgers": []})
        self.ledger = self.root / "calls.jsonl"
        self.body = {"model": "fake", "input": [{"content": [{"type": "input_text", "text": "hello"}]}]}

    def save(self):
        write_json(self.runtime / "receipt.json", self.receipt)

    def reserve(self, name="one", stage="understand", amount=".1", **kwargs):
        return reserve_meta(self.root, self.root / name / "calls.jsonl", stage, name, amount,
                            max_calls=kwargs.get("max_calls", 6), cap_usd=kwargs.get("cap_usd", "1"))

    def test_global_stop_cannot_be_reset_by_fresh_ledgers_or_stage(self):
        self.receipt["Meta Model API"]["historical_usd"] = "119.8"
        self.save()
        self.reserve(amount=".1")
        for stage in ("understand", "record_muse"):
            with self.assertRaises(ReconstructionPaused):
                self.reserve("fresh-" + stage, stage, ".1")
        self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 1)

    def test_global_contract_count_across_fresh_ledgers(self):
        self.reserve(max_calls=1)
        with self.assertRaises(ReconstructionPaused):
            self.reserve("fresh", max_calls=1)

    def test_first_seen_caller_ledger_also_counts_toward_global_stop(self):
        self.receipt["Meta Model API"]["historical_usd"] = "119.5"
        self.save()
        self.ledger.write_text(json.dumps({"request_id": "legacy", "provider": "Meta Model API",
                                           "reserved_usd": ".45"}) + "\n")
        with self.assertRaises(ReconstructionPaused):
            reserve_meta(self.root, self.ledger, "understand", "new", ".1", max_calls=6, cap_usd=1)
        self.assertEqual(read_json(self.runtime / "reservations.json")["requests"], [])

    def test_real_processes_share_meta_lock_and_journal(self):
        self.receipt["Meta Model API"]["historical_usd"] = "119.85"
        self.save()
        code = '''
import sys
from pathlib import Path
from Build.guardrails.reservations import reserve_meta
from Build.guardrails.admission import ReconstructionPaused
try:
    reserve_meta(Path(sys.argv[1]), Path(sys.argv[1])/sys.argv[2]/"meta.jsonl",
                 "understand", sys.argv[2], ".1", max_calls=6, cap_usd=1)
    print("admitted")
except ReconstructionPaused:
    print("paused")
'''
        def child(name):
            return subprocess.run([sys.executable, "-c", code, str(self.root), name], cwd=REPO,
                                  capture_output=True, text=True, check=True, timeout=45).stdout.strip()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(child, ("one", "two")))
        self.assertEqual(sorted(results), ["admitted", "paused"])
        self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 1)

    def test_failed_meta_append_retains_liability_and_missing_inventory_pauses(self):
        target = self.root / "blocked"
        target.write_text("not a directory")
        with self.assertRaises(ReconstructionPaused):
            self.reserve("blocked")
        self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 1)
        with self.assertRaises(ReconstructionPaused):
            self.reserve("fresh")

    def test_meta_credit_and_result_overrun_not_lower_estimate_control_admission(self):
        self.receipt["Meta Model API"]["credit_headroom_usd"] = ".05"
        self.save()
        with self.assertRaises(ReconstructionPaused):
            self.reserve()
        self.receipt["Meta Model API"]["credit_headroom_usd"] = "150"
        self.save()
        key = self.reserve(amount=".1")
        with (self.root / "one/calls.jsonl").open("a") as stream:
            stream.write(json.dumps({"request_id": key, "provider": "Meta Model API", "reserved_usd": ".1",
                                     "est_usd": ".01", "billed_usd": ".95"}) + "\n")
        with self.assertRaises(ReconstructionPaused):
            self.reserve("fresh", amount=".1")

    def test_global_contract_dollars_and_replay_across_fresh_ledgers(self):
        self.reserve(amount=".7")
        with self.assertRaises(ReconstructionPaused):
            self.reserve("fresh", amount=".4")
        with self.assertRaises(ReconstructionPaused):
            reserve_meta(self.root, self.root / "other.jsonl", "understand", "one", ".1", max_calls=6, cap_usd=1)

    def test_meta_row_written_before_understand_post_and_results_fold(self):
        def transport(*args, **kwargs):
            self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 1)
            self.assertEqual(json.loads(self.ledger.read_text())["stage"], "understand")
            return SimpleNamespace(status_code=200, headers={"content-type": "application/json"}, json=lambda: {})
        with patch.object(understand, "ROOT", self.root), patch("httpx.post", side_effect=transport), \
                patch("dotenv.dotenv_values", return_value={"MODEL_API_BASE_URL": "https://invalid.example", "MODEL_API_KEY": "SYNTHETIC"}):
            understand.live_post(self.ledger)(self.body, "fake-key")
            self.assertGreater(understand.reserve(self.body, self.ledger), 0)

    def test_understand_missing_corrupt_paused_and_locked_state_never_posts(self):
        for fault in ("paused", "corrupt", "missing", "locked"):
            with self.subTest(fault=fault):
                self.receipt["paused"] = fault == "paused"
                self.save()
                path = self.runtime / "receipt.json"
                if fault == "corrupt":
                    path.write_text("{broken")
                if fault == "missing":
                    path.unlink()
                if fault == "locked":
                    (self.runtime / "admission.lock").write_text("fake owner")
                with patch.object(understand, "ROOT", self.root), patch("httpx.post") as post:
                    with self.assertRaises(StageError) as caught:
                        understand.live_post(self.ledger)(self.body, "blocked")
                    self.assertEqual((caught.exception.code, caught.exception.retryable), ("SPEND_PAUSED", False))
                    post.assert_not_called()
                (self.runtime / "admission.lock").unlink(missing_ok=True)

    def test_transport_failure_keeps_reservation_and_refuses_replay(self):
        with patch.object(understand, "ROOT", self.root), patch("httpx.post", side_effect=RuntimeError("fake failure")), \
                patch("dotenv.dotenv_values", return_value={"MODEL_API_BASE_URL": "https://invalid.example", "MODEL_API_KEY": "SYNTHETIC"}):
            with self.assertRaises(RuntimeError):
                understand.live_post(self.ledger)(self.body, "failed")
            with self.assertRaises(StageError):
                understand.live_post(self.ledger)(self.body, "failed")
        self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 1)

    def test_record_muse_persists_before_post_and_keeps_failed_transport(self):
        import httpx
        scene = self.root / "scene"
        scene.mkdir()
        (scene / "scene.json").write_text("{}")
        def transport(*args, **kwargs):
            self.assertEqual(read_json(self.runtime / "reservations.json")["requests"][0]["stage"], "record_muse")
            self.assertTrue(self.ledger.exists())
            raise httpx.ConnectError("SYNTHETIC offline failure")
        with patch.object(record_muse, "ROOT", self.root), patch.object(record_muse, "LEDGER", self.ledger), \
                patch.object(record_muse, "FIXTURES", self.root / "fixtures"), \
                patch.object(record_muse, "scene_context", return_value={}), \
                patch.object(record_muse.muse, "build_request", return_value={"model": "fake", "input": "{}"}), \
                patch.object(record_muse.muse, "understand", return_value={}), \
                patch.object(record_muse, "dotenv_values", return_value={"MODEL_API_BASE_URL": "https://invalid.example", "MODEL_API_KEY": "SYNTHETIC"}), \
                patch.object(record_muse.httpx, "post", side_effect=transport):
            record_muse.main("fake", "scene")
            self.assertGreater(record_muse.reserve({"input": "{}"}), 0)
        self.assertEqual(len(self.ledger.read_text().splitlines()), 2)

    def test_record_muse_pause_never_posts(self):
        self.receipt["paused"] = True
        self.save()
        scene = self.root / "scene"
        scene.mkdir()
        (scene / "scene.json").write_text("{}")
        with patch.object(record_muse, "ROOT", self.root), patch.object(record_muse, "LEDGER", self.ledger), \
                patch.object(record_muse, "scene_context", return_value={}), \
                patch.object(record_muse.muse, "build_request", return_value={"input": "{}"}), \
                patch.object(record_muse.httpx, "post") as post:
            with self.assertRaisesRegex(SystemExit, "SPEND_PAUSED"):
                record_muse.main("fake", "scene")
            post.assert_not_called()

    def test_standalone_and_pipeline_share_same_job_cap(self):
        with patch.object(standalone, "ROOT", self.root), patch.dict(os.environ, {"S20_MODAL_RESERVATION_USD": ".5"}):
            standalone.admit_standalone("fake")
            reserve_gpu(self.root, self.root / "gpu.jsonl", "segment", "fake", ".5", max_jobs=2, cap_usd=1)
            standalone.admit_standalone("third")  # S07j envelope 2: cumulative 3 jobs/$1.50
            with self.assertRaises(ReconstructionPaused):
                standalone.admit_standalone("fresh")

    def seed_envelope1(self):
        """Mirror S07i: OWN01 $0.60 + batch $0.40 in the old ledger, both still unsettled."""
        old = self.runtime / "standalone-gpu-ledger.jsonl"
        for key, amount in (("modal-track:OWN01:x", ".6"), ("modal-track:batch:OWN02:y", ".4")):
            reserve_gpu(self.root, old, "segment", key, amount, max_jobs=2, cap_usd=1)
        return old, old.read_bytes(), read_json(self.runtime / "reservations.json")["requests"]

    def test_envelope2_keeps_old_rows_and_admits_only_its_bound(self):
        old, before, rows = self.seed_envelope1()
        self.assertEqual(standalone.LEDGER, "evidence/S20/runtime/standalone-gpu-ledger-2.jsonl")
        with patch.object(standalone, "ROOT", self.root):
            with patch.dict(os.environ, {"S20_MODAL_RESERVATION_USD": ".51"}), self.assertRaises(ReconstructionPaused):
                standalone.admit_standalone("modal-track:batch:OWN07")  # $1.00 old + $0.51 > $1.50
            with patch.dict(os.environ, {"S20_MODAL_RESERVATION_USD": ".4"}):
                request = standalone.admit_standalone("modal-track:batch:OWN07")
                with self.assertRaises(ReconstructionPaused):
                    standalone.admit_standalone("modal-track:batch:again")  # 3 jobs reached
            with patch.dict(os.environ, {"S20_MODAL_RESERVATION_USD": ".01"}), self.assertRaises(ReconstructionPaused):
                standalone.admit_standalone("modal-track:tiny")
        journal = read_json(self.runtime / "reservations.json")["requests"]
        self.assertEqual((old.read_bytes(), journal[:2]), (before, rows))  # never cleared/rewritten/released
        self.assertEqual(len(journal), 3)
        self.assertTrue(request.startswith(standalone.LEDGER + ":segment:"))
        new = (self.root / standalone.LEDGER).read_text().splitlines()
        self.assertEqual([json.loads(r)["reserved_usd"] for r in new], ["0.40000000"])

    def test_envelope2_still_requires_global_modal_headroom(self):
        self.seed_envelope1()
        self.receipt["Modal"]["credit_headroom_usd"] = "1.2"  # < $1.00 old liability + $0.40
        self.save()
        with patch.object(standalone, "ROOT", self.root), patch.dict(os.environ, {"S20_MODAL_RESERVATION_USD": ".4"}):
            with self.assertRaises(ReconstructionPaused):
                standalone.admit_standalone("modal-track:batch:OWN07")
        self.assertEqual(len(read_json(self.runtime / "reservations.json")["requests"]), 2)
        self.assertFalse((self.root / standalone.LEDGER).exists())

    def test_standalone_requires_explicit_bound_and_valid_runtime(self):
        with patch.object(standalone, "ROOT", self.root), patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ReconstructionPaused):
                standalone.admit_standalone("fake")
        self.assertEqual(read_json(self.runtime / "reservations.json")["requests"], [])

    def test_all_five_standalone_main_admission_tails_pause_before_launch(self):
        files = ["Build/gpu/runtime.py", "Build/gpu/scene_job.py", "Build/measurement/runtime/modal_track.py",
                 "Build/reconstruction/spike/modal_rm02.py", "Build/reconstruction/spike/modal_scenes.py"]
        self.receipt["paused"] = True
        self.save()
        for file in files:
            with self.subTest(file=file):
                tree = ast.parse((REPO / file).read_text(encoding="utf-8"))
                main = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "main")
                guard = next(i for i, n in enumerate(main.body) if isinstance(n, ast.ImportFrom)
                             and n.module == "Build.guardrails.standalone")
                # Execute the real entrypoint's launch tail without importing Modal or running frame preflight.
                tail = ast.fix_missing_locations(ast.Module(body=main.body[guard:], type_ignores=[]))
                with patch.object(standalone, "ROOT", self.root), patch.dict(os.environ, {"S20_MODAL_RESERVATION_USD": ".1"}):
                    with self.assertRaises(ReconstructionPaused):
                        exec(compile(tail, file, "exec"), {"scene": "fake", "clip": "fake"})


if __name__ == "__main__":
    unittest.main()
