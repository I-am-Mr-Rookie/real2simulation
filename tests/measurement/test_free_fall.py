"""Synthetic mathematical checks only, not actual-media calibration or Gate M."""
import copy
import math
import unittest

from Build.measurement.free_fall import fit_free_fall, evaluate_held_out, FitAbstention

def record(*, g=9.81, velocity=1.2, ratio=0.25, origin=1000000.0,
           times=(0, .09, .21, .35, .51, .70, .94, 1.2)):
    scale = .01
    return {
        "clip_id": "SYNTHETIC", "source_sha256": "a" * 64,
        "licence": "CC0-1.0", "provenance": "synthetic generated coordinates",
        "approval": {"scope": "metric_measurement", "evidence": "synthetic only"},
        "motion": "earth_free_fall", "width_px": 10000, "height_px": 10000,
        "continuous_segment_evidence": "synthetic continuous fall",
        "scale": {"method": "independent_reference", "m_per_px": scale,
                  "uncertainty_m_per_px": .001, "plane_verified": True,
                  "evidence": "synthetic scale; no real footage approval"},
        "timebase": {"capture_seconds_per_pts_second": ratio,
                     "uncertainty_factor": .01, "verified": True,
                     "evidence": "synthetic clock"},
        "last_training_frame": 5,
        "frames": [{"frame_index": i, "pts_s": origin + t / ratio,
                    "x_px": 30., "y_px": (2 + velocity*t + .5*g*t*t)/scale}
                   for i, t in enumerate(times)],
    }


