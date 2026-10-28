# S09c REPORT — Load real point-cloud or splat artifacts

- Status: **DONE** (acceptance: loader validates inputs; real artifact integration still waits for S05)
- Lane/model: CLAUDE; requested Opus 5.5 medium; actual = orchestrator-delegated Claude-agent session in Codex desktop, exact model/effort not exposed.
- UTC: start 2026-10-27T18:55:06Z, verification end 18:59:34Z (host clock). Merged SHA 524fd93 (ff after rebase on 4f24bf4).

## Objective
Real-bundle loadScene for the viewer that validates inputs fail-closed, plus splat support; no real artifacts (S05 pending).

## Changes (Owns: Build/web/src/viewer/, tests/viewer/, evidence/S09/)
- Build/web/src/viewer/artifact-loader.mjs (new): createArtifactLoader → loadScene(sceneRef, signal); checkManifest; readCapped.
  Path allowlist + root confinement, kind↔format, size/point caps, redirect 'error', Content-Length precheck + streamed cap, exact length + SHA-256.
- scene-model.mjs: strict decodeSplats (32-byte LE records); splats modelled as render.kind 'points' + sourceKind 'splats' + splat {scales, opacity, rotations}.
- adapter.mjs: viewer-authored loader ViewerErrors (LOAD_FAILED/INVALID_ARTIFACT/UNSUPPORTED) pass through; others stay LOAD_FAILED.
- tests/viewer/artifact-loader.test.mjs (7 tests); viewer README; evidence/S09/S09c.md.

## Commands and results
- node --test tests/viewer/viewer.test.mjs tests/viewer/three-renderer.test.mjs tests/viewer/artifact-loader.test.mjs → 24/24 pass, fail 0 (worktree, after rebase, on main).
- 8 mutations (loader SHA, path allowlist, Content-Length cap, point limit, redirect, splat quaternion, splat scale, adapter passthrough) → each fail 1; restored, diff clean.
- node tests/viewer/browser-smoke.mjs → exit 0, ok=true (before and after rebase).
- python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json → PASS.

## Limits
- Synthetic data only (fixture over fake fetch; generated splats). Not reconstruction, measured/simulated, or Gate R evidence.
- No real HTTP server/CORS test; splats drawn as centre points (no Gaussian rasteriser, no browser splat smoke); GLB → UNSUPPORTED; mobile LOD not fetched.
- Duplicate JSON keys not detected client-side (Python validator does). Size/point limits are defaults, not measured budgets.
- Tests written alongside code (not strict TDD red); compensated with mutation checks. node_modules junction used in worktree (ignored, removed; target intact).

## Skills/plugins
- Read Superpowers verification-before-completion SKILL.md; applied gate: fresh full commands, read pass/fail counts and exit codes before claims.
- Not used: test-driven-development (no strict red), Playwright MCP (existing CDP smoke sufficed), web/MCP tools (offline task).

## Cost / quota
Tokens unavailable; Claude quota unavailable; Meta/service/GPU $0. Owner questions: 0. No D1/D2 decisions.

## Next
S09d CLAUDE Opus 5.5 medium (colliders, camera path, labels). Real artifact wiring after S05.
