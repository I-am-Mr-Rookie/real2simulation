# S09a report — DONE

- Objective: viewer adapter + synthetic fixture scene. Lane CLAUDE; planned Opus 5.5 / medium.
  Actual: orchestrator-delegated Claude-agent session in Codex desktop; exact model ID/effort not exposed (not verified).
- UTC start 2026-10-27T18:11:53Z; verification end 18:17:20Z. Merged SHA b4af6e8cd97493cf5058433e95689065846e776f (ff, after rebase on 492f66f).

## Changes
- Build/web/src/viewer/adapter.mjs — createViewerAdapter({createRenderer}).mount(host, request, services) per S04a; DTO check mirrors integration.schema viewer def; states loading/ready/error/unavailable; abort/dispose lifecycle.
- Build/web/src/viewer/scene-model.mjs — bundle → frozen model; re-checks id/version/synthetic label, byte length, SHA-256; strict PLY xyz+rgb decode; physicsEnabled/gateEvidence always false.
- Build/web/src/viewer/fixture.mjs — SYNTHETIC_FIXTURE (S04a mount → S05a room-v1, no copy) + SYNTHETIC_BANNER.
- Build/web/src/viewer/common.mjs, README.md (contract details, limits, dep request).
- tests/viewer/viewer.test.mjs (11 tests), tests/viewer/fixture-bundle.mjs (Node loader; runs S05a validator).
- evidence/S09/S09a.md.

## Commands and results
- RED: node --test tests/viewer/viewer.test.mjs → ERR_MODULE_NOT_FOUND (before implementation).
- GREEN: same → 11/11 pass (worktree, after rebase, on main).
- python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json → PASS (not Gate R evidence).
- python Build/web/src/shell/test_contract.py → OK.
- Mutations (removed SHA check; removed dispose guard) → 1 and 2 failures; restored.

## Decisions (routine, logged here)
- Framework-free .mjs, no package.json: S04a assigns manifest to CODEX-2.
- Mystery mode → UNAVAILABLE without loading until S10 redacted payload.
- Only points render kind; mesh/splats → UNSUPPORTED. Viewer-specific error codes (INVALID_REQUEST, LOAD_FAILED, INVALID_ARTIFACT, UNSUPPORTED, RENDER_FAILED, UNAVAILABLE); upstream messages never forwarded.

## Limits
- No renderer/canvas/camera/browser/WebGL test; no GPU leak measurement. Fixture is synthetic: not reconstruction, physics or Gate R evidence. No app route serves it.

## Next
- S09b (CLAUDE Opus 5.5 medium): render fixture geometry + orbit camera. Needs a 3D library in Build/web/package.json from CODEX-2 (S04 owner) — request, not edit.

## Skills/plugins
- Superpowers test-driven-development (read SKILL.md): failing run observed before code, then green, plus mutation checks.
- Ponytail (principle via SKILLS_AND_PLUGINS.md): smallest change, trust-boundary checks kept; not separately invoked.
- verification-before-completion: checks rerun after rebase and on main. No plugins/MCP needed (offline task).

## Cost / quota
- Tokens: unavailable. Claude quota: unavailable. Meta/service/GPU $0. Owner questions: 0.
