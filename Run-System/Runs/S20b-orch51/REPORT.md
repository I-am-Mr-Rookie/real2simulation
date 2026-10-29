# S20b-orch51 — DONE (scoped offline guard, not live enforcement)

CODEX-2; step S20; assigned gpt-6.1-sol/medium. Parent project Meta AI Hackathon
`91e441f8-e40c-4ec4-bea2-de7fa1582d97` per controller contract. Branch
`run/S20b-orch51`, base `c19fbf793284450931f39d929719be1ff74af615`, isolated
`.worktrees/S20b-orch51`. Not merged; controller owns integration/canonical controls.

Issued 2026-10-29T22:04:09+00:00; first instrumented worker clock 22:04:49Z;
implementation cutoff 22:29:09Z; deadline 22:34:09Z (04:34:09 Dhaka).
Actual UTC work-stop/report timestamps are recorded in `TIMEBOX.json`.
Fully verified scoped work finished early; no terminal incomplete exception needed.

## Delivered

- `Build/guardrails/admission.py`: 88-line fail-closed preflight reusing S20a
  `usd`, `liability_usd`, `meta_snapshot`. Preserves strict Meta $120 routine stop,
  independent Modal $30 ceiling and $5 remaining floor while failover stays OFF.
  Includes candidates and pending/worst-known liabilities; only evidence-backed
  final reconciliation releases an individual reservation. No live balance assumed.
- Server-owned snapshot shape rejects missing, unreadable, corrupt, duplicate-key,
  unknown-schema, unverified, paused, future and stale (>5 min) state. Monetary
  JSON decimals are parsed without float conversion. Raises nonretryable
  `SPEND_PAUSED`; no path/file contents leak through invalid-state errors.
- `Build/guardrails/ADMISSION.md` + small CONTRACT annotation: state trust boundary,
  source projection, exact caller handoff and explicit non-live status.
- `tests/guardrails/test_admission.py`: 17 new offline tests. Real existing upload
  store and reservation writer work below cap in a harness; breach leaves both
  unchanged. Missing/corrupt state pauses. Existing public-library contract and
  SYNTHETIC precomputed manifest remain readable without consulting admission.
- `evidence/S20/S20b/`: fresh transcripts and small component-render check using
  already-installed Next SWC/React. No install/server/network/provider client.

## Fresh verification

Python 3.14.5; Node v24.18.0. All evidence under `evidence/S20/S20b/`.

| Command | Result | Evidence |
|---|---|---|
| `python -m unittest discover -s tests/guardrails -v` | 34 PASS (17 prior + 17 new) | guardrails-tests.txt |
| `python -m unittest discover -s tests/pipeline -v` | 52 PASS; unchanged, fake transports | pipeline-tests.txt |
| `python -m unittest discover -s Build/gpu -p test_cost_log.py -v` | 5 PASS; unchanged | cost-log-tests.txt |
| `python -m unittest discover -s Build/web/src/shell -p test_contract.py -v` | 7 PASS; unchanged | library-contract-tests.txt |
| `node evidence/S20/S20b/render-library.mjs ../../Build/web/package.json` | real empty guest component render PASS | library-render.txt |
| staged whitespace + exact Owns + protected-path checks | PASS | scope-check.txt |
| `python Run-System/worker_timebox.py check Run-System/Runs/S20b-orch51/TIMEBOX.json` | TIMING PASS | timebox-check.txt |

**98 unit tests passed**, plus component render. Existing pipeline negative test's
`invalid events` diagnostic is expected inside a passing test. Initial render
harness used one excessive parent-directory traversal (ENOENT); corrected and
fresh render passed. No failed final acceptance check.

## Integration finding — do not claim a live cap

One shared paid call site: **`Build/pipeline/gpu_stages.py::reserve`, line 39**,
called by both segment and reconstruct. Controller must integrate this guard
inside a global cross-process check/reconcile/durable-reserve boundary BEFORE
dispatch, preserving existing per-run caps and stable attempt identities.
Map `ReconstructionPaused` to existing `StageError` without retry. Existing
read/check/append is not globally atomic. A new state file is not a replacement
for the canonical heterogeneous ledgers or verified credit reconciliation.

The upload owner must preflight the same state before accepting new sessions/
bytes and map to existing UploadError SPEND_PAUSED. There is no HTTP upload route
in this checkout. No edits to pipeline/web were authorized or made. Durable
per-user/day quota, source reconciliation, atomic admission, crash/concurrency
enforcement and guarding other CLI/paid entry points remain controller follow-up.

**Library limitation discovered:** real `library/page.jsx` says no demos published
and viewer not connected. Actual static guest rendering and existing SYNTHETIC
precomputed-contract/asset isolation pass while admission pauses. This is NOT
published precomputed playback, HTTP guest E2E, real-scene or physical evidence.
Guest routes must never call the guard or depend on its snapshot.

## Ponytail full / decisions / safety

Read installed `.../ponytail/5.3.3/skills/ponytail/SKILL.md` and applied full:
reused the accounting math and existing upload/reservation APIs; one guard, no
second ledger, reconciler, service wrapper, dependency, provider switch or settings.
Caller search identified both existing reservation callers before edits. Added
one duplicate-JSON-field check because ambiguity can conceal spend. Five-minute
snapshot freshness and post-candidate $5 floor are conservative reversible defaults,
not asserted owner/provider facts. No owner approval question needed for offline work.

Skipped live wiring and durable quota by explicit scope; no AWS switch, deployment,
runtime billing/headroom reconciliation, GPU/Meta/cloud call, media upload, auth,
terms, purchase or publication. No canonical controls modified. No code/data copied
from archive. Synthetic temporary upload and reservation records are not paid jobs.
New paid spend/reservations **$0**; ongoing unrelated infrastructure not verified.
Worker tokens unknown; coding quota **OpenCodex-managed; not polled**.

Communication: mandatory Ponytail/tool-work notice and material library finding
only, then one authorized concise completion callback. Report is the evidence
handoff; no optional progress chatter or duplicate report in chat.

Skipped live integration/E2E; production cap enforcement and precomputed playback
remain unverified. Scoped offline DONE does not complete the parent S20/Gate C.
