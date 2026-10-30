"""Checkpoint facts must resolve to unchanged historical receipts, not model prose."""
import json
import unittest

from test_library_search import ROOT
from Build.library.validate import pointer


class CheckpointTests(unittest.TestCase):
    def test_saved_checkpoint_facts_match_source_json_pointers(self):
        checkpoint = json.loads((ROOT / "evidence/S16/S16h-checkpoint.json").read_text(encoding="utf-8"))
        for section in ("baseten", "fireworks", "failure_safety"):
            evidence = checkpoint[section]
            document = json.loads((ROOT / evidence["source"]).read_text(encoding="utf-8"))
            for ref, expected in evidence["checks"].items():
                with self.subTest(section=section, pointer=ref):
                    self.assertEqual(pointer(document, ref), expected)
        self.assertIn("Ran 100 tests", (ROOT / checkpoint["failure_safety"]["test_log"]).read_text(encoding="utf-8"))
        self.assertFalse(checkpoint["meta_bonus_claimed"])
        self.assertFalse(checkpoint["open_weight_bonus_claimed"])
        self.assertFalse(checkpoint["both_open_unavailable_policy"]["actual_meta_route_implemented"])
