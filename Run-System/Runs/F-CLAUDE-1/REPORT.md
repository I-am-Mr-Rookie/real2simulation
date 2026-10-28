# F-CLAUDE-1 REPORT — Document owned-module edge cases

- Status: **DONE** (acceptance: read only finished CLAUDE-owned modules; concrete missing-case checklist; no implementation or other-lane edits)
- Lane/model: CLAUDE; requested Opus 5.5 medium; actual = orchestrator-delegated Claude-agent session in Codex desktop, exact model/effort not exposed.
- UTC (host clock): start 2026-10-27T19:46:51Z; end ~19:51Z. Merged SHA 8cb81e7 (ff from 8722a99; main had not moved).

## Objective
Missing-case checklist for finished CLAUDE viewer modules S09a–S09g.

## Changes (Owns only: evidence/fillers/CLAUDE/1/)
- [CHECKLIST.md](../../../evidence/fillers/CLAUDE/1/CHECKLIST.md): 9 P1, 13 P2, 6 P3 items with file:line, impact, needed fix/test; process note.
- No product, test or other-lane file changed.

## Commands and results
- `node --test tests/viewer/{viewer,three-renderer,artifact-loader,scene-overlays,render-budget}.test.mjs` (main checkout) → 42/42 PASS.
- Same in fresh worktree → three-renderer.test.mjs ERR_MODULE_NOT_FOUND (`Build/web/node_modules/three` not installed in worktrees); recorded as process note.
- Read-only node probes: `decodePlyXyzRgb` accepts `1e39` → Float32 `Infinity`, and `0x10`/`1e2`/`255.0` tokens [verified]; `overlayAlignment` with `labels:[null]` does not throw (records issue only).
- `git diff --quiet main -- Build/web/src/viewer tests/viewer` → identical (checklist reflects main 8722a99).

## Key findings
- Highest risk for S09h: PLY float32 overflow, camera-pose convention for real S05 paths, points vs bounds_m unchecked, manifest geometry errors surfacing as RENDER_FAILED, label crash/"undefined" text.
- Structural bottleneck: reduced tier still fetches/decodes full asset (whole-file string split) before decimating; mobile LOD unused.

## Limits
- Most items are code-reading findings [R], not executed. No browser or device run. Not gate evidence.

## Skills/tools
- Superpowers verification-before-completion read and applied (fresh suite run, probes before claims). TDD/debugging skills not applicable (no implementation). No other plugin needed.

## Communication compliance
- Silent workflow; no owner questions (none needed); one-line completion signal.

## Next
- S09h (CLAUDE) should take the P1 list; confirm camera convention/scale in contracts/scene with S05 owner. F-CLAUDE-2 (test coverage gaps) can reuse this list.
