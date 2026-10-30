# S15m — smallest honest upload-to-report path (integration map + plan)

Read-only plan, 2026-10-30, main 7dde2c9. Source: S15k-orch122 REPORT (deploy/auth/private-route PASS; Upload/Interview/Run/Fit/Report NOT-WIRED) + code read below. No code, deploy, paid call or secret read. Facts cite files; estimates/recommendations are marked.

## 0. Bottom line
- Structural bottleneck: **web image is Node-only; every stage brain except the simulator is Python** (pipeline, agent, fitter, reports, guardrails, S08 validator). Fix = host the Python stages in the **existing FastAPI API service** (python:3.12 image, already has redis/psycopg/boto3) and have web call it through **one Clerk-authenticated server proxy route**. No new service, no Python in web, no new dependency.
- Second bottleneck: **no persistent private scene/upload storage** (`Build/web/src/auth/dev-scenes.mjs` shortcut = one empty read-only fixture per user). Smallest fix: owner-scoped Redis keys (already deployed by S04f; `pipeline/jobs.py` store API = redis-py `set/get/delete/rpush/lrange` signatures) + upload bytes on the API container FS (ephemeral shortcut) or the S04f bucket.
- Honesty rule for the demo: uploads accepted **only if sha256 equals an approved `clips.csv` file** (reuse `pipeline/e2e.py` validate step). Owner films nothing, so this is also the privacy gate. Paid stages (Muse understand, SAM3.1 segment, MapAnything reconstruct) default to **RECORDED replay of the real S13h-orch46 live RM04 run** (144.4 s, evidence/S13/S13h/live), labelled RECORDED with original UTC; live execution is a separate, cuttable row behind S20 guardrails.
- Interview, spec validation, simulator run, fit and report cost $0 and can run **live** in the deployed app.

## 1. Stage map
| # | Stage | Existing module (reuse as-is) | Host | Live on dev by Nov 4? | Spend gate |
|---|---|---|---|---|---|
| 1 | Upload (resumable chunks) | `Build/pipeline/uploads.py` UploadService (`put_chunk`, `complete` verifies whole-file sha; S13a chunk rule `contracts.chunk_decision`) | API | LIVE (approved-clip sha only) | S20a upload quota (contracts/jobs/policy.json); no money |
| 2 | Validate | sha256 vs `clips.csv` (pattern in `pipeline/e2e.py`) | API | LIVE | none |
| 3 | Keyframes | `pipeline/keyframes.py` (ffmpeg) | API would need ffmpeg in image -> **RECORDED** (S13h keyframes) | RECORDED | none |
| 4 | Understand (Muse Wonder) | `pipeline/understand.py` + `agent/muse.py`; recorded fixtures `tests/agent/fixtures/muse` | API (replay) | RECORDED (Meta billing hold; S14e notes "no live calls while Meta billing is on hold") | Meta $120 routine stop incl. reservations; `record_muse.reserve` ledger; S20 admission before any live call |
| 5 | Segment (SAM3.1) + reconstruct (MapAnything) | `pipeline/gpu_stages.py` (`reserve` ledger-before-dispatch, `segment`, `reconstruct`), `pipeline/jobs.py` JobRunner idempotency/lease | API (replay); live = local CLI only (Modal client + creds are not in any Railway image) | RECORDED from S13h; live = optional S13j | Modal: `guardrails/admission.require_reconstruction` (cap $30, `MODAL_FLOOR_USD`=5) + `gpu_stages.reserve`; standing GPU auth; no overage |
| 6 | Progress feed | `pipeline/progress.py` -> display-safe `job_progress` doc; web reducer event `JOB_UPDATE` (`workspace/workflow.mjs`) | API (GET poll) | LIVE (over replayed events) | none |
| 7 | Interview (1-3 questions) | `agent/interview.py` `template_of`, `questions`, `answers_to_spec` (S08c `validate_setup`), no model calls | API | LIVE | $0 |
| 8 | Run (simulate) | `Build/web/src/lab/browser-simulator.mjs` `runBrowserSimulation` (needs a Python-validated setup export) + `Build/simulator` JS; workspace `runcontrol.mjs`/`run-view.mjs` | Browser (validated export from API) | LIVE | $0 |
| 9 | Instruments | `Build/instruments/` + `workspace/instruments.mjs` | Browser/API per existing contract | LIVE (simulated labels) | $0 |
| 10 | Fit | `Build/fitter/api.py` `handle(request)` (offline, simulation-only) | API | LIVE | $0 |
| 11 | Report | `Build/reports/typeset.render_html` (+`render.build_tables`, `contract` validation); `compile.py` returns explicit `html-print-fallback` when pdflatex absent | API -> HTML (CSP) | LIVE as HTML; PDF = print-from-browser | $0 |
| 12 | Muse Spark trial check | `agent/trial.py` `tool_only` fallback | API | tool_only (no model) | Meta gate if ever live |

