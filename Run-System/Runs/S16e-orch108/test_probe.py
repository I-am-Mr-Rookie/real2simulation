"""Offline check of the one-shot evidence collector; never contacts a provider."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("s16e_probe", Path(__file__).with_name("probe.py"))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class ProbeTest(unittest.TestCase):
    def test_validated_mapping_sanitized_usage_and_no_second_request(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            folder = Path(folder)
            env, out = folder / "fake.env", folder / "proof.json"
            env.write_text("BASETEN_API_KEY=fake-secret\nBASETEN_BASE_URL=" + p.s.BASE_URL
                           + "\nBASETEN_MODEL=" + p.s.MODEL_ID, encoding="utf-8")
            ids = [item["id"] for item in p.s._catalogue(
                p.ROOT / "test-data/library-artifacts/free-fall.json", p.ROOT)][:2]
            raw = json.dumps({"model": p.s.MODEL_ID, "choices": [{"finish_reason": "stop",
                "message": {"content": json.dumps({"ids": ids})}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5,
                          "total_tokens": 15, "sensitive": "excluded"}}).encode()
            with patch.object(p, "OUT", out), patch.object(sys, "argv", ["probe", "--env-file", str(env)]), \
                    patch.object(p.s, "transport", return_value=raw) as send, patch("builtins.print"):
                p.main()
                data = json.loads(out.read_text(encoding="utf-8"))
                self.assertEqual(data["status"], "usable")
                self.assertEqual(data["ranked_ids"], ids)
                self.assertTrue(data["validated_card_mapping"])
                self.assertEqual(data["usage_measured"],
                                 {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15})
                self.assertNotIn("fake-secret", out.read_text(encoding="utf-8"))
                self.assertNotIn("sensitive", out.read_text(encoding="utf-8"))
                with self.assertRaises(FileExistsError):
                    p.main()
                self.assertEqual(send.call_count, 1)


if __name__ == "__main__":
    unittest.main()
