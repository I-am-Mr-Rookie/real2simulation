import copy, json, sys, unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import about


class AboutTest(unittest.TestCase):
    def test_committed_about_matches_regeneration(self):
        self.assertEqual(json.loads(about.OUT.read_text(encoding="utf-8")), about.build())

    def test_gates_and_classes(self):
        d = about.build()
        self.assertEqual(d["gates"]["gate_m"], "NOT_MET_INPUT_READINESS")
        self.assertEqual(d["gates"]["gate_rs"], "NOT_MET")
        self.assertEqual(d["gates"]["gate_a"], "MET_AMENDED_Q16")
        for s in d["sections"].values():
            for r in s["rows"]:
                if r["class"] == "unavailable":
                    self.assertIsNone(r["value"]); self.assertTrue(r["reason"])

    def test_gate_disagreement_fails_closed(self):
        real = json.loads
        def fake(b, *a, **k):
            x = real(b, *a, **k)
            if isinstance(x, dict) and "billed" in x.get("summary", {}):
                x = copy.deepcopy(x); x["gates"]["gate_rs"] = "MET"
            return x
        with mock.patch.object(about.json, "loads", fake):
            with self.assertRaisesRegex(ValueError, "disagree"):
                about.build()


if __name__ == "__main__":
    unittest.main()
