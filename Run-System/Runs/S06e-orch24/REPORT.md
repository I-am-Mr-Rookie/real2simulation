# S06e-orch24 REPORT — DONE

Lane CODEX-1; model anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Issued 2026-10-29T15:02:44+00:00,
worker start 15:03:21Z, end 2026-10-29T15:19:26+00:00 (deadline 15:32:44+00:00). Base main 57deb4b; branch run/S06e-orch24 (not merged; controller integrates).

## Result (acceptance: scene logs include cold start, GPU seconds, estimated vs billed cost)
- New Build/gpu/cost_log.py: scene_log() builds receipt s06e-scene-log/1 (timing, GPU seconds estimated/upper/billed,
  cost estimated/upper/billed at Modal list rates); reconcile() fills billed ONLY from this app's rows of the read-only
  `modal billing report --json --show-resources`; no rows -> billed stays "unavailable" with reason. CLI reconciles a log file.
- Build/gpu/scene_job.py: container returns container-start (module import), function start/end epochs, model-load and
  inference seconds; local entrypoint times the call and writes <out>/<scene>-scene-log.json BEFORE bundle conversion.
- One bounded A10G run, RM02 (approved, same frames as S05b/S06d), app ap-HT56BJbqGtr7qg1pdadmu0, retries 0, no image
  rebuild: evidence/S06/S06e/RM02-scene-log.json — container boot 6.46 s, cold start 10.81 s, model load 19.73 s
  (ready 30.54 s), inference 1.45 s, function 21.72 s, round trip 39.55 s; GPU seconds est 28.07 / upper 41.55 /
  billed 30.01; cost est $0.01032 vs billed $0.01135 (est - billed = -$0.00103, ~2 s pre-import boot billed) vs upper $0.01528.
  Cap $0.30; ledger evidence/S06/S06e/job-ledger.json. Containers [] and app stopped/0 tasks after (post-verify.txt; [] again 15:18:35Z).
- Honest failure detail: client rc=1 — remote GPU work returned, then the local uv client env lacked jsonschema for
  validate_scene. Log + npz were already written; the bundle was completed OFFLINE with system python
  (validate.txt PASS x2), no second Modal call. First attempt 15:10:01Z died in uv (--env-file path with spaces) before any Modal call.
  README now documents the working command (run from event root, --with numpy --with jsonschema).
- Billing lag observed: 15:12:14Z read gave a partial $0.00514 / 13.98 GPU s; 15:18:32Z read $0.01135 / 30.01 s.
  Latest read wins; may still change — recheck with cost_log.py.

## Files
Build/gpu/{cost_log.py, test_cost_log.py, scene_job.py}; infra/modal/README.md (S06e section);
evidence/S06/S06e/{.gitignore, job-ledger.json, RM02-scene-log.json, scene-RM02-gpu.json, run-log.txt, post-verify.txt,
billing-pre-today-hourly.json, billing-pre-month.json, billing-post-today-hourly.json, tests.txt, validate.txt};
media (npz, PLY) in gitignored evidence/S06/S06e/local/. Run-System/Runs/S06e-orch24/{PLAN.md, TIMEBOX.json, REPORT.md}.

## Checks (fresh)
- python -m unittest discover -s Build/gpu: 21 OK (5 new: timing/estimate math, list rates reproduce one ~26 s lifetime
  from the three independently billed S06d resources, billed only from own app rows, missing rows stay unavailable,
  missing remote timing refused). contracts/scene: 11 OK. image_spec.py rc 0. validate_scene on RM02 bundle: PASS.
- Rates A10G $0.000306/s (modal.com/pricing via pre-reset READINESS.md), CPU $0.0000131/core-s, Memory $0.00000222/GiB-s:
  cross-checked by back-solving S06d's billed rows (all ~26.0 s); not re-read from the live pricing page this run.

## Ponytail (applied, full)
- Reuse: S06d scene_job + decorator, S06b RUNTIME_IMAGE/load_model, validate_scene, offline npz path (finished the bundle
  without re-running GPU), S06b/S06d uv+modal 1.6.3 + read-only billing/container procedure, existing billing CLI JSON
  (--show-resources gives per-resource billed; GPU seconds back-solved, no API client added).
- Smallest complete: one pure module + one test; 3 return fields + timestamps in scene_job; resource constants hoisted
  once so decorator and estimate cannot drift. No new deps, no image change, no extra GPU job.
- Skipped: auto-fetch of billing inside the entrypoint (report lags; separate reconcile is honest), RM04/RM05, S06f
  <=5 min target, AWS adapter, any change to Modal billing/account.

## Limits / risks
- Not Gate R, not calibrated scale, not physical evidence. Client/container clocks differ (NTP), sub-second skew possible.
- container_boot_s starts at module import; image pull/runtime start before Python is only visible in billed seconds.
- Billed figure may still accrue; billed GPU seconds are back-solved at list rate (discounts/credits would skew it).
- Total new Modal spend ~$0.0113 billed (cap $0.30). Communication: silent; one completion line to controller only.

Next: S06f (one licensed room clip, <=5 min including cold start) can use this receipt directly.
