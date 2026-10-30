"""Exercise the browser ESM against fresh, real guest projections, not copied fixtures."""
import base64
import json
from pathlib import Path
import subprocess
import unittest

from Build.library.guest import load_guest


class LoaderContractTests(unittest.TestCase):
    def test_browser_loader_contract(self):
        manifest, objects = load_guest()
        root = Path(__file__).resolve().parents[2]
        fixture = {"manifest": manifest, "objects": {
            sha: base64.b64encode(data).decode("ascii") for sha, data in objects.items()}}
        result = subprocess.run(
            ["node", "--test-reporter=tap", str(root / "tests/library/loader.test.mjs")],
            input=json.dumps(fixture), text=True, capture_output=True, cwd=root, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("# fail 0", result.stdout)
        self.assertIn("# pass", result.stdout)


if __name__ == "__main__":
    unittest.main()
