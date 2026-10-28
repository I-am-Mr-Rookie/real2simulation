"""Offline structural contract tests; authored synthetic inputs, not physics evidence."""

import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "contracts/experiment/experiment.schema.json").read_text(encoding="utf-8"))


def quantity(value, unit):
    return {
        "value": value, "unit": unit, "uncertainty": None,
        "source": {"label": "synthetic", "evidence": "test_experiment_schema.py:authored-fixture"},
    }


def fixture(template="free_fall"):
    """Only schema test data: not a product generator or valid physics guarantee."""
    params = {
        "free_fall": {"drop_height": quantity(1, "m"), "initial_vertical_velocity": quantity(0, "m/s")},
        "projectile": {"launch_height": quantity(1, "m"), "horizontal_speed": quantity(1, "m/s")},
        "ramp": {
            "length": quantity(1, "m"), "incline_angle": quantity(0.5, "rad"),
            "friction_coefficient": quantity(0.1, "1"), "initial_speed": quantity(0, "m/s"),
        },
        "pendulum": {
            "length": quantity(1, "m"), "release_angle": quantity(0.1, "rad"),
            "initial_angular_velocity": quantity(0, "rad/s"),
        },
    }
    return {
        "schema_version": "1.0.0", "experiment_id": "synthetic-spec", "template": template,
        "scene": {
            "scene_id": "synthetic-room", "schema_version": "1.0.0",
            "coordinate_system": "right-handed-y-up-metres", "scale_status": "estimated",
            "constraints": {
                "bounds_m": {"min": [-2, 0, -2], "max": [2, 3, 2]},
                "allowed_surface_ids": ["floor"], "collision_obstacle_ids": [],
                "clearance": quantity(0.01, "m"),
            },
        },
        "environment": {"gravity": quantity(9.81, "m/s^2"), "gravity_direction": [0, -1, 0], "air_resistance": "neglected"},
        "body": {"mass": quantity(0.1, "kg"), "radius": quantity(0.02, "m")},
        "placement": {
            "origin": {"value": [0, 2, 0], "unit": "m", "source": quantity(0, "m")["source"]},
            "surface_id": None,
        },
        "parameters": params[template],
        "simulation": {"duration": quantity(1, "s"), "time_step": quantity(0.001, "s"), "seed": 42},
    }


class ExperimentSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = Draft202012Validator(SCHEMA)

    def assertRejected(self, spec):
        self.assertTrue(list(self.validator.iter_errors(spec)), "Expected structural rejection")

    def test_schema_is_valid_and_offline(self):
        Draft202012Validator.check_schema(SCHEMA)

        def check_refs(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    self.assertTrue(value["$ref"].startswith("#/$defs/"))
                for child in value.values():
                    check_refs(child)
            elif isinstance(value, list):
                for child in value:
                    check_refs(child)

        check_refs(SCHEMA)

    def test_all_four_structural_variants(self):
        for template in ("free_fall", "projectile", "ramp", "pendulum"):
            with self.subTest(template=template):
                self.validator.validate(fixture(template))

    def test_versions_are_exact(self):
        for where in ("experiment", "scene"):
            for version in ("2.0.0", "1.0", 1, None):
                with self.subTest(where=where, version=version):
                    spec = fixture()
                    target = spec if where == "experiment" else spec["scene"]
                    target["schema_version"] = version
                    self.assertRejected(spec)

    def test_top_level_fields_required_and_closed(self):
        for field in SCHEMA["required"]:
            with self.subTest(missing=field):
                spec = fixture()
                del spec[field]
                self.assertRejected(spec)
        spec = fixture()
        spec["result"] = {"g": 9.81}
        self.assertRejected(spec)

    def test_units_are_explicit_and_typed(self):
        paths = [
            ("body", "mass", "m"), ("body", "radius", "cm"),
            ("environment", "gravity", "m/s"), ("simulation", "duration", "frames"),
            ("simulation", "time_step", "ms"), ("parameters", "drop_height", "kg"),
            ("parameters", "initial_vertical_velocity", "rad/s"),
        ]
        for section, field, unit in paths:
            with self.subTest(section=section, field=field, unit=unit):
                spec = fixture()
                spec[section][field]["unit"] = unit
                self.assertRejected(spec)
        for template, field, unit in (("ramp", "incline_angle", "deg"), ("ramp", "friction_coefficient", "rad"), ("pendulum", "initial_angular_velocity", "m/s")):
            spec = fixture(template)
            spec["parameters"][field]["unit"] = unit
            self.assertRejected(spec)

    def test_quantities_require_provenance_and_uncertainty(self):
        for field in ("value", "unit", "source", "uncertainty"):
            spec = fixture()
            del spec["environment"]["gravity"][field]
            self.assertRejected(spec)
        for source in ({"label": "measured"}, {"label": "model", "evidence": "test"}, {"label": "assumed", "evidence": "  "}):
            spec = fixture()
            spec["environment"]["gravity"]["source"] = source
            self.assertRejected(spec)

    def test_labels_are_metadata_not_proof(self):
        for label in ("measured", "simulated", "assumed", "synthetic"):
            spec = fixture()
            spec["environment"]["gravity"]["source"]["label"] = label
            self.validator.validate(spec)

    def test_unknown_drafts_require_nulls_not_default_numbers(self):
        spec = fixture()
        gravity = spec["environment"]["gravity"]
        gravity["source"]["label"] = "unknown"
        self.assertRejected(spec)
        gravity["value"] = None
        self.validator.validate(spec)
        gravity["uncertainty"] = 0
        self.assertRejected(spec)
        spec = fixture()
        spec["environment"]["gravity"]["value"] = None
        self.assertRejected(spec)

    def test_position_shape_and_unknown_draft(self):
        for value in ([1, 2], [1, 2, 3, 4], [1, "2", 3], None):
            spec = fixture()
            spec["placement"]["origin"]["value"] = value
            self.assertRejected(spec)
        spec = fixture()
        origin = spec["placement"]["origin"]
        origin["source"]["label"] = "unknown"
        origin["value"] = None
        self.validator.validate(spec)

    def test_scene_constraints_required_and_closed(self):
        for field in ("bounds_m", "allowed_surface_ids", "collision_obstacle_ids", "clearance"):
            spec = fixture()
            del spec["scene"]["constraints"][field]
            self.assertRejected(spec)
        for field, value in (("coordinate_system", "left-handed"), ("scale_status", "guessed")):
            spec = fixture()
            spec["scene"][field] = value
            self.assertRejected(spec)
        spec = fixture()
        spec["scene"]["constraints"]["allowed_surface_ids"] = ["floor", "floor"]
        self.assertRejected(spec)
        spec = fixture()
        spec["scene"]["constraints"]["bounds_m"]["min"] = [0, 0]
        self.assertRejected(spec)

    def test_template_mixing_and_unimplemented_variants_rejected(self):
        spec = fixture()
        spec["template"] = "custom"
        self.assertRejected(spec)
        for template in ("free_fall", "projectile", "ramp", "pendulum"):
            spec = fixture(template)
            spec["parameters"]["unexpected"] = quantity(1, "m")
            self.assertRejected(spec)
            spec = fixture(template)
            del spec["parameters"][next(iter(spec["parameters"]))]
            self.assertRejected(spec)
        spec = fixture("free_fall")
        spec["parameters"] = copy.deepcopy(fixture("projectile")["parameters"])
        self.assertRejected(spec)

    def test_seed_is_uint32(self):
        for seed in (-1, 2**32, 0.1, "42", True):
            spec = fixture()
            spec["simulation"]["seed"] = seed
            self.assertRejected(spec)
        for seed in (0, 2**32 - 1):
            spec = fixture()
            spec["simulation"]["seed"] = seed
            self.validator.validate(spec)

    def test_baseline_environment_is_unambiguous(self):
        for field, value in (("gravity_direction", [0, 0, -1]), ("air_resistance", "enabled")):
            spec = fixture()
            spec["environment"][field] = value
            self.assertRejected(spec)


if __name__ == "__main__":
    unittest.main()
