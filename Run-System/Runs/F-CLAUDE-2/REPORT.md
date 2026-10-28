# F-CLAUDE-2 REPORT — Review owned-module test coverage gaps

- Status: **DONE** (acceptance: read only finished CLAUDE modules; concrete missing-case checklist; no implementation/other-lane edits)
- Lane/model: CLAUDE; requested Opus 5.5 medium; actual = orchestrator-delegated Claude-agent session in Codex desktop, exact model/effort not exposed.
- UTC (host clock): start 2026-10-27T19:52:47Z; verification end ~19:55Z. Start commit 489c1be; merged 24e5814 (ff, main had not moved).

## Objective
Map existing viewer tests and independently probe F-CLAUDE-1 high-risk claims (reproduced/refuted/unverified).

## Changes (Owns only: evidence/fillers/CLAUDE/2/)
- [COVERAGE.md](../../../evidence/fillers/CLAUDE/2/COVERAGE.md): per-file test map, verdict table, 10 missing tests.
- [probes.mjs](../../../evidence/fillers/CLAUDE/2/probes.mjs): read-only probe script (imports main-checkout product code; fake DOM/GL).
- No product, test or other-lane file changed (`git diff --quiet main -- Build tests` → 0 before merge).

## Commands and results
- `node --test tests/viewer/{viewer,three-renderer,artifact-loader,scene-overlays,render-budget}.test.mjs` (main) → 42/42 pass, exit 0.
- `node evidence/fillers/CLAUDE/2/probes.mjs .` (main, pre- and post-merge) → outputs quoted in COVERAGE.md.

## Key findings
- Reproduced: invalid bounds/collider/up → RENDER_FAILED; label without anchor throws every frame; missing label text → "undefined"; outlier point ignored by overlayAlignment; empty IO entries throw; two mounts reset host position; loader sends creds URL and POST; non-numeric Content-Length wrong message; throwing onError leaks plain Error; no signal → TypeError; context-loss and mobile LOD absent (static; mobile LOD is a documented README limit).
- Refuted: camera convention (contract fixes -Z forward, viewer test asserts it; risk is S05 adapter side). Play-while-paused does not jump ahead — it stalls by the pause→play gap (measured). Null label entry → INVALID_ARTIFACT, not "undefined".

## Limits
- Fake DOM/GL only; no browser/device. Stylesheet-position, resize fallback, multi-touch, reduced-motion, banner clip, several P3 items unverified. Not gate evidence.

## Skills/tools
- Superpowers verification-before-completion read and applied (fresh suite run and probe reruns before claims). TDD/debugging not applicable (no implementation). No other plugin needed.

## Communication compliance
- Silent workflow; no owner questions; one-line completion signal.

## Next
- S09h (CLAUDE): add COVERAGE.md §3 tests alongside F-CLAUDE-1 P1 fixes.