class FitterTests(unittest.TestCase):
    fit = staticmethod(fit_free_fall)
    evaluate = staticmethod(evaluate_held_out)
    abstention = FitAbstention

    def test_known_g_initial_state_units_and_vfr_capture_conversion(self):
        data = record()
        fitted = self.fit(data)
        self.assertAlmostEqual(fitted.g_m_s2, 9.81, places=7)
        self.assertAlmostEqual(fitted.initial_y_m, 2., places=7)
        self.assertAlmostEqual(fitted.initial_velocity_m_s, 1.2, places=7)
        self.assertEqual(fitted.origin_pts_s, 1000000.)
        self.assertEqual(fitted.sign_convention, "source image y down positive")
        self.assertLess(fitted.training.rmse_m, 1e-9)
        self.assertEqual(fitted.training.frame_indices, tuple(range(6)))
        self.assertEqual(fitted.residual_dof, 3)
        self.assertLess(self.evaluate(fitted, data).rmse_m, 1e-8)
        self.assertEqual(fitted, self.fit(copy.deepcopy(data)))

    def test_suffix_coordinates_cannot_change_fit_but_change_evaluation(self):
        data = record()
        fitted = self.fit(data)
        changed = copy.deepcopy(data)
        for frame in changed["frames"][6:]:
            frame["y_px"] += 20
        self.assertEqual(fitted, self.fit(changed))
        evaluation = self.evaluate(fitted, changed)
        self.assertAlmostEqual(evaluation.rmse_m, .2, places=7)
        self.assertEqual(evaluation.frame_indices, (6, 7))
        for residual in evaluation.residuals_m:
            self.assertAlmostEqual(residual, .2, places=7)
        with self.assertRaises(AttributeError):
            fitted.g_m_s2 = 1

    def test_origin_shift_and_position_offset_do_not_change_gravity(self):
        base = self.fit(record(origin=0))
        shifted = record(origin=1e9)
        for frame in shifted["frames"]:
            frame["y_px"] += 5000
        fitted = self.fit(shifted)
        self.assertAlmostEqual(fitted.g_m_s2, base.g_m_s2, places=4)
        self.assertAlmostEqual(fitted.initial_y_m, base.initial_y_m + 50, places=5)

    def test_nonzero_noise_has_honest_residuals_not_an_interval(self):
        data = record(origin=0)
        for frame, noise in zip(data["frames"], (0, .5, -.4, .3, -.2, .1, 0, 0)):
            frame["y_px"] += noise
        fitted = self.fit(data)
        self.assertGreater(fitted.training.rmse_m, .001)
        self.assertLess(abs(fitted.g_m_s2 - 9.81), .15)
        # Least-squares optimum: residual vector orthogonal to all three columns.
        times = [(f["pts_s"] - data["frames"][0]["pts_s"])
                 * data["timebase"]["capture_seconds_per_pts_second"]
                 for f in data["frames"][:6]]
        for power in (0, 1, 2):
            self.assertAlmostEqual(math.fsum(r*t**power for r, t in
                zip(fitted.training.residuals_m, times)), 0., places=10)
        self.assertFalse(hasattr(fitted, "confidence_interval"))

    def test_unknown_calibration_or_scene_only_scope_abstains(self):
        for key, value, reason in (("scale", None, "scale_unverified"),
                                   ("timebase", None, "capture_timebase_unverified"),
                                   ("approval", {"scope": "scene_tracking", "evidence": "synthetic"},
                                    "metric_use_not_approved")):
            data = record()
            data[key] = value
            with self.subTest(key=key), self.assertRaises(self.abstention) as error:
                self.fit(data)
            self.assertIn(reason, error.exception.blockers)

    def test_malformed_inputs_are_not_silently_repaired(self):
        for key, value in (("pts_s", math.nan), ("y_px", math.inf),
                           ("pts_s", 1000000.), ("frame_index", True)):
            data = record()
            data["frames"][1][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.fit(data)
        data = record()
        data["last_training_frame"] = 1
        with self.assertRaises(ValueError):
            self.fit(data)

    def test_three_training_samples_have_zero_residual_degrees_of_freedom(self):
        data = record(origin=0)
        data["last_training_frame"] = 2
        fitted = self.fit(data)
        self.assertEqual(fitted.residual_dof, 0)
        self.assertAlmostEqual(fitted.g_m_s2, 9.81, places=8)

    def test_ill_conditioned_distinct_times_abstain(self):
        data = record(origin=0, times=(0, 1e-15, 2e-15, 3e-15, 4e-15, 1, 1.1, 1.2))
        with self.assertRaises(self.abstention) as error:
            self.fit(data)
        self.assertIn("ill_conditioned_time_samples", error.exception.blockers)

    def test_non_downward_acceleration_abstains(self):
        for g in (0., -1.):
            with self.subTest(g=g), self.assertRaises(self.abstention):
                self.fit(record(g=g, origin=0))

    def test_numeric_conversion_overflow_abstains(self):
        data = record(origin=0)
        data["scale"]["m_per_px"] = 1e308
        with self.assertRaises(self.abstention):
            self.fit(data)

    def test_capture_duration_underflow_or_acceleration_underflow_abstains(self):
        for ratio in (5e-324, 1e200):
            data = record(origin=0)
            data["timebase"]["capture_seconds_per_pts_second"] = ratio
            with self.subTest(ratio=ratio), self.assertRaises(self.abstention):
                self.fit(data)

    def test_multiple_accelerations_and_time_units_not_an_earth_constant(self):
        for g in (.2, 1.62, 9.81, 23.):
            for ratio in (.125, 1., 4.):
                data = record(g=g, velocity=-.25, ratio=ratio, origin=0)
                fitted = self.fit(data)
                with self.subTest(g=g, ratio=ratio):
                    self.assertAlmostEqual(fitted.g_m_s2, g, places=9)
                    self.assertAlmostEqual(fitted.initial_velocity_m_s, -.25, places=9)
                    self.assertLess(self.evaluate(fitted, data).max_abs_m, 1e-10)

    def test_evaluation_rejects_mismatched_prefix_or_calibration(self):
        data = record()
        fitted = self.fit(data)
        for change in ("prefix", "scale", "source"):
            changed = copy.deepcopy(data)
            if change == "prefix":
                changed["frames"][0]["y_px"] += 1
            elif change == "scale":
                changed["scale"]["m_per_px"] *= 2
            else:
                changed["source_sha256"] = "b" * 64
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.evaluate(fitted, changed)


if __name__ == "__main__":
    unittest.main()