Measured-vs-simulated: the e2e workspace fit is **simulated** (fitter is "simulation-only"); real-scene measured fits/prediction (S12 Gate RS) are NOT on this path and must not be implied.

## 2. Hosts and request contracts (proposed; names fixed here so rows can build in parallel)
Web (Next, Clerk) — new BFF route `/api/workspace/[...path]` (row S04n): requires Clerk `auth()` userId else 401; body cap (reuse `app/api/lab/route.js` `readCapped` pattern; 8388608 = contracts/jobs/policy.json `chunk_bytes` for chunk PUTs, 1 MB JSON — the lab route's 1 MB cap alone would reject chunks); forwards to `${WORKSPACE_API_URL}/internal/workspace/<path>` (Railway private network) with headers `x-workspace-owner: <clerk userId>` and `x-workspace-token: <WORKSPACE_INTERNAL_TOKEN>`; `cache-control: no-store`; never forwards cookies.
API (FastAPI) — `/internal/workspace/*`, rejects missing/mismatched token (constant-time compare) with 401; owner = header; every key owner-scoped. redis-py client needs `decode_responses=True` (JobRunner json.loads stored strings). Variable names only: `WORKSPACE_INTERNAL_TOKEN` (API+web), `WORKSPACE_API_URL` (web). Values set provider-side, never printed.

| Method path | Request | Response | Module |
|---|---|---|---|
| POST uploads | {filename, media_type, size_bytes, sha256} | S13a upload session DTO | UploadService |
| PUT uploads/{id}?offset=N (+x-chunk-sha256) | bytes | session DTO / chunk_decision error | UploadService.put_chunk |
| POST uploads/{id}/complete | — | {upload_id, sha256, approved_clip: id or null}; unapproved -> 422 INVALID_INPUT | complete + clips.csv |
| POST jobs | {upload_id} | S13a job DTO (status queued) | JobRunner (executor=recorded by default) |
| GET jobs/{id}/progress?after=R | — | `job_progress` doc (pipeline/progress.py); web dispatches {type:'JOB_UPDATE', job} | progress.progress |
| GET scenes/{id}/questions | — | interview.questions(scene_id, template) | agent/interview |
| POST scenes/{id}/spec | {answers} | {ok, spec, validated_setup} or {ok:false, errors} -> EDIT_SPEC/INTERVIEW_SPEC | answers_to_spec + validate_setup |
| POST fit | fitter request (observations from instruments) | fitter response -> FIT_RESULT / FIT_FAIL | fitter/api.handle |
| POST report | {spec, fit} | {status, html} (html-print-fallback label) -> REPORT_OPEN | reports typeset/render |
Run stays client-side: RUN_START -> `runBrowserSimulation({mode:'normal', validatedSetup})` -> RUN_COMPLETE.
Errors map to existing reducer codes: UNAUTHORIZED, NOT_FOUND, INVALID_INPUT, DEPENDENCY_UNAVAILABLE, SPEND_PAUSED (guardrails ReconstructionPaused), PROCESSING_FAILED.

## 3. Recorded vs live (demo truth table)
- LIVE in deployed dev: sign-in, upload of an approved clip (bytes really uploaded+sha-verified), job progress UI, interview, spec validation, browser simulation, instruments, fit, HTML report.
- RECORDED (labelled, original timestamps, run id S13h-orch46): keyframes, understand, segment, reconstruct. Tracked bytes: `evidence/S13/S13h/live/reconstruct/bundle/scene.json` + `RM04-scene-log.json` + `reconstruction.json`; **geometry bytes (PLY) are not in git** (STATE: RM02/RM04 PLY absent locally). Without them the viewer must show "geometry not retained" (DEPENDENCY_UNAVAILABLE for viewport), never a fake mesh. Optional S13j can re-capture bytes into the private dev bucket under standing GPU auth.
- Replay key = approved clip sha256 -> recorded run. Any other approved clip without a recording -> job `failed` DEPENDENCY_UNAVAILABLE "no recorded run; live GPU disabled on dev" (honest, not faked).

## 4. Spend gates (must wrap every paid call; none are on the default path)
1. Default executor makes **zero** paid calls (assert in S13i tests: executor=recorded never imports/launches modal or posts to Meta).
2. Live Modal (S13j only, local/worker): `guardrails.standalone.admit_standalone` / `admission.require_reconstruction(candidate_modal_usd=...)` -> raises ReconstructionPaused at $30 cap or $5 credit floor -> SPEND_PAUSED; `gpu_stages.reserve` appends ledger before dispatch; JobRunner idempotency prevents re-dispatch on retry; stop container after job.
3. Live Muse: blocked while Meta billing hold stands; if lifted, same admission + `record_muse.reserve` with the $120 routine stop (historical + in-flight + estimates) and $30 demo reserve.
4. AWS failover stays disabled-by-default (S20c); not on this path.

## 5. Risks (realistic) and cut order
Risks: (R1) PLY bytes absent -> viewport empty for recorded scene (mitigate S13j or honest notice). (R2) API image grows. **Checked locally (python -B import of agent.interview, fitter.api, reports.{typeset,render,compile}, pipeline.{uploads,jobs,progress,contracts}, guardrails.admission):** repo packages pulled = Build/{agent,fitter,guardrails,pipeline,reports} + contracts/{agent,experiment,fit} (+ contracts/jobs data); only new third-party = **jsonschema** (absent from Build/api/health/requirements.txt -> S04m pins it). Plus clips.csv and interview scene_root data; S04m runs the in-image import smoke. (R3) Upload bytes on ephemeral API FS lost on redeploy (shortcut; bucket later). (R4) Clerk userId as owner is trusted only via the internal token; token leak = cross-user access on dev (rotate; dev only). (R5) Next proxy streaming of chunk bodies — keep chunks small (policy size) and buffered. (R6) S15n controller is the biggest UI change; reducer phases already exist so risk is wiring, not design. (R7) Claude 5h quota stalls (S15k stalled once) — rows sized <=30 min each.
Cut order if time runs out (latest first): S13j live GPU -> Muse live -> report PDF (keep HTML) -> upload (fallback: "Use recorded approved clip RM04" button that starts the same recorded job with no bytes; label it) -> instruments detail. Never cut: auth/owner scoping, approved-clip sha gate, RECORDED/SIMULATED labels, spend gates.

## 6. Sequence
Parallel wave 1: S14i (API analysis routers + shared auth) | S15n (workspace controller vs this contract, fake fetch) | S04n (web proxy vs contract, mocked fetch).
Wave 2: S13i (API upload/job/recorded replay; imports S14i auth).
Wave 3: S04m (mount routers, image, vars, dev deploy API) -> S04o (PrivateWorkspace uses controller; deploy web).
Wave 4: S15o (browser re-walk). Optional/parallel anytime after S13i: S13j (live GPU capture, cuttable).
Estimate (not measured): 7 core rows x 30 min, 4 waves -> feasible by Nov 1-2 if dispatched Oct 31.

## 7. Files read (evidence of map)
Build/web/src/shell/PrivateWorkspace.mjs; Build/web/src/workspace/{react.mjs,workflow.mjs,fixtures.mjs}; Build/web/src/app/api/lab/route.js; Build/lab/session-service.mjs (spawns python -> fails on Railway); Build/web/src/lab/{browser-simulator.mjs,fit-contract.mjs}; Build/pipeline/{uploads,jobs,e2e,contracts,progress,understand,gpu_stages}.py; Build/agent/{interview,muse,record_muse,trial,tools}.py; Build/fitter/api.py; Build/reports/{compile,render,typeset}.py; Build/guardrails/{admission,standalone}.py + CONTRACT.md; Build/api/health/{app.py,requirements.txt}; infra/railway/dev/{CONTRACT.md,*.Dockerfile}; Build/web/src/auth/dev-scenes.mjs; QUEUE.md statuses; STATE.md top; API_BUDGET.md stop lines; Run-System/Runs/S13h-orch46/REPORT.md head.

