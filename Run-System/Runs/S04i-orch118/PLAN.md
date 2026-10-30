# S04i-orch118 — private fixture repository and workspace mount

- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
- Lane/model: CODEX-2; assigned gpt-6.1-sol/high; OpenCodex-managed, not polled.
- Base: main `74427f179e1c6e1d6533283a97903075124e4f4a`; clean isolated branch `run/S04i-orch118`.
- Issued 2026-10-30T09:17:50+00:00; implementation cutoff 09:42:50Z; deadline 09:47:50Z (15:47:50 Dhaka).

## Objective and reach

Connect the existing owner-check policy to a server-only, read-only, per-user
development fixture repository and mount S15's public React workspace interface.
Reach: repository/policy callers, private layout and scene leaf, a signed-in
workspace entry link, focused security/mount tests, auth documentation. Preserve
the public library and all S15 implementation files. No database application
helpers exist: S04f identifies resources, not a usable repository client.

Owns: Build/web/src/app/, auth/, shell/, Build/web/package.json,
tests/web-private/, evidence/S04i/, this run directory. Requested a precise
extension for Build/web/src/proxy.js: Clerk auth() requires its trusted session
context. Controller explicitly granted that exact file; matcher workspace-only,
no provider/config/credential/env changes, bounded library/health/request checks.
No canonical controls,
merge, deploy, credential/config/provider change or dependency install.

## Smallest complete approach / risks

Reuse authorizePrivateScene, Clerk session-token auth, initialState,
createWorkspace(React), existing viewer adapter and CSS. A dev fixture is an
empty private scene container, explicitly FIXTURE/SYNTHETIC, not invented
reconstruction/physics data. Deterministic user-bound IDs; exact ownership reads;
uniform notFound for unavailable, guest, unknown or nonowner. No persistence,
upload, mutations, live workflow services or fake successful artifacts.

## Checks

1. Focused tests: owner/nonowner/guest/unknown/malformed IDs, missing config,
   dependency failures, dev-vs-production scope, public S15 mount and labels.
2. Existing auth/workspace regressions, next build, emitted bundle scan.
3. Production HTTP guest/library denial smoke; real signed-in Clerk browser
   behavior only if supported without credentials/deploy changes, otherwise
   explicitly retain that verification limitation.

Ponytail full read and applied: reuse existing contracts and modules, no new
dependency, no speculative database/asset upload infrastructure. Shared
node_modules junction is build-only and ignored; authored files use absolute
worktree paths. Mandatory initial update/skill notice is a silence exception.
