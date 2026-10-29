import json
import tempfile
import unittest
from pathlib import Path

import image_spec as s


class DryRunContract(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def lock(self, text):
        path = self.tmp / "lock.txt"
        path.write_text(text)
        return path

    def test_current_pins_pass(self):
        result = s.dry_run()
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["runtime_env"]["HF_HUB_OFFLINE"], "1")

    def test_crlf_checkout_hashes_like_lf(self):
        lf = s.LOCK.read_bytes().replace(b"\r\n", b"\n")
        path = self.tmp / "crlf.txt"
        path.write_bytes(lf.replace(b"\n", b"\r\n"))
        self.assertEqual(s.lock_sha256(path), s.LOCK_SHA256)

    def test_drift_and_unpinned_rejected(self):
        text = s.LOCK.read_text().replace("torch==2.8.0", "torch>=2.8")
        errors = s.dry_run(lock=self.lock(text))["errors"]
        self.assertTrue(any("sha256 drift" in e for e in errors))
        self.assertIn("unpinned requirement: torch>=2.8", errors)
        self.assertIn("missing pin: torch==2.8.0", errors)

    def test_nc_or_moved_weights_rejected(self):
        rev = json.loads(s.REVISIONS.read_text())
        rev["map_weights"].update(license="cc-by-nc-4.0", revision="main")
        path = self.tmp / "rev.json"
        path.write_text(json.dumps(rev))
        errors = s.dry_run(revisions=path)["errors"]
        self.assertIn("weights not ungated apache-2.0", errors)
        self.assertIn("weight revision differs from S05 revisions.json", errors)


if __name__ == "__main__":
    unittest.main()
