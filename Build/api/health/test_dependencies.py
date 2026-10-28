"""Synthetic configuration/adapter tests, NOT live service or event-gate evidence."""
import importlib
import os
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient


CONFIG = {
    "R2S_ENVIRONMENT": "development", "RAILWAY_ENVIRONMENT_NAME": "dev",
    "DATABASE_URL": "postgresql://canary:canary@127.0.0.1:1/dev",
    "REDIS_URL": "redis://127.0.0.1:1/0",
    "BUCKET_ENDPOINT": "https://bucket.invalid", "BUCKET_NAME": "dev-canary",
    "BUCKET_REGION": "auto", "BUCKET_ACCESS_KEY_ID": "canary-id",
    "BUCKET_SECRET_ACCESS_KEY": "canary-secret",
}


class DependencyTests(unittest.TestCase):
    def module(self):
        return importlib.import_module("Build.api.health.dependencies")

    def test_configured_but_failed_connections_are_unavailable_not_missing(self):
        for name in ("api", "worker"):
            module = importlib.import_module(f"Build.{name}.health.app")
            with patch.dict(os.environ, CONFIG, clear=True), TestClient(module.create_app()) as client:
                response = client.get("/health/ready")
                self.assertEqual(response.status_code, 503)
                body = response.json()
                self.assertEqual(body["dependencies"]["postgres" if name == "api" else "redis"], "unavailable")
                self.assertNotIn("canary", str(body))

    def test_successful_adapter_checks_enable_api_but_never_worker_heartbeat(self):
        deps = self.module()
        for name in ("api", "worker"):
            module = importlib.import_module(f"Build.{name}.health.app")
            with patch.dict(os.environ, CONFIG, clear=True), patch.object(deps, "probe", return_value=True), TestClient(module.create_app()) as client:
                response = client.get("/health/ready")
                self.assertEqual(response.status_code, 200 if name == "api" else 503)
                self.assertEqual(response.json()["dependencies"]["bucket"], "ok")
                if name == "worker":
                    self.assertEqual(response.json()["dependencies"]["heartbeat"], "unavailable")

    def test_nondev_and_incomplete_configuration_never_connects(self):
        deps = self.module()
        for overrides in ({"R2S_ENVIRONMENT": "production"}, {"RAILWAY_ENVIRONMENT_NAME": "production"}, {"BUCKET_NAME": ""}):
            env = CONFIG | overrides
            with patch.object(deps, "probe", return_value=True) as probe:
                health = deps.DependencyHealth(env, ("bucket",))
                self.assertIn(health.check()["bucket"], ("unavailable", "not-configured"))
                probe.assert_not_called()

    def test_probe_failure_is_sanitized_and_independent(self):
        deps = self.module()
        def adapter(name, env):
            if name == "redis":
                raise RuntimeError("canary-secret")
            return True
        with patch.object(deps, "probe", side_effect=adapter):
            states = deps.DependencyHealth(CONFIG, ("postgres", "redis", "bucket")).check()
        self.assertEqual(states, {"postgres": "ok", "redis": "unavailable", "bucket": "ok"})

    def test_deadline_and_repeated_requests_do_not_enqueue_duplicate_probes(self):
        deps = self.module()
        def slow(*args):
            time.sleep(.15)
            return True
        with patch.object(deps, "probe", side_effect=slow) as probe:
            health = deps.DependencyHealth(CONFIG, ("redis",), deadline=.01)
            start = time.monotonic()
            self.assertEqual(health.check(), {"redis": "unavailable"})
            self.assertEqual(health.check(), {"redis": "unavailable"})
            self.assertLess(time.monotonic() - start, .12)
            self.assertEqual(probe.call_count, 1)
            time.sleep(.16)
            self.assertEqual(health.check(), {"redis": "ok"})
            self.assertEqual(probe.call_count, 1)

    def test_liveness_never_invokes_dependency_checks(self):
        deps = self.module()
        module = importlib.import_module("Build.api.health.app")
        with patch.dict(os.environ, CONFIG, clear=True), patch.object(deps.DependencyHealth, "check", side_effect=AssertionError("no I/O")), TestClient(module.create_app()) as client:
            self.assertEqual(client.get("/health/live").status_code, 200)

    def test_postgres_probe_uses_read_only_query_and_bounded_connection(self):
        deps = self.module()
        with patch("psycopg.connect") as connect:
            cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
            cursor.fetchone.return_value = (1,)
            self.assertTrue(deps.probe("postgres", CONFIG))
            cursor.execute.assert_called_once_with("SELECT 1")
            self.assertEqual(connect.call_args.kwargs["connect_timeout"], 2)
            self.assertEqual(connect.call_args.kwargs["options"], "-c statement_timeout=2000")

    def test_redis_probe_checks_ping_and_disables_retries(self):
        deps = self.module()
        with patch("redis.Redis.from_url") as connect:
            client = connect.return_value.__enter__.return_value
            client.ping.return_value = True
            self.assertTrue(deps.probe("redis", CONFIG))
            client.ping.assert_called_once_with()
            self.assertEqual(connect.call_args.kwargs["socket_connect_timeout"], 2)
            self.assertEqual(connect.call_args.kwargs["socket_timeout"], 2)
            self.assertEqual(connect.call_args.kwargs["retry"].get_retries(), 0)
            client.ping.return_value = False
            self.assertFalse(deps.probe("redis", CONFIG))

    def test_bucket_probe_head_only_explicit_credentials_timeout_and_cleanup(self):
        deps = self.module()
        with patch("boto3.client") as connect:
            client = connect.return_value
            client.head_bucket.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
            self.assertTrue(deps.probe("bucket", CONFIG))
            client.head_bucket.assert_called_once_with(Bucket="dev-canary")
            client.close.assert_called_once_with()
            self.assertEqual([call[0] for call in client.method_calls], ["head_bucket", "close"])
            config = connect.call_args.kwargs["config"]
            self.assertEqual((config.connect_timeout, config.read_timeout), (2, 2))
            self.assertEqual(config.retries, {"total_max_attempts": 1})
            self.assertEqual(config.s3, {"addressing_style": "virtual"})
            self.assertEqual(connect.call_args.kwargs["aws_access_key_id"], CONFIG["BUCKET_ACCESS_KEY_ID"])
            client.reset_mock()
            client.head_bucket.side_effect = RuntimeError("canary-secret")
            with self.assertRaises(RuntimeError):
                deps.probe("bucket", CONFIG)
            client.close.assert_called_once_with()

    def test_invalid_connection_schemes_never_reach_sdk(self):
        deps = self.module()
        for name, field in (("postgres", "DATABASE_URL"), ("redis", "REDIS_URL"), ("bucket", "BUCKET_ENDPOINT")):
            self.assertFalse(deps.probe(name, CONFIG | {field: "http://canary.invalid"}))


if __name__ == "__main__":
    unittest.main()
