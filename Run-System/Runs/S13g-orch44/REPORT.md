# S13g-orch44 REPORT — Stream job progress to shell integration interface

Status: **DONE** (offline). Lane CODEX-1; assigned anthropic/claude-opus-5-5/medium; coding quota OpenCodex-managed; not polled. Tokens/cost: unknown/unobservable; $0 spend (no GPU/Modal/Meta).
Issued 2026-10-29T21:35:50Z; started 21:36:17Z; work stopped/reported 2026-10-29T21:39:12Z (verified DONE, early finish allowed); deadline 22:05:50Z. Base main b42dfd2; branch run/S13g-orch44. Not merged (controller integrates).

## Changed (Owns only)
- [Build/pipeline/progress.py](../../../Build/pipeline/progress.py) (new): `progress(job_id, events, after=0, scene=None)` -> versioned `job_progress` 1.0.0 doc = display rows (`revision, stage, status, attempt, ts, retryable, message`, revisions > after, in order) + `job` = existing `job_snapshot`. `readable()` strips control chars, redacts absolute paths/token-like values, caps 240. Whole sequence validated (`check_events`) before projection; doc schema-validated (explicit raise, survives -O). CLI `python -m Build.pipeline.progress EVENTS.jsonl [AFTER_REVISION]`.
- [Build/pipeline/jobs.py](../../../Build/pipeline/jobs.py): `JobRunner.progress(job_id, after, scene)` over the runner's own stored events (one method; emission path unchanged).
- [contracts/jobs/jobs.schema.json](../../../contracts/jobs/jobs.schema.json): `$defs/progress_event`, `$defs/job_progress` (additive, same 1.0.0 `$id`; top-level oneOf extended). `retryable` null unless failed.
- [contracts/jobs/CONTRACT.md](../../../contracts/jobs/CONTRACT.md): "Job progress feed (S13g)" section.
- [tests/pipeline/test_progress.py](../../../tests/pipeline/test_progress.py) (new, 7 SYNTHETIC tests).

## Shell integration (no UI edits)
Existing consumer: Build/web/src/workspace/workflow.mjs `JOB_UPDATE {job}` edge (parseJob; ignores stale/equal revisions) + status.mjs log. Host polls the feed with `after_revision` = last seen and dispatches `{type:'JOB_UPDATE', job: doc.job}`; `doc.events` are the stage rows to display. Test asserts `doc.job == JobRunner.run()` snapshot.

## Ponytail (applied)
Reuse: existing stage_event (already has stage/status/at/error.retryable), JobRunner event list, `check_events`, `job_snapshot`, `_retry_allowed`, `errors()` validator, existing JOB_UPDATE reducer edge, test_jobs `fixture`/`runner`. Smallest complete: a projection function + one runner method + additive schema defs; no new store/transport. Skipped: HTTP route/SSE (Build/api and Build/web outside Owns; no existing job route to extend), a new contract major version (change is additive), progress percentages/ETAs.

## Fresh checks
- `python -m unittest tests.pipeline.test_progress tests.pipeline.test_gpu_stages tests.pipeline.test_jobs tests.pipeline.test_contracts tests.pipeline.test_keyframes tests.pipeline.test_understand tests.pipeline.test_uploads` -> **50 OK** (43 prior + 7 new).
- `python -O -m unittest tests.pipeline.test_progress` -> OK.
- Covered: success (12 ordered rows, job ready), retryable failure (failed retryable=true, attempt 2/2 shown), retryable code out of attempts (retryable=false, "Not retried."), never-retry INVALID_INPUT (terminal; abs path/token/idempotency key/input hash absent; relative evidence/ pointer kept), after_revision paging + out-of-order and schema-invalid sequences raise, schema rejects extra keys/bad retryable/empty or >240 message/bad ts, CLI over append-only JSONL (+ invalid file rc 1).
- `python Run-System/worker_timebox.py check Run-System/Runs/S13g-orch44/TIMEBOX.json` -> TIMING PASS.

## Limits / not claimed
No transport endpoint wired (host must call progress/CLI); redaction is a regex safety net, not a secret scanner; real Redis not exercised. No gate, GPU, real-scene or physical claim.
Communication: silent; one completion message to controller chat.
Next: S13h or a Build/api/web owner adds a GET route (poll) calling `progress`.
