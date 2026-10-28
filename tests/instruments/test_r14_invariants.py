"""R14 independent instrument oracles; failing regressions are intentionally red.

No product fix or new noise/uncertainty policy is supplied here. Dyadic inputs
avoid any ambiguity between decimal rounding intent and binary64 values.
"""
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from fractions import Fraction

from Build.instruments import (camera_observation, light_gate_observation,
                               ruler_observation, stopwatch_observation)
from contracts.fit.quantity import Quantity, validate_quantity


def exact_quantize(value, resolution):
    """Integer quotient/remainder implements the documented half-away rule."""
    value, resolution = Fraction.from_float(value), Fraction.from_float(resolution)
    ratio = abs(value) / resolution
    whole, remainder = divmod(ratio.numerator, ratio.denominator)
    ticks = whole + (2 * remainder >= ratio.denominator)
    result = float(ticks * resolution)
    return -result if value < 0 else result


def observations(value, resolution):
    """Exercise every public instrument, including signed camera coordinates."""
    camera = camera_observation(
        7, value, value, -value, time_resolution_s=resolution,
        pixel_resolution_px=resolution, time_uncertainty_s=0.125,
        pixel_uncertainty_px=0.25, time_bias_s=0, pixel_bias_px=0)
    return {
        "light_gate": light_gate_observation(value, resolution_s=resolution,
                                             uncertainty_s=0.125, bias_s=0),
        "ruler": ruler_observation(value, resolution_m=resolution,
                                    uncertainty_m=0.25, bias_m=0),
        "stopwatch": stopwatch_observation(value, seed=17, bias_s=0,
                                           noise_std_s=0, resolution_s=resolution,
                                           uncertainty_s=0.125),
        "camera.time": camera["time"], "camera.x": camera["x"], "camera.y": camera["y"],
    }


