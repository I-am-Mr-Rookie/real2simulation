# S16f-orch111 — explicit Fireworks search fallback

Objective: add an explicitly configured Fireworks alternative to the existing
sidebar library.search adapter, with truthful per-call execution provenance and
fail-closed errors. Offline fake transports only; zero inference/spend.

## Contract

- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`;
  controller-supplied association, not independently inspectable.
- CODEX-2; assigned gpt-6.1-sol / medium; OpenCodex-managed; not polled.
- Issued 2026-10-30T08:55:26+00:00; implementation cutoff 09:20:26Z;
  deadline 09:25:26Z / 15:25:26 Dhaka. Stop new implementation at cutoff;
  fully verified DONE may finish early, otherwise use the full window.
- Branch `run/S16f-orch111`, plain Git worktree `.worktrees/S16f-orch111`,
  base main `8fa101a9ce1995a28b96cc7211b1af822a829cfc`; initial status clean.
- Exact Owns: `Build/sidebar-tools/`, `tests/sidebar-tools/`, `evidence/S16/`,
  `Run-System/Runs/S16f-orch111/`. No canonical controls, integration or installs.

## Reach / smallest complete change (Ponytail full)

Reuse library_search.search, bounded stdlib transport, catalogue validation,
validate_call/validate_result and existing spec_sha256 boundaries (no spec edits).
Reach: adapter configuration and logging, additive result-provenance schema,
adapter/contract tests, CONTRACT.md, sanitized offline evidence and this run's
records. Existing Baseten callers retain their pinned default. No UI dispatcher,
new provider framework, retry chain, model alias assumptions or bonus eligibility.
Search is metadata-only: never modify store, physics receipts, rights or gates.

## Acceptance / verification

1. Only explicit provider configuration selects Fireworks; absent config stays
   Baseten; provider failures make exactly one attempt, never auto-switch.
2. Output/evidence distinguishes selected/served/not-requested/failed provider
   and configured model; no inferred Muse/Meta/open-weight bonus claim.
3. Fake transports prove both providers' success/failure, endpoint/model checks,
   no secret leakage and unchanged source cards; full sidebar suite stays green.

Run `python -B -m unittest discover -s tests/sidebar-tools -t tests/sidebar-tools`;
save fresh sanitized evidence, run timebox check and git diff --check, commit only
named owned files. Report skips/risks. Controller alone merges and updates controls.
