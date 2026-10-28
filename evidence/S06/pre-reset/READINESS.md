# S06p — useful GPU work before reset

Observed Oct28, 2026 Asia/Dhaka (Oct27 22:31–22:40 UTC). This is readiness evidence, not permission to run jobs.

## Baseline and account access

**Owner-validated planning baseline retained:** approximately20 GPU-hours needed, approximately15h current Modal allocation, reset on/after Nov1. Approximately5h remains for after the observed reset if still useful. None is a measured consumption target.

| Check | Observation / limitation |
|---|---|
| Supported browser inventory | Only in-app browser and MCP Apps; no pre-existing tabs or authenticated Modal tab exposed. Native inventory timed out; no claim native control is unavailable. Native fallback was not needed/requested. |
| Existing-account read | Opened Modal homepage, followed visible Log in link. Fresh state: `https://modal.com/login?next=%2Fapps`, title `Sign in | Modal`, heading `Log in to Modal`, GitHub/Google/SSO choices and blank email field. Initial navigation snapshot timed out; subsequent state succeeded. No sign-in submitted. |
| Actual allowance, units, GPU class, credit bucket/expiry, usage limit, spend limit | Not visible without authenticated dashboard. Unknown operational values; NOT a rejection of the owner baseline. No credentials retrieved, CLI authentication, token endpoint calls or account creation. |
| Exact reset and timezone | Not exposed. Do not substitute Nov1 midnight, public free-tier marketing, or historic token authentication for account billing evidence. |
| Modal purpose-built connector | No Modal connector in exposed tools. Existing Railway tools do not answer Modal allocation questions. |

Account execution bookkeeping is therefore **blocked**, while read-only readiness acceptance is satisfied by this precise limitation. Owner fallback Q5 requests only a sanitized existing-account observation, not credentials or renewed approval of the estimates.

## Local runtime/dependency observations

Read-only `Get-Command` plus Python distribution metadata; no import of GPU libraries, install, build, image pull or remote invocation:

| Item | Actual observation |
|---|---|
| Python | 3.14.5, installed Python314 executable |
| Modal CLI / Python distribution | CLI absent from PATH; distribution NOT_INSTALLED in this Python interpreter |
| torch / torchvision / mapanything / trimesh | NOT_INSTALLED in this interpreter |
| numpy / opencv-python | 2.4.6 / 4.13.0.92 installed; not evidence of compatibility with selected reconstruction stack |
| nvidia-smi | Not on PATH; no assertion that the PC has no GPU |
| Docker | Client29.9.2; Linux daemon unavailable: named pipe `dockerDesktopLinuxEngine` not found. No daemon started. The formatting command returned exit0 despite the connection error; NOT a successful server probe. |
| Product GPU adapter | `git ls-files Build/gpu infra/modal` returned no tracked files at starting main. No S06 image, entry point, resource limits or billing instrumentation exists yet. |
| Existing S05 | Contracts/licence boundary only; no working reconstructor. Existing scene requirements pin jsonschema4.23.0, not the GPU stack. |

Pinned S05 sources in `evidence/S05/upstream/revisions.json` and `LICENSE_REVIEW.md` are the owning evidence. MapAnything README recommends Python3.12 and explicitly does not pin PyTorch/CUDA. Thus Python3.14 on this PC is NOT a verified target runtime. Later S06 work must pin Python3.12 plus compatible torch/torchvision/CUDA/base image and dependency licences, then measure actual memory. No numeric VRAM minimum is asserted here.

Use only `facebook/map-anything-apache`, weight revision `00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a`, code revision `3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9`, subject to installation-time source/dependency recheck. Default `facebook/map-anything` NC weights are excluded. SAM3D custom terms/manual access remain blocked: no access requests or terms acceptance. Primitive meshes are the approved fallback. No assets/weights downloaded.

## Spend reconciliation — enforce before any actual job

The older **$30 Modal live-budget baseline remains the conservative authorized ceiling**, not a verified cash/credit balance. The owner's15h allowance is a planning allocation, not automatic authorization to bill15h on any GPU. The guide's$100 offer is not account credit evidence.

