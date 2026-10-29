# Workspace state graph (S15a)

Pure reducer `workflow.mjs`: `reduce(state, event, deps) -> state`. No DOM/React/network; S15b+ render it.
Illegal events return the **same state object** (no throw). Phases come from `PHASES`; allowed events per phase
from `availableEvents(state)`. `fixtures.mjs` is visibly synthetic: inert, deliberately non-physical placeholders,
not fitter/simulator output and never gate, real-scene or physical evidence.

## Consumed contracts
| Contract | Use |
|---|---|
| `shell/integration.schema.json` job DTO | `parseJob` (closed shape, ready⇔result, failed⇔error); revision ordering; new job id per retry |
| `lab/fit-contract.mjs` `parseFitReveal` (S11) | only source of fit numbers; must match the expected `sessionId`; label `simulated` |
| S08 spec validator | injected as `deps.validateSpec`; missing = fail closed |
| S10 hidden-g rule | run output containing gravity/hidden/mystery keys is rejected before a fit exists |
| viewer adapter (S09) | not imported; S15b mounts it via the shell `viewer` slot using `state.scene` |

## Graph
```
upload.idle --UPLOAD_STARTED--> upload.queued --JOB_UPDATE--> upload.running --JOB_UPDATE--> interview.active (ready)
                                     \--------> upload.failed | upload.cancelled   (terminal; UPLOAD_STARTED = retry, new job id)
interview.active --INTERVIEW_SPEC (validated)--> run.ready --RUN_START--> run.running <--RUN_PAUSE/RUN_RESUME--> run.paused
run.running --RUN_COMPLETE--> run.done  | --RUN_FAIL--> run.failed ; running/paused --RUN_CANCEL--> run.ready
run.done / run.failed --RUN_START (seeded replay)--> run.running
run.done / fit.failed --FIT_START--> fit.running --FIT_RESULT--> fit.done | fit.failed ; --FIT_CANCEL--> run.done
fit.done --REPORT_OPEN--> report.open --REPORT_CLOSE--> fit.done
run.ready/run.done/run.failed/fit.done/fit.failed/report.open --EDIT_SPEC--> interview.active (clears spec, run, fit)
any --RESET--> upload.idle (abandons scene; never cancels a server job)
```

## States
`upload.idle` `upload.queued` `upload.running` `upload.failed` `upload.cancelled` `interview.active`
`run.ready` `run.running` `run.paused` `run.done` `run.failed` `fit.running` `fit.done` `fit.failed` `report.open`

## Events
`UPLOAD_STARTED` `JOB_UPDATE` `INTERVIEW_SPEC` `RUN_START` `RUN_PAUSE` `RUN_RESUME` `RUN_CANCEL` `RUN_COMPLETE`
`RUN_FAIL` `FIT_START` `FIT_CANCEL` `FIT_RESULT` `FIT_FAIL` `REPORT_OPEN` `REPORT_CLOSE` `EDIT_SPEC` `RESET`

## Invariants
- Job `ready` means an artifact exists, not accuracy or a passed gate; `scene.evidence` is preserved (synthetic stays labelled).
- Equal/older job revisions, other job ids, status regression and terminal-state updates are ignored.
- Run completion must match the run seed; observations must be finite `time_s`/`position_m`.
- Editing the spec discards run and fit; edit is blocked while a run or fit is in flight (cancel first).
- Interview (S14) is consumed only through a validated spec; S14 transcript/chip states are S15d's, not modelled here.
- Not covered: transport/polling, auth, rendering, real validator wiring, browser behaviour (S15b–S15k).



## S15b: layout and viewport mount
Files: `layout.mjs` (state -> slots/stage rail/viewer request/job text, pure), `viewport.mjs` (mount controller), `view.mjs` (markup, `h`-injected), `react.mjs` (`createWorkspace(React)`), `workspace.css` (grid; one column under 860 px).
- Slots (names match the shell README): `stage-nav`, `viewport`, `panel`, `job-status`. The panel is a placeholder; upload/failure surfaces are S15c, interview S15d.
- Viewer contact is only `adapter.mount(host, request, { loadScene, signal, onState, onError }) -> { dispose }`. Adapter and `loadScene` are injected; workspace imports no viewer, shell, app or auth module (tested).
- Request is built from `state.scene` (set by a ready job): audience `signed-in`, mode `inspect`, never `mystery`; no job id/owner/token. One mount per (scene, mode, audience); scene change aborts + disposes the old mount; late mounts are disposed; callbacks after replace/destroy are dropped. The viewport stays mounted from interview through report because the scene persists.
- The `.ws-host` div has no React children (the viewer owns its contents). Synthetic scenes show a banner. A ready job is an artifact, not accuracy or a gate.
- App composition (S04 owns the page; not edited here): in a client module, `createWorkspace(React)` + `import './workspace.css'`, passing `createThreeViewer()` and `createArtifactLoader({ bundleUrl })`; authorise the scene server-side first.