class R14ContractChecks(unittest.TestCase):
    def test_exact_oracle_self_check(self):
        for value, expected in ((0.0, 0.0), (0.5, 1.0), (-0.5, -1.0),
                                (1.5, 2.0), (-1.5, -2.0), (1.25, 1.0)):
            self.assertEqual(exact_quantize(value, 1.0), expected)

    def test_established_decimal_resolution_tie_uses_binary64_quotient(self):
        # Existing camera fixture establishes quotient rounding, not an exact binary grid.
        self.assertEqual(1.25 / 0.1, 12.5)
        self.assertLess(Fraction.from_float(1.25) / Fraction.from_float(0.1), Fraction(25, 2))
        for name, item in observations(1.25, 0.1).items():
            with self.subTest(instrument=name):
                self.assertEqual(item["value"], -1.3 if name == "camera.y" else 1.3)

    def test_regular_dyadic_values_match_units_error_and_quantity_schema(self):
        for value in (0.0, 0.25, 0.5, 1.0, 1.5, 2.75, 17.0):
            for resolution in (0.25, 0.5, 1.0, 2.0):
                for name, item in observations(value, resolution).items():
                    with self.subTest(value=value, resolution=resolution, name=name):
                        truth = -value if name == "camera.y" else value
                        self.assertEqual(item["value"], exact_quantize(truth, resolution))
                        self.assertEqual(item["error"], item["value"] - truth)
                        unit = "px" if name in ("camera.x", "camera.y") else "m" if name == "ruler" else "s"
                        self.assertEqual(item["unit"], unit)
                        self.assertEqual(item["uncertainty"], 0.25 if unit in ("px", "m") else 0.125)
                        self.assertEqual(item["source"]["label"], "simulated")
                        self.assertTrue(item["source"]["evidence"])
                        self.assertEqual(validate_quantity(item), item)
                        self.assertEqual(Quantity(**item).to_dict(), item)
                        json.dumps(item, allow_nan=False)

    def test_finite_extremes_with_representable_grid(self):
        for value in (math.ulp(0.0), sys.float_info.min, sys.float_info.max):
            for item in observations(value, value).values():
                self.assertTrue(math.isfinite(item["value"]))
                self.assertEqual(abs(item["value"]), value)

    def test_signed_coordinates_but_not_negative_time_distance_or_frame(self):
        for call in (
            lambda: light_gate_observation(-1, resolution_s=1, uncertainty_s=0, bias_s=0),
            lambda: ruler_observation(-1, resolution_m=1, uncertainty_m=0, bias_m=0),
            lambda: stopwatch_observation(-1, seed=0, resolution_s=1, uncertainty_s=0,
                                           bias_s=0, noise_std_s=0),
        ):
            with self.assertRaises(ValueError):
                call()
        kwargs = dict(time_resolution_s=1, pixel_resolution_px=1, time_uncertainty_s=0,
                      pixel_uncertainty_px=0, time_bias_s=0, pixel_bias_px=0)
        for frame, time in ((-1, 0), (True, 0), (0.5, 0), (0, -1)):
            with self.assertRaises(ValueError):
                camera_observation(frame, time, 0, 0, **kwargs)
        item = camera_observation(0, 0, -1, -2, **kwargs)
        self.assertEqual((item["x"]["value"], item["y"]["value"]), (-1.0, -2.0))

    def test_every_numeric_parameter_rejects_boolean_nonfinite_and_overflowing_int(self):
        calls = (
            (stopwatch_observation, dict(true_seconds=1.0, seed=1, bias_s=0.0,
                                        noise_std_s=0.0, resolution_s=0.25, uncertainty_s=0.0)),
            (light_gate_observation, dict(true_seconds=1.0, resolution_s=0.25, uncertainty_s=0.0, bias_s=0.0)),
            (ruler_observation, dict(true_distance_m=1.0, resolution_m=0.25, uncertainty_m=0.0, bias_m=0.0)),
            (camera_observation, dict(frame_index=0, time_s=1.0, x_px=-1.0, y_px=2.0,
                                     time_resolution_s=0.25, pixel_resolution_px=0.25,
                                     time_uncertainty_s=0.0, pixel_uncertainty_px=0.0,
                                     time_bias_s=0.0, pixel_bias_px=0.0)),
        )
        for call, kwargs in calls:
            for field in kwargs.keys() - {"seed", "frame_index"}:
                for invalid in (True, math.nan, math.inf, -math.inf, 10 ** 1000, "1", None):
                    with self.subTest(instrument=call.__name__, field=field, invalid_type=type(invalid).__name__):
                        with self.assertRaises(ValueError):
                            call(**{**kwargs, field: invalid})
            for field in kwargs:
                if "resolution" in field:
                    with self.assertRaises(ValueError):
                        call(**{**kwargs, field: 0.0})
                if "resolution" in field or "uncertainty" in field or field == "noise_std_s":
                    with self.assertRaises(ValueError):
                        call(**{**kwargs, field: -0.25})

    def test_reaction_seed_replay_and_explicit_uncertainty_are_not_conflated(self):
        kwargs = dict(seed=73, bias_s=0.125, noise_std_s=0.25,
                      resolution_s=2 ** -16, uncertainty_s=0.0)
        item = stopwatch_observation(10.0, **kwargs)
        self.assertEqual(item, stopwatch_observation(10.0, **kwargs))
        self.assertNotEqual(item["value"], stopwatch_observation(10.0, **{**kwargs, "seed": 74})["value"])
        changed = stopwatch_observation(10.0, **{**kwargs, "uncertainty_s": 123.0})
        self.assertEqual(changed["value"], item["value"])
        self.assertEqual(changed["error"], item["value"] - 10.0)
        self.assertEqual(item["uncertainty"], 0.0)
        self.assertEqual(changed["uncertainty"], 123.0)
        self.assertIn("seed=73", item["source"]["evidence"])
        for field, invalid in (("seed", True), ("seed", 1.0)):
            with self.assertRaises(ValueError):
                stopwatch_observation(10.0, **{**kwargs, field: invalid})

    def test_actual_fitter_binds_units_without_using_diagnostic_error_as_uncertainty(self):
        from Build.fitter.api import handle

        request = {
            "times": [light_gate_observation(t, resolution_s=0.25, uncertainty_s=0.125, bias_s=0)
                      for t in (0, 1, 2, 3)],
            "positions": [ruler_observation(y, resolution_m=0.25, uncertainty_m=0.25, bias_m=0)
                          for y in (0, 1, 4, 9)],
        }
        baseline = handle(request)
        self.assertEqual(baseline["status"], "ok")
        for field, wrong_unit in (("times", "m"), ("positions", "s")):
            malformed = {**request, field: [{**item, "unit": wrong_unit} for item in request[field]]}
            self.assertEqual(handle(malformed)["status"], "error")
        changed_error = {key: [{**item, "error": 123.0} for item in items] for key, items in request.items()}
        self.assertEqual(handle(changed_error), baseline)


