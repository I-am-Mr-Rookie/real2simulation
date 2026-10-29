# S06e-orch24 PLAN

Objective (QUEUE S06e): scene logs include cold start, GPU seconds and estimated versus billed cost.
Lane CODEX-1; anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Base main 57deb4b; branch run/S06e-orch24.
Issued 2026-10-29T15:02:44+00:00; deadline 15:32:44+00:00; minute-25 cutoff 15:27:44+00:00. Worker start 15:03:21Z.

Owns: Build/gpu/; infra/modal/; evidence/S06/; Run-System/Runs/S06e-orch24/.

Steps
1. Offline first: Build/gpu/cost_log.py (pure timing/estimate/reconcile + read-only reconcile CLI) + test; scene_job.py
   returns container/function epochs, model-load and inference seconds; local entrypoint writes <scene>-scene-log.json.
2. One bounded A10G run of existing approved RM02 scene job (standing auth evidence/owner/S05/GPU-AUTHORIZATION.md),
   cap <=$0.30 all-in reservation, retries 0, max 1 container; ledger evidence/S06/S06e/job-ledger.json before launch.
3. Verify no running containers/app stopped; reconcile billed from read-only 'modal billing report --json --show-resources';
   if no rows yet, billed=unavailable with reason (never invented).
Checks: unittest discover Build/gpu; validate_scene on bundle; image_spec dry run.
Not claimed: Gate R, calibration, physical evidence, S06f <=5 min target.
