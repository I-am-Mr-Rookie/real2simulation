"""One-shot DEV Redis copy. Run inside Railway; emit counts, never keys or values."""
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def database_url(url, database):
    parts = urlsplit(url)
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if k != "db"])
    return urlunsplit(parts._replace(path=f"/{database}", query=query))


def category(key):
    if key.startswith(b"job:"):
        return "job_" + next((s for s in ("input", "owner", "events", "provenance")
                              if key.endswith(b":" + s.encode())), "other")
    return "idempotency_output" if key.startswith(b"out:") else "active_lease" if key.startswith(b"claim:") else "other"


def snapshot(client):
    keys = sorted(set(client.scan_iter(count=500)))
    pipe = client.pipeline(transaction=False)
    for key in keys:
        pipe.type(key)
        pipe.pttl(key)
        pipe.dump(key)
    values = pipe.execute()
    result = {}
    for index, key in enumerate(keys):
        kind, ttl, payload = values[index * 3:index * 3 + 3]
        if ttl != -1 or payload is None or category(key) == "active_lease":
            raise ValueError("Expiring, missing or active lease key: stop without cutover")
        result[key] = (kind, hashlib.sha256(payload).digest(), payload)
    if client.dbsize() != len(result):
        raise ValueError("Key count changed during snapshot")
    return result


def verify(source, target):
    if source.keys() != target.keys() or any(source[k][:2] != target[k][:2] for k in source):
        raise ValueError("Key/type/per-key DUMP checksum mismatch")
    return {"keys": len(source), "nonexpiring": len(source),
            "categories": dict(Counter(category(k) for k in source)),
            "types": dict(Counter(v[0].decode() for v in source.values())),
            "every_key_dump_sha256_matches": True, "checked_dump_payloads": len(source)}


def copy_database(source, target):
    if target.dbsize():
        raise ValueError("Destination is not empty; no overwrite allowed")
    before = snapshot(source)
    pipe = target.pipeline(transaction=True)
    for key, (_, _, payload) in before.items():
        pipe.restore(key, 0, payload, replace=False)
    pipe.execute()
    receipt = verify(before, snapshot(target))
    verify(before, snapshot(source))
    target.save()
    receipt["synchronous_save"] = True
    return receipt


def pause_writes(source):
    # redis-py 8 accepts arbitrary kwargs; mode="WRITE" silently pauses ALL instead.
    source.execute_command("CLIENT", "PAUSE", 600000, "WRITE")


def main():
    from redis import Redis
    source = Redis.from_url(os.environ["REDIS_URL"], socket_timeout=20, socket_connect_timeout=10,
                            single_connection_client=True)
    destination = Redis.from_url(os.environ["N41_DEST_REDIS_URL"], socket_timeout=20, socket_connect_timeout=10,
                                 single_connection_client=True)
    if source.connection_pool.connection_kwargs["host"] == destination.connection_pool.connection_kwargs["host"]:
        raise ValueError("Source and destination must be different")
    databases = sorted({0} | {int(db[2:]) for db in source.info("keyspace")})
    if destination.info("keyspace"):
        raise ValueError("Destination contains data; stop")
    # API must already be stopped. This also fences unknown Redis writers.
    pause_writes(source)
    started = datetime.now(timezone.utc).isoformat()
    try:
        receipts = {}
        for database in databases:
            with Redis.from_url(database_url(os.environ["REDIS_URL"], database),
                                socket_timeout=20, socket_connect_timeout=10) as a, \
                 Redis.from_url(database_url(os.environ["N41_DEST_REDIS_URL"], database),
                                socket_timeout=20, socket_connect_timeout=10) as b:
                receipts[f"db{database}"] = copy_database(a, b)
        print(json.dumps({"label": "MEASURED", "fence_started_utc": started,
                          "server_write_pause_ms": 600000, "databases": receipts,
                          "fence_release": "explicit CLIENT UNPAUSE after cutover; auto expires after 10 minutes"}))
    except Exception:
        source.client_unpause()
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"error_type": type(error).__name__, "cutover_allowed": False}))
        raise SystemExit(1)
