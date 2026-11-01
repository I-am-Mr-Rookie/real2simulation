# N19: wave-1 security and spend review

**Verdict: HOLD paid/live-processing DEV exposure.** Read-only review, no fixes applied. Unpaid liveness and already-isolated read paths need not be taken down.

- Baseline: `b085708c42d0d071ada7d8937386654318eb832d`, branch `run/N19-orch259`.
- Reviewed the named storage/BFF, daily cap, on-demand GPU/status, agent/API, hosted SAM and lab-editor modules, plus their immediate auth/runtime/deployment dependencies. Applied PLAN-NOV1 including Owner decisions.
- Found 3 P1 and 4 P2 issues; no demonstrated P0 or cross-user data disclosure.
- Evidence: `probes.py`, `PROBE-RESULTS.txt`. Synthetic credentials and mocked transports only. No actual Meta/Modal calls, deployments, source changes, or .env reads.

## Findings

### F1 [P1] Actual paid transports bypass the daily cap entirely

**Locations:** `Build/agent/core.py:248-260,267-279`; `Build/api/agent/__init__.py:20-28,36`; `Build/measurement/hosted_sam.py:50-58`; `Build/gpu/ondemand.py:29-40`.

The production agent defaults call `_send` directly for both Responses and transcription. Hosted SAM `track` calls `requests.post` directly. None imports or invokes `daily_cap.reserve/settle`. The two GPU entry points also provide no budgeted dispatch wrapper; the comment assigning this obligation to callers is not enforcement. There is no wave-1 budgeted on-demand invocation path in the reviewed API modules. The task's assertion that every paid call already uses reserve/settle is false at this baseline.

**Reproduction:** fill an isolated ledger with a $10 reservation, then invoke the real agent text, voice and hosted SAM transports with only their network I/O mocked. All three send; ledger remains $10. `CAP_BYPASS` in probe output. Modal omission is static evidence, not a real remote invocation.

**Concrete fix:** route every live transport and GPU dispatch through the shared persistent ledger before network/remote allocation. Reserve a validated worst-case cost including bounded tokens/frames/runtime, cold start and billed idle GPU time; settle from trusted usage/billing, retaining liability on ambiguous timeouts. Test that exhausted budget causes zero outbound calls for all models and both GPU jobs. Do not infer that recording a larger actual cost after execution is a hard stop.

**Blocks DEV exposure:** **YES**, for paid agent, transcription, hosted tracking and GPU work. Existing authentication is not a spend guard.

### F2 [P1] The supposed single GPU/queue is two independent container pools

**Locations:** `Build/gpu/ondemand.py:25,29-40`; `Build/api/gpu/__init__.py:42-51,72-99`.

`max_containers=1` is applied separately to `reconstruct` and `track`. Both functions can therefore have one GPU simultaneously, each with a 900-second idle window. The SQLite job table records and displays order, but does not dispatch or serialize work between those pools. Summing their stats does not impose a global resource limit. This violates the binding one-GPU/one-queue decision and makes a one-container cost reservation unsafe. No external global queue/lock was demonstrated in this baseline.

