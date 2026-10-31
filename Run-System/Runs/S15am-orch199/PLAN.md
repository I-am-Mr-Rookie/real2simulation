# S15am-orch199 PLAN

- Issued 2026-10-31T09:29:38Z; deadline 09:59:38Z; cutoff 09:54:38Z. Lane CLAUDE, anthropic/claude-opus-5-5/high (OpenCodex-managed, not polled).
- Objective: six COLOR_MODES in the existing theme layer + compact theme menu; workspace redlines (full-bleed, B2 dropzone keeping #ws-upload-file, B1 empty viewport, tinted notices, single-line title, stepper pills, B5/B6); per-mode shadow levels.
- Owns: Build/web/src/workspace/ (not controller.mjs/workflow.mjs), Build/web/src/shell/, Build/web/src/app/(private)/, tests/workspace/, tests/shell-workspace/, evidence/S15am/, this run dir.
- Checks: node --test 4 suites; npm run build; local screenshots 6 modes @1280 + dark/light @375.
- No deploy (controller merges S15ai + S15am and redeploys).
