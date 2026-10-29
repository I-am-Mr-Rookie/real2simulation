import json
import tempfile
import unittest
from pathlib import Path

import sam3d_option as m

OBJ = [{"id": "ball", "min": [0.0, 0.0, 0.0], "max": [0.2, 0.2, 0.2], "surface_id": None}]
ON = {m.ENV_FLAG: "1"}


class Sam3dOption(unittest.TestCase):
    def setUp(self):
        self.receipt = Path(tempfile.mkdtemp()) / "SAM3D-ACCESS.md"
        self.receipt.write_text("synthetic test receipt, not owner evidence")

    def test_default_off_even_with_receipt_and_vram(self):
        r = m.object_meshes(OBJ, 49152, env={}, receipt=self.receipt)
        self.assertEqual(r["backend"], "primitive")
        self.assertTrue(r["reasons"][0].startswith("disabled"))

    def test_missing_receipt_and_a10g_too_small(self):
        reasons = m.gate(m.MEASURED_A10G_MIB, env=ON, receipt=self.receipt.with_name("absent.md"))
        self.assertTrue(any(x.startswith("licence/access") for x in reasons), reasons)
        self.assertTrue(any(x.startswith("vram") for x in reasons), reasons)
        self.assertEqual(m.gate(None, env=ON, receipt=self.receipt), [f"vram: None MiB < {m.MIN_VRAM_MIB} MiB required"])

    def test_runner_failure_falls_back(self):
        def boom(_):
            raise MemoryError("CUDA out of memory")
        r = m.object_meshes(OBJ, 49152, runner=boom, env=ON, receipt=self.receipt)
        self.assertEqual(r["backend"], "primitive")
        self.assertIn("runner failed: MemoryError", r["reasons"][0])
        self.assertEqual(r["colliders"][0]["half_extents_m"], [0.1, 0.1, 0.1])

    def test_no_runner_falls_back_and_success_path_uses_runner(self):
        self.assertEqual(m.object_meshes(OBJ, 49152, env=ON, receipt=self.receipt)["backend"], "primitive")
        r = m.object_meshes(OBJ, 49152, runner=lambda o: ["mesh"], env=ON, receipt=self.receipt)
        self.assertEqual((r["backend"], r["meshes"]), ("sam3d", ["mesh"]))

    def test_primitive_boxes_match_scene_schema(self):
        from jsonschema import Draft202012Validator
        schema = json.loads((m.ROOT / "contracts/scene/scene.schema.json").read_text(encoding="utf-8"))
        v = Draft202012Validator({"$ref": "#/$defs/collider", "$defs": schema["$defs"]})
        for box in m.primitive_boxes(OBJ + [{"id": "table", "min": [-1, 0.7, -0.5], "max": [1, 0.75, 0.5], "surface_id": "table"}]):
            self.assertEqual(list(v.iter_errors(box)), [])
        with self.assertRaises(ValueError):
            m.primitive_boxes([{"id": "flat", "min": [0, 0, 0], "max": [1, 0, 1]}])


if __name__ == "__main__":
    unittest.main()