Modal documents [per-function pool limits](https://modal.com/docs/guide/scale) and [billing while idle](https://modal.com/docs/guide/cold-start). This is configuration/API-contract evidence, not a live concurrency measurement.

**Concrete fix:** use one bounded GPU dispatcher/container pool for both job kinds, with a transactional shared queue, or an equivalently enforced global capacity limit that also addresses the second warm GPU. Budget the permitted 900-second idle residency before allocation; job-body settlement alone misses that cost. Test simultaneous track/reconstruct admission and queue ordering without remote execution.

**Blocks DEV exposure:** **YES**, before enabling the on-demand GPU path under the approved single-GPU spend policy. Status-only reads can remain available.

### F3 [P1] The API image lacks the validator and silently skips the 120-second limit

**Locations:** `Build/api/storage/files.py:42-52,174-180`; `infra/railway/dev/api.Dockerfile:1-11`; `Build/api/health/requirements.txt:1-8`.

`video_seconds` returns `None` when ffprobe is absent; upload then skips duration enforcement and accepts an eight-byte magic match as sufficient video validation. The checked-in API image uses `python:3.12-slim`, installs Python requirements, and never installs ffprobe. Thus the development image recipe does not supply this mandatory validator. Actual deployed image contents were not inspected.

**Reproduction:** make ffprobe unavailable in an isolated router and upload `ftyp` plus garbage named `spoof.mp4`, declaring `text/html`. It returns 201 with `media_type=video/mp4` and `duration_s=null`. Header spoofing alone is not an XSS finding here: the issue is missing container/duration validation. Valid very long, highly compressed videos are likewise not subject to the 120-second admission rule on this branch.

**Concrete fix:** include ffprobe in the API image, check its availability/readiness, and do not silently bypass the duration cap when probing fails. Require a finite positive duration, a readable supported video stream, and at most 120 seconds before processing/spend admission; run the probe off the async event loop with a timeout. Test the actual image and missing-validator/corrupt/overlong input cases.

**Blocks DEV exposure:** **YES**, for open video uploads feeding live processing until the deployed runtime demonstrably enforces the stated limits. Images are a separate path.

### F4 [P2] Upload quotas are only atomic within one Store instance

**Locations:** `Build/api/storage/files.py:69-70,102-117`.

The quota snapshot and insert use a Python instance lock, not a SQLite transaction. Two Store instances/processes sharing the same metadata database can both see remaining capacity and then insert. SQLite serializes the inserts, not the preceding reads. Moving the file before the metadata insert also leaves unaccounted bytes if the insert fails.

**Reproduction:** two connections synchronized just after their final quota snapshots admit uploads 20 and 21; another run admits two eight-byte files with only ten bytes remaining, exceeding storage by six bytes. No large files needed. The current Docker command is single-worker, so this is not evidence that its one cached Store alone has the same completed-upload race.

**Concrete fix:** acquire `BEGIN IMMEDIATE` before reading quota and hold through the insert, with rollback and cleanup of a moved destination on failure. Test two separate Store connections/processes, not just threads sharing one lock. Separately bound/reserve in-flight upload storage so parallel multipart spooling cannot exhaust disk before the committed quota check.

**Blocks DEV exposure:** **CONDITIONAL**. Fix before multiple API writers/replicas or overlapping writers against one volume. Single cached-Store, single-process DEV can proceed with that limitation explicit and upload concurrency bounded.

### F5 [P2] The number guard accepts sign/unit/provenance changes and is skipped for questions

**Locations:** `Build/agent/core.py:146-155,190-204`.

Numeric comparison takes absolute values and discards quantity context, labels and uncertainty. A tool's acceleration `-9.81` authorizes `+9.81`; a duration `9.81` authorizes a measured mass `9.81 kg`. The `ask_user` early return bypasses even this check for both the question and visible option labels. Allowlisted tools and their finite-number argument validation do not make generated prose evidence-backed.

**Reproduction:** both substitutions produce an empty `unbacked_numbers` result. A fake model `ask_user` response returns `MEASURED gravity is 12345 m/s2` to a user who supplied no numbers, without stopping. This proves a guard gap, not that a particular live model will emit that text.

**Concrete fix:** render measured result quantities/labels/uncertainty directly from typed tool results, rather than authorizing any occurrence of the same scalar in prose. Preserve signs and units. Validate every model-authored visible surface, including questions/options, or keep questions free of scientific result claims. Add adversarial sign, unit, label, uncertainty and ask-user tests.

**Blocks DEV exposure:** **YES for presenting agent-authored measurements as trustworthy results**; not a reason to disable plain navigation or the deterministic fitter itself. No code execution or cross-user access was demonstrated.

### F6 [P2] Agent routes do not match the authenticated BFF namespace

**Locations:** `Build/api/agent/__init__.py:22-24,32`; `Build/api/health/app.py:45`; `Build/web/src/app/api/workspace/[...path]/route.js:52`.

Agent mounts at `/workspace/agent/*`, but the only supported BFF builds `/internal/workspace/agent/*`. Both turn and transcription therefore return 404 via that route. The agent itself still requires the internal token and a valid owner header; this is an integration failure, not an unauthenticated paid-call exposure.

**Reproduction:** owner-gated `/workspace/agent/turn` returns 200 with a fake model, while `/internal/workspace/agent/turn` returns 404; no-token request returns 401.

**Concrete fix:** align the agent router prefix with `/internal/workspace/agent` and add an end-to-end BFF-to-ASGI contract test for turn and transcription. Preserve the shared owner dependency; do not expose an alternative unauthenticated direct route. Fix F1 before making the working paid route available.

**Blocks DEV exposure:** **YES for claiming an operational signed-in agent**, not for isolated storage/status DEV checks.

### F7 [P2] Transcription caps disagree and the API checks size only after buffering

**Locations:** `Build/api/agent/__init__.py:33-38`; `Build/agent/core.py:22,230-237`; `Build/web/src/app/api/workspace/[...path]/route.js:6,46-47`.

`request.body()` buffers the entire audio request before enforcing four million bytes. The BFF uses its one-million-byte JSON cap for transcription because only `POST /files` gets a specialized cap. Once routing is fixed, valid audio between one and four million bytes will still be rejected by the BFF. The backend has no independent streaming size limit for an internal caller or a future BFF change.

**Reproduction:** a synthetic six-chunk ASGI input is consumed in full (6 MB) before the four-million-byte check rejects it. WAV format/channel/rate and 60-second duration checks do exist after the read.

**Concrete fix:** enforce the byte cap while consuming the API request stream, checking declared length only as an early optimization. Give the exact transcription path the same bounded binary cap in the BFF, not the JSON cap. Test missing/false content length, over-limit streaming and valid audio above one million bytes.

**Blocks DEV exposure:** **NO as an isolated public memory-exhaustion claim at this baseline**: current BFF has a smaller cap and F6 prevents reaching this endpoint. **YES before treating voice input as an integrated, correctly bounded feature.**

## Checks and retained protections

- **39 Python tests passed** across `tests/api-storage/test_storage.py`, `tests/guardrails/test_daily_cap.py`, `tests/gpu/test_ondemand.py`, `tests/agent/test_core.py`, `tests/measurement/test_hosted_sam.py`. Runtime: cached uv Python 3.12, FastAPI 0.124.4, Starlette 0.50.0, httpx 0.28.1, multipart 0.0.20, redis 8.1.0, jsonschema 4.23.0, numpy 2.2.6. One upstream anyio deprecation warning.
- **8 Node tests passed**: `node --test tests/api-storage/proxy_files.test.mjs tests/lab-editor/lab-editor.test.mjs`. Shared canonical node_modules junction; no npm install. Existing typeless-module warning only.
- **7 offline probe groups passed**, with actual output retained in `PROBE-RESULTS.txt`. They demonstrate defects, not successful paid operation. The probe deliberately coordinates legal concurrent snapshots to make quota races reproducible.
- Daily-cap admission itself uses `BEGIN IMMEDIATE`, integer USD units and upward rounding. Existing tests verify exactly $10 admission, concurrent refusal, Dhaka midnight, the inclusive Nov 5-8 $20 window including the year, lower-cost settlement and duplicate-settle rejection. No arithmetic/date defect found in that implementation; F1 is its missing use.
- Internal authentication fails closed, compares the shared token in constant time, and restricts owner IDs to path-safe characters. File/project lookups are owner-filtered SQL parameters; UUID-only file IDs and server-created disk names avoid user-filename traversal. BFF ignores client owner/token headers and supplies the Clerk identity. No cross-owner disclosure or traversal found in the inspected paths.
- BFF file bodies are streaming-capped, download responses stream without whole-file buffering, Range is forwarded, and 206 headers survive. Storage tests cover real partial download and owner isolation. Existing tests do not establish every malformed/multi-range edge case or deployment/proxy behavior.
- Agent history strips privileged roles, tools are allowlisted with strict extra-key/type/length/finite-number checks, exceptions do not expose tracebacks, and the six-model-call step cap is tested. These are deterministic checks, not proof that a live model obeys the physics-only prompt or never follows injection inside user/tool text. No arbitrary code-execution tool exists in this module.
- Lab scene imports enforce finite bounded values, allowed fields/kinds and 50 objects; traces are SIMULATED and sampling is bounded. Editor tests ran without a rendered browser; no remote assets/spend were exercised.

## Reproduction and limitations

From this worktree root:

```powershell
uv run --offline --with pytest --with fastapi==0.124.4 --with httpx==0.28.1 --with python-multipart==0.0.20 --with requests --with redis==8.1.0 --with jsonschema==4.23.0 --with numpy==2.2.6 python -m pytest -q tests/api-storage/test_storage.py tests/guardrails/test_daily_cap.py tests/gpu/test_ondemand.py tests/agent/test_core.py tests/measurement/test_hosted_sam.py
node --test tests/api-storage/proxy_files.test.mjs tests/lab-editor/lab-editor.test.mjs
uv run --offline --with pytest --with fastapi==0.124.4 --with httpx==0.28.1 --with python-multipart==0.0.20 --with requests --with redis==8.1.0 --with jsonschema==4.23.0 --with numpy==2.2.6 python -c "import runpy; runpy.run_path('evidence/reviews/R-N/probes.py', run_name='__main__')"
```

Initial bare Python lacked pytest; an unpinned FastAPI run produced 38 passes and a route-introspection incompatibility. Repeating with the repository's FastAPI pin yielded the 39 passes above; this was an environment mismatch, not a reported product bug. Cached test dependencies changed no repository manifests. The first editor run lacked the worktree dependency junction; it passed after the required junction was created.

Skipped: source fixes, web build (no web changes), headed Clerk/browser E2E, container build, deployed environment/volume/secret inspection, live model injection testing, GPU allocation, billing reconciliation and real paid calls. Static image-recipe observations do not prove current Railway runtime contents. No credentials or private owner media used. Residual risk: current passing unit tests do not cover the demonstrated production-path gaps; do not treat this as paid/live DEV clearance.
