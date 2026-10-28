# F-CODEX-1-2 — DONE (evidence-only coverage review)

Objective, Owns and claim: [PLAN.md](PLAN.md). Deliverable: [CHECKLIST.md](CHECKLIST.md). Prior prose is linked, not duplicated.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python -B evidence/fillers/CODEX-1/2/review.py`: exit0; 17 independent observations; 91 spec tests and 11 scene tests pass, zero skips/errors/failures. Logs: [spec](tests-spec.txt), [scene](contracts-scene.txt); method inventory/source SHA256/in-process line map: [results.json](results.json).
- P1/P2 independently reproduced with expanded signed-integer and coordinate-spacing controls. P3/P4 retained as integration limits, not product failures. None of the prior four findings refuted. Coverage gaps and unverified domains are separated in checklist.
- Only assigned evidence files authored. Existing tests use temporary directories under Owns; no bytecode writes. No product/test/other-lane edit, gate result, live service call, deployment, private data, or publication.
- Rebased onto S04g1 completion02962da; full review command repeated exit0 (17 observations,91+11 tests). `git diff --exit-code main -- Build contracts tests test-data` and `git diff --check` exit0. Logs refreshed from this post-rebase run; initial receipts remain in original evidence commit2f4df45.

## Skills/plugins applied

- Installed `verification-before-completion`: fresh executable observations, full existing-suite receipts, explicit limits before completion.
- Installed Ponytail5.3.2 `ponytail-review`: read connected owned validators/templates, fixtures, tests and contract docs; source-linked missing cases, smallest follow-up checks; distinguish documented limits from bugs. Assumed load: local offline caller; performance not measured.
- Installed Superpowers7.0.1 `using-git-worktrees`: isolation detection, ignored-directory check and explicit repository-selected run branch/path; higher-priority manual lifecycle overrides native default placement. No dependency install required; existing jsonschema used. `coverage` import unavailable; used stdlib tracing rather than install.
- Repository skill/plugin checklist applied. Thread coordination tool used only for necessary authorized serialization with controller. Browser/native, design, GitHub, Railway, inference plugins skipped: unrelated to read-only local coverage scope. No skill/plugin installed or enabled.

## Lifecycle, routing and communication

- Claim UTC2026-10-27T20:52:25Z; b563519 on main after S04g1 d6e22f8 and controller-granted exclusive lock; clean shared/index state verified. Canonical lock released promptly; all review work isolated on run/F-CODEX-1-2.
- Read current canonical AGENTS, README/owner checklist, plan context, run/skill protocol, queue/state/decisions/budget/rubric and last three report receipts. No historical memory used.
- Requested CODEX-1 GPT-6.1 Sol medium; actual delegated Codex exact model/effort/tokens/coding cost unavailable. OpenCodex-managed; not polled. New Meta/inference/GPU calls0; no new task-attributable API spend; historical balances and existing infrastructure charges not measured.
- Communication: mandatory higher-priority brief pre-tool update and skill announcement only; authorized controller messages for claim/final serialization; no optional narration or duplicated report. No owner question; fallback unchanged.
- Next: separately authorize CODEX-1 P1/P2 regression/fix work. No product changes authorized by this review.
- Final main verification UTC2026-10-27T20:58:20Z: full command exit0 again (17 observations;91 spec in29.508s,11 scene in5.133s). Verified FF2ac94ff after controller-granted final window; current raw logs are main receipts. Product/contracts/tests/test-data unchanged from02962da. Clean explicit run worktree removed; branch retained. Final shared controls serialized under this worker's lock; evidence/report remain only in assigned Owns (no duplicate Run-System report). No owner question. End/control finalization UTC20:59Z; under15m from claim.
