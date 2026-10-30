# S16b-orch89 — validator-first spec patch

- CODEX-2, assigned gpt-6.1-sol / medium; OpenCodex-managed; not polled.
- Parent project Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`;
  inherited delegation association, no new session launched.
- Issued 2026-10-30T06:21:50+00:00; cutoff 06:46:50Z;
  deadline 06:51:50Z / 12:51:50 Dhaka. Fully verified DONE may finish early.
- Isolated plain git worktree `.worktrees/S16b-orch89`, branch `run/S16b-orch89`,
  main base `1dfc4e2ce76708aa39e998ecc385237c44877a0c`.

## Objective / exact Owns

Implement a local spec.patch application boundary that copies before applying whole
sections, reuses S16a validation and authoritative experiment validate_setup before
returning a rebuild-required handoff. Invalid calls raise typed errors; no rebuild,
persistence, provider, spend, or canonical-control writes. S16c owns rebuild execution.

Owns only `Build/sidebar-tools/`, `tests/sidebar-tools/`, `evidence/S16/`,
`Run-System/Runs/S16b-orch89/`. Controller integrates, no worker merge.

## Reach / risks / smallest complete choice

Existing callers searched: only S16a contract tests, no runtime patch dispatcher.
Add one application module, tests reusing synthetic S08 fixtures, contract usage docs,
and local evidence. No UI/config/exports or dependencies need changing. Keep
whole-section semantics and current digest/scene binding, no recursive patch engine.
Never mutate base/call/scene or let invalid input reach a downstream rebuild caller.
Passing checks proves synthetic preflight only, not real scene rights or runtime.

## Acceptance

1. Valid patches across four templates produce a defensive contract-valid result.
2. Invalid numeric/domain/geometry/scene/stale/identity input raises SidebarContractError
   before any downstream rebuild handoff; inputs unchanged on success and failure.
3. Fresh sidebar and relevant spec suites, diff check, timing checker, named-file commit.

Ponytail full 5.3.3 read/applied: reuse existing validators, digest, schema and fixtures;
no new patch language, callback dispatcher, persistence, provider or test dependency.
