# S16e-orch108

- Objective: one real dev invocation of the merged library-search adapter, pinned to `meta-models/muse-spark-open-1026`, returning ranked validated library cards.
- Owns: `Build/sidebar-tools/`, `tests/sidebar-tools/`, `evidence/S16/`, this run directory only. No canonical controls or deployment.
- Branch `run/S16e-orch108`; plain isolated worktree from main `3b07b4eefe12b3f1543ce74f05512c738c39ee2b`.
- CODEX-2; assigned gpt-6.1-sol/medium; OpenCodex-managed, not polled. Parent project `91e441f8-e40c-4ec4-bea2-de7fa1582d97` supplied by controller; launcher association not independently inspectable.
- Issued 2026-10-30T07:28:55+00:00; cutoff 07:53:55Z; deadline 07:58:55Z / 13:58:55 Dhaka. Fully verified DONE may finish early; otherwise controller exception or original deadline required.
- Acceptance: actual request through existing adapter, usable source-owned cards with measured latency/response token usage, sanitized cost/balance evidence; required sidebar tests pass; timebox validator passes; named-file commit.
- Budget: owner Q17 confirms organizer-issued $100 restricted credit; remaining balance unobservable. At most three requests authorized, initially ONE bounded request, adapter max_tokens 2048, no retries/redirects/substitution. No Baseten browser/login/billing access.
- Ponytail full: reuse existing adapter, transport and catalogue validation, no production changes unless real evidence requires them. Add only a one-shot stdlib probe and sanitized records; no SDK, server, UI, fixture expansion, provider changes or dependency installs. Affected surface: run probe and evidence; existing callers, exports, configuration and fixtures remain unchanged.
- Secret boundary: only three required environment fields loaded in-process from canonical `.env`; never persist or print credential/config values. Provider content and exceptions never logged. Use assertions for probe safety and existing suite for adapter behavior.
