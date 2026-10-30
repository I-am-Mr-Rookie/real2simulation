import copy, json, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import costs as co
import manifest as mf


def _docs():
    m = json.loads(mf.DEFAULT.read_text(encoding="utf-8"))
    docs, errs = mf._load({"evidence": {**m["evidence"], **co.EXTRA}})
    assert not errs, errs
    return copy.deepcopy(docs)


class CostsTest(unittest.TestCase):
    def test_committed_output_matches_regeneration(self):
        self.assertEqual(json.loads(co.OUT.read_text(encoding="utf-8")), co.build())
        self.assertIn(co.markdown(co.build()), (mf.ROOT / "BENCHMARK.md").read_text(encoding="utf-8"))

    def test_classes_separate(self):
        rows = {x["id"]: x for x in co.build()["rows"]}
        self.assertEqual(rows["rm02_scene_billed_usd"]["class"], "billed")
        self.assertEqual(rows["rm02_scene_estimated_usd"]["class"], "estimated")
        self.assertEqual(rows["rm02_cold_start_s"]["class"], "measured")
        self.assertEqual(rows["s06e_reservation_usd"]["class"], "reservation")
        self.assertEqual(rows["meta_s16e_cost_usd"]["class"], "unavailable")
        self.assertIsNone(rows["meta_s16e_cost_usd"]["value"])
        self.assertTrue(all(x["class"] == "simulated" for k, x in rows.items() if k.startswith("s20d_")))
        for x in rows.values():
            self.assertIn(x["class"], co.CLASSES); self.assertTrue(x["sources"])

    def test_non_null_meta_cost_fails_closed(self):
        d = _docs(); d["meta_s16e"]["cost_usd"] = 0.01
        with self.assertRaisesRegex(ValueError, "expected null"):
            co.rows(d)

    def test_unbilled_status_or_live_sim_rejected(self):
        d = _docs(); d["scene_cost_rm02"]["cost"]["billed"]["status"] = "pending"
        with self.assertRaisesRegex(ValueError, "not 'billed'"):
            co.rows(d)
        d = _docs(); d["sim_s20d"]["provider_calls"] = 1
        with self.assertRaisesRegex(ValueError, "zero-call"):
            co.rows(d)

    def test_tampered_pin_rejected(self):
        extra = copy.deepcopy(co.EXTRA); extra["meta_s16e"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "evidence pin failed"):
            co.build(extra=extra)


if __name__ == "__main__":
    unittest.main()
