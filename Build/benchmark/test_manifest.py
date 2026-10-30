import copy, json, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import manifest as mf

M = json.loads(mf.DEFAULT.read_text(encoding="utf-8"))


class ManifestTest(unittest.TestCase):
    def test_frozen_manifest_passes(self):
        out = mf.check(M)
        self.assertTrue(out["ok"], out["errors"])
        self.assertEqual(out["gates"], {"gate_m": "NOT_MET_INPUT_READINESS", "gate_rs": "NOT_MET"})
        self.assertLess(out["split"]["train_range"][1], out["split"]["heldout_range"][0])

    def test_authored_number_rejected(self):
        m = copy.deepcopy(M); m["metrics"][0]["value"] = 0.01
        self.assertTrue(any("authored number" in e for e in mf.check(m)["errors"]))

    def test_heldout_leak_detected(self):
        m = copy.deepcopy(M); m["split"]["heldout_frames"] = m["split"]["train_frames"]
        self.assertTrue(any("leak" in e for e in mf.check(m)["errors"]))

    def test_suffix_read_detected(self):
        m = copy.deepcopy(M); m["split"]["suffix_observations_read_at_fit"] = m["split"]["training_count"]
        self.assertIn("held-out observations were read at fit time", mf.check(m)["errors"])

    def test_sha_mismatch_and_dangling_pointer(self):
        m = copy.deepcopy(M); m["evidence"]["gate_rs"]["sha256"] = "0" * 64
        self.assertTrue(any("sha256 mismatch" in e for e in mf.check(m)["errors"]))
        m = copy.deepcopy(M); m["metrics"][0]["value"]["pointer"] = "/nope"
        self.assertTrue(any("dangling" in e for e in mf.check(m)["errors"]))

    def test_unavailable_must_be_null(self):
        m = copy.deepcopy(M); m["metrics"][1]["value"] = m["metrics"][0]["value"]
        self.assertTrue(any("unavailable needs null" in e for e in mf.check(m)["errors"]))


if __name__ == "__main__":
    unittest.main()
