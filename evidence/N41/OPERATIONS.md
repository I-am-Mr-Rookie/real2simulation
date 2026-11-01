# N41 DEV dependency migration

Scope: two new Railway template services. The Singapore services and volumes are retained.
No Redis keys, owner identifiers, values, or rendered connection variables leave Railway.
The worker is only a health sidecar, not a job consumer. A temporary destination reference
on that sidecar runs the copy without exposing credentials.

## Preservation protocol

1. Restore the checksum-checked N38 PostgreSQL archive into the new PostgreSQL service.
2. Confirm both new service volumes actually report us-east4-eqdc4a, not merely desired config.
3. Stop the API deployment and verify no API instance remains running.
4. Apply Redis CLIENT PAUSE 600000 WRITE as a second, server-side fence.
5. Enumerate all source databases and all keys. Reject expiring keys or active leases.
6. RESTORE each binary DUMP into an empty destination without REPLACE.
7. Compare every key, type and DUMP SHA256, source before/after, and category totals.
8. Synchronously SAVE the destination. Only then switch API variable references and redeploy.
9. Read a preserved job through the authenticated API, run the DEV verifier and N38 latency probe.
10. Explicitly UNPAUSE the source. Repoint the health-only worker to US Redis and
    remove its temporary destination reference. Retain both old services pending owner confirmation.

## Observed tooling failures, recovered before final cutover

- MCP replica configuration rejects zero. Railway CLI scale-to-zero removes the final
  region instead of leaving zero replicas and defaults desired config to us-west2.
  Desired config was immediately restored to us-east4; the accidental build was stopped.
  The API volume remained in us-east4. Use deployment stop, not scale-to-zero.
- redis-py 8.1 accepts an unused mode=WRITE keyword while its default all=True
  pauses ALL commands. The first copy consequently timed out before writing the destination.
  New connections also cannot authenticate while ALL is paused. No service was restarted,
  avoiding any risk to the original Redis data. The bounded pause expires automatically.
  The corrected implementation sends the explicit CLIENT PAUSE ... WRITE command;
  the exact argument sequence has an offline regression test.
- A network/502 interruption stopped the chat after the final API redeploy was
  triggered at 22:59:59 UTC. The controller resumed this worker at 23:26:58 UTC.
  The 10-minute WRITE fence auto-expired at approximately 23:09:48 UTC.
  Fresh 23:27 UTC verification found the API healthy in US East, with all 228
  keys present. A 23:28 UTC full read-only comparison again matched every DUMP.
  Explicit CLIENT UNPAUSE subsequently succeeded. No inference or user writes
  were generated to test the cutover.
- Provider status timestamps span 22:48:53.842 to 23:00:16.024 UTC
  (682.182 seconds including the failed first fence); the final API-stop/cutover
  span was 138.039 seconds. Exact HTTP downtime was not continuously sampled.
- PostgreSQL restore attempts during service initialization failed closed. The subsequent
  completed restore has exit-on-error, one transaction, matching backup checksum and zero tables.

## Rollback

Before resuming writes: restore API references to Postgres.DATABASE_URL and Redis.REDIS_URL,
restore worker REDIS_URL to Redis.REDIS_URL, redeploy the known-good builds, and clear the source pause.
After writes resume on US: stop/fence writes again and reconcile or reverse-copy new US
records before repointing. Blindly repointing to the retained SG snapshot can lose new jobs.

## Limits

Seven latency samples give an observed range, not a confidence interval.
The legacy verifier does not test paid inference or a new upload.
New template services incur ordinary Railway usage; exact incremental billing is unavailable.

## MEASURED latency

Same N38 API-container probe, seven samples per dependency:

| Dependency | N38 median ms | N41 pre-cutover median ms | N41 US median ms | US observed range ms |
| --- | ---: | ---: | ---: | ---: |
| PostgreSQL SELECT 1 | 214.226 | 213.973 | 0.255 | 0.229 to 1.163 |
| Redis PING | 227.270 | 244.283 | 0.239 | 0.204 to 7.967 |

Redis latency includes its first connection. The probe's partial SCAN is not the
preservation inventory; copy.json and redis-final.json enumerate and compare all keys.
