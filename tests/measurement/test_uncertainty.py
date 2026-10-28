"""Synthetic conditional uncertainty, never footage calibration or Gate M."""
import copy
import math
import unittest

from test_free_fall import record
from Build.measurement.free_fall import FitAbstention
from Build.measurement.uncertainty import classify_clock, propagate_uncertainty


def assumptions(n=6, detection=0., timestamp=0.):
    return {
        "detection_std_px": [detection] * n,
        "timestamp_std_pts_s": [timestamp] * n,
        "scale_clock_correlation": 0.,
        "independent_frame_errors": True,
        "calibration_independent_of_frames": True,
        "small_error_linearization": True,
        "remaining_systematics_negligible": True,
        "evidence": "synthetic explicit error model, not real calibration",
    }


class UncertaintyTests(unittest.TestCase):
    def test_clock_is_not_delivered_fps_or_unverified_ratio(self):
        data = record(origin=0)
        self.assertEqual(classify_clock(data).classification, "slow_motion")
        for ratio, label in ((1., "real_time"), (2., "sped_up")):
            data["timebase"]["capture_seconds_per_pts_second"] = ratio
            self.assertEqual(classify_clock(data).classification, label)
        for clock in (None, {"capture_seconds_per_pts_second": .25,
                             "uncertainty_factor": 0., "verified": False}):
            data["timebase"] = clock
            data["delivered_fps"] = 240
            self.assertEqual(classify_clock(data).classification, "unknown")
            with self.assertRaises(FitAbstention):
                propagate_uncertainty(data, assumptions())

    def test_absolute_scale_clock_uncertainty_and_signed_sensitivities(self):
        data = record(origin=0)
        out = propagate_uncertainty(data, assumptions())
        self.assertAlmostEqual(out.fit.g_m_s2, 9.81, places=9)
        self.assertAlmostEqual(out.scale_sensitivity, 981., places=7)
        self.assertAlmostEqual(out.clock_sensitivity, -78.48, places=7)
        expected = math.hypot(.981, .7848)
        self.assertAlmostEqual(out.standard_uncertainty_m_s2, expected, places=9)
        for field, factor, expected_g in (("scale", 2., 19.62), ("timebase", 2., 2.4525)):
            changed = copy.deepcopy(data)
            key = "m_per_px" if field == "scale" else "capture_seconds_per_pts_second"
            changed[field][key] *= factor
            self.assertAlmostEqual(propagate_uncertainty(changed, assumptions()).fit.g_m_s2,
                                   expected_g, places=8)

    def test_external_noise_not_residual_rmse_or_three_point_interval(self):
        data = record(origin=0)
        data["scale"]["uncertainty_m_per_px"] = 0.
        data["timebase"]["uncertainty_factor"] = 0.
        zero = propagate_uncertainty(data, assumptions())
        noisy = propagate_uncertainty(data, assumptions(detection=1., timestamp=.001))
        self.assertEqual(zero.standard_uncertainty_m_s2, 0.)
        self.assertGreater(noisy.detection_standard_m_s2, 0.)
        self.assertGreater(noisy.timestamp_standard_m_s2, 0.)
        self.assertLess(noisy.fit.training.rmse_m, 1e-10)
        data["last_training_frame"] = 2
        with self.assertRaises(FitAbstention):
            propagate_uncertainty(data, assumptions(n=3))

    def test_unknown_noise_systematics_and_correlation_abstain(self):
        for key in assumptions():
            model = assumptions()
            del model[key]
            with self.subTest(key=key), self.assertRaises(FitAbstention):
                propagate_uncertainty(record(origin=0), model)
        for key in ("remaining_systematics_negligible", "independent_frame_errors",
                    "calibration_independent_of_frames", "small_error_linearization"):
            model = assumptions()
            model[key] = False
            with self.subTest(key=key), self.assertRaises(FitAbstention):
                propagate_uncertainty(record(origin=0), model)

    def test_correlated_calibration_uses_signed_clock_derivative(self):
        model = assumptions()
        model["scale_clock_correlation"] = 1.
        positive = propagate_uncertainty(record(origin=0), model)
        self.assertAlmostEqual(positive.standard_uncertainty_m_s2, .1962, places=9)
        model["scale_clock_correlation"] = -1.
        negative = propagate_uncertainty(record(origin=0), model)
        self.assertAlmostEqual(negative.standard_uncertainty_m_s2, 1.7658, places=9)

    def test_suffix_cannot_tune_any_uncertainty_or_noise(self):
        data = record(origin=0)
        model = assumptions(detection=.3, timestamp=.0001)
        original = propagate_uncertainty(data, model)
        for frame in data["frames"][6:]:
            frame["y_px"] += 700
            frame["pts_s"] += 100
        self.assertEqual(original, propagate_uncertainty(data, model))
        model["detection_std_px"].append(100.)
        with self.assertRaises(ValueError):
            propagate_uncertainty(data, model)

    def test_detection_and_timestamp_jacobians_match_independent_refits(self):
        from Build.measurement.free_fall import fit_free_fall
        data = record(origin=0)
        # Nonzero residuals exercise the design-matrix derivative, not just -v*dt.
        for i, offset in enumerate((.2, -.4, .1, .5, -.3, .2)):
            data["frames"][i]["y_px"] += offset
        out = propagate_uncertainty(data, assumptions(detection=.5, timestamp=.001))
        dy, dt = [], []
        for i in range(6):
            for field, step, target in (("y_px", .001, dy), ("pts_s", .00001, dt)):
                plus, minus = copy.deepcopy(data), copy.deepcopy(data)
                plus["frames"][i][field] += step
                minus["frames"][i][field] -= step
                # First timestamp must remain nonnegative for central differences.
                if i == 0 and field == "pts_s":
                    plus["frames"][i][field] += 1
                    minus["frames"][i][field] += 1
                    for j in range(1, 8):
                        plus["frames"][j][field] += 1
                        minus["frames"][j][field] += 1
                target.append((fit_free_fall(plus).g_m_s2 - fit_free_fall(minus).g_m_s2)/(2*step))
        self.assertAlmostEqual(out.detection_standard_m_s2, math.hypot(*dy)*.5, places=7)
        self.assertAlmostEqual(out.timestamp_standard_m_s2, math.hypot(*dt)*.001, places=7)

    def test_ill_conditioning_and_numeric_boundaries(self):
        bad = record(origin=0, times=(0, 1e-15, 2e-15, 3e-15, 4e-15, 1, 1.1, 1.2))
        with self.assertRaises(FitAbstention):
            propagate_uncertainty(bad, assumptions())
        for value in (True, -1., float("nan"), float("inf"), "0", 10**1000):
            model = assumptions()
            model["detection_std_px"][0] = value
            with self.subTest(value=str(value)[:20]), self.assertRaises(ValueError):
                propagate_uncertainty(record(origin=0), model)
        for value in (True, -1.01, 1.01, float("nan")):
            model = assumptions()
            model["scale_clock_correlation"] = value
            with self.subTest(correlation=value), self.assertRaises(ValueError):
                propagate_uncertainty(record(origin=0), model)
        model = assumptions(timestamp=1e308)
        with self.assertRaises(FitAbstention):
            propagate_uncertainty(record(origin=0), model)

    def test_rejects_silent_underflow_and_unsupported_schema(self):
        with self.assertRaises(FitAbstention):
            propagate_uncertainty(record(origin=0), assumptions(detection=5e-324))
        model = assumptions()
        model["frame_correlation"] = .5
        with self.assertRaises(ValueError):
            propagate_uncertainty(record(origin=0), model)

    def test_permission_scale_and_sign_guards_remain_in_force(self):
        for change in ("permission", "scale", "sign"):
            data = record(g=-1. if change == "sign" else 9.81, origin=0)
            if change == "permission":
                data["approval"]["scope"] = "scene_tracking"
            if change == "scale":
                data["scale"] = None
            with self.subTest(change=change), self.assertRaises(FitAbstention):
                propagate_uncertainty(data, assumptions())

    def test_precision_units_scaling_and_minimum_four_sample_prefix(self):
        data = record(origin=0)
        one = propagate_uncertainty(data, assumptions(detection=.5, timestamp=.001))
        two = propagate_uncertainty(data, assumptions(detection=1., timestamp=.002))
        self.assertAlmostEqual(two.detection_standard_m_s2,
                               2*one.detection_standard_m_s2, places=10)
        self.assertAlmostEqual(two.timestamp_standard_m_s2,
                               2*one.timestamp_standard_m_s2, places=10)
        data["last_training_frame"] = 3
        self.assertEqual(propagate_uncertainty(data, assumptions(n=4)).fit.residual_dof, 1)

    def test_hand_derived_equal_spacing_and_short_span_amplification(self):
        data = record(g=.4, ratio=1., origin=0, times=(0, 1, 2, 3, 4, 5, 6))
        data["last_training_frame"] = 4
        out = propagate_uncertainty(data, assumptions(n=5, detection=1.))
        # Acceleration weights for five unit-spaced samples are [2,-1,-2,-1,2]/7.
        self.assertAlmostEqual(out.detection_standard_m_s2, .005345224838248488, places=12)
        short = record(g=.4, ratio=1., origin=0,
                       times=(0, .001, .002, .003, .004, .005, .006))
        short["last_training_frame"] = 4
        amplified = propagate_uncertainty(short, assumptions(n=5, detection=1.))
        self.assertAlmostEqual(amplified.detection_standard_m_s2,
                               1e6*out.detection_standard_m_s2, places=6)


if __name__ == "__main__":
    unittest.main()