## S15c: upload status and failure surfaces
Files: `status.mjs` (pure: `reduceLogged`, `statusSurface`, `failureSurface`, `partialState`, `jobTimeline`), `renderStatus` in `view.mjs`, `.ws-*` rules in `workspace.css`.
- **Event log:** keep `{ state, log, seq }` with `reduceLogged(m, event, deps)` instead of bare `reduce`. Each event (applied or ignored: stale revision, wrong job, illegal phase) adds one bounded (50) entry made of the event type, phases and an allow-listed job status/revision; payload text is never copied. The panel shows the last 8 since the latest upload start.
- **Timeline:** Queued -> Processing -> Scene ready for the upload job; failed/cancelled adds a terminal marker after the furthest step seen in the log.
- **Failures:** upload/run/fit failed or cancelled show a title, cause-specific advice and a retry button. Retry is an existing graph edge (`UPLOAD_STARTED`/`RUN_START`/`FIT_START`) and is withheld for `SPEND_PAUSED` and `UNAUTHORIZED` (retrying cannot help). The button calls `onAction({ type })`; the host adds the payload (new jobId, seed, sessionId) and dispatches. Without `onAction` it is disabled.
- **Partial state:** derived from state, never assumed: "Kept" (scene, spec, simulated run observations) and "Not available" (no scene was created, no stored run result, no fit value shown). A fit number never appears outside a validated reveal.
- Wiring: `<Workspace state log onAction ... />`; layout `jobStatus.surface` carries the model. Not covered: polling/transport that produces JOB_UPDATE, real upload UI, browser rendering.
+
## S15d: interview chips and free-text panel
Files: `interview.mjs` (pure parser, reducer, view model), `renderInterview` in `view.mjs`, `.ws-*` rules in `workspace.css`, fixtures `tests/workspace/fixtures/interview-responses.json` (built and drift-checked by `evidence/S15/interview_fixtures.py`).
- **Input:** an S14a `agent-response` already validated by `contracts/agent/validate.py` (plus the `toolOutputs` that back any number segment). `parseQuestions` re-checks only what the panel needs (scene id, <=3 questions, <=6 chips, kind/chips consistency, unique ids, no digit in text, number refs resolve to a labelled quantity) and fails closed; it also rejects duplicate question ids (the schema does not).
- **Reducer** `reduceInterview(state, event)`: `Q_LOADED {response, sceneId, toolOutputs}` (only idle/complete; mid-answer is illegal) -> `Q_CHIP {chipId}` (toggle) / `Q_TEXT {text}` (<=500 chars, control chars stripped) -> `Q_SUBMIT` (needs a chip, or text where the kind allows it; otherwise the position is kept and `state.error` says why) -> next question or `complete`; `Q_BACK` restores the previous answer; `Q_RESET`. Illegal events return the same state object.
- **Output:** `interviewAnswers(state)` = `[{questionId, chipId, text}]` once complete. That is user input for the agent / S15e template step, never a spec, measurement or number; S15a's `INTERVIEW_SPEC` still requires the S08 validator.
- **Wiring:** keep `interview` state next to the workspace state; `<Workspace state interview onAction />` shows the panel only in `interview.active`. `onAction` receives `Q_*` events; the host runs `reduceInterview`. Without `onAction` the controls are disabled. User text is rendered as text only.
- Not covered: transport to/from the agent (S14), real model replies beyond the recorded S14b fixtures, browser behaviour beyond the SSR/preview checks in `evidence/S15/`. Fixture validity is not Gate A, real-scene or physical evidence.


