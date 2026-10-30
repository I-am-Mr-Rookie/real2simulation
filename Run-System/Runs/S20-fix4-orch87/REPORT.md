# S20-fix4-orch87 — DONE (offline fix/verification scope, not Gate C acceptance)

CODEX-2 / S20; assigned gpt-6.1-sol/high. OpenCodex-managed; not polled.
Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97, as supplied by delegation.
Actual backend identity, tokens and subscription cost unobservable. Cloud/API spend $0.
Issued 2026-10-30T06:17:59+00:00; first observed execution 06:18:59Z.
Implementation/test work stopped 2026-10-30T06:37:37+00:00; reported 2026-10-30T06:38:46+00:00.
Cutoff 06:42:59Z; deadline 06:47:59Z / 12:47:59 Dhaka. Fully verified DONE early.
Plain isolated worktree .worktrees/S20-fix4-orch87; branch run/S20-fix4-orch87;
base main e72338c. Main advanced independently; controller integrates. No merge/push.

## Controller-visible predecessor correction
S20-fix3-orch78 is timing FAILED, PARTIAL, NOT accepted. Its WIP commits
7809496 and 075e8b7 were explicitly cherry-picked as 83e9431 and ee2c941.
Historical fix3 PLAN/REPORT/TIMEBOX and evidence were preserved. This run independently
verified/repaired the code; it does not retroactively pass the predecessor's timing.

## Delivered / reach
- Verified N1 understand.live_post and M3 record_muse: shared canonical lock, global
  durable Meta reservation before POST, result folding, strict global caps and fail-closed
  missing/corrupt state. Existing fix3 regressions exercise mocked actual transport
  boundaries, pre-POST durability, replay, first-seen ledger liabilities and processes.
- Verified N2: all five standalone Modal mains guard dispatch with admit_standalone.
  Added repository-root import bootstrap in their LOCAL mains for file-based launchers.
- Found/fixed a fix3 operational defect: pipeline parent and Modal child reserved the
  SAME job twice, and parent never supplied the standalone amount variable. Parent now
  forwards its request ID; claim_gpu atomically consumes that valid active reservation
  ONCE, rechecking fresh state/budgets, without reserving a second slot. Unknown,
  wrong-stage, stale, claimed and settled IDs pause. Segment's scoped ContextVar is
  always reset. A regression covers forwarding to both actual subprocess call seams.
- N4 settlement: new Build/guardrails/settlement.py accepts reviewed, hash-bound final
  billing/cost_log evidence, matching single-app/request identity, completed status,
  containers [], chronology, explicit final review, exact nonnegative totals and
  unambiguous billing resource/interval/environment rows. Missing/lagging/ambiguous,
  changed or contradictory evidence and write failure release nothing.
- Settlement retains old requests, reservations and ledger events. Active two-job/$1
  limits exclude verified settled rows; ACTUAL bills/overruns remain in monthly $30
  accounting and credit-floor projection. Settled replay still pauses. Every admission
  rechecks immutable settlement evidence. No manual reset/delete/refill path.
- Fixed projection's dropped app identity and copy-on-project behavior, needed for
  unique binding and immutable journal reconciliation.
- Documentation/procedure and remaining trust boundaries:
  evidence/S20/FIX4-SETTLEMENT.md. This supersedes fix3's N4 lifetime-limit decision.
  Changes stay in assigned Owns; only explicitly authorized predecessor run history
  comes from cherry-picking. No canonical controls edited.

## Canonical operational check — no mutation
At 06:32:47Z, canonical evidence/S20/runtime contained only .gitignore.
reservations.json AND receipt.json were absent; a second read at close also confirmed
absence. Thus current journal row count is UNAVAILABLE, not a verified zero.
See evidence/S20/fix4-canonical-journal.json. Nothing was provisioned or settled live.
Without this fix, a future initialized journal would permanently pause after two jobs
or $1 lifetime reservations, including tracking/reconstruction. Now reviewed final
settlement frees outstanding capacity without erasing monthly spend. Missing live
state remains a hard pause; standing GPU authorization is not revoked or re-requested.

## Fresh verification
All final commands used PYTHONPATH="$PWD;$PWD/tests/measurement", temporary synthetic
admission state, mocked transports or offline fixtures; no real journals/providers.
Logs: evidence/S20/fix4-*.
- python -m unittest discover -s tests/guardrails -v: 91 OK.
- python -m unittest discover -s tests/pipeline -v: 53 OK.
- python -m unittest discover -s tests/agent -v: 52 OK.
- python -m unittest discover -s tests/measurement -v: 81 OK, 1 existing skip
  (Windows directory-symlink creation unavailable).
- python -m unittest discover -s Build/gpu -p test_aws_adapter.py -v: 7 OK.
- python evidence/reviews/R-C/recheck/probes_recheck.py: 13/13 expectations met.
  Its N-REFILL intentionally demonstrates privileged journal tampering; N-META-UNDERSTAND
  still exercises the PURE local calculator, not live_post. Those historical findings
  are NOT reported as independent proof that the newly guarded transport is open.
- New settlement/claim tests: 12, included in the 91 above. They cover same-ledger
  third-job admission after settlement; preserved monthly spend, overrun, replay,
  missing/duplicate/nonfinal/changed bills, conflicting observed bills, duplicate
  app mapping, stale/claimed/settled handoff and durable-write failure.
- Pipeline handoff regression included in the 53 above. All six final commands exit 0.
- git diff --check: PASS. TIMEBOX checker saved separately before commit.

## Skills/plugins — Ponytail full applied
Read installed 5.3.3 Ponytail SKILL.md. Reused repository_root, project/project_ledger,
liability_usd/usd, require_reconstruction, existing exclusive lock and atomic/fsynced
write_json. One settlement command and one claim function, not a new budget engine,
dependency, journal schema or provider route. Existing five mains and their tests
remain the integration points. No new abstraction for pricing or automatic finality.
Observed failing settlement tests exposed projection dropping app identity; repaired
the shared projection and verified all suites fresh. Chose explicit reviewed final
evidence over treating lower estimates/lagging hourly bills as permission to release.

## Skips / risks / next action
No live Meta/Modal/AWS, actual billing reconciliation, container-stop verification,
journal bootstrap/reset, new grant claim, installs, deployment, UI or quota polling.
No independent cross-vendor review done here; controller must review/integrate this
successor and arrange R-C acceptance. Canonical state is absent; live paid admission
and physical/product gates remain unverified. Trusted final-billing reviewer and
immutable evidence are required; settled evidence deletion/tamper pauses subsequent work.
Multi-app envelopes fail closed. N3 journal tamper anchoring and N5 independent-clone
coordination remain explicitly unimplemented; no new authority or monthly reset logic.

Communication: silent except mandatory developer runtime/skill/finding updates and
the authorized controller completion callback; no additional worker/schedule/messages.
Callback delivery failed twice with ActiveTurnNotSteerable { turn_kind: Compact };
no controller delivery is confirmed. No further retry/poll loop. Code/evidence commit
fa69667 was created 06:39:29Z, before cutoff/deadline; this note records only delivery.
