"""Offline search over accepted local metadata; every provider response is fake."""
import copy
from importlib import import_module
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
s = import_module("Build.sidebar-tools.library_search")
c = s.contracts
SECRET = "fake-secret-never-log-this"
ENV = {"BASETEN_API_KEY": SECRET, "BASETEN_MODEL": s.MODEL_ID,
       "BASETEN_BASE_URL": s.BASE_URL}
MANIFEST = ROOT / "test-data/library-artifacts/free-fall.json"


def call():
    return {"schema_version": c.VERSION, "id": "search_one", "scene_id": "scene_one",
            "tool": "library.search", "arguments": {"query": "free fall", "limit": 3,
                                                        "templates": [], "licenses": []}}


def response(ids):
    return json.dumps({"model": s.MODEL_ID, "choices": [{"finish_reason": "stop",
                       "message": {"content": json.dumps({"ids": ids})}}]}).encode()


class LibrarySearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = s._catalogue(MANIFEST, ROOT)
        cls.ids = [item["id"] for item in cls.items]

    def run_search(self, send=None, **kwargs):
        return s.search(call(), environ=ENV, send=send or Mock(return_value=response(self.ids[:2])), **kwargs)

    def assert_unavailable(self, result):
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["payload"]["code"], "not_ready")
        self.assertIn("unavailable", result["payload"]["issues"][0])
        self.assertEqual(result["tool_outputs"], [])
        c.validate_result(result, call())

    def test_request_shape_and_store_owned_results(self):
        send = Mock(return_value=response(self.ids[:2][::-1]))
        request_call = call()
        before = copy.deepcopy(request_call)
        result = s.search(request_call, environ=ENV, send=send)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["payload"]["items"], self.items[:2][::-1])
        self.assertEqual(result["call_id"], request_call["id"])
        self.assertEqual(result["tool_outputs"], [])
        self.assertEqual(request_call, before)
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, s.BASE_URL + "/chat/completions")
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer " + SECRET)
        self.assertEqual(request.get_header("Content-type"), "application/json")
        body = json.loads(request.data)
        self.assertEqual(body["model"], "meta-models/muse-spark-open-1026")
        self.assertFalse(body["stream"])
        self.assertEqual([m["role"] for m in body["messages"]], ["system", "user"])
        user = json.loads(body["messages"][1]["content"])
        self.assertEqual(user["query"], "free fall")
        self.assertEqual(user["limit"], 3)
        self.assertEqual([item["id"] for item in user["candidates"]], self.ids)
        self.assertNotIn(SECRET, request.data.decode())
        self.assertEqual(send.call_args.kwargs, {"timeout": s.TIMEOUT_SECONDS})
        self.assertEqual(len(self.items), 4)
        for item in result["payload"]["items"]:
            self.assertTrue(item["synthetic"])
            self.assertEqual(item["source"]["kind"], "synthetic")
            self.assertEqual(item["provenance"]["numeric_label"], "synthetic")
            self.assertFalse(item["scale_verified"])
            self.assertEqual(item["availability"], "metadata-only")
            self.assertEqual(item["gates"]["M"], "NOT_MET")
            self.assertTrue((ROOT / item["artifact"]["path"]).is_file())

    def test_model_only_logged_once_each_call_and_no_secrets(self):
        send = Mock(side_effect=RuntimeError(SECRET + " https://user:password@private.invalid"))
        with self.assertLogs(s.LOGGER, level="INFO") as logs:
            result = self.run_search(send)
        self.assert_unavailable(result)
        self.assertEqual(len(logs.output), 1)
        self.assertIn("model=" + s.MODEL_ID, logs.output[0])
        for value in (SECRET, "password", "private.invalid", "free fall"):
            self.assertNotIn(value, " ".join(logs.output) + json.dumps(result))

    def test_rejected_config_logs_only_pinned_model(self):
        with self.assertLogs(s.LOGGER, level="INFO") as logs:
            result = s.search(call(), environ=dict(ENV, BASETEN_MODEL=SECRET), send=Mock())
        self.assert_unavailable(result)
        self.assertEqual(len(logs.output), 1)
        self.assertIn("model=" + s.MODEL_ID, logs.output[0])
        self.assertNotIn(SECRET, " ".join(logs.output))

    def test_missing_config_and_model_mismatch_fail_closed(self):
        for key in ENV:
            for value in (None, "", 42):
                with self.subTest(key=key, value=value):
                    env = dict(ENV, **{key: value})
                    send = Mock()
                    self.assert_unavailable(s.search(call(), environ=env, send=send))
                    send.assert_not_called()
        send = Mock()
        result = s.search(call(), environ=dict(ENV, BASETEN_MODEL=SECRET), send=send)
        self.assert_unavailable(result)
        self.assertIn("must exactly match " + s.MODEL_ID, result["payload"]["issues"][0])
        self.assertNotIn(SECRET, json.dumps(result))
        send.assert_not_called()

    def test_endpoint_validation_prevents_secret_exfiltration(self):
        for url in ("http://inference.baseten.co/v1", "https://evil.invalid/v1",
                    s.BASE_URL + "?key=" + SECRET, "https://user:pass@inference.baseten.co/v1"):
            send = Mock()
            result = s.search(call(), environ=dict(ENV, BASETEN_BASE_URL=url), send=send)
            self.assert_unavailable(result)
            self.assertNotIn(url, json.dumps(result))
            send.assert_not_called()

    def test_trailing_slash_and_process_environment(self):
        with patch.dict(s.os.environ, dict(ENV, BASETEN_BASE_URL=s.BASE_URL + "/")):
            result = s.search(call(), send=Mock(return_value=response([])))
        self.assertEqual(result["status"], "ok")

    def test_timeout_http_network_and_unexpected_errors_are_safe(self):
        errors = [TimeoutError(SECRET), URLError(SECRET),
                  HTTPError(s.BASE_URL, 429, SECRET, {}, io.BytesIO(SECRET.encode())),
                  RuntimeError(SECRET)]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                send = Mock(side_effect=error)
                result = self.run_search(send)
                self.assert_unavailable(result)
                self.assertNotIn(SECRET, json.dumps(result))
                self.assertEqual(send.call_count, 1)
                if isinstance(error, HTTPError):
                    self.assertTrue(error.closed)

    def test_malformed_responses_and_model_invented_items_rejected(self):
        valid = json.loads(response(self.ids[:1]))
        variants = [b"not JSON", b"\xff", b"[]", b"null", b"{}", b"{}" * s.RESPONSE_BYTES,
                    SECRET, response(["invented-item"]), response([self.ids[0]] * 2),
                    response(self.ids), response([{"id": self.ids[0]}])]
        for content in ('{"ids":[],"text":"invented gravity"}', '{"ids":[],"ids":[]}',
                        '```json\n{"ids":[]}\n```', 'null', '{"ids":"not-list"}'):
            bad = copy.deepcopy(valid)
            bad["choices"][0]["message"]["content"] = content
            variants.append(json.dumps(bad).encode())
        for change in (lambda x: x.update(model="wrong"), lambda x: x.update(choices=[]),
                       lambda x: x["choices"][0].update(finish_reason="length"),
                       lambda x: x["choices"][0]["message"].update(tool_calls=[{}])):
            bad = copy.deepcopy(valid)
            change(bad)
            variants.append(json.dumps(bad).encode())
        for raw in variants:
            with self.subTest(raw_type=type(raw).__name__, size=len(raw)):
                self.assert_unavailable(self.run_search(Mock(return_value=raw)))

    def test_filters_are_applied_before_request_and_empty_catalogue_is_free(self):
        for filters in ({"templates": ["pendulum"]}, {"licenses": ["Pexels"]}):
            request = call()
            request["arguments"].update(filters)
            send = Mock()
            result = s.search(request, environ=ENV, send=send)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["payload"]["items"], [])
            send.assert_not_called()

    def test_no_match_returns_empty_tool_result(self):
        result = self.run_search(Mock(return_value=response([])))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["payload"]["items"], [])

    def test_invalid_wire_and_wrong_tool_do_not_dispatch(self):
        for mutate in (lambda x: x.update(tool="scene.rebuild"),
                       lambda x: x["arguments"].update(query=""),
                       lambda x: x["arguments"].update(limit=21),
                       lambda x: x.update(api_key=SECRET)):
            request = call()
            mutate(request)
            send = Mock()
            with self.assertRaises(c.SidebarContractError):
                s.search(request, environ=ENV, send=send)
            send.assert_not_called()

    def test_library_failure_and_path_escape_are_safe(self):
        send = Mock()
        with patch.object(s, "validate_file", side_effect=ValueError(SECRET)):
            self.assert_unavailable(self.run_search(send))
        self.assert_unavailable(self.run_search(send, manifest_path=ROOT.parent / "outside.json"))
        self.assert_unavailable(self.run_search(send, manifest_path=ROOT / "missing.json"))
        send.assert_not_called()

    def test_return_values_do_not_mutate_store(self):
        before = MANIFEST.read_bytes()
        first = self.run_search()
        first["payload"]["items"][0]["title"] = "modified"
        self.assertEqual(self.run_search()["payload"]["items"][0], self.items[0])
        self.assertEqual(MANIFEST.read_bytes(), before)

    def test_clip_projection_reuses_rights_and_fixture_provenance(self):
        manifest = json.loads(MANIFEST.read_bytes())
        demo = manifest["demos"][0]
        demo["label"] = "fixture"
        with patch.object(s, "validate_file", return_value={"demos": [demo]}), \
                patch.object(s, "checked_ref", return_value=(None, b'{"template":"free_fall"}')):
            item = s._catalogue(MANIFEST, ROOT)[0]
        self.assertEqual(item["source"]["clip_id"], "RM02")
        self.assertEqual(item["source"]["license"], demo["source"]["licence"])
        self.assertEqual(item["source"]["license_url"], demo["source"]["licence_url"])
        self.assertEqual(item["source"]["approval_evidence"], s.APPROVAL)
        self.assertTrue(item["synthetic"])
        self.assertEqual(item["provenance"]["numeric_label"], "synthetic")
        c._check(item, c.LIBRARY_ITEM)

    def test_synthetic_source_cannot_claim_measured_or_external_licence(self):
        result = self.run_search()
        result["payload"]["items"][0]["synthetic"] = False
        result["payload"]["items"][0]["provenance"]["numeric_label"] = "measured"
        with self.assertRaises(c.SidebarContractError):
            c.validate_result(result, call())
        request = call()
        request["arguments"]["licenses"] = ["Pexels"]
        result = self.run_search()
        with self.assertRaises(c.SidebarContractError):
            c.validate_result(result, request)

    def test_real_transport_has_bounded_read_and_no_redirect(self):
        stream = Mock(status=200)
        stream.read.return_value = response([])
        opener = Mock()
        opener.open.return_value.__enter__ = Mock(return_value=stream)
        opener.open.return_value.__exit__ = Mock(return_value=False)
        with patch.object(s, "build_opener", return_value=opener) as factory:
            self.assertEqual(s.transport(Mock(), timeout=15), response([]))
        self.assertIsInstance(factory.call_args.args[0], s._NoRedirect)
        stream.read.assert_called_once_with(s.RESPONSE_BYTES + 1)
        self.assertIsNone(s._NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.invalid"))
        stream.read.return_value = b"x" * (s.RESPONSE_BYTES + 1)
        with patch.object(s, "build_opener", return_value=opener), self.assertRaises(ValueError):
            s.transport(Mock(), timeout=15)
        stream.status = 503
        with patch.object(s, "build_opener", return_value=opener), self.assertRaises(ValueError):
            s.transport(Mock(), timeout=15)


if __name__ == "__main__":
    unittest.main()
