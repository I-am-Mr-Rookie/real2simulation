"""Offline adversarial boundaries; fake secrets/providers are never live evidence."""
import copy
import io
import json
import shutil
import tempfile
import traceback
import unittest
from importlib import import_module
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

from test_spec_patch import BUNDLE, c, p, request, setup
from test_rebuild import INSTRUMENTS
from test_library_search import ENV, SECRET, call, response, s
from test_fireworks import FIREWORKS, MODEL, fireworks_response

r = import_module("Build.sidebar-tools.rebuild")


class PatchFailureSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.base, self.scene = setup()
        self.scene_path = self.folder / "scene.json"
        self.scene_path.write_text(json.dumps(self.scene), encoding="utf-8")
        shutil.copyfile(BUNDLE / "points.ply", self.folder / "points.ply")
        self.session = r.RebuildSession(self.base, scene_path=self.scene_path,
                                       instruments=INSTRUMENTS, scratch_dir=self.folder)

    def reject_everywhere(self, bad):
        original = copy.deepcopy(bad)
        before = {p.name: p.read_bytes() for p in self.folder.iterdir()}
        with patch.object(r, "run_lab") as execute:
            for boundary in (
                lambda: c.validate_call(bad, base_spec=self.base),
                lambda: p.apply_patch(bad, base_spec=self.base, scene=self.scene,
                                      scene_root=self.folder),
                lambda: self.session.handle(bad),
            ):
                with self.assertRaises(c.SidebarContractError) as caught:
                    boundary()
                message = str(caught.exception)
                self.assertTrue(message.strip())
                self.assertLess(len(message), 512)
                self.assertNotIn(SECRET, message)
                self.assertNotIn(SECRET, "".join(traceback.format_exception(caught.exception)))
            execute.assert_not_called()
        self.assertEqual(self.session.current_spec, self.base)
        self.assertEqual(bad, original)
        self.assertEqual({p.name: p.read_bytes() for p in self.folder.iterdir()}, before)

    def test_malformed_out_of_scope_and_traversal_never_write(self):
        variants = [None, [], "not JSON", {}]
        for section in ("scene", "template", "../outside", "..\\outside", "/tmp/outside",
                        "C:\\outside", SECRET):
            variants.append(request(self.base, {section: {}}))
        for value in ([], None, {"../outside": SECRET}, {"seed": 1}):
            variants.append(request(self.base, {"simulation": value}))
        bad = request(self.base)
        bad["arguments"]["patch"]["simulation"]["duration"]["unit"] = SECRET
        variants.append(bad)
        bad = request(self.base)
        bad["arguments"]["base_spec_sha256"] = "0" * 64
        variants.append(bad)
        for index, bad in enumerate(variants):
            with self.subTest(kind=type(bad).__name__, index=index):
                self.reject_everywhere(bad)

    def test_oversized_patch_rejected_before_experiment_validation(self):
        bad = request(self.base)
        bad["arguments"]["patch"]["simulation"]["extra"] = SECRET * 10000
        with patch.object(c, "validate") as validate:
            self.reject_everywhere(bad)
        validate.assert_not_called()

    def test_call_limit_counts_utf8_bytes_and_accepts_exact_boundary(self):
        good = request(self.base)
        source = good["arguments"]["patch"]["simulation"]["duration"]["source"]
        source["evidence"] = "x"
        size = len(json.dumps(good, ensure_ascii=False, allow_nan=False).encode("utf-8"))
        source["evidence"] += "x" * (c.MAX_CALL_BYTES - size)
        self.assertEqual(c.validate_call(good, base_spec=self.base), good)
        source["evidence"] += "x"
        self.reject_everywhere(good)
        source["evidence"] = "\u754c" * (c.MAX_CALL_BYTES // 2)
        self.reject_everywhere(good)

    def test_deep_circular_and_unencodable_calls_are_typed(self):
        bad = request(self.base)
        bad["arguments"]["patch"]["simulation"]["extra"] = "\ud800"
        self.reject_everywhere(bad)
        for circular in (False, True):
            bad = request(self.base)
            nested = bad
            if circular:
                bad["loop"] = bad
            else:
                for _ in range(1100):
                    nested["loop"] = {}
                    nested = nested["loop"]
            for boundary in (lambda: c.validate_call(bad, base_spec=self.base),
                             lambda: p.apply_patch(bad, base_spec=self.base, scene=self.scene,
                                                   scene_root=self.folder),
                             lambda: self.session.handle(bad)):
                with self.assertRaises(c.SidebarContractError) as caught:
                    boundary()
                self.assertLess(len(str(caught.exception)), 512)
            self.assertEqual(self.session.current_spec, self.base)

    def test_nested_candidate_schema_errors_cannot_escape_as_recursion_crash(self):
        for depth in (100, 300, 600, 900):
            bad = request(self.base)
            nested = bad["arguments"]["patch"]["simulation"]
            for _ in range(depth):
                nested["extra"] = {}
                nested = nested["extra"]
            nested["extra"] = SECRET
            for boundary in (lambda: c.validate_call(bad, base_spec=self.base),
                             lambda: p.apply_patch(bad, base_spec=self.base, scene=self.scene,
                                                   scene_root=self.folder),
                             lambda: self.session.handle(bad)):
                with self.subTest(depth=depth):
                    with self.assertRaises(c.SidebarContractError) as caught:
                        boundary()
                    self.assertNotIn(SECRET, "".join(traceback.format_exception(caught.exception)))
                    self.assertLess(len(str(caught.exception)), 512)
            self.assertEqual(self.session.current_spec, self.base)

    def test_raw_malformed_duplicate_json_does_not_echo_input(self):
        for raw in ('{"' + SECRET + '":1,"' + SECRET + '":2}',
                    '{"patch":' + SECRET, '{"value":NaN}'):
            with self.subTest(raw=raw):
                with self.assertRaises(c.SidebarContractError) as caught:
                    c.parse_json(raw)
                self.assertNotIn(SECRET, "".join(traceback.format_exception(caught.exception)))
                self.assertLess(len(str(caught.exception)), 512)

    def test_malformed_rebuild_spec_has_safe_error_not_raw_schema_trace(self):
        for value in (SECRET, {"extra": SECRET}):
            spec = copy.deepcopy(self.base)
            spec["simulation"]["duration"]["value"] = value
            bad = {"schema_version": c.VERSION, "id": "bad_rebuild", "tool": "scene.rebuild",
                   "scene_id": self.base["scene"]["scene_id"], "arguments": {
                       "spec": spec, "spec_sha256": c.spec_sha256(self.base)}}
            with patch.object(r, "run_lab") as execute:
                with self.assertRaises(c.SidebarContractError) as caught:
                    self.session.handle(bad)
                self.assertNotIn(SECRET, "".join(traceback.format_exception(caught.exception)))
                self.assertLess(len(str(caught.exception)), 512)
                execute.assert_not_called()
            self.assertEqual(self.session.current_spec, self.base)


class SearchFailureSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = s._catalogue(s.ROOT / "test-data/library-artifacts/free-fall.json", s.ROOT)

    def assert_receipt(self, result, provider, state, status):
        c.validate_result(result, call())
        self.assertEqual(result["status"], status)
        self.assertEqual(result["execution"], {
            "provider": provider, "model": s.MODEL_ID if provider == "baseten" else MODEL,
            "state": state, "meta_bonus_claimed": False})
        self.assertEqual(result["tool_outputs"], [])
        self.assertNotIn(SECRET, json.dumps(result))
        if status == "error":
            self.assertEqual(result["payload"]["code"], "not_ready")
            self.assertIn("Library search unavailable:", result["payload"]["issues"][0])
            self.assertIn("no automatic provider switch", result["payload"]["issues"][0])

    def test_both_providers_failure_matrix_no_leak_retry_or_switch(self):
        for provider in ("baseten", "fireworks"):
            for failure in (TimeoutError(SECRET), URLError(SECRET), RuntimeError(SECRET),
                            HTTPError("https://invalid/" + SECRET, 503, SECRET, {}, io.BytesIO(SECRET.encode())),
                            b"", b"not JSON " + SECRET.encode(), b"null", b"[]", b"\xff",
                            b"x" * (s.RESPONSE_BYTES + 1),
                            json.dumps({"choices": [{"message": {"content": SECRET}}]}).encode()):
                with self.subTest(provider=provider, failure=type(failure).__name__):
                    send = Mock(side_effect=failure) if isinstance(failure, Exception) else Mock(return_value=failure)
                    with patch.object(s, "_catalogue", return_value=copy.deepcopy(self.items)), \
                            self.assertLogs(s.LOGGER, level="INFO") as logs:
                        result = s.search(call(), environ={**ENV, **FIREWORKS,
                            "SIDEBAR_SEARCH_PROVIDER": provider}, send=send)
                    self.assert_receipt(result, provider, "failed", "error")
                    self.assertNotIn(SECRET, " ".join(logs.output))
                    self.assertEqual(send.call_count, 1)
                    self.assertEqual(send.call_args.kwargs, {"timeout": s.TIMEOUT_SECONDS})
                    endpoint = s.BASE_URL if provider == "baseten" else s.FIREWORKS_BASE_URL
                    self.assertEqual(send.call_args.args[0].full_url, endpoint + "/chat/completions")
                    if isinstance(failure, HTTPError):
                        self.assertTrue(failure.fp.closed)

    def test_both_providers_empty_success_and_unavailable_are_distinct(self):
        for provider, env, encode in (("baseten", ENV, response),
                                      ("fireworks", FIREWORKS, fireworks_response)):
            with self.subTest(provider=provider):
                send = Mock(return_value=encode([]))
                with patch.object(s, "_catalogue", return_value=copy.deepcopy(self.items)):
                    result = s.search(call(), environ=env, send=send)
                self.assert_receipt(result, provider, "served", "ok")
                self.assertEqual(result["payload"]["items"], [])
                self.assertEqual(send.call_count, 1)
                send.reset_mock()
                with patch.object(s, "_catalogue", return_value=[]):
                    result = s.search(call(), environ=env, send=send)
                self.assert_receipt(result, provider, "not_requested", "ok")
                self.assertEqual(result["payload"]["items"], [])
                send.assert_not_called()
                result = s.search(call(), environ={"SIDEBAR_SEARCH_PROVIDER": provider}, send=send)
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["execution"]["state"], "not_requested")
                self.assertFalse(result["execution"]["meta_bonus_claimed"])
                send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
