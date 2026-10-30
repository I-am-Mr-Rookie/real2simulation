# S16b-orch89 — DONE (validator-first patch tool only)

- CODEX-2; assigned gpt-6.1-sol / medium. OpenCodex-managed; not polled.
- Parent project Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`;
  inherited controller delegation association, no launcher/new worker used.
- Issued 2026-10-30T06:21:50+00:00; substantive work stopped 06:29:37Z;
  reported 2026-10-30T06:30:28+00:00. Cutoff 06:46:50Z; deadline 06:51:50Z / 12:51:50 Dhaka.
  Fully verified DONE early; no padded work or incomplete early terminal report.
- Plain isolated worktree `.worktrees/S16b-orch89`; branch `run/S16b-orch89`;
  base `1dfc4e2ce76708aa39e998ecc385237c44877a0c`.
  Controller integrates. No main merge, canonical controls or unrelated files touched.

## Delivered

- `Build/sidebar-tools/spec_patch.py`: `apply_patch(call, *, base_spec, scene, scene_root)`.
  Reuses S16a call validation, applies complete sections to a deep copy, requires
  authoritative experiment `validate_setup`, constructs and validates the correlated
  spec.patch result with digest and `rebuild_required: true`. Invalid calls/preflight
  raise existing typed SidebarContractError; original preflight cause is retained.
  Caller inputs untouched; no numeric tool receipts invented.
- `Build/sidebar-tools/CONTRACT.md`: signature, usage, validation order, typed errors,
  caller trust boundary and exact handoff-versus-execution distinction.
- `tests/sidebar-tools/test_spec_patch.py`: 15 focused offline test methods.
- `evidence/S16/S16b-orch89-{VERIFY.md,sidebar.txt}`: verification scope/raw sidebar log.
- This run's PLAN/TIMEBOX/REPORT. Stage only named files, no caches.

## Fresh checks

- Exact requested sidebar discovery: **38 tests passed**, 4.638s (exit 0).
- Existing spec discovery: **93 tests passed**, 50.632s (exit 0).
- Total **131 passed**, all synthetic/offline; details in VERIFY.md.
- `git diff --check`: exit 0. Timing check and staged diff/commit inspection are
  finalization commands after this report; their receipts remain in worker output.

## Ponytail full — concrete application

Read installed 5.3.3 SKILL.md. Searched existing patch callers before editing:
only S16a contract tests existed, no runtime dispatcher/UI caller to change.
Reused existing contract validate_call/validate_result/spec_sha256, existing
experiment validate_setup (which itself runs validate), and S08 synthetic setup
fixtures. Kept whole-section semantics and existing SidebarContractError instead
of adding a patch engine, new exception hierarchy, schema, dependency or dispatcher.
One small application module; no abstraction/callback configuration added.
Tests cover the trust boundary and both numeric-only and authoritative-bundle failures.

## Skips / risks / next

- No actual persistence or rebuild dispatch: S16c owns that plumbing. This function
  returns a validated handoff only; both rejected and accepted patches start zero jobs.
  A future consumer must serialize persistence/admission and recheck current digest,
  with budget/auth/resource gates. Trusted snapshots are caller-owned prerequisites.
- No model/provider/network/GPU calls, spend, installs, secrets, UI, deployment,
  publication, source acquisition, legal acceptance or new sessions.
- No physical/calibrated/runtime/rights-proof claim from synthetic preflight.
  Parent S16 and all other gate/readiness state unchanged.
- Observable tokens/cost unknown; no paid calls made.
- Next: controller reviews this branch/commit and integrates; S16c consumes handoff.

Communication compliance: one mandatory developer skill announcement; otherwise
silent. Final authorized controller pointer only. Higher-priority Ponytail final
skip/risk disclosure is a minimal mandatory exception to one-line worker chat output.
