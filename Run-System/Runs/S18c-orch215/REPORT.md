# S18c-orch215 PARTIAL (projectile verified on main; bounce UNAVAILABLE)

Lane CODEX-2 run by anthropic/claude-sonnet-5-5 medium; OpenCodex-managed, not polled; tokens/cost unknown, spend $0. Window 14:07:51Z to 14:37:51Z. Worktree .worktrees/S18c-orch215, branch run/S18c-orch215 from main 10510171. Only Owns paths written.

## Result
- Projectile: four SIMULATED demos (S18c-orch94) already on main; rebuilt with `python -B -m Build.library.projectile`, appear in guest manifest (evidence/S18/S18c-orch215/guest-check.txt: 4 simulated-projectile entries). Reused as is; no rework.
- Bounce: not built. Build/simulator has no bounce output: contacts.mjs detects first sphere-floor touch only, restitution is an input, positions stay RK4. A post-bounce path = new physics outside Owns, and would be an authored number. Manifest still lists bounce UNAVAILABLE; note updated in test-data/library-artifacts/bounce-UNAVAILABLE.md.
- Held-out comparisons/uncertainty with original clip IDs: not met. Projectile metrics are simulated analytic comparisons; no real clip, no invented held-out result. SIMULATED/SCALE_UNVERIFIED labels unchanged.
- Snapshot: Build/web/library-snapshot is generated at staging (infra stage.py), not tracked; guest projection verified live instead. Not deployed.

## Fresh checks
- tests/library: 85/85 OK (evidence/S18/S18c-orch215/library-tests.txt).
- node --test over 33 files in tests/workspace, shell-workspace, web-private, web-workspace-api, pwa, web-library: 225/225 pass.
- npm run build in Build/web: success.
- Used an untracked junction Build/web/node_modules to the canonical install; not committed.

## Ponytail / skips / risks
Reused S18b builder, projectile.py and guest projection; wrote no code. Skipped bounce physics, GPU/paid calls, deploy, snapshot regeneration. Risk: bounce remains absent from /library; needs an accepted bounce simulation or clip run first.
Communication: silent; one completion line.