## S15e: experiment template controls
Files: `template.mjs` (pure parser, reducer, view model), `template-view.mjs` (`renderTemplate`), `.ws-template/.ws-field` rules in `workspace.css`, fixtures `tests/workspace/fixtures/template-cases.json` (recorded from the real Python `answers_to_spec` -> S08 `validate_setup` by `evidence/S15/template_fixtures.py [--check]`).
- **Fields:** one text input per parameter of the chosen template (free_fall, projectile, ramp, pendulum). The label always shows the contract unit `(m)`; the hint lists accepted typed units (`rad or deg or ° (unit required)`; blank = contract unit where Python allows it). Grammar/factors mirror `Build/agent/interview.py`; a test compares FIELDS to the Python table. No default numbers: fields start empty (or prefilled only from an existing spec's contract-unit values).
- **Reducer** `reduceTemplate`: `T_LOAD {template, spec?}` -> `T_EDIT {param,text}` -> `T_SUBMIT` (local parse; failures stay in `editing` with per-field errors and never reach the validator) -> status `checking`. The host sends `validationRequest(state)` = `{template, answers:{param:{text}}}` to the server (`answers_to_spec`) and dispatches `T_VERDICT {answers, result:{ok,spec|errors}}`. Accepted only if status is `checking`, the echoed answers equal the current texts (stale verdicts ignored), `ok === true`, and the returned spec has the right template and, for every field, the contract unit and the typed value. Anything else -> `rejected` with validator errors (<=5, 240 chars). Editing clears the spec. Illegal events return the same state.
- **Output:** `acceptedSpec(state)` is the only spec to pass on, as S15a `INTERVIEW_SPEC` (that reducer still runs its injected validator). In `run.ready` the panel is read-only (`Edit setup` -> `EDIT_SPEC`, which discards run and fit).
- **Wiring:** `<Workspace state template onAction />`; the panel shows in `interview.active` and `run.ready`; `onAction` receives `T_*` and `EDIT_SPEC`. Controls are disabled without `onAction` and while checking. User text is rendered as text only.
- Not covered: transport to the validator, real scene bundles (verdicts use the synthetic S08 test scene), prefill for non-contract units, the oracle envelope (pendulum amplitude <= 0.1 rad is enforced by `analytic_pendulum`, not `validate_setup`; the recorded 2 rad pendulum verdict is accepted by S08 but has no oracle). Fixture validity is not Gate P/A, real-scene or physical evidence.


## S15f: run, pause and seeded replay controls
Files: `runcontrol.mjs` (playback model, `prepareRun`, `verifyReplay`, `completionEvent`, `runView`), `run-view.mjs` (`renderRun`), `.ws-run/.ws-meter` in `workspace.css`, fixture runner in `fixtures.mjs`.
- **Contract (Build/simulator/replay.mjs, `s10-replay-v1`):** `runner(parameters, seed, version)` returns a dense trace once, up front; `createReplayRecord` binds seed + parameters + trace by SHA-256; `replayRecord` re-runs and rejects any difference. The simulator API is *injected* (`{ createReplayRecord, replayRecord, runner }`), so the workspace package imports nothing from Build/simulator. Seed is replay identity, not trajectory randomization: same seed -> identical trace, hashes; other seed -> same trace, different `replayHash`.
- **Run / pause / resume / cancel** use the existing S15a edges (`RUN_START`, `RUN_PAUSE`, `RUN_RESUME`, `RUN_CANCEL`). Pause only freezes a playback cursor (`R_TICK` is a same-reference no-op outside `run.running`), so it cannot change the trace. `RUN_COMPLETE` is sent from `completionEvent()` only after every frame was played; observations are the trace verbatim (S15a still rejects malformed output and hidden-physics keys).
- **Host loop:** send every event to both the S15a/S15c reducer and `reduceRun(m, e, state)`; on `RUN_START` (host adds the seed) call `prepareRun` then `R_LOAD {record}` (on throw: `RUN_FAIL`); a timer sends `R_TICK`; on `R_REPLAY_START` call `verifyReplay` and send `R_REPLAY_RESULT {result}`. `RUN_START`, `RUN_CANCEL`, `EDIT_SPEC`, `RESET` clear the model (no stale record or replay result).
- **UI:** `<Workspace state run={runModel} onAction />` shows Run/Run again, Pause, Resume, Cancel run, Replay with same seed (done only), a progress meter, current frame, seed, short trace/replay hashes and the replay verdict (a mismatch is an alert). Controls are disabled without `onAction`.
- Not covered: the timer/host wiring in the S04 page, real-simulator traces in the UI (tests use the real `replay.mjs` with a fixture runner), a persisted session. The fixture trace is deliberately non-physical; a verified replay shows consistency, not authentication, accuracy or any gate/real-scene/physical evidence.


## S15g: virtual instrument controls
Files: `instruments.mjs` (reducer, reading parser, host `measure`, `instrumentView`), `instrument-view.mjs` (`renderInstruments`), `.ws-instruments/.ws-trial/.ws-tag/.ws-src` in `workspace.css`. Fixture: `tests/workspace/fixtures/instrument-readings.json`, generated by `evidence/S15/instrument_fixtures.py [--check]` from the REAL `Build/instruments` models (stopwatch, light gate, ruler, camera).
- **Contract:** each reading is a `contracts/fit/quantity` object (`value, unit, uncertainty, source {label, evidence}`; camera adds `frame_index` with time/x/y). The parser is closed-shape and requires a finite value, the instrument's contract unit, finite uncertainty >= 0, `source.label === 'simulated'` (the only label that contract admits; `measured` is not producible here) and non-empty evidence. Hidden-physics keys (S15a rule) reject the reading. The workspace imports no instrument module: the host injects `service(instrumentId, nthReadingOfThatInstrument) -> reading`.
- **No hand-written numbers:** the view formats only parsed reading fields (`toPrecision(10)` strips binary noise, nothing else). Every row shows `value ± uncertainty unit`, the `simulated` tag and `source: <evidence>`.
- **Signed instrument error is dropped.** It is the distance to the hidden true value, so a trial view never shows or stores it (tested).
- **Host loop:** send events to `reduceInstruments(m, e, state)` (`I_SELECT`, `I_MEASURE`, `I_READING`, `I_FAIL`); on `I_MEASURE` call `measure(service, m)` and dispatch its result. `I_MEASURE` works only in `run.done` and one at a time; the panel stays visible (read-only) through fit/report phases. `RUN_START`, `RUN_CANCEL`, `EDIT_SPEC`, `RESET` clear the trials. Unrequested/stale readings and ineligible events return the same model object.
- **UI:** `<Workspace state instruments={model} onAction />`: instrument toggle chips, Take reading, status, trial list. Controls are disabled without `onAction`.
- Not covered: the S04 page wiring, a real instrument service/transport, using trial readings as fit input (S15h+), real or calibrated instruments. Settings (resolution, bias, noise, uncertainty) and true inputs in the fixture are SYNTHETIC choices of `instrument_fixtures.py`, not calibration, physics, gate or real-scene evidence.


## S15h: fit table and residual chart
Files: `fit-view.mjs` (`parseFit`, `fitView`, `renderFit`), wired as `<Workspace state fit={{ times, output }} />` (shown only in `fit.done` / `report.open`). Fixture `tests/workspace/fixtures/fit-output.json` is generated by `evidence/S15/fit_fixtures.py [--check]`: REAL `Build/fitter.api.handle` output (degree 2, AIC selection) on observations from the REAL `Build/instruments` models; only settings/true inputs are SYNTHETIC choices.
- **No hand-written numbers:** every table/residual text is a parsed fitter field (gravity, RMSE, RSS, degree, dof, n, selected degree, residuals) or an input time quantity; `toPrecision(10)` strips float noise only. The chart's pixel positions are geometry, never displayed; exact values are in the residual table (text alternative). Tests assert equality with the fitter output.
- **Labels:** each row/residual carries the fitter's own `source.label` (`simulated` or `measured`), never upgraded; unknown label, length mismatch, non-finite number or malformed block shows a rejection alert and no numbers. Null gravity shows "unavailable".
- **Accessibility:** `<table>` with captions and `scope`, SVG `role="img"` with title/desc. Existing deps only.
- Not covered: S04 page wiring, real fitter transport, the S11 reveal (`state.fit`) is not required by this panel, real/calibrated data, gate evidence.

## S15i: sidebar and report navigation

Files: `navigation.mjs` (`sidebarOf`, `renderSidebar`, `parseReport`, `reportView`, `renderReport`). Opt-in: `<Workspace navigate report={reportJson} interview={interviewState} onAction />`; without `navigate` the markup is unchanged.
- **Sidebar:** one button per stage; a button carries an event only if the S15a reducer accepts it (`REPORT_OPEN`/`REPORT_CLOSE`/`EDIT_SPEC`/`RESET`); run and fit are never directly reachable. Destructive moves (`EDIT_SPEC`, `RESET`) show their consequence. Report needs both `fit.done` and a received report. The host dispatches `event` to the reducer. The interview entry shows progress from the agent interview state.
- **Agent (Build/agent, S14):** reached only via its JSON contract (`contracts/agent`, already parsed by `parseQuestions`); no import of Build/agent.
- **Report (Build/reports, S17):** reached only via the `r2s.report/1` JSON. `parseReport` is a closed-shape mirror (schema, template, number entries, label in measured|simulated, placeholders resolve, no bare digits in prose). Numbers render from `numbers` with unit, uncertainty and label; unit `1` prints nothing. Fixture `tests/workspace/fixtures/report-output.json` is built through the public `Build.reports` API (`evidence/S15/report_fixtures.py [--check]`).
- Not covered: JS cannot recompute the fitter digest (server `validate_report` does); no live Meta/agent call; S04 page wiring; report tables/charts/PDF (Build/reports render outputs have no JSON transport contract yet).

