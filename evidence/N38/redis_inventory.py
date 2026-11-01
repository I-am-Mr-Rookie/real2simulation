"""Inventory all Redis databases by aggregate purpose only, never print keys or values."""
import json
import os
from collections import Counter
from redis import Redis


if __name__ == "__main__":
    root = Redis.from_url(os.environ["REDIS_URL"], socket_timeout=10, socket_connect_timeout=10)
    result = {}
    for database, info in root.info("keyspace").items():
        client = Redis.from_url(os.environ["REDIS_URL"], db=int(database[2:]), socket_timeout=10,
                                socket_connect_timeout=10)
        counts = Counter()
        # shortcut: cap the read-only inventory at 1000 keys, use a bounded maintenance audit for larger stores.
        for index, key in enumerate(client.scan_iter(count=200)):
            if index >= 1000:
                raise SystemExit("Inventory exceeds safe audit limit; no changes made")
            category = "other"
            if key.startswith(b"job:"):
                category = "job_" + next((suffix for suffix in ("input", "owner", "events", "provenance")
                                         if key.endswith(b":" + suffix.encode())), "other")
            elif key.startswith(b"out:"):
                category = "idempotency_output"
            elif key.startswith(b"claim:"):
                category = "active_lease"
            counts[category] += 1
        result[database] = {"keyspace": info, "categories": dict(counts)}
    print(json.dumps(result, indent=2))
