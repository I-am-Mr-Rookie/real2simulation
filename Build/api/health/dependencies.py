"""Read-only dev dependency probes. No schema changes, writes, uploads or jobs."""
from concurrent.futures import ThreadPoolExecutor, wait
import threading
import time
from urllib.parse import urlsplit


FIELDS = {
    "postgres": ("DATABASE_URL",),
    "redis": ("REDIS_URL",),
    "bucket": ("BUCKET_ENDPOINT", "BUCKET_NAME", "BUCKET_REGION",
               "BUCKET_ACCESS_KEY_ID", "BUCKET_SECRET_ACCESS_KEY"),
}
# Bounded process-wide pool; at most one outstanding check/dependency/app.
_POOL = ThreadPoolExecutor(max_workers=3, thread_name_prefix="dependency-health")


def probe(name, env):
    """Return true only after a service-level operation, never mere TCP success."""
    if name == "postgres":
        if urlsplit(env["DATABASE_URL"]).scheme not in ("postgres", "postgresql"):
            return False
        import psycopg
        with psycopg.connect(env["DATABASE_URL"], connect_timeout=2,
                             options="-c statement_timeout=2000", autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone() == (1,)
    if name == "redis":
        if urlsplit(env["REDIS_URL"]).scheme not in ("redis", "rediss"):
            return False
        from redis import Redis
        from redis.backoff import NoBackoff
        from redis.retry import Retry
        with Redis.from_url(env["REDIS_URL"], socket_connect_timeout=2,
                            socket_timeout=2, retry=Retry(NoBackoff(), 0)) as client:
            return client.ping() is True
    if name == "bucket":
        endpoint = urlsplit(env["BUCKET_ENDPOINT"])
        if endpoint.scheme != "https" or not endpoint.hostname or endpoint.username or endpoint.password:
            return False
        import boto3
        from botocore.config import Config
        # Explicit credentials avoid ambient AWS/profile/instance-metadata lookup.
        client = boto3.client("s3", endpoint_url=env["BUCKET_ENDPOINT"],
            region_name=env["BUCKET_REGION"],
            aws_access_key_id=env["BUCKET_ACCESS_KEY_ID"],
            aws_secret_access_key=env["BUCKET_SECRET_ACCESS_KEY"],
            config=Config(connect_timeout=2, read_timeout=2,
                          retries={"total_max_attempts": 1},
                          s3={"addressing_style": "virtual"}))
        try:
            result = client.head_bucket(Bucket=env["BUCKET_NAME"])
            return result.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200
        finally:
            client.close()
    return False


def _safe_probe(name, env):
    try:
        return "ok" if probe(name, env) is True else "unavailable"
    except Exception:
        # Never return/log exception strings, hosts, connection URLs or SDK data.
        return "unavailable"


class DependencyHealth:
    def __init__(self, env, names, deadline=3.0):
        self.env = {key: env.get(key, "") for fields in FIELDS.values() for key in fields}
        self.enabled = env.get("R2S_ENVIRONMENT") == "development" and env.get("RAILWAY_ENVIRONMENT_NAME", "dev") == "dev"
        self.names = names
        self.deadline = deadline
        self.lock = threading.Lock()
        self.pending = {}
        self.started = {}

    def check(self):
        states = {}
        with self.lock:
            for name in self.names:
                if not all(self.env[field].strip() for field in FIELDS[name]):
                    states[name] = "not-configured"
                elif not self.enabled:
                    states[name] = "unavailable"
                else:
                    future = self.pending.get(name)
                    # Cache for five seconds; never enqueue duplicates while slow.
                    if future is None or (future.done() and time.monotonic() - self.started[name] >= 5):
                        self.pending[name] = _POOL.submit(_safe_probe, name, self.env)
                        self.started[name] = time.monotonic()
                    states[name] = "unavailable"
            pending = {name: self.pending[name] for name in states if name in self.pending}
        if pending:
            wait(pending.values(), timeout=self.deadline)
            for name, future in pending.items():
                if future.done():
                    states[name] = future.result()
        return states
