"""Synthetic numeric-contract regression; not simulator or real-scene evidence."""

import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_experiment_schema import fixture


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "contracts/experiment/validate_experiment.py"
MODULE_SPEC = importlib.util.spec_from_file_location("experiment_validator", SCRIPT)
validator = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(validator)


class NumericValidationTests(unittest.TestCase):
    def rejected(self, spec, path, reason):
        with self.assertRaises(validator.ExperimentValidationError) as caught:
            validator.validate(spec)
        self.assertIn(path, str(caught.exception))
        self.assertIn(reason, str(caught.exception))
        self.assertTrue(caught.exception.issues)

    def test_four_variants_and_no_mutation(self):
        for template in ("free_fall", "projectile", "ramp", "pendulum"):
            with self.subTest(template=template):
                spec = fixture(template)
                before = copy.deepcopy(spec)
                self.assertIs(validator.validate(spec), spec)
                self.assertEqual(spec, before)
                self.assertEqual(validator.parse_json(json.dumps(spec)), spec)

    def test_wrong_dimensions_and_noncanonical_units(self):
        for template, section, field, unit, expected in (
            ("free_fall", "body", "mass", "m", "kg"),
            ("free_fall", "environment", "gravity", "m/s", "m/s^2"),
            ("free_fall", "simulation", "duration", "ms", "s"),
            ("projectile", "parameters", "horizontal_speed", "rad/s", "m/s"),
            ("ramp", "parameters", "incline_angle", "1", "rad"),
            ("pendulum", "parameters", "release_angle", "deg", "rad"),
            ("pendulum", "parameters", "initial_angular_velocity", "m/s", "rad/s"),
        ):
            with self.subTest(template=template, field=field):
                spec = fixture(template)
                spec[section][field]["unit"] = unit
                self.rejected(spec, f"$.{section}.{field}.unit", expected)

    def test_nonfinite_anywhere_in_python_input(self):
        for number in (math.nan, math.inf, -math.inf, 10**400):
            for target in ("value", "uncertainty", "bounds", "origin", "seed"):
                with self.subTest(number=str(number)[:15], target=target):
                    spec = fixture()
                    if target in ("value", "uncertainty"):
                        spec["body"]["mass"][target] = number
                        path = "$.body.mass." + target
                    elif target == "bounds":
                        spec["scene"]["constraints"]["bounds_m"]["min"][0] = number
                        path = "$.scene.constraints.bounds_m.min[0]"
                    elif target == "origin":
                        spec["placement"]["origin"]["value"][1] = number
                        path = "$.placement.origin.value[1]"
                    else:
                        spec["simulation"]["seed"] = number
                        path = "$.simulation.seed"
                    self.rejected(spec, path, "finite")

    def test_strict_json_tokens_overflow_duplicate_and_syntax(self):
        for text, reason in (("NaN", "non-JSON"), ("Infinity", "non-JSON"),
                             ("-Infinity", "non-JSON"), ("1e999", "finite"),
                             ('{"nested":{"x":1,"x":2}}', "duplicate JSON key"),
                             ('{"x":}', "invalid JSON")):
            with self.subTest(text=text):
                with self.assertRaisesRegex(validator.ExperimentValidationError, reason):
                    validator.parse_json(text)

    def test_positive_common_domains(self):
        for section, field in (("body", "mass"), ("body", "radius"),
                               ("environment", "gravity"), ("simulation", "duration"),
                               ("simulation", "time_step")):
            for value in (0, -1):
                with self.subTest(field=field, value=value):
                    spec = fixture()
                    spec[section][field]["value"] = value
                    self.rejected(spec, f"$.{section}.{field}.value", "> 0")

    def test_template_domain_rejections(self):
        cases = (("free_fall", "drop_height", 0), ("projectile", "launch_height", -1),
                 ("projectile", "horizontal_speed", -1), ("ramp", "length", 0),
                 ("ramp", "incline_angle", 0), ("ramp", "incline_angle", math.pi/2),
                 ("ramp", "friction_coefficient", -0.1), ("ramp", "initial_speed", -1),
                 ("pendulum", "length", -1), ("pendulum", "release_angle", math.pi+0.01),
                 ("pendulum", "release_angle", -math.pi-0.01))
        for template, field, value in cases:
            with self.subTest(template=template, field=field, value=value):
                spec = fixture(template)
                spec["parameters"][field]["value"] = value
                self.rejected(spec, f"$.parameters.{field}.value", "must be")

    def test_signed_velocities_and_angle_boundary_accepted(self):
        for template, field, values in (
            ("free_fall", "initial_vertical_velocity", [-2, 0, 2]),
            ("pendulum", "initial_angular_velocity", [-2, 0, 2]),
            ("pendulum", "release_angle", [-math.pi, 0, math.pi]),
            ("ramp", "friction_coefficient", [0, 1, 2]),
            ("projectile", "horizontal_speed", [0, 1]),
        ):
            for value in values:
                with self.subTest(template=template, field=field, value=value):
                    spec = fixture(template)
                    spec["parameters"][field]["value"] = value
                    validator.validate(spec)

    def test_uncertainty_nonnegative_not_implicitly_zero(self):
        for uncertainty in (None, 0, 100):
            spec = fixture()
            spec["body"]["mass"]["uncertainty"] = uncertainty
            validator.validate(spec)
            self.assertEqual(spec["body"]["mass"]["uncertainty"], uncertainty)
        spec["body"]["mass"]["uncertainty"] = -0.01
        self.rejected(spec, "$.body.mass.uncertainty", "nonnegative")

    def test_unknown_drafts_reject_before_range_comparisons(self):
        spec = fixture()
        spec["body"]["mass"].update(value=None, uncertainty=None)
        spec["body"]["mass"]["source"]["label"] = "unknown"
        self.rejected(spec, "$.body.mass.value", "unknown draft")
        spec = fixture()
        spec["placement"]["origin"]["value"] = None
        spec["placement"]["origin"]["source"]["label"] = "unknown"
        self.rejected(spec, "$.placement.origin.value", "unknown draft")

    def test_bounds_clearance_and_step_relation(self):
        spec = fixture()
        spec["scene"]["constraints"]["bounds_m"]["min"][0] = 3
        self.rejected(spec, "$.scene.constraints.bounds_m.min[0]", "maximum")
        spec = fixture()
        spec["scene"]["constraints"]["clearance"]["value"] = -0.01
        self.rejected(spec, "$.scene.constraints.clearance.value", ">= 0")
        spec = fixture()
        spec["simulation"]["time_step"]["value"] = 2
        self.rejected(spec, "$.simulation.time_step.value", "duration")
        spec["simulation"]["time_step"]["value"] = 1
        validator.validate(spec)

    def test_malformed_shapes_reject_readably(self):
        for spec in (None, [], {}, True, {"template": "unknown"}):
            with self.subTest(spec=spec):
                self.rejected(spec, "$", "")
        spec = fixture()
        spec["body"]["mass"]["value"] = True
        self.rejected(spec, "$.body.mass.value", "number")
        spec = fixture()
        spec["parameters"]["extra"] = 1
        self.rejected(spec, "$.parameters", "Additional properties")

    def test_no_geometry_or_stability_success_claim(self):
        spec = fixture()
        spec["placement"]["origin"]["value"] = [1000, 1000, 1000]
        validator.validate(spec)  # Explicitly reserved for S08c: numeric pass != runnable.

    def test_cli_success_failure_and_missing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "synthetic.json"
            path.write_text(json.dumps(fixture()), encoding="utf-8")
            passed = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertIn("NOT execution approval", passed.stdout)
            path.write_text('{"x": NaN}', encoding="utf-8")
            failed = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(failed.returncode, 1)
            self.assertIn("non-JSON numeric constant", failed.stdout)
            path.unlink()
            missing = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(missing.returncode, 1)
            self.assertIn("FAIL:", missing.stdout)


if __name__ == "__main__":
    unittest.main()
