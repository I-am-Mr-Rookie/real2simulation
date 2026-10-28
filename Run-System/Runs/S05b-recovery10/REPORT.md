# S05b-recovery10 — DONE (local F3 repair only)

Local absolute-clock and result-preservation criteria complete; parent S05b stays
PARTIAL, NOT paid-ready. No reconstruction, live stop or physical result claimed.

## Scope / identity

Direct owner authorized this existing chat as sole serial worker until2026-10-28
16:30Z=22:30BDT; no new chat/subagent/schedule/dispatcher. Requested CODEX-1 managed
Sol/medium; exact runtime/effort/tokens/subscription cost not independently exposed.
OpenCodex-managed; not polled. Existing project/root inherited, no launcher binding
claimed. Start15:54:01Z; scoped issue15:56:13Z, cutoff16:21:13Z, deadline16:26:13Z.
Branch run/S05b-recovery10 from f977804; canonical claim e35a4da. Owner's removal
of R2 in RUNS preserved in STATE as historical, not regenerated as an open review.

## Changes / acceptance

- Existing parent supervisor now passes its absolute monotonic child deadline.
  Guard uses the earlier absolute/relative end; exhausted admission fails BEFORE
  app setup. Runner reserves existing10s exit margin; production resource/timeout,
  revision, retry and input limits unchanged. Receipts record actual clock bounds.
- New23-line stdlib result helper verifies length/hash, atomically renames payload,
  then atomically writes a PENDING marker. Callback runs before remote cleanup.
  Only successful guarded cleanup permits atomic CONFIRMED final metadata.
  Saved payload never overrides parent kill/nonzero or failed cleanup.
- Tests exercise preflight elapsed time, invalid/exhausted/too-distant deadlines,
  persistence failures with mandatory stop, integrity failures, pending-marker
  failure, actual runner main body with fake provider, and actual production
  guard/helper/supervisor with a subprocess stuck in cleanup. Real provider module
  never imported; synthetic bytes are explicitly not a real NPZ/model result.
- Prior57-test default suite passed; target3.11 exposed an existing assertion
  assuming expiry always happens before CLI launch. It may validly occur DURING
  bounded subprocess wait. Test now accepts those two timeout classes while still
  requiring incident/failed independent confirmation/original elapsed bound.
  Production behavior unchanged. Integrated child initially had only0.5s for cold
  imports and failed once; isolated diagnostic passed. Test alone now reserves2s
  startup work rather than mistaking import scheduling for product failure.

## Fresh checks

Evidence: evidence/S05/S05b/recovery10/. Red deadline24 tests/errors5 saved, then
green24/24 and result4/4. Complete updated suites58/58 PASS on Python3.14.5 and
3.11.15, each under100s parent cap (verified-checks.json/full logs). Two subsequent
actual-main tests pass in runner suite7/7. Scene11/11 PASS with30s cap. Initial
failures and superseding results retained, not overwritten. Source SHA256s and
gate/spend distinctions recorded in audit.json. Final rebased/main60-test checks
and timing/integration receipt will be recorded below before canonical acceptance.

### Integration / closeout

Rebased complete spike60/60 PASS on BOTH3.14.5 and3.11.15, logs/commands in
rebased-checks.json (100s parent caps). Verified FF c43e500 into canonical main.
Initial raw-byte cross-checkout hash comparison rejected two new files because
main checked them out with CRLF. No test was claimed from that failed command.
Corrected audit checks normalized contents against the tested worktree plus
`git diff --quiet c43e500 -- Build/reconstruction/spike` (PASS), then fresh main
actual runner7/7 and scene11/11 PASS under30s caps. main-source-audit.json records
exact raw differences and normalized hashes. Product operations stopped16:07:42Z;
closure/control bookkeeping afterward. TIMEBOX checker must pass before closeout.
All local child criteria met early; parent progress remains55/203 and PARTIAL.

## Ponytail / limitations

Applied installed Ponytail full/default: reused atomic_json, existing async/CLI
seams, Fake APIs and AST isolation; stdlib only, no dependency/provider framework.
Small shared callback replaces duplicate return paths. Tests exceed production
diff because this is bounded-compute and data-preservation safety code.
Skipped all Modal imports/real CLI/network/browser/jobs/downloads/install/uploads,
credential/account/policy changes, remote publication and speculative calibration
work. No new paid reservation; existing$2.85/$30 retained, exact billing unknown.

Atomicity is per-file, not fsync/crash durability or a multi-file transaction.
Unfinished writes may leave ignored temporary bytes. Noncooperative disk/OS stalls,
parent death, unreceived results and lost-ID F4 still require operator incident
reconciliation. Provider/auth/CLI semantics/headroom/no-paid-overage and independent
review remain unverified. No paid-readiness release; all physical/S12 holds remain.

Communication: mandatory initial update, skill announcement and changed-finding
update only; no delegation, optional repeated status or duplicated chat report.
