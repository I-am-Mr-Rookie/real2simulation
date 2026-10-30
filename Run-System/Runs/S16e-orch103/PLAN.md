# S16e-orch103 — Verify real dev search inference

- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`, as supplied by controller; launcher association not independently observable here.
- Controller: `01a1882d-3481-7ce3-8f88-45c942e341cd`.
- Assigned route: gpt-6.1-sol / medium, CODEX-2, step S16. OpenCodex-managed; not polled.
- Isolated worktree: `.worktrees/S16e-orch103`; branch `run/S16e-orch103`; base `020f00552847471a49d678f3353f97b7fc467846`.
- Issued: 2026-10-30T07:10:08+00:00. Implementation cutoff: 07:35:08Z. Deadline: 07:40:08Z / 13:40:08 Dhaka.

## Objective / acceptance

Verify credited Baseten balance read-only in the signed-in ChatGPT in-app browser before any inference. Only if confirmed, use the merged adapter with exact model `meta-models/muse-spark-open-1026` for a real request and verify ranked IDs resolve to validated library cards; retain sanitized latency, usage and cost. At most three requests; no model substitution, credential disclosure or auth/billing/terms changes.

## Owns / smallest complete choice

Only `Build/sidebar-tools/`, `tests/sidebar-tools/`, `evidence/S16/`, and `Run-System/Runs/S16e-orch103/` in this worktree. Canonical controls are controller-owned. Reuse the merged adapter, catalogue validator and existing offline tests; do not add a provider SDK, duplicate adapter, loader or deployment. Product code, callers, fixtures, config and exports need no change when spend is blocked.

## Observed blocker / revised scope

The app redirected to Baseten's sign-in page, not billing. Credited balance is unobservable. Sent one nonterminal blocker to controller, with zero inference calls. Controller then explicitly approved resource_stop and prohibited sign-in/inference. Finish the existing offline sidebar check, write sanitized evidence/report/timing, commit named files, and stop under that exception.

Receipt: canonical `Run-System/Runs/ORCH-20261029-1654/EXCEPTION-S16e-orch103.md`; approval also received directly in this chat.
