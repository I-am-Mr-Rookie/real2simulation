import copy, json, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import errors as er
import manifest as mf


class ErrorsTest(unittest.TestCase):
    def test_committed_output_matches_regeneration(self):
        self.assertEqual(json.loads(er.OUT.read_text(encoding="utf-8")), er.build())
        self.assertIn(er.markdown(er.build()), (mf.ROOT / "BENCHMARK.md").read_text(encoding="utf-8"))

    def test_classes_and_gates(self):
        doc = er.build()
        self.assertEqual(doc["gates"], {"gate_m": "NOT_MET_INPUT_READINESS", "gate_rs": "NOT_MET"})
        for x in doc["rows"]:
            self.assertTrue(x["sources"], x["id"])
            if x["class"] == "unavailable":
                self.assertIsNone(x["value"]); self.assertTrue(x["reason"] and x["reason_sources"])
            else:
                self.assertIsInstance(x["n"], int)
        ids = {x["id"]: x for x in doc["rows"]}
        self.assertEqual(ids["gravity_magnitude_error_m_s2"]["class"], "unavailable")
        self.assertEqual(ids["rm02_metric_scale_error"]["class"], "unavailable")

    def test_non_null_unavailable_fails_closed(self):
        docs, _ = mf._load(json.loads(mf.DEFAULT.read_text(encoding="utf-8")))
        docs = copy.deepcopy(docs); docs["scale_s05d"]["RM02"]["gravity"]["magnitude_m_s2"] = 9.81
        with self.assertRaisesRegex(ValueError, "expected null"):
            er.rows(docs)

    def test_tampered_freeze_rejected(self):
        m = json.loads(mf.DEFAULT.read_text(encoding="utf-8")); m["evidence"]["scale_s05d"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "frozen manifest check failed"):
            er.build(m)


if __name__ == "__main__":
    unittest.main()
