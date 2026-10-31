# S15ae-orch191 REPORT — DONE
Lane CLAUDE; model anthropic/claude-opus-5-5 medium (assigned); coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). Railway DEV web build only; no Meta/GPU call, no secrets read, no Chrome, no publication.
UTC start 2026-10-31T07:23:45Z (issued 07:22:58Z); end 2026-10-31T07:34:46+00:00. Branch run/S15ae-orch191, worktree .worktrees/S15ae-orch191, rebased on main 6cdcc2d; code commit adaf10d.

## What changed
- Build/web/src/shell/workspace-shell.mjs: PANES (navigate = existing NAV routes "Go to"; project = existing SECTIONS anchors "This project"; no Clips/Runs pane: no extra rail data on the page without duplicating right-panel Tools), pure railReduce({pane,open,preview}) with events toggle, iconClick(id), hoverEnter(id), hoverLeave, pin, escape (no-ops return same state); initialRail (validated stored pane, narrow starts closed), shownPane, HOVER_OPEN_MS 150 / HOVER_CLOSE_MS 250. renderShell: rail of buttons (aria-label, title, aria-current="true" on the current pane in every state, aria-expanded, aria-controls r2s-pane-<id>), panes are role=region + aria-label, hidden when not shown, data-mode pinned|temporary, temporary pane has a "Keep open" pin button. Header toggle button unchanged (aria-expanded = current pane open, Ctrl/Cmd+B).
- PrivateWorkspace.mjs: rail state via railReduce; timers: mouse pointerenter on icon -> hoverEnter after 150 ms; leaving icon or pane -> hoverLeave after 250 ms; entering pane cancels close; hover ignored for non-mouse pointers and <=760px. Ctrl/Cmd+B and header button = toggle. Escape order: temporary pane (focus returned to its icon only if focus was inside it) > right panel > narrow drawer. Link click in a temporary pane closes it; on narrow closes the drawer. Persistence: existing LEFT_KEY 'r2s.workspace.left' semantics unchanged (wide only), new PANE_KEY 'r2s.workspace.pane'. No focus moves on hover/focus.
- workspace.css: rail column 3.25rem always visible; pinned pane fills existing --sh-left (14rem expanded); temporary pane absolute overlay (does not push centre); current icon light filled tile + hard shadow; <=760px rail stays as 3.25rem grid column, panes are fixed drawers above the scrim; reduced-motion rule already covers .r2s-shell * transitions.
- tests/shell-workspace/rail-activity.test.mjs (8 tests: every reducer rule incl. owner "collapsed Home hover" case, click-while-preview pins, no-op identity, persistence, render aria/aria-current/hidden/temporary/pin/no-focus-steal, handler routing); shell-toggle.test.mjs updated to pass rail.
- evidence/S15ae/: static_render.mjs (reuses renderShell + S15ad pattern, synthetic fixture), static-{open,collapsed,preview}.html + 1280 PNGs, static-narrow-drawer.html + static-375.html/png (iframe 375 approximation).

## Fresh checks
- node --test tests/workspace, tests/shell-workspace, tests/web-private, tests/web-workspace-api: 150/150 pass (Build/web/node_modules junction to canonical, removed afterwards).
- npm run build (Build/web): exit 0; built CSS contains r2s-railbtn.
- Edge headless probes: open 1280: doc 1256/1256, centreLeft 224, pane navigate@53 w170, current=navigate. collapsed: centreLeft 52, no pane. preview(project while collapsed): centreLeft 52 (centre NOT pushed), pane project@52, current=navigate. 375 (iframe): doc 375/375 no horizontal scroll, drawer project@52.
- Deploy: python infra/railway/dev/stage.py web (113 files, source_revision adaf10dbeb1972790ec9ede9bdbd17054f7e918e) + railway up --detach --project/--environment/--service per README. Railway list_deployments: fbb52f25-e1e1-448e-92fd-d8165b5f762e SUCCESS (created 07:30:21Z, updated 07:31:27Z); previous 4b869e4a REMOVED. GET / 200; /workspace 404 unauthenticated (expected facade).
deployments.json web lines for controller (file NOT edited):
"deploymentId": "fbb52f25-e1e1-448e-92fd-d8165b5f762e", "previousDeploymentId": "4b869e4a-0238-46f3-b74a-057ca6289989", "sourceRevision": "adaf10dbeb1972790ec9ede9bdbd17054f7e918e", "redeployNote": "S15ae-orch191: stage.py web + railway up (left rail activity bar: toggle/click/hover preview/pin)", "providerStatus": "SUCCESS"

## Ponytail / skills
Applied Ponytail full: reused NAV/SECTIONS/navList/icon/initialLeft/LEFT_KEY/existing shortcut map and S15ad render script; one pure reducer + timers in the existing component; no new deps, no new abstraction; CSS-only layout using existing --sh-left grid. Deleted old collapsed-label hiding rules (labels now only in panes). make-interfaces-feel-better/myfront: kept existing tokens, 12 ms-class transitions, active tile with hard shadow matching shell; did not read myfront round-3 in full beyond reusing the shell style (time).
Unchanged: right agent panel, question card, centre layout, controller.mjs/workflow.mjs/interview/API; all RECORDED/SIMULATED/what-if/scale-unverified/owner-clip/Held-out labels.

## Skipped / risks
- Skipped: Clips/Runs panes (would duplicate right Tools data); signed-in real hover/click walk (controller's job); real 375 device (iframe approximation).
- Risks: the temporary pane overlays the sticky header left edge at wide widths (z-index 6 > header 5) by design; hover timers untested in a real browser (reducer + handler routing tested only); "Keep open" button is extra beyond icon-click pin (spec allows a pane pin action).
- Communication: silent; mcp__codex_app namespace was removed mid-run, so the completion message to controller chat may not be sendable; final line recorded here.

