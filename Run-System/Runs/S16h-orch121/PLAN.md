# S16h-orch121 — checkpoint open-weight evidence and fallback claims

- Objective: source-linked evidence checkpoint; explicitly refuse an unimplemented Meta Spark fallback after open-provider failure, with no implicit route or bonus claim.
- Lane/model: CODEX-2, assigned gpt-6.1-sol / medium; OpenCodex-managed; not polled.
- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`, supplied by controller; launcher association not independently inspectable.
- Canonical root: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
- Worktree: `.worktrees/S16h-orch121`, branch `run/S16h-orch121`, initial clean main `c72f455b50bac0ef8fc284a86c2feb350529b1f1`.
- Issued: 2026-10-30T09:28:24+00:00. Implementation cutoff: 09:53:24Z. Deadline: 09:58:24Z / 15:58:24 Dhaka. Verified fully DONE may finish early.
- Owns only: `Build/sidebar-tools/`, `tests/sidebar-tools/`, `evidence/S16/`, `Run-System/Runs/S16h-orch121/`. No canonical controls or integration.
- Scope map: shared `library_search.search`, existing Fireworks tests, provider contract, checkpoint JSON/Markdown and run receipts. Existing contract receipt stays unchanged; no callers, exports, fixtures or global configuration require changes for a refusal.
- Reuse: existing unavailable result and validation, fake transports, pinned Baseten/live receipt, Fireworks/offline receipt and S16g safety log. No new adapter, retry chain, dependency, live request or secret access.
- Acceptance: historical measured/offline/unverified claims have file/JSON pointers; both-open-failure never silently selects a third provider; explicit `meta` config safely refuses and drops claims; existing 100 tests plus focused regression tests green; TIMEBOX validates and only named owned files committed.
- Risks: refusal is not a working Meta Spark adapter, Fireworks live availability is unverified, Baseten cost/balance are unknown, no deployed-web/bonus eligibility claim.
