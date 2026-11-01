# S15bg-orch244 REPORT
Status: DONE. Lane CLAUDE, anthropic/claude-sonnet-5-5/medium (OpenCodex-managed; not polled). UTC 2026-11-01T08:12:38 to 2026-11-01T08:22:31+00:00. Tokens/cost: unobservable.

## Change
- Build/web/src/shell/PrivateWorkspace.mjs: exported `workspaceHeading(api, scene)`; h1 uses it. Fixture note not rendered while api = checking. Root cause: first paint used scene.title (fixture) until probe resolved.
- Tests: tests/shell-workspace/private-workspace.test.mjs (new heading rule test; source-match updated), shell-toggle.test.mjs (first-paint SSR is neutral).
- Evidence: evidence/S15bg/probe-announce.mjs, result-live.json, result-unavailable.json, live.png, unavailable.png.

## Checks (fresh)
- node --test tests/shell-workspace/*.test.mjs: 31 pass, 0 fail.
- npm run build (Build/web, canonical node_modules via junction, not committed): green.
- Headless Playwright Chromium, real PrivateWorkspace module from the tree, health delayed 2.5 s. Live: before probe h1 "Workspace", after "Private workspace", no fixture wording anywhere in body, all [role=status]/[aria-live] nodes fixture-free, no [role=alert] nodes. Unavailable: before "Workspace", after fixture title (genuine fixture disclosure kept). document.title "Real2Simulation" throughout.

## Ponytail
Reused existing probe/api state; one 1-line pure helper, no new state/props/deps. dev-scenes.mjs left as is (needed for fixture mode). Shortcut: harness is not the deployed Next app.

## Skipped / risks
- Not run against the deployed Railway/Clerk app or a local signed-in build: no Clerk keys locally, no deploy allowed. Harness has no Next route announcer; the announcer reads h1/document.title, both verified. Deployed dev still has the old behaviour until redeployed. No pre-fix baseline captured in browser (R-D/S22i record the old alert).
- Communication: silent; no em dashes in UI text added.
