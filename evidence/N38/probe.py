"""Read-only API-container measurements. Never emit URLs, credentials or key names."""
import json
import os
import statistics
import time
from datetime import datetime, timezone

import psycopg
from psycopg import sql
from redis import Redis


def measure(call):
    samples = []
    for _ in range(7):
        start = time.perf_counter()
        call()
        samples.append(round((time.perf_counter() - start) * 1000, 3))
    return {"samples_ms": samples, "median_ms": statistics.median(samples),
            "min_ms": min(samples), "max_ms": max(samples)}


def main():
    result = {"label": "MEASURED", "observed_utc": datetime.now(timezone.utc).isoformat(),
              "uncertainty": "7 samples, observed range only; not a confidence interval",
              "region": os.environ.get("RAILWAY_REPLICA_REGION"),
              "deployment_id": os.environ.get("RAILWAY_DEPLOYMENT_ID")}
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=10,
                          options="-c default_transaction_read_only=on -c statement_timeout=10000") as conn:
        conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        result["postgres"] = measure(lambda: conn.execute("SELECT 1").fetchone())
        tables = conn.execute("SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema') ORDER BY 1, 2").fetchall()
        result["table_row_counts"] = {f"{schema}.{table}": conn.execute(
            sql.SQL("SELECT count(*) FROM {}.{}").format(sql.Identifier(schema), sql.Identifier(table))).fetchone()[0]
            for schema, table in tables}
        result["postgres_version"] = conn.execute("SHOW server_version").fetchone()[0]
    with Redis.from_url(os.environ["REDIS_URL"], socket_timeout=10, socket_connect_timeout=10) as redis:
        result["redis"] = measure(redis.ping)
        result["redis_dbsize"] = redis.dbsize()
        result["redis_keyspace"] = redis.info("keyspace")
        types = {}
        nonexpiring = 0
        scanned = 0
        cursor, keys = redis.scan(count=100)
        pipeline = redis.pipeline(transaction=False)
        for key in keys:
            pipeline.type(key)
            pipeline.ttl(key)
        inspected = pipeline.execute()
        for index, key in enumerate(keys):
            scanned += 1
            kind = inspected[index * 2].decode()
            types[kind] = types.get(kind, 0) + 1
            nonexpiring += inspected[index * 2 + 1] == -1
        result["redis_scan"] = {"scanned": scanned, "types": types, "nonexpiring": nonexpiring,
                                "complete": cursor == 0}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"error_type": type(error).__name__}))
        raise SystemExit(1)
