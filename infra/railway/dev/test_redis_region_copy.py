"""Offline tests of the no-overwrite, no-expiry, full-payload copy contract."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock

spec = importlib.util.spec_from_file_location("copy_redis", Path(__file__).with_name("redis_region_copy.py"))
copy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(copy)


class CopyTests(unittest.TestCase):
    def test_fence_is_explicit_write_only_not_ignored_keyword(self):
        source = Mock()
        copy.pause_writes(source)
        source.execute_command.assert_called_once_with("CLIENT", "PAUSE", 600000, "WRITE")

    def test_database_selection_overrides_path_and_query(self):
        self.assertEqual(copy.database_url("redis://host/1?db=2&protocol=2", 3),
                         "redis://host/3?protocol=2")

    def test_type_and_every_dump_checksum_must_match(self):
        source = {b"job:private:input": (b"string", b"digest", b"payload")}
        self.assertEqual(copy.verify(source, source)["checked_dump_payloads"], 1)
        for target in ({}, {b"job:private:input": (b"list", b"digest", b"payload")},
                       {b"job:private:input": (b"string", b"changed", b"other")}):
            with self.assertRaises(ValueError):
                copy.verify(source, target)

    def test_nonempty_target_is_never_modified(self):
        target = Mock()
        target.dbsize.return_value = 1
        with self.assertRaises(ValueError):
            copy.copy_database(Mock(), target)
        target.pipeline.assert_not_called()

    def test_expiring_missing_and_active_lease_keys_rejected(self):
        for key, ttl, payload in ((b"job:private:input", 100, b"x"),
                                  (b"job:private:input", -2, None), (b"claim:private", -1, b"x")):
            client = Mock()
            client.scan_iter.return_value = [key]
            client.pipeline.return_value.execute.return_value = [b"string", ttl, payload]
            with self.assertRaises(ValueError):
                copy.snapshot(client)

    def test_binary_copy_restores_without_replace_and_saves(self):
        source, target = Mock(), Mock()
        source.scan_iter.return_value = [b"job:private:input"]
        source.pipeline.return_value.execute.return_value = [b"string", -1, b"\x00\xff"]
        source.dbsize.return_value = 1
        target.dbsize.side_effect = [0, 1]
        target.scan_iter.return_value = [b"job:private:input"]
        target.pipeline.return_value.execute.side_effect = [[], [b"string", -1, b"\x00\xff"]]
        result = copy.copy_database(source, target)
        target.pipeline.return_value.restore.assert_called_once_with(b"job:private:input", 0, b"\x00\xff", replace=False)
        target.save.assert_called_once()
        self.assertTrue(result["every_key_dump_sha256_matches"])
        self.assertNotIn("private", str(result))


if __name__ == "__main__":
    unittest.main()
