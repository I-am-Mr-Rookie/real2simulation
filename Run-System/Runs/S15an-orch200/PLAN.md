# S15an-orch200 PLAN

- Task: QUEUE S15an (workspace/chrome design fixes a-g from controller DEV walk 10:00Z, evidence/S15/s15o/controller/35-42).
- Lane/model: CLAUDE, anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
- Window: issued 2026-10-31T10:05:38Z, cutoff 10:30:38Z, deadline 10:35:38Z. Worktree .worktrees/S15an-orch200, branch run/S15an-orch200 from main 09cf0fcc.
- Owns: Build/web/src/shell/; Build/web/src/workspace/ (not controller.mjs/workflow.mjs); Build/web/src/app/(private)/; app/SiteFrame.jsx; app/ThemeToggle.jsx; app/styles.css; tests/workspace/; tests/shell-workspace/; evidence/S15an/; this folder.
- Approach (smallest complete): fix (a) by widening the existing S15am :has() selector; (b) move the existing S15am swatch menu into the existing global ThemeToggle, delete the workspace copy; (c) one z-index rule; (d) cancel the marketing h1 max-width; (e) render-only changes in view.mjs + CSS; (f) phase-scoped CSS on the existing data-phase; (g) native <details> chip. No new deps/state.
- Checks: 4 node test globs, npm run build, static SSR screenshots dark/paper/contrast at 1280 + 375, contrast.py.
