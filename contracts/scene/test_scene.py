import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from validate_scene import load_json, validate

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "test-data/synthetic/scene/room-v1"


class SceneContractTests(unittest.TestCase):
    def setUp(self):
        self.scene = load_json(FIXTURE / "scene.json")

    def test_valid_fixture_and_reduced_content(self):
        validate(self.scene, FIXTURE)
        self.scene["surfaces"] = []
        self.scene["colliders"] = []
        self.scene["labels"] = []
        validate(self.scene, FIXTURE)

    def test_unknown_scale_is_explicit(self):
        self.scene["scale"].update(status="unknown", metres_per_source_unit=None)
        validate(self.scene, FIXTURE)
        self.scene["scale"]["metres_per_source_unit"] = 1
        with self.assertRaises(ValueError):
            validate(self.scene, FIXTURE)

    def test_reject_invalid_fields(self):
        cases = [
            (["schema_version"], "2.0.0"),
            (["coordinates", "up"], "+Z"),
            (["scale", "metres_per_source_unit"], 0),
            (["scale", "metres_per_source_unit"], None),
            (["gravity", "direction"], [0, -1, 0]),
            (["assets", 0, "path"], "../outside.ply"),
            (["assets", 0, "path"], "C:/outside.ply"),
            (["assets", 0, "path"], "https://example.com/p.ply"),
            (["assets", 0, "path"], "dir\\points.ply"),
            (["render", "asset_id"], "missing"),
            (["render", "mobile_asset_id"], "missing"),
            (["render", "point_count"], 9),
            (["render", "point_count"], True),
            (["colliders", 0, "surface_id"], "missing"),
            (["colliders", 0, "half_extents_m"], [-1, 1, 1]),
            (["colliders", 0, "pose", "rotation_xyzw"], [0, 0, 0, 2]),
            (["surfaces", 0, "normal"], [0, 0, 0]),
            (["bounds_m", "min"], [2, 0, 0]),
            (["camera_path", 1, "time_s"], 0),
            (["camera_path", 0, "vertical_fov_deg"], 180),
            (["camera_path", 0, "pose", "position_m"], [float("inf"), 1, 3]),
            (["synthetic"], False),
        ]
        for path, value in cases:
            with self.subTest(path=path, value=value):
                scene = copy.deepcopy(self.scene)
                target = scene
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                with self.assertRaises(ValueError):
                    validate(scene, FIXTURE)

    def test_unknown_fields_fail(self):
        self.scene["unexpected"] = "value"
        with self.assertRaises(ValueError):
            validate(self.scene, FIXTURE)

    def test_duplicate_ids_fail(self):
        for collection in ("assets", "surfaces", "colliders", "labels"):
            with self.subTest(collection=collection):
                scene = copy.deepcopy(self.scene)
                scene[collection].append(copy.deepcopy(scene[collection][0]))
                with self.assertRaises(ValueError):
                    validate(scene, FIXTURE)

    def test_gravity_direction_without_magnitude(self):
        self.scene["gravity"].update(status="estimated", direction=[0, -1, 0])
        validate(self.scene, FIXTURE)
        self.scene["gravity"]["direction"] = [0, -2, 0]
        with self.assertRaises(ValueError):
            validate(self.scene, FIXTURE)

    def test_asset_integrity_and_missing_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "points.ply"
            with self.assertRaises(ValueError):
                validate(self.scene, directory)
            data = (FIXTURE / "points.ply").read_bytes()
            path.write_bytes(data + b"\n")
            with self.assertRaisesRegex(ValueError, "byte length"):
                validate(self.scene, directory)
            path.write_bytes(data.replace(b"120", b"121", 1))
            with self.assertRaisesRegex(ValueError, "SHA256"):
                validate(self.scene, directory)

    def test_ply_payload_rejected_even_with_correct_hash(self):
        cases = [
            (b"120", b"999"),
            (b"-1 0 -1", b"nan 0 -1"),
            (b"-1 0 -1", b"-9 0 -1"),
            (b"element vertex 8", b"element vertex 9"),
            (b"format ascii 1.0", b"format binary 1.0"),
        ]
        for old, new in cases:
            with self.subTest(new=new), tempfile.TemporaryDirectory() as directory:
                data = (FIXTURE / "points.ply").read_bytes().replace(old, new, 1)
                (Path(directory) / "points.ply").write_bytes(data)
                scene = copy.deepcopy(self.scene)
                scene["assets"][0].update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
                with self.assertRaises(ValueError):
                    validate(scene, directory)

    def test_real_source_and_model_identity(self):
        self.scene["synthetic"] = False
        self.scene["provenance"]["method"] = "mapanything-apache"
        with self.assertRaises(ValueError):
            validate(self.scene, FIXTURE)
        self.scene["provenance"]["sources"] = [{
            "clip_id": "test-only", "source_url": "https://example.invalid/test",
            "license": "CC0-1.0", "attribution": "test only", "approval_evidence": "test only, not actual approval"
        }]
        model = {"id": "facebook/map-anything-apache", "revision": "a" * 40,
                 "code_revision": "b" * 40, "license": "Apache-2.0"}
        self.scene["provenance"]["models"] = [model]
        validate(self.scene, FIXTURE)  # Structural validation is not an approval check.
        model["id"] = "facebook/map-anything"
        with self.assertRaisesRegex(ValueError, "unapproved"):
            validate(self.scene, FIXTURE)
        model["id"] = "facebook/map-anything-apache"
        self.scene["provenance"]["sources"][0]["license"] = "CC-BY-NC-4.0"
        with self.assertRaises(ValueError):
            validate(self.scene, FIXTURE)

    def test_strict_json_parser(self):
        for content in ('{"x":NaN}', '{"x":Infinity}', '{"x":1,"x":2}'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "invalid.json"
                path.write_text(content)
                with self.assertRaises(ValueError):
                    load_json(path)

    def test_missing_required_field(self):
        del self.scene["scale"]
        with self.assertRaises(ValueError):
            validate(self.scene, FIXTURE)


if __name__ == "__main__":
    unittest.main()
