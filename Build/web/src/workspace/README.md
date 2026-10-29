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

