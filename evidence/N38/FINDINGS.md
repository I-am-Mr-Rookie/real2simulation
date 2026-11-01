# N38 safety stop

## Measured before migration

Read-only SSH probe ran inside the existing api deployment, US East. No service
variables, connection strings, Redis keys or stored values were exported.
`before.json` records seven samples per dependency, including the first Redis
connection. These ranges describe observations, not statistical confidence.

- PostgreSQL SELECT 1 median: 214.226 ms; range 214.056 to 428.378 ms.
- Redis PING median: 227.270 ms; range 226.854 to 1370.697 ms.
- PostgreSQL 18.6: zero non-system tables, so the table-count mapping is empty.
- Redis db0: 228 keys, zero expiring keys. Other databases absent from INFO keyspace.
- Full, separate SCAN inventory: 69 job inputs, 69 owner mappings, 69 provenance
  records, 15 job event lists, 6 idempotency outputs. No active lease keys observed.

## Concrete data-loss risk

Redis is NOT disposable cache/queue data. `Build/api/workspace/jobs.py` uses Redis
as its store. `Build/pipeline/jobs.py` reads event histories to resume jobs and
retains outputs to prevent duplicate dispatch. A cold start would lose owner/job
lookup information and output deduplication, not merely rebuild a cache.
No active lease keys at one instant is not a write fence. There is no verified
consistent snapshot or cutover protocol protecting writes by the live api.
The task explicitly says to stop and report PARTIAL when data loss is at risk.
Therefore no region changes, new services, variable changes or redeploys occurred.

## Supported paths and preservation constraint

[Railway regions documentation](https://docs.railway.com/deployments/regions#volumes)
confirms that changing a service region migrates its attached volume with downtime.
N23 used that supported path for api-volume. Doing it to these singleton databases
would move the originals, contrary to this task's stronger requirement to leave
the Singapore services untouched until Koushik confirms.

A later run should provision separate US services, preserve ALL Redis records
(not cold-start), establish a maintenance/write fence covering every writer,
take and validate final PostgreSQL and Redis snapshots, restore into new volumes,
compare PostgreSQL table counts plus Redis key/type/TTL and content integrity,
then switch only api DATABASE_URL/REDIS_URL references and verify. Keep the old
services for rollback; resuming writes requires a deliberate rollback policy.
No such unverified cutover was attempted here.

## Backup and checks

`private/postgres-before.dump` is a gitignored local custom-format pg_dump.
Remote pg_restore --list passed; decoded local bytes matched the remote SHA256.
Receipt: `backup-receipt.json`. This is not a restore drill. Keep this worktree
until the controller preserves its private backup; Git does not contain it.

Live `python infra/railway/dev/verify.py`: exit 0, all 11 checks passed. This is
the unchanged deployment, not a post-migration acceptance claim.
Six new offline safety tests passed. Existing verifier tests: eight tests,
71 failures. The fixture pins db6060d while the verifier pins a932d0f; these
files were untouched by N38. Full output retained in verifier-tests.txt.

Do not remove either Singapore service now: Postgres
33692dd8-74ea-4bd1-a95f-fb9a41d9272e (postgres-volume) and Redis
eee6243b-85a7-426a-97a0-46db3f6adefb (redis-volume). They still serve DEV.
`provider-final.json` records original deployment IDs and regions unchanged.
No after-migration latency or before/after row comparison exists because no
migration took place. No Meta/Modal/GPU calls or additional services were used;
ordinary existing Railway usage continues, incremental probe cost unreported.
