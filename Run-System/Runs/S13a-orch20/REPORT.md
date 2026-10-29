# S13a-orch20 REPORT — DONE

- Lane CODEX-1; model anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Tokens/cost: unknown; service spend $0.
- Issued 2026-10-29T12:05:40+00:00, deadline 12:35:40+00:00; work start 12:07:01Z, work stopped 2026-10-29T12:18:13+00:00. Base main 4f193cf, branch run/S13a-orch20.
- Acceptance "File limits, retry semantics and stage events versioned": met as contracts + offline tests on SYNTHETIC fixtures.

## Files (all within Owns)
- contracts/jobs/jobs.schema.json — `urn:real2simulation:jobs:1.0.0`: upload_session, chunk_ack, stage_event.
- contracts/jobs/policy.json — limits (100 MiB, 8 MiB chunks, mp4/mov/webm, 60 s, 24 h TTL), stage order + max_attempts, never_retry codes, backoff, 360 s target.
- contracts/jobs/CONTRACT.md, examples.json — semantics; synthetic examples.
- Build/pipeline/contracts.py (+__init__.py) — `errors`, `chunk_decision` (resume/duplicate/conflict/gap), `check_events` (revision, order, attempt, idempotency key, never-retry), `job_snapshot` (→ S04g shell job DTO).
- tests/pipeline/test_contracts.py — 8 tests.

## Ponytail (applied)
- Reuse: S04g shell schema read directly in tests — error-code enum must equal shell's, snapshots validated against `Build/web/src/shell/integration.schema.json`; its revision rule and "terminal never transitions, retry = new job id" adopted, not redefined. S06a referenced by contract id `S06a-gpu-image/v1` on reconstruct stage. Installed jsonschema/unittest (no pytest; none added).
- Smallest complete: one schema + one policy file + ~110-line pure module; no transport, storage, Redis, ffmpeg or class hierarchy (S13b–g own those). Schema/policy numeric duplication guarded by a consistency test instead of a generator.
- Hardening: `job_snapshot` raises ValueError (not assert) so -O keeps checks; non-stage docs rejected by `check_events`.

## Checks (fresh, [tests.txt](tests.txt))
- `python -m unittest tests.pipeline.test_contracts`: 8 OK; same under `python -O`: 8 OK.
- Each sequence-violation case asserts its specific reason (skip stage, revision gap, finish-without-start, after-ready, never-retry marked retryable, validate retried, job id change, key prefix, wrong kind); manual -O probe confirmed reasons.
- Neighbours unchanged and green: shell contract tests (discover Build/web/src/shell) 8 OK; tests.fitter.test_api OK.

## Decisions (routine, reversible; for Reviews for Koushik)
- Limits 100 MiB / 60 s / 8 MiB chunks / 24 h TTL are contract choices, not measured capacity; revisit at S13h measurement.
- Paid stages (understand, segment, reconstruct) max 2 attempts; validate 1; idempotency key = stage + input sha256 so retries/new jobs reuse outputs without re-spend (S13d implements).

## Skipped / limits
- No live services, bucket writes, uploads, deploys, installs, GPU, real media. Duration/type sniffing is a validate-stage duty (S13b/c), not schema-enforced. Cancellation not modelled as a stage event. No gate/real-scene/physical claim.
- Communication: silent; only the authorized final controller line.
