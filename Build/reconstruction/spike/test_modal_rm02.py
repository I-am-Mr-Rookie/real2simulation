"""Offline guard regressions; not model or provider-behavior evidence."""
import ast
from pathlib import Path
import unittest


class ProbeGuards(unittest.TestCase):
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
                            "timeout": 900, "startup_timeout": 90, "retries": 0,
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
        self.assertAlmostEqual(planned_compute, .340464)
        self.assertLess(planned_compute, .95)
        self.assertLessEqual(.95, 1)

    def test_recovery7_output_preserves_recovery5_inputs_and_explicit_stop(self):
        source = Path(__file__).with_name("modal_rm02.py").read_text()
        self.assertIn('ROOT / "evidence/S05/S05b/recovery5"', source)
        self.assertIn('(FRAME_EVIDENCE / frame["path"]).read_bytes()', source)
        self.assertIn('INPUT_EVIDENCE / "input.json"', source)
        guard = Path(__file__).with_name("rm02_deadline.py").read_text()
        self.assertIn('finally:', guard)
        self.assertIn('app.stop.aio', guard)
        self.assertIn('ROOT / "evidence/S05/S05b/recovery7"', source)
        self.assertIn('"deadline.json"', source)

    def test_result_egress_boundary(self):
        tree = ast.parse(Path(__file__).with_name("modal_rm02.py").read_text())
        probe = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "probe")
        guard = next(n for n in probe.body if isinstance(n, ast.Assert)
                     and isinstance(n.test, ast.Compare)
                     and isinstance(n.test.left, ast.Call)
                     and isinstance(n.test.left.func, ast.Name)
                     and n.test.left.func.id == "len"
                     and isinstance(n.test.left.args[0], ast.Name)
                     and n.test.left.args[0].id == "data")
        code = compile(ast.Module(body=[guard], type_ignores=[]), "egress-guard", "exec")
        # Execute the production guard without allocating a 256MiB test payload.
        for size in (0, 268435456):
            exec(code, {"data": range(size)})
        with self.assertRaises(AssertionError):
            exec(code, {"data": range(268435457)})


if __name__ == "__main__":
    unittest.main()
