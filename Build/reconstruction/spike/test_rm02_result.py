"""Synthetic local persistence tests; no Modal import or real inference."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import rm02_result as result_store


class ResultTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.data = b"synthetic-not-a-real-npz"
        self.result = ({"clip_id": "RM02", "output_bytes": len(self.data),
                        "output_sha256": hashlib.sha256(self.data).hexdigest()}, self.data)

    def test_payload_then_pending_marker_never_claims_cleanup_success(self):
        result_store.persist_result(self.directory, self.result)
        self.assertEqual((self.directory / "local/RM02-mapanything.npz").read_bytes(), self.data)
        marker = json.loads((self.directory / "result-received.json").read_text())
        self.assertEqual(marker["remote_cleanup_status"], "PENDING")
        self.assertEqual(marker["output_sha256"], self.result[0]["output_sha256"])
        self.assertFalse((self.directory / "gpu-result.json").exists())

    def test_failed_payload_replace_leaves_no_commit_marker(self):
        with patch.object(result_store.os, "replace", side_effect=OSError("disk")):
            with self.assertRaises(OSError):
                result_store.persist_result(self.directory, self.result)
        self.assertFalse((self.directory / "result-received.json").exists())
        self.assertFalse((self.directory / "local/RM02-mapanything.npz").exists())

    def test_pending_marker_failure_keeps_payload_but_never_success(self):
        with patch.object(result_store, "atomic_json", side_effect=OSError("metadata")):
            with self.assertRaises(OSError):
                result_store.persist_result(self.directory, self.result)
        self.assertEqual((self.directory / "local/RM02-mapanything.npz").read_bytes(), self.data)
        self.assertFalse((self.directory / "gpu-result.json").exists())

    def test_payload_integrity_is_checked_before_writing(self):
        for receipt in (dict(self.result[0], output_bytes=0),
                        dict(self.result[0], output_sha256="wrong")):
            with self.assertRaises(ValueError):
                result_store.persist_result(self.directory, (receipt, self.data))
        self.assertFalse((self.directory / "local").exists())
