# S15c-orch18 — DONE

- Model: anthropic/claude-sonnet-5-5 high (assigned). OpenCodex-managed; not polled. Tokens/cost: unknown.
- UTC: issued 2026-10-29T11:38:56Z, deadline 12:08:56Z; work stopped 2026-10-29T11:43:46+00:00 (verified fully DONE except the visual check noted below). Branch run/S15c-orch18.
- Files (all inside Owns): Build/web/src/workspace/status.mjs (new), view.mjs (renderStatus), layout.mjs, react.mjs, workspace.css, README.md (S15c section); tests/workspace/status.test.mjs (new, 9 tests); evidence/S15/{react-ssr-check.mjs (extended),react-ssr-check-s15c.out.txt,workspace-tests-s15c.out.txt,failure-preview.html}.

## Result
- Job-stage events visible: reduceLogged wraps the S15a reducer, keeps a bounded log of applied AND ignored events (stale revision, wrong job, illegal phase); panel shows timeline Queued -> Processing -> Scene ready (+ Failed/Cancelled marker) and the last 8 events since the latest upload start.
- Failure/retry: upload/run/fit failed or cancelled show title, cause-specific advice and retry button. Retry = existing reducer edge (UPLOAD_STARTED/RUN_START/FIT_START), verified legal and recovering (new job id; late update from the dead job ignored). Withheld for SPEND_PAUSED/UNAUTHORIZED; disabled without onAction.
- Partial state: kept/not-available lists derived from state (scene, spec, simulated observations; no scene created; no run result; no fit value without validated reveal). Tested for upload, run and fit failures.
- S15a reducer and fixtures, viewer, shell, app untouched; no new dependency.

## Checks (fresh)
- node --test tests/workspace/{status,layout,workflow}.test.mjs: 26 pass / 0 fail (9 new; 17 prior still pass).
- evidence/S15/react-ssr-check.mjs with real React 19.3.1 SSR (read-only canonical node_modules): idle/scene asserts plus failure surface, retry button, blocked-retry copy: ok.
- Tests also cover: log bound 50, payload text never copied (HTML-like status/revision), error text rendered as text node, import boundary (status.mjs imports only ./workflow.mjs).

## Ponytail (full)
Reuse: S15a reducer/availableEvents/fixtures, S15b layout slots/view/react props, existing .ws-error. Smallest-complete: wrapper over reduce instead of editing the reducer; one pure module; retry reports { type } and host supplies payload; no state lib, no timers, no deps. Skipped: polling/transport producing JOB_UPDATE, real upload form, toasts/animation, interview chips (S15d), app page wiring (S04-owned).
Fixtures: only S15a visibly synthetic fixtures; no gate, real-scene, physical or number claims.

## Risks / unverified
- Not viewed in a browser: failure-preview.html is static SSR+CSS; the added CSS and 44px retry target are visually unverified (no server started; file:// previously blocked).
- StrictMode/DOM behaviour of the retry button covered only via markup tests and SSR, not a DOM renderer.
- Copy is English-only; advice strings are fixed text keyed on the schema error codes, server message shown verbatim as text (<=240 chars).
- Host must dispatch retry with fresh ids; a missing/invalid id is ignored by the reducer (state unchanged, logged as ignored).
- Communication: silent; one completion line to controller.
