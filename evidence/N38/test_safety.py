"""Offline checks for archive integrity and secret-safe SSH failures."""
import base64
import hashlib
import subprocess
import unittest
from unittest.mock import patch

from backup import decode_backup
from remote import remote


class SafetyTests(unittest.TestCase):
    def archive(self, data, digest=None):
        digest = digest or hashlib.sha256(data).hexdigest()
        return digest.encode() + b"  /tmp/n38.dump\n\nN38_DUMP\n" + base64.b64encode(data) + b"\n"

    def test_valid_archive(self):
        data = b"PGDMP\x00synthetic"
        self.assertEqual(decode_backup(self.archive(data)), (data, hashlib.sha256(data).hexdigest()))

    def test_wrong_format(self):
        with self.assertRaises(ValueError):
            decode_backup(self.archive(b"not a postgres archive"))

    def test_wrong_checksum(self):
        with self.assertRaises(ValueError):
            decode_backup(self.archive(b"PGDMPsynthetic", "0" * 64))

    def test_invalid_base64(self):
        with self.assertRaises(ValueError):
            decode_backup(b"hash\nN38_DUMP\n%%%")

    def test_ssh_failure_withholds_output(self):
        with patch("remote.subprocess.run", return_value=subprocess.CompletedProcess([], 1, b"secret", b"secret")):
            with self.assertRaisesRegex(RuntimeError, "raw output suppressed") as error:
                remote("api", "read-only")
            self.assertNotIn("secret", str(error.exception))

    def test_ssh_uses_exact_identity_and_capture(self):
        with patch("remote.subprocess.run", return_value=subprocess.CompletedProcess([], 0, b"ok", b"")) as run:
            self.assertEqual(remote("api", "read-only"), b"ok")
            args, kwargs = run.call_args
            self.assertIn("-i", args[0])
            self.assertTrue(kwargs["capture_output"])
            self.assertEqual(kwargs["timeout"], 120)


if __name__ == "__main__":
    unittest.main()
