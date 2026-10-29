# S13d-orch25 REPORT — DONE

- Lane CODEX-1; model anthropic/claude-opus-5-5 / medium. UTC start 2026-10-29T15:24:00Z (issued 15:23:27Z); end 2026-10-29T15:29:08+00:00.
- Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable). Spend: $0 (no Modal/API/Railway).
- Base: main ba5f668 (S13a-c merged). Branch run/S13d-orch25, worktree .worktrees/S13d-orch25.
- Handout listed Dhaka deadline with +00:00; actual Dhaka deadline is 21:53:27+06:00 (recorded in TIMEBOX).

## Changed
- Build/pipeline/jobs.py (new): `JobRunner` lifecycle/resume, `MemoryStore` (redis-py-shaped), `StageError`, `Busy`.
- tests/pipeline/test_jobs.py (new): 10 tests, SYNTHETIC workers.
- contracts/jobs/CONTRACT.md: S13d section (keys, reuse, lease, crash recovery, at-least-once limit).

## Acceptance: retry does not duplicate artifacts or spend without idempotency
- Within-job retry + new-job user retry reuse `out:<idempotency_key>`: paid understand/segment dispatched once
  across two jobs; one `out:` record per stage key (test_user_retry_new_job_reuses_outputs_without_paid_redispatch).
- Concurrent same-key job gets `Busy` before any event/dispatch (test_live_lease_blocks_duplicate_paid_dispatch);
  dead worker lease expires then proceeds (test_crashed_worker_lease_expires).
- Bounded retries: keyframes 3 calls, backoff [5,30], terminal and frozen on rerun; paid reconstruct max 2;
  SPEND_PAUSED forced non-retryable; crash mid-stage resumes via recorded output or a counted PROCESSING_FAILED.
- Every appended event passes S13a `check_events` (explicit raise, survives -O).

## Fresh checks
- `python -m unittest tests.pipeline.test_contracts tests.pipeline.test_uploads tests.pipeline.test_keyframes tests.pipeline.test_jobs` -> Ran 30, OK.
- `python -O -m unittest tests.pipeline.test_jobs` -> Ran 10, OK.
- Mutation sanity: disabling `out:` reuse -> 3 failures; disabling NX lease -> 2 failures (tests bite).
- `python Run-System/worker_timebox.py check Run-System/Runs/S13d-orch25/TIMEBOX.json` -> TIMING PASS.

## Ponytail (full) applied
- Reuse: S13a `check_events`, `_retry_allowed`, `job_snapshot`, policy `backoff_s`/`never_retry`; existing
  `PROCESSING_FAILED` code for lost workers -> no schema/policy change; unittest style of the suite.
- Smallest complete: no redis client installed -> in-memory store using redis-py call shapes (no adapter layer,
  no install); one runner loop derives state from events (no separate state record); inject sleep/clock/now for tests.
- Skipped: real Redis/RQ queue, worker process/pool, Lua token-checked lease release, metrics, cancellation (later user action).

## Limits / risks
- No Redis server or client exercised; drop-in claim for `redis.Redis(decode_responses=True)` is untested.
- At-least-once: paid call that ran but crashed before `out:` write can repeat once (bounded by max_attempts 2);
  provider-side idempotency must use the forwarded key (S13e+).
- Unconditional lease delete can drop a lease re-taken after expiry (shortcut comment); lease_s must exceed stage runtime.
- Event append is read-then-push, safe only under the per-key lease (one writer per job stage).
- SYNTHETIC only: no gate, real-scene, GPU or physical evidence.

## Communication
Silent; one completion message to controller chat. No canonical control edits, installs, deploys or spend.

## Next
S13e: Muse understanding worker passes the idempotency key; real Redis client decision at deploy time.
