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

