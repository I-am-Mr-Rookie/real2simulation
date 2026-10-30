# S16g-orch116 — patch safety and search failure behavior

- CODEX-2, assigned gpt-6.1-sol/medium; OpenCodex-managed; not polled.
- Parent project: 91e441f8-e40c-4ec4-bea2-de7fa1582d97 (controller supplied).
- Issued 2026-10-30T09:11:25+00:00; implementation cutoff 09:36:25Z;
  deadline 09:41:25Z / 15:41:25 Dhaka. Fully verified DONE may finish early.
- Base main d3a1343c98bb17692f15f8047acfd209c68b2ca5; plain Git worktree
  .worktrees/S16g-orch116, branch run/S16g-orch116. Canonical changes preserved.
- Owns: Build/sidebar-tools/; tests/sidebar-tools/; evidence/S16/;
  Run-System/Runs/S16g-orch116/. No canonical control edits or integration.

## Objective / scope

Exercise malformed, oversized, out-of-scope, traversal and stale patches through
validate_call, apply_patch and RebuildSession. Reject before state changes or
execution. Exercise both configured search providers with fake unavailable,
timeout, HTTP, malformed and empty responses; preserve readable safe errors,
one-attempt routing and false bonus receipts.

Read/apply Ponytail full 5.3.3. Reuse existing strict experiment/schema validation,
typed SidebarContractError, serialized session and injected transport. Reach:
contracts.py consumers spec_patch/rebuild/library_search, focused tests and
CONTRACT.md; no config, dependency, export, hosted API or UI addition needed.
Preserve valid hashes and existing typed-error contract. Main risk: raw schema
errors echo untrusted input; oversized calls lack an admission bound.

## Acceptance

1. Focused offline rejection matrix proves no mutation, write or rebuild on bad
   patch; readable bounded errors do not echo fake secret input.
2. Both providers fail safely without retry/switch, raw body/secret leakage,
   numeric outputs or bonus claims; distinguish empty success from unavailable.
3. Full sidebar-tools unittest discovery remains green; save fresh evidence,
   diff checks and checked TIMEBOX.json; commit only named owned files.

No real keys, network requests, inference, spend, installs, deployment or unrelated
physics changes. Controller owns merge and parent gate acceptance.
