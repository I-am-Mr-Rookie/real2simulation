"""S15az (Gate D D1/D6): owner-clip live fit runs the pure fitter on stored RECORDED prefix points with the user's scale."""
import json
import unittest
from pathlib import Path

from Build.api.workspace.analysis import LIVE_FIT_LABEL, owner_live_fit, user_scale
from Build.api.workspace.jobs import OWNER_CLIPS, owner_measurement
from Build.fitter.core import fit_least_squares

ROOT = Path(__file__).resolve().parents[2]


def fit(clip, text):
    return owner_live_fit(owner_measurement(clip), user_scale({"text": text}))


class LiveFitTest(unittest.TestCase):
    def test_answer_changes_scale_and_g(self):
        a, b = fit("OWN05", "book cover edge, 20.28 cm"), fit("OWN05", "book cover edge, 10 cm")
        self.assertEqual((a["status"], a["label"], a["stage"]["fit"]), ("ok", LIVE_FIT_LABEL, "done"))
        self.assertAlmostEqual(a["scale"]["m_per_px"] / b["scale"]["m_per_px"], 2.028)
        self.assertAlmostEqual(a["g"] / b["g"], 2.028)
        self.assertTrue(a["scale"]["label"].startswith("user-declared scale 0.2028 m"))

    def test_displayed_values_equal_fitter_on_prefix_only(self):
        m = owner_measurement("OWN05")
        train = [p for p in m["series"]["points"] if not p["held_out"]]
        held = [p for p in m["series"]["points"] if p["held_out"]]
        self.assertTrue(held)
        out = fit("OWN05", "20.28 cm")
        mpp = 0.2028 / m["scale"]["reference_px"]
        ref = fit_least_squares([p["t_s"] for p in train], [p["y_px"] * mpp for p in train], 2)
        self.assertEqual((out["n_fit"], out["n_held_out"], out["dof"]), (len(train), len(held), len(train) - 3))
        self.assertAlmostEqual(out["g"], 2 * ref.coefficients[2])
        exp = [p["y_px"] - y / mpp for p, y in zip(held, ref.predict([p["t_s"] for p in held]))]
        for got, want in zip(out["held_out_residuals_px"], exp):
            self.assertAlmostEqual(got, want)
        # a held-out point never moves the fit
        moved = {**m, "series": {**m["series"], "points": [p | {"y_px": p["y_px"] + 500} if p["held_out"] else p
                                                            for p in m["series"]["points"]]}}
        self.assertEqual(owner_live_fit(moved, user_scale({"text": "20.28 cm"}))["g"], out["g"])

    def test_missing_points_or_reference_is_an_error_not_a_number(self):
        for m in (owner_measurement("OWN06"), {**owner_measurement("OWN05"), "series": {"points": []}}):
            out = owner_live_fit(m, user_scale({"text": "20.28 cm"}))
            self.assertEqual(out["status"], "error")
            self.assertNotIn("g", out)
        m = owner_measurement("OWN05")
        out = owner_live_fit({**m, "scale": {**m["scale"], "reference_px": None}}, user_scale({"text": "20.28 cm"}))
        self.assertEqual((out["status"], out["error"]), ("error", "no_recorded_reference_px"))

    def test_unusable_answer_uses_labelled_owner_scale(self):
        out = owner_live_fit(owner_measurement("OWN05"), user_scale({"text": "a book"}))
        self.assertTrue(out["scale"]["label"].startswith("owner-declared scale (recorded) 0.2028 m"))

    def test_reference_px_rederived_from_s07(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("arp", ROOT / "evidence/S15az/add_reference_px.py")
        arp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(arp)
        clips = json.loads(OWNER_CLIPS.read_text(encoding="utf-8"))["clips"]
        derived = arp.reference_px()
        self.assertTrue({c for c, e in clips.items() if "series" in e} <= set(derived))
        for c, (px, _src) in derived.items():
            self.assertAlmostEqual(clips[c]["scale_reference_px"], px)


if __name__ == "__main__":
    unittest.main()