class R14ActualPipelineCheck(unittest.TestCase):
    def test_actual_pipeline_preserves_explicit_instrument_metadata(self):
        from Build.lab.pipeline import run_lab
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "spec"))
        from test_setup_validation import BUNDLE, setup

        settings = dict(time_resolution_s=2 ** -14, time_uncertainty_s=2 ** -10,
                        time_bias_s=0.125, distance_resolution_m=2 ** -14,
                        distance_uncertainty_m=2 ** -9, distance_bias_m=0.25)
        spec, scene = setup("free_fall")
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            (folder / "spec.json").write_text(json.dumps(spec), encoding="utf-8")
            (folder / "scene.json").write_text(json.dumps(scene), encoding="utf-8")
            shutil.copyfile(BUNDLE / "points.ply", folder / "points.ply")
            result = run_lab(folder / "spec.json", folder / "scene.json", instruments=settings)
        samples, observed = result["trajectory"]["samples"], result["observations"]
        self.assertEqual(result["fit"]["status"], "ok")
        self.assertEqual(result["fit"]["gravity"]["unit"], "m/s^2")
        self.assertEqual(len(samples), len(observed["times"]))
        self.assertEqual(len(samples), len(observed["positions"]))
        origin = samples[0]["position_m"][1]
        for sample, time, distance in zip(samples, observed["times"], observed["positions"]):
            for item, truth, bias, uncertainty, unit in (
                (time, sample["time_s"], 0.125, 2 ** -10, "s"),
                (distance, origin - sample["position_m"][1], 0.25, 2 ** -9, "m"),
            ):
                self.assertEqual(item["value"], exact_quantize(math.fsum((truth, bias)), 2 ** -14))
                self.assertEqual(item["error"], item["value"] - truth)
                self.assertEqual(item["uncertainty"], uncertainty)
                self.assertEqual(item["unit"], unit)
                self.assertEqual(validate_quantity(item), item)
        json.dumps(result, allow_nan=False)


class R14FrozenQuantizationRegressions(unittest.TestCase):
    def assert_all_instruments_match(self, value, resolution):
        for name, item in observations(value, resolution).items():
            with self.subTest(instrument=name, value_hex=value.hex(), resolution_hex=resolution.hex()):
                truth = -value if name == "camera.y" else value
                self.assertEqual(item["value"], exact_quantize(truth, resolution))

    def test_strictly_below_half_is_not_a_tie(self):
        self.assert_all_instruments_match(math.nextafter(0.5, 0.0), 1.0)

    def test_exact_lattice_point_is_never_moved_one_tick(self):
        self.assert_all_instruments_match(float(2 ** 52 + 1), 1.0)

    def test_exact_subnormal_lattice_point_is_preserved(self):
        self.assert_all_instruments_match(math.nextafter(sys.float_info.min, math.inf), math.ulp(0.0))


if __name__ == "__main__":
    unittest.main()
