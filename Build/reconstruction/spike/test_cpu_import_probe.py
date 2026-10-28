import ast
from pathlib import Path
import unittest


class CpuImportGuards(unittest.TestCase):
    def test_no_gpu_bounded_setup_and_installed_imports(self):
        source = Path(__file__).with_name("cpu_import_probe.py").read_text()
        tree = ast.parse(source)
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
        options = {kw.arg: ast.literal_eval(kw.value) for kw in fn.decorator_list[0].keywords
                   if kw.arg != "image"}
        self.assertNotIn("gpu", options)
        self.assertEqual(options["timeout"], 520)
        self.assertEqual(options["startup_timeout"], 60)
        self.assertEqual(options["retries"], 0)
        self.assertEqual(options["max_containers"], 1)
        self.assertEqual(options["cpu"], (1, 2))
        self.assertEqual(options["memory"], (8192, 16384))
        self.assertIn("timeout=450", source)
        self.assertIn("timeout=60", source)
        self.assertIn("CPU_IMPORTS_OK", source)
        self.assertIn("app.stop()", source)
        self.assertNotIn("from_pretrained", source)
        # The locked antlr4 runtime is source-only; setup still has a hard timeout.
        self.assertNotIn("--only-binary=:all:", source)

    def test_recovery5_receipts_do_not_overwrite_history(self):
        source = Path(__file__).with_name("cpu_import_probe.py").read_text()
        self.assertIn('"evidence/S05/S05b/recovery5"', source)
        self.assertNotIn('"evidence/S05/S05b/recovery3"', source)
        self.assertIn('evidence.mkdir(parents=True, exist_ok=True)', source)


if __name__ == "__main__":
    unittest.main()
