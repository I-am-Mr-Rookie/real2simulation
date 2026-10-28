import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
PREFLIGHT = ROOT / "Build/measurement/runtime/preflight.py"


class SamRuntimePreflightTests(unittest.TestCase):
    def test_missing_source_fails_closed_without_importing_sam(self):
        with tempfile.TemporaryDirectory() as directory:
            process = subprocess.run(
                [sys.executable, str(PREFLIGHT), directory, "--json"],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(process.returncode, 2)
        result = json.loads(process.stdout)
        self.assertFalse(result["ok"])
        self.assertIsNone(result["checks"][0]["observed"])

    def test_manifest_records_exact_asset_build_and_kernel_contract(self):
        namespace = {}
        exec(PREFLIGHT.read_text(encoding="utf-8"), namespace)
        manifest = namespace["MANIFEST"]
        self.assertEqual(manifest["revision"], "f1647e8d0c1d280991f4d1b7d974c2704537fe66")
        self.assertEqual(manifest["files"]["sam3/assets/bpe_simple_vocab_16e6.txt.gz"],
                         "924691ac288e54409236115652ad4aa250f48203de50a9e4722a6ecd48d6804a")
        self.assertEqual(manifest["builder"]["use_fa3"], True)
        self.assertEqual(manifest["optional_kernels"], ["flash-attn-3", "cc_torch"])


if __name__ == "__main__":
    unittest.main()
