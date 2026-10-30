"""Synthetic offline contracts only; no scene, model, worker or search execution."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests/spec"))
from test_experiment_schema import fixture

MODULE = importlib.util.spec_from_file_location("sidebar_contracts", ROOT / "Build/sidebar-tools/contracts.py")
c = importlib.util.module_from_spec(MODULE)
MODULE.loader.exec_module(c)


def call(tool="spec.patch"):
    spec = fixture()
    args = {
        "spec.patch": {"base_spec_sha256": c.spec_sha256(spec),
                       "patch": {"simulation": copy.deepcopy(spec["simulation"])}},
        "scene.rebuild": {"spec": spec, "spec_sha256": c.spec_sha256(spec)},
        "library.search": {"query": "falling ball", "limit": 5, "templates": [], "licenses": []},
    }
    return {"schema_version": c.VERSION, "id": "call_one", "scene_id": spec["scene"]["scene_id"],
            "tool": tool, "arguments": args[tool]}


def item():
    return {"id": "demo_one", "title": "Synthetic contract fixture", "template": "free_fall",
        "synthetic": True,
        "source": {"clip_id": "clip_one", "source_url": "https://example.org/clip",
                   "license": "Public-Domain", "license_url": "https://example.org/rights",
                   "attribution": "Synthetic fixture; no footage acquired",
                   "approval_evidence": "evidence/owner/fixture.md"},
        "artifact": {"path": "library/demo_one.json", "sha256": "a" * 64},
        "provenance": {"run_id": "synthetic-fixture", "evidence": "evidence/fixture.json",
                       "numeric_label": "synthetic"}}


def result(request):
    spec = fixture()
    payload = {
        "spec.patch": {"spec": spec, "spec_sha256": c.spec_sha256(spec), "rebuild_required": True},
        "scene.rebuild": {"job_id": "job_one", "spec_sha256": c.spec_sha256(spec), "state": "queued"},
        "library.search": {"query": "falling ball", "items": [item()]},
    }
    return {"schema_version": c.VERSION, "call_id": request["id"], "scene_id": request["scene_id"],
            "tool": request["tool"], "status": "ok", "payload": payload[request["tool"]], "tool_outputs": []}


class ContractsTest(unittest.TestCase):
    def test_search_execution_receipt_cannot_be_attached_to_patch_or_rebuild(self):
        for tool in ("spec.patch", "scene.rebuild"):
            request = call(tool)
            response = result(request)
            response["execution"] = {"provider": "fireworks", "model": "synthetic-test-model",
                                     "state": "served", "meta_bonus_claimed": False}
            with self.assertRaisesRegex(c.SidebarContractError, "only for library.search"):
                c.validate_result(response, request, base_spec=fixture())

    def test_exported_schemas_are_valid_draft202012(self):
        for schema in [c.CALL_SCHEMA, c.RESULT_SCHEMA, c.ERROR_SCHEMA,
                       *c.ARGUMENT_SCHEMAS.values(), *c.PAYLOAD_SCHEMAS.values()]:
            c.Draft202012Validator.check_schema(schema)
            self.assertEqual(json.loads(json.dumps(schema)), schema)

    def test_valid_changed_patch_for_all_experiment_templates(self):
        for template in sorted(c.TEMPLATES):
            with self.subTest(template=template):
                base = fixture(template)
                before = copy.deepcopy(base)
                request = call()
                request["scene_id"] = base["scene"]["scene_id"]
                request["arguments"] = {"base_spec_sha256": c.spec_sha256(base),
                    "patch": {"simulation": {**copy.deepcopy(base["simulation"]), "seed": 12}}}
                candidate = copy.deepcopy(base)
                candidate["simulation"]["seed"] = 12
                response = result(request)
                response["payload"].update(spec=candidate, spec_sha256=c.spec_sha256(candidate))
                c.validate_result(response, request, base_spec=base)
                self.assertEqual(base, before)

    def test_zero_search_results_and_every_canonical_license(self):
        request = call("library.search")
        response = result(request)
        response["payload"]["items"] = []
        c.validate_result(response, request)
        for license_name in c.LICENSES:
            response = result(request)
            response["payload"]["items"][0]["source"]["license"] = license_name
            request["arguments"]["licenses"] = [license_name]
            c.validate_result(response, request)

    def test_all_requests_and_results_roundtrip_without_mutation(self):
        for tool in c.TOOLS:
            with self.subTest(tool=tool):
                request = call(tool)
                response = result(request)
                originals = copy.deepcopy((request, response, fixture()))
                self.assertEqual(c.validate_call(request, base_spec=fixture()), request)
                self.assertEqual(c.validate_result(response, request, base_spec=fixture()), response)
                self.assertEqual((request, response, fixture()), originals)
                self.assertIsNot(c.validate_call(request, base_spec=fixture()), request)

    def test_patch_requires_trusted_base(self):
        with self.assertRaisesRegex(c.SidebarContractError, "trusted current"):
            c.validate_call(call())

    def test_invalid_patch_rejected_by_existing_experiment_validator(self):
        for field, value in (("value", -1), ("unit", "ms"), ("value", None)):
            request = call()
            request["arguments"]["patch"]["simulation"]["duration"][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(c.SidebarContractError):
                c.validate_call(request, base_spec=fixture())

    def test_patch_cannot_change_identity_scene_or_template(self):
        for key, value in (("scene", fixture()["scene"]), ("template", "ramp"),
                           ("experiment_id", "different"), ("__proto__", {})):
            request = call()
            request["arguments"]["patch"][key] = value
            with self.subTest(key=key), self.assertRaises(c.SidebarContractError):
                c.validate_call(request, base_spec=fixture())

    def test_patch_is_section_replacement_not_partial_deep_merge(self):
        request = call()
        request["arguments"]["patch"] = {"simulation": {"seed": 4}}
        with self.assertRaises(c.SidebarContractError):
            c.validate_call(request, base_spec=fixture())

    def test_empty_patch(self):
        request = call()
        request["arguments"]["patch"] = {}
        with self.assertRaises(c.SidebarContractError):
            c.validate_call(request, base_spec=fixture())

    def test_stale_patch_and_cross_scene_calls(self):
        for tool in ("spec.patch", "scene.rebuild"):
            for bad in ("digest", "scene"):
                request = call(tool)
                if bad == "digest":
                    key = "base_spec_sha256" if tool == "spec.patch" else "spec_sha256"
                    request["arguments"][key] = "b" * 64
                else:
                    request["scene_id"] = "another_scene"
                with self.subTest(tool=tool, bad=bad), self.assertRaises(c.SidebarContractError):
                    c.validate_call(request, base_spec=fixture())

    def test_digest_canonicalizes_mapping_order(self):
        spec = fixture()
        self.assertEqual(c.spec_sha256(spec), c.spec_sha256(dict(reversed(list(spec.items())))))
        spec["simulation"]["seed"] += 1
        self.assertNotEqual(c.spec_sha256(fixture()), c.spec_sha256(spec))

    def test_nonfinite_bool_unknown_fields_wrong_version(self):
        for key, value in (("limit", True), ("limit", 21), ("limit", 0),
                           ("query", "  "), ("limit", float("nan")), ("extra", 1)):
            request = call("library.search")
            request["arguments"][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(c.SidebarContractError):
                c.validate_call(request)
        for key, value in (("schema_version", "future"), ("tool", "shell"), ("extra", "x")):
            request = call("library.search")
            request[key] = value
            with self.subTest(key=key), self.assertRaises(c.SidebarContractError):
                c.validate_call(request)

    def test_result_correlation(self):
        request = call("library.search")
        for field in ("call_id", "scene_id", "tool"):
            response = result(request)
            response[field] = "spec.patch" if field == "tool" else "wrong"
            with self.subTest(field=field), self.assertRaises(c.SidebarContractError):
                c.validate_result(response, request)

    def test_patch_result_must_be_exact_candidate(self):
        request = call()
        for bad in ("digest", "candidate"):
            response = result(request)
            if bad == "digest":
                response["payload"]["spec_sha256"] = "b" * 64
            else:
                response["payload"]["spec"]["simulation"]["seed"] += 1
            with self.subTest(bad=bad), self.assertRaises(c.SidebarContractError):
                c.validate_result(response, request, base_spec=fixture())

    def test_patch_result_hash_checks_actual_snapshot_not_python_numeric_equality(self):
        request = call()
        response = result(request)
        # Python considers 0 == 0.0; their wire encodings/digests are different.
        response["payload"]["spec"]["simulation"]["seed"] = float(fixture()["simulation"]["seed"])
        with self.assertRaises(c.SidebarContractError):
            c.validate_result(response, request, base_spec=fixture())

    def test_invalid_result_spec_uses_sidebar_error(self):
        request = call()
        response = result(request)
        response["payload"]["spec"]["simulation"]["seed"] = False
        with self.assertRaises(c.SidebarContractError):
            c.validate_result(response, request, base_spec=fixture())

    def test_rebuild_result_cannot_claim_completion_or_change_digest(self):
        request = call("scene.rebuild")
        for key, value in (("state", "done"), ("spec_sha256", "b" * 64)):
            response = result(request)
            response["payload"][key] = value
            with self.subTest(key=key), self.assertRaises(c.SidebarContractError):
                c.validate_result(response, request)

    def test_all_source_and_provenance_fields_required(self):
        request = call("library.search")
        for section in ("source", "artifact", "provenance"):
            for field in item()[section]:
                response = result(request)
                del response["payload"]["items"][0][section][field]
                with self.subTest(section=section, field=field), self.assertRaises(c.SidebarContractError):
                    c.validate_result(response, request)

    def test_unsafe_licenses_urls_and_paths_rejected(self):
        request = call("library.search")
        for section, field, value in (("source", "license", "CC BY-NC"),
            ("source", "license", "CC BY-ND"), ("source", "source_url", "javascript:alert(1)"),
            ("source", "approval_evidence", "../secret"), ("artifact", "path", "/tmp/file"),
            ("artifact", "path", "a/../../b"), ("artifact", "path", "C:\\private")):
            response = result(request)
            response["payload"]["items"][0][section][field] = value
            with self.subTest(value=value), self.assertRaises(c.SidebarContractError):
                c.validate_result(response, request)

    def test_search_filters_duplicates_query_limit_and_synthetic_label(self):
        for bad in ("license", "template", "duplicate", "query", "limit", "synthetic"):
            request = call("library.search")
            response = result(request)
            if bad == "license":
                request["arguments"]["licenses"] = ["CC0-1.0"]
            elif bad == "template":
                request["arguments"]["templates"] = ["ramp"]
            elif bad == "duplicate":
                response["payload"]["items"] *= 2
            elif bad == "query":
                response["payload"]["query"] = "unrelated"
            elif bad == "limit":
                request["arguments"]["limit"] = 1
                response["payload"]["items"] *= 2
            else:
                response["payload"]["items"][0]["synthetic"] = False
            with self.subTest(bad=bad), self.assertRaises(c.SidebarContractError):
                c.validate_result(response, request)

    def test_error_shape_and_no_numbers_on_errors(self):
        request = call("library.search")
        response = result(request)
        response.update(status="error", payload={"code": "not_ready", "issues": ["Library unavailable"]})
        c.validate_result(response, request)
        response["tool_outputs"] = [{"value": 9}]
        with self.assertRaises(c.SidebarContractError):
            c.validate_result(response, request)

    def test_existing_agent_numeric_contract_reused(self):
        request = call("scene.rebuild")
        response = result(request)
        output = {"schema_version": "agent-tool-output/1.0.0", "id": "sim_result", "tool": "simulator",
                  "status": "ok", "quantities": {"gravity": {"value": 9.8, "unit": "m/s^2",
                  "uncertainty": 0.1, "source": {"label": "simulated", "evidence": "synthetic test"}}}}
        response["tool_outputs"] = [output]
        c.validate_result(response, request)
        response["tool_outputs"] *= 2
        with self.assertRaisesRegex(c.SidebarContractError, "duplicate"):
            c.validate_result(response, request)
        response["tool_outputs"] = [copy.deepcopy(output)]
        response["tool_outputs"][0]["quantities"]["gravity"]["source"]["label"] = "assumed"
        with self.assertRaises(c.SidebarContractError):
            c.validate_result(response, request)

    def test_wire_parser_reuses_duplicate_key_and_nonfinite_rejection(self):
        for text in ('{"id":"a","id":"b"}', '{"value":NaN}'):
            with self.assertRaises(ValueError):
                c.parse_json(text)


if __name__ == "__main__":
    unittest.main()
