# S13d-orch25 PLAN

- Issued 2026-10-29T15:23:27+00:00 UTC; deadline 2026-10-29T15:53:27+00:00 (Dhaka 21:53:27+06:00); cutoff 15:48:27Z.
- Model: anthropic/claude-opus-5-5 / medium (assigned). Coding quota: OpenCodex-managed; not polled.
- Objective: Redis-shaped job lifecycle + retry so retries never duplicate artifacts or paid dispatch.
- Owns: Build/pipeline/; contracts/jobs/; tests/pipeline/; Run-System/Runs/S13d-orch25/.
- Approach: reuse S13a contracts (check_events, _retry_allowed, job_snapshot, policy); no redis client installed
  -> in-memory store with redis-py method shapes; unittest like existing suite. No installs, Modal, Railway, spend.
- Checks: test_jobs (idempotent reuse, lease vs duplicate paid dispatch, bounded retries, terminal freeze, crash resume);
  full pipeline suite still green.