Public reference rates read from [Modal pricing](https://modal.com/pricing): L4 $0.000222/s, A10 $0.000306/s, L40S $0.000542/s. Derived single-GPU, GPU-only costs: 15h = $11.988/$16.524/$29.268 respectively; 20h = $15.984/$22.032/$39.024. CPU, memory, storage and transfer are additional. These are scenarios, not selected GPU classes, account entitlement or runtime quotes. L40S15h leaves only$0.732 of a$30 ceiling before other charges; below the project's$5 upload-stop threshold. No GPU fits by declaration: actual VRAM/workload feasibility must be measured later.

[Modal budgets](https://modal.com/docs/guide/budgets) distinguishes gross usage limits before credits from net out-of-pocket spend limits. Default spend settings may permit paid charges. Environment limits do not encompass every Workspace charge. **No dashboard settings were inspected or changed.** [Billing](https://modal.com/docs/guide/billing) describes monthly and incremental charging; remaining credit alone is not a hard no-overage guarantee.

Before launch, a separately authorized executor must record:

1. Existing workspace, allocation unit, GPU class/count, applicable credit balance/expiry, exact cycle/reset timezone, usage consumed and remaining. Omit identifiers/payment details from committed evidence.
2. Gross usage cap and net spend limit, shared-workspace reservations/usage, whether a no-paid-overage stop is actually enforced. If safety cannot be established read-only, stop; changing settings needs separate authorization, not S06p.
3. Reserve worst-case job cost (GPU multiplicity × timeout × rate plus CPU/memory/storage/transfer and failure headroom) against the **minimum** of verified applicable remaining credits, gross usage headroom and unspent authorized$30 baseline. Separately enforce no paid overage and the below$5 new-upload stop while AWS pending. Do not add$30 to credits as extra spend authority.
4. Never convert the15h baseline to money without its actual units/class. If all20h cannot fit existing limits, shorten useful work / use approved fallback; log the conflict, do not buy, change billing, switch to AWS or expand limits. A reset refreshes verified entitlement, not automatically the project spending ceiling.

## Concrete conditional execution order (Asia/Dhaka)

**Earliest useful work now, Oct28:** this readiness/account check and CPU-only prerequisite preparation under their own authorized runs. **Earliest eligible GPU job:** S05b bounded reconstruction setup/probe only AFTER S02c + S02d + S02e complete, source/weight/dependency rights pass, compatible runtime is pinned, and account/budget preflight above clears. No eligible product GPU job was found now. S06p does not waive S05 or permit early S06a implementation.

| Window / order | Useful output and prerequisite | Stop / checkpoint |
|---|---|---|
| Oct28, first | Finish existing S02c in its separate lane; then S02d timebase/scale/rights review and S02e owner final-use approval. In parallel, resolve sanitized account Q5 and prepare dependency/version/licence review without jobs/uploads. | Provisional local acquisition Q2 is NOT final product/upload approval. No claim that any current candidate is fit. |
| Oct28–29, as soon as eligible | S05b → S05c → S05d → S05e: Apache-only reconstruction, scene conversion, metric scale/floor, GateR on approved inputs. Start one bounded scene before any batch. GateR target <=4 GPU min/scene is acceptance, NOT measured duration. | Capture input hash/licence, model and code revisions, peakVRAM, elapsed/cold/billed runtime, output and failures. Stop OOMs for diagnosis, not blind retry churn. |
| Immediately after measured GateR | Required other-vendor R-R review; S05f records measured pass or named fallback. Do not spend GPU time to fill the gap while waiting for review. | GateR thresholds unchanged; points/primitive meshes rather than blocked SAM3D. |
| Oct29–30 if S05 finishes | S06a → S06b pins/contracts and container; S06c records optional SAM3D blocked/fallback (not fake installation); S06d/e adds entrypoint and timing/cost. Then S06f one licensed room scene; S06g CPU dry-run/AWS-disabled check; S06h runtime checkpoint. | Image construction may have CPU/storage charges and uploads; later scope/approval required. Target <=5min including cold start remains unmeasured. No rerunning successful S05 outputs solely for quota use. |
| Oct30–31, remaining verified allowance | S13a–e contracts/queue only after S04/S06/S01 prerequisites; S13f/g integration and end-to-end scene, then later library artifacts only when S12/S13/S18 dependencies permit. Prioritize valid representative scenes, reproducible failures/fixes and cacheable artifacts. | Up to current~15h only on useful ready jobs, not a reservation to exhaust. Scene targets suggest actual usage could be far lower. Do not invent expensive training/repeated benchmarks. |
| On/after Nov1, **after observed reset** | Save before/after sanitized balance/reset evidence. Resume only missing representative scenes, failed-job fixes and integration regressions; approximate remainder~5h if measured need remains. Reuse cached outputs with valid provenance. | If refresh is later, shift remaining eligible work to the actual window; don't assume ET or Dhaka midnight. If it never appears before stop-work, reduce scope within existing allowance. |
| Nov3 18:00 freeze → Nov4 18:00 stop | Only authorized necessary fixes/verification; preserve final artifacts for demo. Stop all compute/session resources and reconcile ledger. | No scheduled work after Nov4 18:00 Dhaka; no judging deployment/publication/submission authorization inferred. |

The queue's S05→S06→S13 chain and footage approval are the structural bottlenecks, not a reason to defer all GPU work until November. Dates are conditional priorities, not completion forecasts. Missing a prerequisite changes the schedule, never the gate.

## Required per-job receipt (future runs; no rows claimed)

`job_id, input_sha256, clips_csv_revision, S02e_approval_ref, code_revision, model_revision, GPU_type, GPU_count, UTC_start/end, wall_seconds, billed_GPU_seconds, GPU_hours_sum_across_devices, peak_VRAM, cold_start_seconds, cost_reserved/actual, allowance_before/after_units, credit_before/after, output_hash/revision, status, resource_stopped_evidence`

AWS remains off until owner confirms us-east-2 quota AND creates$50 EC2 alert; stop GPU after each session. No personal media, archive data, sports or unlicensed clips. No purchases, uploads, secrets, accounts/terms or policy/routing changes occurred.
