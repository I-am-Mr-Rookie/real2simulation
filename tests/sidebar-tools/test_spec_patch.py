"""Synthetic offline preflight; these tests do not execute or approve rebuilds."""
import copy
from importlib import import_module
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests/spec"))
from test_setup_validation import BUNDLE, setup

p = import_module("Build.sidebar-tools.spec_patch")
c = p.contracts


def request(base, sections=None):
    return {"schema_version": c.VERSION, "id": "patch_one",
            "scene_id": base["scene"]["scene_id"], "tool": "spec.patch",
            "arguments": {"base_spec_sha256": c.spec_sha256(base),
                          "patch": sections if sections is not None else {
                              "simulation": {**copy.deepcopy(base["simulation"]), "seed": 12}}}}


class SpecPatchTests(unittest.TestCase):
    def apply(self, call, base, scene, root=BUNDLE):
        return p.apply_patch(call, base_spec=base, scene=scene, scene_root=root)

    def reject(self, call, base, scene, reason, root=BUNDLE):
        before = copy.deepcopy((call, base, scene))
        rebuild = Mock()
        with self.assertRaisesRegex(p.SidebarContractError, reason):
            result = self.apply(call, base, scene, root)
            # A future S16c consumer can only see a handoff after validation returns.
            rebuild(result)
        rebuild.assert_not_called()
        self.assertEqual((call, base, scene), before)

    def test_valid_four_templates_return_contract_result_without_mutation(self):
        for template in sorted(c.TEMPLATES):
            with self.subTest(template=template):
                base, scene = setup(template)
                call = request(base)
                before = copy.deepcopy((call, base, scene))
                result = self.apply(call, base, scene)
                self.assertEqual(c.validate_result(result, call, base_spec=base), result)
                self.assertEqual(result["payload"]["spec"]["simulation"]["seed"], 12)
                self.assertTrue(result["payload"]["rebuild_required"])
                self.assertEqual(result["tool_outputs"], [])
                self.assertEqual((call, base, scene), before)
                result["payload"]["spec"]["body"]["mass"]["value"] = 20
                result["payload"]["spec"]["simulation"]["seed"] = 99
                self.assertEqual((call, base, scene), before)

    def test_validation_precedes_handoff_and_uses_applied_copy(self):
        base, scene = setup()
        call = request(base)
        with patch.object(p, "validate_setup", wraps=p.validate_setup) as check:
            result = self.apply(call, base, scene)
        check.assert_called_once()
        candidate, actual_scene, root = check.call_args.args
        self.assertIsNot(candidate, base)
        self.assertIsNot(candidate["simulation"], call["arguments"]["patch"]["simulation"])
        self.assertEqual(candidate, result["payload"]["spec"])
        self.assertIs(actual_scene, scene)
        self.assertEqual(root, BUNDLE)

    def test_multiple_sections_and_source_labels_are_preserved(self):
        base, scene = setup()
        sections = copy.deepcopy({key: base[key] for key in c.PATCH_FIELDS})
        sections["body"]["mass"]["value"] = 0.2
        sections["parameters"]["drop_height"]["value"] = 0.5
        sections["simulation"]["seed"] = 12
        call = request(base, sections)
        result = self.apply(call, base, scene)
        candidate = result["payload"]["spec"]
        for key in c.PATCH_FIELDS:
            self.assertEqual(candidate[key], sections[key])
            self.assertIsNot(candidate[key], sections[key])
        self.assertNotEqual(result["payload"]["spec_sha256"], c.spec_sha256(base))
        self.assertEqual(candidate["scene"], base["scene"])
        self.assertEqual(candidate["experiment_id"], base["experiment_id"])
        self.assertEqual(result["tool_outputs"], [])

    def test_invalid_numeric_patch_never_reaches_setup_or_handoff(self):
        for field, value in (("value", -1), ("value", None), ("value", True),
                             ("unit", "kg"), ("uncertainty", -1)):
            with self.subTest(field=field, value=value):
                base, scene = setup()
                call = request(base)
                call["arguments"]["patch"]["simulation"]["duration"][field] = value
                with patch.object(p, "validate_setup") as check:
                    self.reject(call, base, scene, ".")
                check.assert_not_called()

    def test_nonfinite_patch_rejected_without_mutating_inputs(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value):
                base, scene = setup()
                call = request(base)
                call["arguments"]["patch"]["simulation"]["duration"]["value"] = value
                with self.assertRaises(p.SidebarContractError):
                    self.apply(call, base, scene)
                self.assertEqual(base["simulation"]["duration"]["value"], 1)

    def test_geometry_invalid_numeric_patch_rejected_before_handoff(self):
        base, scene = setup()
        placement = copy.deepcopy(base["placement"])
        placement["origin"]["value"] = [100, 2, 0]
        call = request(base, {"placement": placement})
        c.validate_call(call, base_spec=base)  # Numeric-only validation accepts this.
        self.reject(call, base, scene, "bounds")

    def test_timestep_and_step_budget_preflight(self):
        for duration, step in ((1, 0.1), (1000, 0.001)):
            with self.subTest(duration=duration, step=step):
                base, scene = setup()
                call = request(base)
                simulation = call["arguments"]["patch"]["simulation"]
                simulation["duration"]["value"] = duration
                simulation["time_step"]["value"] = step
                c.validate_call(call, base_spec=base)
                self.reject(call, base, scene, "time_step|steps")

    def test_scene_binding_and_bundle_integrity_cannot_be_bypassed(self):
        for bad in ("id", "scale", "gravity", "bounds", "asset"):
            with self.subTest(bad=bad):
                base, scene = setup()
                call = request(base)
                if bad == "id":
                    scene["id"] = "other_scene"
                elif bad == "scale":
                    scene["scale"]["status"] = "unknown"
                elif bad == "gravity":
                    scene["gravity"]["magnitude_m_s2"] = 1.62
                elif bad == "bounds":
                    scene["bounds_m"]["max"][0] = 20
                else:
                    scene["assets"][0]["sha256"] = "0" * 64
                self.reject(call, base, scene, ".")

    def test_missing_bundle_asset_is_typed_rejection(self):
        base, scene = setup()
        self.reject(request(base), base, scene, "bundle", BUNDLE / "missing")

    def test_stale_and_cross_scene_call_rejected(self):
        for bad in ("digest", "scene"):
            base, scene = setup()
            call = request(base)
            if bad == "digest":
                call["arguments"]["base_spec_sha256"] = "0" * 64
            else:
                call["scene_id"] = "other_scene"
            self.reject(call, base, scene, "stale|scene_id")

    def test_patch_requires_current_trusted_base(self):
        base, scene = setup()
        self.reject(request(base), None, scene, "trusted current base_spec")

    def test_base_changed_after_call_rejected(self):
        base, scene = setup()
        call = request(base)
        base["simulation"]["seed"] = 22
        self.reject(call, base, scene, "stale")

    def test_section_replacement_not_merge_and_no_identity_edits(self):
        for sections in ({}, {"simulation": {"seed": 1}}, {"template": "projectile"},
                         {"scene": {}}, {"body": None}, {"not_a_section": {}}):
            with self.subTest(sections=sections):
                base, scene = setup()
                self.reject(request(base, sections), base, scene, ".")

    def test_wrong_tool_and_unknown_envelope_fields_rejected(self):
        base, scene = setup()
        call = request(base)
        call.update(tool="scene.rebuild", arguments={"spec": base, "spec_sha256": c.spec_sha256(base)})
        self.reject(call, base, scene, "spec.patch")
        call = request(base)
        call["rebuild"] = True
        self.reject(call, base, scene, ".")

    def test_setup_error_retains_typed_cause(self):
        base, scene = setup()
        scene["gravity"]["magnitude_m_s2"] = 1.62
        with self.assertRaises(p.SidebarContractError) as caught:
            self.apply(request(base), base, scene)
        self.assertIsInstance(caught.exception.__cause__, ValueError)
        self.assertTrue(caught.exception.__cause__.issues)


if __name__ == "__main__":
    unittest.main()
