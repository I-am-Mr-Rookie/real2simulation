"""Explicit fallback configuration; all provider responses and credentials are fake."""
import copy
import json
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
import io

from test_library_search import ENV, MANIFEST, ROOT, SECRET, c, call, response, s

MODEL = "accounts/fireworks/models/synthetic-ranker"
FIREWORKS = {"SIDEBAR_SEARCH_PROVIDER": "fireworks", "FIREWORKS_API_KEY": SECRET,
             "FIREWORKS_MODEL": MODEL, "FIREWORKS_BASE_URL": s.FIREWORKS_BASE_URL}


def fireworks_response(ids):
    body = json.loads(response(ids))
    body["model"] = MODEL
    return json.dumps(body).encode()


class FireworksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = s._catalogue(MANIFEST, ROOT)
        cls.ids = [item["id"] for item in cls.items]

    def search(self, *, env=None, send=None, request=None):
        return s.search(call() if request is None else request,
                        environ=FIREWORKS if env is None else env,
                        send=Mock(return_value=fireworks_response(self.ids[:2])) if send is None else send)

    def assert_unavailable(self, result):
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["payload"]["code"], "not_ready")
        self.assertIn("Library search unavailable:", result["payload"]["issues"][0])
        self.assertEqual(result["tool_outputs"], [])
        self.assertNotIn(SECRET, json.dumps(result))
        c.validate_result(result, call())

    def test_explicit_fireworks_request_reuses_store_and_transport_limits(self):
        send = Mock(return_value=fireworks_response(self.ids[:2][::-1]))
        request_call = call()
        before = copy.deepcopy(request_call)
        result = self.search(send=send, request=request_call, env={**ENV, **FIREWORKS})
        self.assertEqual(result["payload"]["items"], self.items[:2][::-1])
        self.assertEqual(result["execution"], {"provider": "fireworks", "model": MODEL,
                         "state": "served", "meta_bonus_claimed": False})
        self.assertEqual(request_call, before)
        self.assertEqual(result["tool_outputs"], [])
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, s.FIREWORKS_BASE_URL + "/chat/completions")
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer " + SECRET)
        self.assertEqual(request.get_header("Content-type"), "application/json")
        body = json.loads(request.data)
        self.assertEqual(body["model"], MODEL)
        self.assertFalse(body["stream"])
        self.assertEqual(body["max_tokens"], 2048)
        self.assertEqual(json.loads(body["messages"][1]["content"])["candidates"][0]["id"], self.ids[0])
        self.assertNotIn(s.MODEL_ID, request.data.decode() + json.dumps(result))
        self.assertNotIn(SECRET, request.data.decode() + json.dumps(result))
        send.assert_called_once_with(request, timeout=s.TIMEOUT_SECONDS)

    def test_fireworks_keys_alone_never_select_fireworks(self):
        env = {key: value for key, value in FIREWORKS.items() if key != "SIDEBAR_SEARCH_PROVIDER"}
        send = Mock()
        self.assert_unavailable(self.search(env=env, send=send))
        send.assert_not_called()
        send = Mock(return_value=response(self.ids[:1]))
        result = self.search(env={**env, **ENV}, send=send)
        self.assertEqual(result["execution"]["provider"], "baseten")
        self.assertEqual(result["execution"]["model"], s.MODEL_ID)
        self.assertEqual(result["execution"]["state"], "served")
        self.assertEqual(send.call_args.args[0].full_url, s.BASE_URL + "/chat/completions")

    def test_explicit_baseten_is_backwards_compatible(self):
        result = self.search(env={**FIREWORKS, **ENV, "SIDEBAR_SEARCH_PROVIDER": "baseten"},
                             send=Mock(return_value=response(self.ids[:1])))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["execution"]["provider"], "baseten")
        self.assertFalse(result["execution"]["meta_bonus_claimed"])

    def test_baseten_missing_response_model_retains_legacy_behavior(self):
        body = json.loads(response(self.ids[:1]))
        del body["model"]
        result = self.search(env=ENV, send=Mock(return_value=json.dumps(body).encode()))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["execution"]["model"], s.MODEL_ID)

    def test_wire_arguments_cannot_select_provider_or_model(self):
        for field, value in (("provider", "fireworks"), ("model", MODEL)):
            request = call()
            request["arguments"][field] = value
            send = Mock()
            with self.assertRaises(c.SidebarContractError):
                self.search(request=request, send=send)
            send.assert_not_called()

    def test_unknown_provider_is_not_echoed_or_dispatched(self):
        for provider in ("", "auto", "Fireworks", SECRET, None, 42, [], {}):
            with self.subTest(provider_type=type(provider).__name__):
                send = Mock()
                with self.assertLogs(s.LOGGER, level="INFO") as logs:
                    result = self.search(env={**ENV, **FIREWORKS, "SIDEBAR_SEARCH_PROVIDER": provider}, send=send)
                self.assert_unavailable(result)
                self.assertEqual(result["execution"], {"provider": None, "model": None,
                                 "state": "not_requested", "meta_bonus_claimed": False})
                self.assertNotIn(SECRET, " ".join(logs.output))
                send.assert_not_called()

    def test_selected_provider_requires_own_complete_config(self):
        for key in ("FIREWORKS_API_KEY", "FIREWORKS_MODEL", "FIREWORKS_BASE_URL"):
            for value in (None, "", " ", 42):
                with self.subTest(key=key, value=value):
                    send = Mock()
                    result = self.search(env={**ENV, **FIREWORKS, key: value}, send=send)
                    self.assert_unavailable(result)
                    self.assertEqual(result["execution"]["state"], "not_requested")
                    send.assert_not_called()

    def test_fireworks_endpoint_is_pinned_and_credential_safe(self):
        for url in (s.BASE_URL, "http://api.fireworks.ai/inference/v1",
                    "https://evil.invalid/v1", s.FIREWORKS_BASE_URL + "?key=" + SECRET,
                    "https://user:password@api.fireworks.ai/inference/v1"):
            send = Mock()
            self.assert_unavailable(self.search(env={**FIREWORKS, "FIREWORKS_BASE_URL": url}, send=send))
            send.assert_not_called()
        result = self.search(env={**FIREWORKS, "FIREWORKS_BASE_URL": s.FIREWORKS_BASE_URL + "/"})
        self.assertEqual(result["status"], "ok")

    def test_model_must_be_explicit_resource_without_logging_raw_config(self):
        for model in (s.MODEL_ID, "synthetic-ranker", SECRET, MODEL + "\n" + SECRET,
                      MODEL + "?key=" + SECRET, MODEL + "/extra", "accounts/a/models/" + "x" * 129):
            send = Mock()
            with self.assertLogs(s.LOGGER, level="INFO") as logs:
                result = self.search(env={**FIREWORKS, "FIREWORKS_MODEL": model}, send=send)
            self.assert_unavailable(result)
            self.assertIsNone(result["execution"]["model"])
            self.assertNotIn(SECRET, " ".join(logs.output))
            send.assert_not_called()

    def test_both_provider_failures_do_not_retry_or_switch(self):
        for provider in ("baseten", "fireworks"):
            for error in (TimeoutError(SECRET), URLError(SECRET), RuntimeError(SECRET)):
                with self.subTest(provider=provider, error=type(error).__name__):
                    send = Mock(side_effect=error)
                    result = self.search(env={**ENV, **FIREWORKS, "SIDEBAR_SEARCH_PROVIDER": provider}, send=send)
                    self.assert_unavailable(result)
                    self.assertEqual(result["execution"]["provider"], provider)
                    self.assertEqual(result["execution"]["state"], "failed")
                    self.assertIn("no automatic provider switch", result["payload"]["issues"][0])
                    send.assert_called_once()
                    endpoint = s.BASE_URL if provider == "baseten" else s.FIREWORKS_BASE_URL
                    self.assertEqual(send.call_args.args[0].full_url, endpoint + "/chat/completions")

    def test_http_error_is_closed_without_reading_or_switching(self):
        body = io.BytesIO(SECRET.encode())
        error = HTTPError(s.FIREWORKS_BASE_URL, 503, SECRET, {}, body)
        send = Mock(side_effect=error)
        self.assert_unavailable(self.search(send=send, env={**ENV, **FIREWORKS}))
        self.assertTrue(body.closed)
        send.assert_called_once()

    def test_fireworks_response_requires_exact_model_identity(self):
        for model in (None, s.MODEL_ID, "accounts/fireworks/models/wrong-model"):
            body = json.loads(fireworks_response(self.ids[:1]))
            if model is None:
                del body["model"]
            else:
                body["model"] = model
            send = Mock(return_value=json.dumps(body).encode())
            result = self.search(send=send)
            self.assert_unavailable(result)
            self.assertEqual(result["execution"]["state"], "failed")
            send.assert_called_once()

    def test_unusable_fireworks_selection_never_becomes_store_evidence(self):
        for raw in (b"not-json", b"x" * (s.RESPONSE_BYTES + 1), SECRET,
                    fireworks_response(["invented"]), fireworks_response([self.ids[0]] * 2)):
            send = Mock(return_value=raw)
            self.assert_unavailable(self.search(send=send))
            send.assert_called_once()

    def test_empty_catalogue_does_not_claim_provider_served(self):
        request = call()
        request["arguments"]["templates"] = ["pendulum"]
        send = Mock()
        result = self.search(request=request, send=send)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["payload"]["items"], [])
        self.assertEqual(result["execution"]["state"], "not_requested")
        send.assert_not_called()

    def test_no_match_still_records_actual_serving_provider(self):
        result = self.search(send=Mock(return_value=fireworks_response([])))
        self.assertEqual(result["payload"]["items"], [])
        self.assertEqual(result["execution"]["state"], "served")

    def test_single_log_records_fireworks_not_muse_and_never_secret(self):
        with self.assertLogs(s.LOGGER, level="INFO") as logs:
            result = self.search()
        self.assertEqual(len(logs.output), 1)
        self.assertIn("provider=fireworks model=" + MODEL, logs.output[0])
        self.assertNotIn(SECRET, " ".join(logs.output) + json.dumps(result))
        self.assertNotIn("muse", " ".join(logs.output) + json.dumps(result))

    def test_source_failure_is_not_claimed_as_provider_failure(self):
        send = Mock()
        with patch.object(s, "validate_file", side_effect=ValueError(SECRET)):
            result = self.search(send=send)
        self.assert_unavailable(result)
        self.assertEqual(result["execution"]["state"], "not_requested")
        send.assert_not_called()

    def test_execution_receipt_rejects_bonus_claim_and_inconsistent_states(self):
        original = self.search()
        for field, value in (("meta_bonus_claimed", True), ("provider", "meta"),
                             ("provider", None), ("model", None),
                             ("state", "failed"), ("state", "not_requested")):
            result = copy.deepcopy(original)
            result["execution"][field] = value
            with self.assertRaises(c.SidebarContractError):
                c.validate_result(result, call())
        result = self.search(send=Mock(side_effect=TimeoutError()))
        result["execution"]["state"] = "served"
        with self.assertRaises(c.SidebarContractError):
            c.validate_result(result, call())


if __name__ == "__main__":
    unittest.main()
