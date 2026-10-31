# S15ab-orch188 REPORT — DONE

- Lane/model: CLAUDE, anthropic/claude-opus-5-5/high (as assigned). Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No Meta/GPU call.
- UTC: issued 2026-10-31T06:03:39Z, work 06:03:57Z–06:17Z (deadline 06:33:39Z). Branch run/S15ab-orch188, based on main 190efaf8 (rebase: up to date).
- Commits: f90de52d (shell + tests + PLAN), 7dac30d9 (CSS fix + evidence), plus this REPORT/TIMEBOX commit.

## What changed (Owns only)
- NEW Build/web/src/shell/workspace-shell.mjs: pure `renderShell(h, ...)`, `toolsOf`, `shellKey`, `initialLeft`.
  - LEFT aside #r2s-left: "Go to" (Private workspace, Demo library, Local simulation lab = existing routes) + "This project" (Scene viewport / Stage panel / Job status anchors). Collapses to a 3.25rem icon rail; labels stay in the DOM (visually hidden) so links keep accessible names; `title` tooltips.
  - Header: left toggle (aria-controls/aria-expanded, Ctrl/Cmd+B, `aria-keyshortcuts`), h1 scene title, RIGHTMOST "Agent & tools" button (Ctrl/Cmd+J, aria-expanded/aria-controls).
  - RIGHT aside #r2s-right (aria-labelledby heading, `hidden` when closed): Tools = Agent (interview/job phase label), Clips (upload status -> focuses #ws-upload-file), Runs & history (job id + phase -> #ws-job), Report (available / not yet -> #ws-panel); Alt+1..4 with `<kbd>` hints. Tools exist only when the private API probe is live; otherwise an honest "No tools: ... not connected" note. Nothing mocked; no tool without a backend.
- Build/web/src/shell/PrivateWorkspace.mjs: holds shell state; left state persisted in localStorage `r2s.workspace.left` (wide screens only; narrow always starts closed; pre-hydration `data-left="auto"` avoids a mobile drawer flash). Focus moves to the panel heading on open and back to the toggle on close; Escape closes panel, then mobile drawer; tool click focuses/scrolls its real section and closes the overlay on narrow. Existing notices, upload, SIMULATED/what-if note, instruments note and <Workspace> are passed unchanged into the center (interview/job panels stay where they were; S15ac relocates the interview).
- Build/web/src/workspace/view.mjs: only added id + tabIndex=-1 to the viewport/panel/job sections (jump targets). No controller.mjs/workflow.mjs/interview/API changes.
- Build/web/src/workspace/workspace.css: `.r2s-*` shell styles on the existing paper/ink tokens + hard offset shadow; <=760px rail/panel become fixed overlay drawers with scrim; reduced-motion respected.
- tests/shell-workspace/shell-toggle.test.mjs (5 tests): expanded/collapsed render + aria-expanded, rightmost-button/panel hidden agreement, tools only real (none offline), key map, persisted state, SSR of the real PrivateWorkspace (ids, labels, honest notices).

## Checks (fresh)
- `node --test "tests/workspace/*.test.mjs" "tests/shell-workspace/*.test.mjs" "tests/web-private/*.test.mjs" "tests/web-workspace-api/*.test.mjs"` -> 136 pass, 0 fail (Build/web/node_modules junction to canonical; junction removed afterwards).
- `npm run build` (Build/web) -> compiled, all routes built (rerun after CSS fix: compiled successfully).
- Static SSR render + CSS (evidence/S15ab/shell-static.html) in Playwright bundled Chromium via 127.0.0.1 http.server (not Chrome): scrollWidth == clientWidth at 1280 and 375 (drawer open/closed). Screenshots: evidence/S15ab/desktop-1280.png, desktop-collapsed.png, mobile-375-right-open.png, mobile-375-closed.png, mobile-375-left-drawer.png. Static states set by DOM attribute, not by real clicks.
- Labels: no RECORDED/SIMULATED/what-if/scale/owner-clip string changed; all still rendered in the center (verified SSR: fixture notice + phase label present).

## Deploy (Railway DEV, web only)
- `python infra/railway/dev/stage.py web <TEMP dir>` (112 files) + `railway up --detach --project ... --environment ... --service ...` (IDs from deployments.json).
- Final: ea2c0708-ab7f-457f-9f96-b3ce0e54ba94 SUCCESS (rev 7dac30d9e9e58daa2c0edf3cecf8da5f61209427); intermediate d9310465-537c-429b-a70c-6f16ba0f16fd (rev f90de52d) now REMOVED; previous 0bb4adb0 REMOVED.
- Smoke: https://web-dev-cd80.up.railway.app/ -> 200; /workspace unauthenticated -> 404 (existing private-route behavior). Signed-in walk NOT done (controller's job).

### deployments.json web lines (controller; file not edited)
"deploymentId": "ea2c0708-ab7f-457f-9f96-b3ce0e54ba94", "previousDeploymentId": "0bb4adb0-b11e-464a-a577-b4e90f01ad02", "sourceRevision": "7dac30d9e9e58daa2c0edf3cecf8da5f61209427", "redeployNote": "S15ab-orch188: stage.py web + railway up (Q21 shell: left rail, right agent/tools panel)", "providerStatus": "SUCCESS"

## Ponytail (full) — applied
- Reuse: PHASE_LABEL/OWNER_INTERVIEW_LABEL from layout.mjs for tool status; uploadView status; existing h-style pure render pattern (view.mjs) so tests need no DOM; existing CSS tokens; existing test createRequire pattern.
- Smallest complete: one new module + host state; no router, no context/provider, no new dependency, no icon library (7 inline SVG paths). Interview/job panels not moved (S15ac scope).
- Skipped: flyout panels from rail icons (rail icons are direct links), "Suggested" items, persisted right-panel state, tool for History separate from Runs (same backend), mobile focus trap inside drawers.

## Skill checklists
- myfront: applied paper/ink home, Instrument Sans/Space Mono, hard black offset shadows, finished hover/active/focus/empty states; skipped new texture/fonts (kept existing system).
- make-interfaces-feel-better: applied scale(.96/.98) press feedback, text-wrap balance/pretty, 40px hit targets, reduced-motion, focus-visible rings; skipped enter/exit animations for drawers.

## Risks / limits
- Ctrl+B/Ctrl+J override browser shortcuts while on the workspace page (Firefox bookmarks sidebar, Chrome downloads). Alt+digit may collide with some OS/IME shortcuts.
- Pre-hydration on mobile the left toggle reports aria-expanded=true while the drawer is hidden (fixed on mount).
- Real signed-in UI, focus round-trip and shortcuts in a real browser are unverified by me (unit + static only).
- Staging dirs %TEMP%/r2s-stage-S15ab-orch188-web{,2} left in place (recursive delete blocked by policy).

Communication: silent; one completion line to controller.
