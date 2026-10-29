# S20c-orch54 — DONE (offline switch, not live dispatch)

CODEX-2 / S20; assigned gpt-6.1-sol / medium. Exact runtime model/effort, tokens
and coding dollars unobservable. **OpenCodex-managed; not polled.**
Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97` per
controller contract; existing associated chat used, no new chat/project created.

Branch `run/S20c-orch54`, base main `eda559f000aae3c8c23a6a06a51b06de18fa0704`.
Worktree: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S20c-orch54`.
Controller integrates; no canonical controls, main merge, push or deployment.

Issued 2026-10-29T22:13:38Z; first observed clock 22:14:13Z; cutoff 22:38:38Z;
deadline 22:43:38Z (Oct30 04:43:38 Dhaka). Technical work stopped 22:19:47Z;
report clock 22:19:57Z; exact timestamps in TIMEBOX.json. All scoped acceptance
criteria verified; early DONE, no early-incomplete exception or idle padding.

## Delivered / acceptance

- `Build/guardrails/failover.py`: 80-line offline provider selector; Modal default,
  AWS only when existing `R2S_ENABLE_AWS` is exactly `"1"`. No environment writes
  or persisted enable state. Reuses unchanged S20b `require_reconstruction`,
  S20a `usd`, duplicate-key validation and existing AWS adapter `activate`.
- Explicit quota AND budget JSON paths required for AWS. Validate owner-recorded
  approvals, schemas, fresh aware timestamps, us-east-2 G/VT spot quota >=4 vCPU,
  correct quota code, exact named $50 USD/month gross EC2 budget and all alerts.
  On-demand/wrong region/unknown or stale evidence refuses nonretryable SPEND_PAUSED.
- Fresh verified credit + reconciled gross headroom must cover a positive all-in
  AWS bound. Headroom cannot round upward into permission; cost rounds upward.
  Plan carries <=3600-second session bound and required stop-on-exit; never launches.
  Budget receipt is an evidence projection from shared accounting, not another ledger.
- S20b admission runs FIRST for both providers. Strict Meta routine cap/pending/
  history/credit and Modal cap/$5 floor remain intact. Failure never auto-selects
  a different provider. Guest library/admission modules remain unchanged.
- `infra/failover/CONTRACT.md`: exact API, schemas, trust boundary and paid-boundary
  obligations. Small cross-reference in `Build/guardrails/CONTRACT.md`.
- `tests/guardrails/test_failover.py`: 13 new synthetic offline tests, including
  missing/corrupt/duplicate-key/invalid/stale receipts, missing nested fields,
  default OFF, explicit plan, on-demand refusal, headroom/cost rounding, cap/credit
  failure, read-only inputs and proof admission failure precedes adapter invocation.

## Fresh verification

Python 3.14.5; transcripts under `evidence/S20/S20c-orch54/`.

| Command | Result | Evidence |
|---|---|---|
| `python -m unittest discover -s tests/guardrails -p 'test_*.py' -v` | 47 PASS (34 existing + 13 new) | guardrails-tests.txt |
| `python -m unittest discover -s Build/gpu -p test_aws_adapter.py -v` | 7 PASS | aws-adapter-tests.txt |
| `python -m unittest discover -s tests/pipeline -v` | 52 PASS; fake transports only | pipeline-tests.txt |
| `git diff --cached --check` + staged Owns/cache assertion | PASS | scope-check.txt |
| `python Run-System/worker_timebox.py check Run-System/Runs/S20c-orch54/TIMEBOX.json` | TIMING PASS | timebox-check.txt |

**106 tests passed.** Expected test-first import failure before the new selector
existed; fresh targeted and full guardrails suites passed after implementation.
Pipeline negative test emits expected `invalid events` diagnostic within a PASS.
One initial historical-report path guessed as S20a-orch50 did not exist; corrected
to actual S20a-orch48. No final failed acceptance checks.

## Scope / Ponytail / communication

Read and applied installed Ponytail full at
`C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.3/skills/ponytail/SKILL.md`.
Concrete smallest-complete choices: reuse two existing guards instead of a second
AWS launcher; preserve S20b without changes; standard-library receipt validation;
one new function surface and tests, no dependency/SDK/config/ledger additions.
Searched callers/AWS code first; selector is new and has no existing production
caller/export to update. Prior S20a/S20b reports and owner AWS decisions read.
No browser/cloud plugins needed for a local offline guard; no installs.

No owner question or nonterminal blocker needed. Silent except mandatory
higher-priority brief skill/work update and authorized final controller callback.
No AWS APIs (including describe), resources, account/quota/budget changes, secrets,
uploads, inference or GPU jobs. New cloud calls/spend: zero; historical balances,
ongoing infrastructure charges and actual applicable credits not reverified.

## Skipped / risks / controller handoff

Skipped live AWS and pipeline/upload wiring (outside Owns), persistent switch
settings, reconcilers, atomic reserve/dispatch and watchdogs. **No live failover,
resource shutdown, hard billing cap, Gate C or product end-to-end claim.**
Receipt flags validate shape, not truth; trusted caller must verify their evidence
and derive headroom from shared source inventory under one global reservation lock.
Integrate at existing `Build/pipeline/gpu_stages.py::reserve` and upload boundary
before any real dispatch; preserve durable reservation and guaranteed termination.

Conservative limitation: AWS selection still requires passing S20b Modal cap/$5
floor. This run does NOT provide low-Modal-credit relief; changing provider-aware
admission needs a separately reviewed scope. Existing owner approvals are reused,
not replaced with new per-job consent. Cross-vendor R-C and S20d remain separate.
