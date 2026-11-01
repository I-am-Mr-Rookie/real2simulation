# N38-orch282
Status: PARTIAL. Safety stop required by task: Redis is durable job/owner/provenance storage, not disposable cache.
Changed: evidence/N38 only, plus this report/timebox; no live configuration, references, deployment, region or volume changed.
MEASURED from api us-east4: PostgreSQL median 214.226 ms (214.056 to 428.378); Redis median 227.270 ms (226.854 to 1370.697); seven samples each, range not a confidence interval.
Postgres 18.6 has zero non-system tables; row counts {}. Redis db0 has 228 keys, none expiring.
Full inventory: 69 inputs, 69 owner mappings, 69 provenance records, 15 event lists, 6 idempotency outputs; cold start would lose durable records/deduplication.
Backup: gitignored evidence/N38/private/postgres-before.dump (885 bytes), pg_restore --list OK, local format/remote SHA256 match; no restore drill.
IMPORTANT: preserve this worktree/private backup before cleanup; backup is deliberately not committed.
Railway supports service+volume region migration, but that would move originals rather than keep Singapore untouched; separate US clones need Redis preservation and a verified write fence.
Checks: 6 new safety tests PASS; live python infra/railway/dev/verify.py exit 0, all 11 checks PASS on unchanged DEV.
Existing verifier suite: 8 tests, 71 failures; test fixture pins db6060d, real verifier pins a932d0f; neither file changed. Full evidence retained.
Retain, DO NOT REMOVE: Singapore Postgres 33692dd8-74ea-4bd1-a95f-fb9a41d9272e / postgres-volume and Redis eee6243b-85a7-426a-97a0-46db3f6adefb / redis-volume. Both still serve DEV.
Paid calls: no model/GPU jobs/new services; existing Railway usage only, incremental read-only probe cost unknown.
Skipped: migration, cutover, redeploy, after latency and post-restore counts. Risk: cross-region latency remains; cold Redis replacement would lose durable data.
Details/source: evidence/N38/FINDINGS.md, before.json, redis-inventory.json, backup-receipt.json, provider-final.json, live-verify.json.
