"""Offline guard regressions; not model or provider-behavior evidence."""
import ast
import asyncio
from contextlib import nullcontext
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from rm02_deadline import ResourceIncident, EXIT_SECONDS
from rm02_result import persist_result
from rm02_watchdog import atomic_json


class ProbeGuards(unittest.TestCase):
    def run_main_offline(self, directory, *, cleanup_failure=False, invalid=None):
        source = Path(__file__).with_name("modal_rm02.py")
        tree = ast.parse(source.read_text())
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        constants = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
                     if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                     and n.targets[0].id in ("CODE_REV", "WEIGHT_REV")}
        frames = []
        for index in range(4):
            data = bytes([index])
            name = f"frame-{index}.bin"
            (directory / name).write_bytes(data)
            frames.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
        manifest = {"clip_id": "RM02", "sample": {"frames": frames}}
        requirements = source.with_name("requirements-linux-py311.txt").read_text()
        if invalid == "size":
            frames[0]["bytes"] = 99
        elif invalid == "hash":
            frames[0]["sha256"] = "0" * 64
        elif invalid == "clip":
            manifest["clip_id"] = "unapproved"
        elif invalid == "count":
            frames.pop()
        elif invalid == "requirements":
            requirements = "numpy==1.26.4\n"
        (directory / "input.json").write_text(json.dumps(manifest))
        (directory / "requirements-linux-py311.txt").write_text(requirements)
        data = b"synthetic-runner-output"
        result = ({"output_bytes": len(data), "output_sha256": hashlib.sha256(data).hexdigest()}, data)
        async def fake_guard(app, probe, args, record, **kwargs):
            if invalid:
                self.fail("invalid preflight reached remote admission")
            self.assertEqual(kwargs["deadline"], 1500 - EXIT_SECONDS)
            self.assertEqual(kwargs["total_seconds"], 1140)
            self.assertEqual(len(args[0]), 4)
            kwargs["save_result"](result)
            record({"synthetic": True})
            if cleanup_failure:
                raise ResourceIncident("synthetic cleanup failure")
            return result
        namespace = dict(constants, __file__=str(directory / "modal_rm02.py"), sys=NS(
            stdout=NS(reconfigure=lambda **kw: None), stderr=NS(reconfigure=lambda **kw: None)),
            INPUT_EVIDENCE=directory, FRAME_EVIDENCE=directory, EVIDENCE=directory,
            Path=Path, hashlib=hashlib, json=json, time=time, os=os, asyncio=asyncio,
            modal=NS(enable_output=nullcontext), app=object(), probe=object(),
            guarded_probe=fake_guard, EXIT_SECONDS=EXIT_SECONDS,
            atomic_json=atomic_json, persist_result=persist_result)
        exec(compile(ast.Module(body=[main], type_ignores=[]), str(source), "exec", optimize=2), namespace)
        with patch.dict(os.environ, RM02_CHILD_DEADLINE="1500", RM02_CHILD_BUDGET="1140",
                        RM02_WATCHDOG_RECEIPT=str(directory / "worker.json")):
            namespace["main"]()

    def test_optimized_main_rejects_invalid_preflight_before_remote_admission(self):
        for invalid in ("size", "hash", "clip", "count", "requirements"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                with self.assertRaises(ValueError):
                    self.run_main_offline(directory, invalid=invalid)
                self.assertFalse((directory / "worker.json").exists())
                self.assertFalse((directory / "local").exists())

    def test_optimized_remote_body_rejects_invalid_gpu_frames_results_and_egress(self):
        source = Path(__file__).with_name("modal_rm02.py")
        tree = ast.parse(source.read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "probe")
        function.decorator_list = []
        namespace = {}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec", optimize=2), namespace)
        class OversizeBytes(bytes):
            def __len__(self):
                return 256 * 1024 * 1024 + 1
        class OversizeBuffer(io.BytesIO):
            def getvalue(self):
                return OversizeBytes(b"tiny synthetic payload")
        for invalid in ("gpu", "gpu_count", "hash", "count", "keys", "egress"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                predictions = [] if invalid == "count" else ([{}] if invalid == "keys" else
                    [{"pts3d": None, "cam_trans": None, "cam_quats": None}])
                model = NS(eval=lambda: model, to=lambda device: model,
                           infer=lambda *args, **kwargs: predictions)
                torch = NS(cuda=NS(is_available=lambda: invalid != "gpu",
                    device_count=lambda: 2 if invalid == "gpu_count" else 1,
                    reset_peak_memory_stats=lambda: None, synchronize=lambda: None,
                    max_memory_allocated=lambda: 0, max_memory_reserved=lambda: 0),
                    Tensor=type("UnusedTensor", (), {}), inference_mode=nullcontext, __version__="synthetic")
                # No tensor entries: shape/codec are outside these trust-boundary cases.
                modules = {"torch": torch, "numpy": NS(savez_compressed=lambda *a, **k: None),
                    "mapanything.models": NS(MapAnything=NS(from_pretrained=lambda *a, **k: model)),
                    "mapanything.utils.image": NS(load_images=lambda paths: paths),
                    "pathlib": NS(Path=lambda path: directory / Path(path).name)}
                if invalid == "egress":
                    modules["io"] = NS(BytesIO=OversizeBuffer)
                data = b"synthetic frame"
                digest = "0" * 64 if invalid == "hash" else hashlib.sha256(data).hexdigest()
                with patch.dict(sys.modules, modules), \
                     patch("subprocess.run"), patch("subprocess.check_output", return_value="synthetic GPU"), \
                     self.assertRaises((ValueError, RuntimeError)):
                    namespace["probe"]([(data, digest)], "synthetic lock", "code", "weights")

    def test_actual_main_persists_pending_then_confirmed_without_importing_modal(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.run_main_offline(directory)
            self.assertEqual((directory / "local/RM02-mapanything.npz").read_bytes(), b"synthetic-runner-output")
            self.assertEqual(json.loads((directory / "result-received.json").read_text())["remote_cleanup_status"], "PENDING")
            self.assertEqual(json.loads((directory / "gpu-result.json").read_text())["remote_cleanup_status"], "CONFIRMED")

    def test_actual_main_preserves_pending_result_but_no_success_after_cleanup_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with self.assertRaises(ResourceIncident):
                self.run_main_offline(directory, cleanup_failure=True)
            self.assertTrue((directory / "result-received.json").exists())
            self.assertFalse((directory / "gpu-result.json").exists())

    def test_official_torch_binary_version_family(self):
        root = Path(__file__).parent
        for name in ("requirements.in", "requirements-linux-py311.txt"):
            pins = (root / name).read_text().splitlines()
            for pin in ("torch==2.8.0", "torchvision==0.23.0", "torchaudio==2.8.0"):
                self.assertIn(pin, pins, name)

    def test_bounded_single_private_invocation(self):
        source = Path(__file__).with_name("modal_rm02.py").read_text()
        tree = ast.parse(source)
        probe = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "probe")
        options = {k.arg: ast.literal_eval(k.value) for k in probe.decorator_list[0].keywords
                   if not isinstance(k.value, ast.Call)}
        image = next(k.value for k in probe.decorator_list[0].keywords if k.arg == "image")
        self.assertEqual({k.arg: ast.literal_eval(k.value) for k in image.keywords},
                         {"python_version": "3.11"})
        self.assertIn('sys.stdout.reconfigure(encoding="utf-8")', source)
        for name, value in {"gpu": "L4", "cpu": (1, 2), "memory": (8192, 16384),
        "timeout": 480, "startup_timeout": 90, "retries": 0,
                            "min_containers": 0, "max_containers": 1, "buffer_containers": 0,
                            "single_use_containers": True, "include_source": False}.items():
            self.assertEqual(options[name], value, name)
        self.assertNotIn("probe.remote(", source)
        self.assertEqual(source.count("asyncio.run(guarded_probe("), 1)
        self.assertNotIn(".deploy(", source)
        self.assertNotIn("modal.Secret", source)
        self.assertIn('"facebook/map-anything-apache", revision=weight_rev', source)
        self.assertNotIn('"facebook/map-anything"', source)
        lock = Path(__file__).with_name("requirements-linux-py311.txt").read_text()
        self.assertIn("numpy==2.2.6", lock)
        self.assertIn("rerun-sdk==0.24.1", lock)
        self.assertIn('"-r", "/tmp/s05b-requirements.txt"', source)
        self.assertLess(source.index('"nvidia-smi"'), source.index('"pip", "install"'))

    def test_planned_compute_allowance_not_a_billing_or_stop_guarantee(self):
        from rm02_deadline import TOTAL_SECONDS
        planned_compute = TOTAL_SECONDS * (.000222 + 2 * .0000131 + 16 * .00000222)
        self.assertAlmostEqual(planned_compute, .255348)
        self.assertLess(planned_compute, .95)
        self.assertLessEqual(.95, 1)

    def test_supervised_output_preserves_recovery5_inputs_and_explicit_stop(self):
        source = Path(__file__).with_name("modal_rm02.py").read_text()
        self.assertIn('ROOT / "evidence/S05/S05b/recovery5"', source)
        self.assertIn('(FRAME_EVIDENCE / frame["path"]).read_bytes()', source)
        self.assertIn('INPUT_EVIDENCE / "input.json"', source)
        guard = Path(__file__).with_name("rm02_deadline.py").read_text()
        self.assertIn('finally:', guard)
        self.assertIn('app.stop.aio', guard)
        self.assertIn('RM02_WATCHDOG_RECEIPT', source)
        self.assertIn('atomic_json(', source)
        self.assertIn('RM02_CHILD_BUDGET', source)
        self.assertIn('deadline=float(os.environ["RM02_CHILD_DEADLINE"]) - EXIT_SECONDS', source)
        self.assertIn('save_result=lambda result: persist_result(EVIDENCE, result)', source)
        self.assertIn('atomic_json(EVIDENCE / "gpu-result.json", receipt)', source)
        self.assertNotIn('.write_bytes(data)', source[source.index('def main():'):])
        self.assertLess(source.index('if not os.environ.get("RM02_WATCHDOG_RECEIPT")'),
                        source.index('import modal'))
        constants = {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse(source).body
                     if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                     and n.targets[0].id in ("CODE_REV", "WEIGHT_REV")}
        self.assertEqual(constants, {"CODE_REV": "3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9",
                                    "WEIGHT_REV": "00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a"})

    def test_result_egress_boundary(self):
        tree = ast.parse(Path(__file__).with_name("modal_rm02.py").read_text())
        probe = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "probe")
        guard = next(n for n in probe.body if isinstance(n, ast.If)
                     and isinstance(n.test, ast.Compare)
                     and isinstance(n.test.left, ast.Call)
                     and isinstance(n.test.left.func, ast.Name)
                     and n.test.left.func.id == "len"
                     and isinstance(n.test.left.args[0], ast.Name)
                     and n.test.left.args[0].id == "data")
        code = compile(ast.Module(body=[guard], type_ignores=[]), "egress-guard", "exec", optimize=2)
        # Execute the production guard without allocating a 256MiB test payload.
        for size in (0, 268435456):
            exec(code, {"data": range(size)})
        with self.assertRaisesRegex(ValueError, "egress"):
            exec(code, {"data": range(268435457)})


if __name__ == "__main__":
    unittest.main()
