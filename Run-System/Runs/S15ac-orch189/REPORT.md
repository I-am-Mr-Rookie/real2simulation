# S15ac-orch189 REPORT — DONE

- Task: QUEUE S15ac (Q21 owner spec): interview as right-panel agent question card; centre keeps scene/stage + non-blocking waiting state; web redeployed to Railway DEV.
- Lane/model: CLAUDE, anthropic/claude-opus-5-5 high. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). Meta/GPU calls: none.
- UTC: issued 2026-10-31T06:19:27Z, start 06:20:03Z, stopped 2026-10-31T06:28:49+00:00. Branch run/S15ac-orch189 (worktree .worktrees/S15ac-orch189), rebased on main 02752987.

## Changes
- Build/web/src/shell/agent-card.mjs (new, pure): renderQuestionCard (labelled section aria-labelledby r2s-q-h; n/N counter; answered questions collapsed in <details> "k answered"; polite live status "Question n of N"; form with legend=prompt, numbered options 1..9 as aria-pressed toggle buttons with <kbd>; "Other (your own answer)" textarea, or "Your answer" for free_text-only questions; Back (Q_BACK); Continue / Finish on last, Ctrl/Cmd+Enter; error role=alert), cardKey (1..9 picks, ignored while typing in textarea), renderWaiting (always-mounted live region; P1 strip "Agent needs your answer. Question n of N: <prompt>" + "Answer in agent panel" button), pendingOf, shouldAutoOpen.
- **No Skip**: the interview reducer has no skip event, so Skip is omitted (per contract).
- Build/web/src/shell/workspace-shell.mjs: renderShell takes v.agent (card shown above Tools) and v.pending (badge on "Agent & tools" toggle only while the panel is closed, with SR text "n questions waiting"); toolsOf({pending}) prefixes the Agent row status with "n question(s) waiting." and targets the card heading.
- Build/web/src/shell/PrivateWorkspace.mjs: card fed the same local.interview, only in phase interview.active (same condition as the old centre panel); interview no longer passed to <Workspace>, so the old centre panel disappears with no view.mjs change; same onAction -> routeAction -> reduceInterview / ctl.submitAnswers path. Panel auto-opens once per new question round unless the user closed it while questions were pending (then badge only); focus goes to the card heading on open, back to the toggle on close; Escape/scrim/X close; Agent tool on narrow screens does not close the drawer it lives in.
- Build/web/src/workspace/workspace.css: .r2s-qcard/.r2s-qopt/.r2s-qother/.r2s-qactions/.r2s-badge/.r2s-waiting/.r2s-pulse; reduced-motion disables press scale + pulse; <=760px hides the Ctrl+Enter hint.
- tests/shell-workspace/agent-card.test.mjs (5 tests): card render (region, 3/3 and 1/3, numbered options incl. "(simulated)" tool label verbatim, Other, Continue vs Finish, no Skip, collapsed answers, key events, inert without onAction); cardKey; owner known-size flow ("book cover horizontal edge 20.28 cm" typed in the card, Finish -> ctl.submitAnswers once with that exact text via the real routeAction); centre waiting + pending Agent status (owner-clip label verbatim) + badge only when closed + card inside #r2s-right; auto-open rule.
- evidence/S15ac/: static_render.mjs + static-{open,closed}.html + static-1280-open.png, static-375-open.png, static-375-closed.png (SSR of the real render functions on the synthetic fixture).
- Untouched: controller.mjs, workflow.mjs, interview.mjs, view.mjs (renderInterview kept for existing tests/other hosts), Build/api.

## Checks (fresh)
- node --test "tests/workspace/*.test.mjs" "tests/shell-workspace/*.test.mjs" "tests/web-private/*.test.mjs" "tests/web-workspace-api/*.test.mjs" -> 141 pass, 0 fail (136 existing + 5 new), before and after rebase. Build/web/node_modules junction to canonical, removed afterwards (Test-Path False).
- npm run build (Build/web) -> exit 0, all routes built.
- Static render in Playwright MCP Chromium via 127.0.0.1:8765 http.server (not Chrome): scrollWidth == clientWidth at 1280 (panel open) and 375 (panel open as overlay drawer; closed with badge + centre waiting strip). States set statically, not by real clicks.

## Deploy (Railway DEV, web only)
- python infra/railway/dev/stage.py web %TEMP%/r2s-stage-S15ac-orch189-web (113 files, source_revision 0ecb497b85843126b90f94576990e52e8e0f73f0) + railway up --detach (project/env/service IDs from deployments.json).
- New deployment 079d2129-1bc2-43c5-b55b-b27afb5fe885 SUCCESS; ea2c0708 now REMOVED. Smoke: / -> 200; /workspace unauthenticated -> 404 (existing private-route behaviour). Signed-in walk NOT done (controller's job).

### deployments.json web lines (controller; file not edited)
"deploymentId": "079d2129-1bc2-43c5-b55b-b27afb5fe885", "previousDeploymentId": "ea2c0708-ab7f-457f-9f96-b3ce0e54ba94", "sourceRevision": "0ecb497b85843126b90f94576990e52e8e0f73f0", "redeployNote": "S15ac-orch189: stage.py web + railway up (interview as right-panel agent question card, centre waiting state)", "providerStatus": "SUCCESS"
(sourceRevision is the staged commit; this REPORT commit adds only Run-System files on top.)

## Ponytail (full) — applied
- Reuse: interviewView/reduceInterview/routeAction unchanged; renderShell slot instead of new layout; existing paper/ink tokens, .r2s-iconbtn, .ws-error; tiny-h pure-render test pattern from shell-toggle.test.mjs; existing fixture interview-responses.json.
- Smallest complete: removing the centre panel = dropping one prop in PrivateWorkspace (no view.mjs edit, old tests stay valid); one new pure module; no new dependency, no context/provider.
- Skipped: Skip button (no contract event), "let the agent answer" (O2) option, flyout/suggested items, persisting userClosed across reloads, focus trap inside the mobile drawer, README updates.

## Skill checklists
- myfront round 3: applied hard black offset shadow on the card, Space Mono for counter/kbd/badge, paper/ink home kept, finished hover/active/pressed/disabled/error/empty states, did not restyle shipped S15ab parts. Skipped: new fonts/texture.
- make-interfaces-feel-better: applied tabular-nums on counter/badge, scale(.96/.98) press, concentric radius (card radius +4px over 6px inner), text-wrap pretty, >=40px hit targets, reduced-motion (pulse + press off). Skipped: enter/exit animation of the card.

## Labels
- No RECORDED/SIMULATED/what-if/scale-unverified/owner-clip string changed; centre notes and stage heading unchanged; OWNER_INTERVIEW_LABEL shown verbatim in the Agent tool status; tool-output chip labels (e.g. "(simulated)") render verbatim (tested).

## Risks / limits
- Real signed-in UI, live auto-open/focus round-trip and keyboard 1..9 in a real browser unverified by me (unit + static only).
- Two polite live regions (centre strip + card progress) may announce the same arrival twice in some screen readers.
- Auto-open moves focus into the card when questions arrive; intended by spec but can interrupt a user mid-task.
- Staging dir %TEMP%/r2s-stage-S15ac-orch189-web left in place (no recursive delete).

Communication: silent. The controller-message tool (codex_app send_message_to_thread) was removed from this session's catalog mid-run, so the one completion line is returned as this chat's final answer instead.
