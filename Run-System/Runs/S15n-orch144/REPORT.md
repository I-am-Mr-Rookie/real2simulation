# S15n-orch144 REPORT — DONE

Lane CLAUDE, assigned anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
UTC start 2026-10-30T11:42:59Z (issued 11:40:47Z); work stopped/reported 2026-10-30T11:49:18+00:00. Tokens/cost: unknown (unobservable); $0 spend — no Meta/Modal/AWS call, no deploy.

## Files
- `Build/web/src/workspace/controller.mjs` — `createController({fetch, simulate, sleep, onChange, ...})`: owns one `workflow.reduce` state + side meta (busy, upload progress, job_progress events, questions, validatedSetup, report html). Methods: `upload(file)` (sha256 -> POST uploads -> PUT uploads/{id}?offset=N + x-chunk-sha256 in server `chunk_bytes` steps -> POST uploads/{id}/complete -> POST jobs -> UPLOAD_STARTED/JOB_UPDATE, then polls GET jobs/{id}/progress?after=R dispatching `doc.job`), `loadQuestions`, `submitAnswers` (POST scenes/{id}/spec; reducer accepts only the exact spec object the API validated), `run(seed)` (injected `simulate(validatedSetup, seed)` = runBrowserSimulation wrapper; missing -> DEPENDENCY_UNAVAILABLE), `fit` (POST fit with stored simulated observations; body goes through existing parseFitReveal gate), `openReport` (POST report -> {status, html} -> REPORT_OPEN). `errorOf(status, body)`: body `error|detail` code wins, else 401/403 UNAUTHORIZED, 404 NOT_FOUND, 400/409/413/415/422 INVALID_INPUT, 402 SPEND_PAUSED, 5xx/network DEPENDENCY_UNAVAILABLE; message capped 240.
- `Build/web/src/workspace/upload-view.mjs` — `uploadView(snapshot)` + `renderUpload(h, v, onFile)` in the same injected-`h` style as run-view.mjs: native `<input type=file>` with `<label htmlFor>`, aria-describedby hint+status, polite status, `<progress>` while busy, role=alert error; disabled while busy; states "only approved clips.csv clips accepted (checksum)". Reuses existing ws-field/ws-hint/ws-progress/ws-meter/ws-error CSS (no CSS edit; not owned).
- `tests/workspace/controller.test.mjs` — 6 tests, synthetic fake BFF.
- `evidence/S15n/node-test-workspace.txt` — full test output.

## Acceptance
1. PASS — fake fetch drives upload.idle -> upload.queued -> upload.running -> JOB_UPDATE(ready)=interview.active -> INTERVIEW_SPEC=run.ready -> RUN_COMPLETE=run.done -> FIT_RESULT=fit.done -> REPORT_OPEN=report.open (exact phase sequence asserted), on PLAN §2 paths; chunk offsets 0/4/8 and per-chunk + whole-file sha256 asserted against node:crypto.
2. PASS — UNAUTHORIZED/INVALID_INPUT/SPEND_PAUSED/DEPENDENCY_UNAVAILABLE (+NOT_FOUND, PROCESSING_FAILED) mapped; transport/API errors keep phase, leave job/scene/spec/fit/report null, busy cleared. Bad progress doc, foreign fit session, report without html, rejected spec, missing simulator, poll timeout all fail closed with no number. Controller imports no fixtures; fixtures only in tests (all labelled SYNTHETIC).
3. PASS — `node --test "tests/workspace/*.test.mjs"`: tests 85, pass 85, fail 0 (79 existing + 6 new), Node v24.18.0. File input labelled (htmlFor===id), no negative tabIndex (native input = keyboard reachable), describedby targets exist.

## Ponytail (full) — reuse / smallest complete change
- Reused workflow.reduce/initialState/parseJob/parseFitReveal unchanged; no new reducer events — transport errors set `state.error` (existing field rendered by view.mjs/status.mjs) without changing phase.
- Spec validation reuses the reducer's injected `validateSpec` dep, pointed at the API verdict (identity check), instead of a new event.
- Web Crypto + fetch only; no dependency, no CSS, no React import (h injected like run-view.mjs).
- Skipped (not asked): retry/backoff policy, upload resume across reloads, cancel, streaming hash (shortcut comment: whole file in memory), React composition (S04o).

## Limits / risks
- Contract-level only: S14i/S13i API and S04n proxy are parallel/unbuilt here; not verified end-to-end. API must return the S11 fit-reveal shape `{status:'ok', sessionId, fit:{gravity:{value,uncertainty,unit,source:{label:'simulated'}}, uncertainty:{model,assumptions}}}` echoing the request `sessionId`; a raw fitter.handle response will be shown as fit.failed (fail-closed, by design). Error bodies expected as `{error:{code,message}}` or FastAPI `{detail:{code,message}}`.
- Upload errors also surface in layout/view error slots; S04o should avoid rendering the same alert twice.
- No browser/visual QA of the upload control (no mount point until S04o); the 375px/visual check belongs to S04o/S15o.
- Communication: silent; one completion message to controller as authorized.

Next: S04o mounts `createController` + `renderUpload` in PrivateWorkspace.
