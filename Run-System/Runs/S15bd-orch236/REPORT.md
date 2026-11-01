# S15bd-orch236 REPORT
Lane/model: CLAUDE anthropic/claude-sonnet-5-5 medium; OpenCodex-managed; not polled. UTC 2026-11-01T06:57:20Z to 2026-11-01T07:04:46+00:00. Status: DONE.

## Changes
- upload-view.mjs: input.value cleared after reading the file, so re-picking the same file retries (P2).
- controller.mjs: keeps lastFile; retryUpload() re-runs upload. PrivateWorkspace.mjs routes UPLOAD_RETRY to it.
- view.mjs: renderError at upload.idle: INVALID_INPUT shows plain NOT_APPROVED copy with code in small text; DEPENDENCY_UNAVAILABLE keeps the message plus a "Try again" button (P2). Divider (hr) and heading "Recorded reference (not affected by your scale)" between live fit and recorded block (P3).
- PrivateWorkspace.mjs: sessionNote(): sessionStorage flag only (no session data) set in interview, cleared on other phases; idle with flag shows "Your earlier session was reset by the page reload. Upload the clip again to start over." (P3).
- tests/workspace/s15bd.test.mjs: one test per item (5).

## Ponytail choices
Reused existing error surface, ws-retry/ws-failure classes, routeAction, and controller; no new component, no persistence, no dependency. Unchanged static hint kept. Module scope: lastFile is a closure variable.

## Fresh checks
node --test (lab, workspace, shell-workspace, web-private, web-workspace-api, pwa): 361/361 pass. Build/web npm run build: OK. No em dashes in new visible text.

## Skips and risks
- Not browser-verified on DEV (no deploy; controller deploys). Real file input clearing in a browser is untested beyond a stub event.
- Try again appears only for upload-stage DEPENDENCY_UNAVAILABLE; other stages keep existing retry. Reset note also shows after an in-tab reset to idle from the interview.
- No CSS added for ws-divider, ws-subhead, ws-code (default styling). Download/print and SPEND_PAUSED rows not in scope.
- Communication compliance: silent; one completion line only.
