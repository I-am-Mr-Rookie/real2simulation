import copy, json, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import manifest as mf
import predictions as pr


def _docs():
    m = json.loads(mf.DEFAULT.read_text(encoding="utf-8"))
    docs, _ = mf._load({"evidence": {**m["evidence"], **pr.EXTRA}})
    return copy.deepcopy(docs), {"after": mf.resolve(docs, m["split"]["scored_frames"]["after"])}


class PredictionsTest(unittest.TestCase):
    def test_committed_output_matches_regeneration(self):
        doc = pr.build()
        self.assertEqual(json.loads(pr.OUT.read_text(encoding="utf-8")), doc)
        self.assertIn(pr.markdown(doc), (mf.ROOT / "BENCHMARK.md").read_text(encoding="utf-8"))

    def test_classes_gates_and_no_leak(self):
        doc = pr.build()
        self.assertEqual(doc["gates"], {"gate_m": "NOT_MET_INPUT_READINESS", "gate_rs": "NOT_MET"})
        ids = {x["id"]: x for x in doc["rows"]}
        for k in ("bounce_height_error", "pendulum_period_error", "gate_rs_median_heldout_error", "st03_range_error"):
            self.assertEqual(ids[k]["class"], "unavailable"); self.assertIsNone(ids[k]["value"])
            self.assertTrue(ids[k]["reason"] and ids[k]["reason_sources"])
        rms = ids["st03_heldout_normalized_rms"]
        self.assertEqual((rms["class"], rms["n"]), ("measured", doc["split"]["scored"]))
        self.assertLess(doc["split"]["train_range"][1], doc["split"]["heldout_range"][0])

    def test_training_frame_in_scored_set_fails_closed(self):
        docs, split = _docs()
        docs["training_st03"]["record"]["frames"].append({"frame_index": split["after"] + 1})
        with self.assertRaisesRegex(ValueError, "training frame"):
            pr.rows(docs, split)

    def test_recomputation_mismatch_fails_closed(self):
        docs, split = _docs()
        docs["heldout_track_st03"]["record"]["frames"][-1]["y_px"] += 1
        with self.assertRaisesRegex(ValueError, "recomputed"):
            pr.rows(docs, split)

    def test_non_null_unavailable_fails_closed(self):
        docs, split = _docs()
        docs["gate_rs"]["result"]["median"] = 0.01
        with self.assertRaisesRegex(ValueError, "expected null"):
            pr.rows(docs, split)

    def test_tampered_s12f_pin_rejected(self):
        saved = pr.EXTRA["fallback_s12f"]["sha256"]
        pr.EXTRA["fallback_s12f"]["sha256"] = "0" * 64
        try:
            with self.assertRaisesRegex(ValueError, "evidence pin failed"):
                pr.build()
        finally:
            pr.EXTRA["fallback_s12f"]["sha256"] = saved


if __name__ == "__main__":
    unittest.main()
