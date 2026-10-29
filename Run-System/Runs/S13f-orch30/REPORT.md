# S13f-orch30 REPORT — Connect SAM masks and Modal reconstruction

Status: **PARTIAL** (reconstruct live-verified; segment offline-only — see finding F1). Lane CLAUDE, anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled.
UTC start 2026-10-29T15:43:22Z (issued 15:42:44Z); work stop/report: see TIMEBOX.json. Base main 90d6f45; branch run/S13f-orch30.

## Changed (Owns only)
- [Build/pipeline/gpu_stages.py](../../../Build/pipeline/gpu_stages.py) — JobRunner workers `reconstruct(key, scene, manifest, out, ledger)` and `segment(key, call, out, ledger, prompt)`, `reserve()` GPU ledger guard (<=2 jobs, <=$1, SPEND_PAUSED non-retryable), CLI for one live reconstruct.
  - reconstruct shells out to the documented, **unedited** S06d command (`uv run ... modal run Build/gpu/scene_job.py --scene --out --manifest`), re-validates the bundle with contracts/scene `validate_scene.validate`, writes `reconstruction.json` (sha returned to JobRunner). rc!=0 -> INVALID_INPUT (approval/licence/SHA/frames text, never retried) or PROCESSING_FAILED (retryable), message = last meaningful line (Rich box borders stripped); full output in `reconstruct-failure.log`.
  - segment wraps the **unedited** S07b `modal_track.track` return (JSON text): rejects `error`, missing stages checkpoint/model_loaded/tracked, empty stream, bad checkpoint sha -> PROCESSING_FAILED retryable; writes `segmentation.json`.
- [tests/pipeline/test_gpu_stages.py](../../../tests/pipeline/test_gpu_stages.py) — 5 offline tests (fake launcher + fake SAM call, synthetic npz via reused S06d `fake_npz`/`build_bundle`).
- `sam_call(frames, metadata, frame_map, prompt)`: live call() for segment that runs the S07b `track` function in an ephemeral app via `modal_track.app.run()`, bypassing its ST03 local entrypoint (which writes accepted evidence). Tested with a fake module only (no modal client locally; not dispatched).
- contracts/jobs/ unchanged (stages segment/reconstruct, retries, never_retry already in policy.json).

## Ponytail (applied)
Reuse: JobRunner/StageError/out:<key> idempotency (S13d) for retry + no duplicate dispatch — no new retry code; S06d documented CLI + `build_bundle`; contracts/scene validator; S06d test `fake_npz`; understand.py's reserve/ledger pattern; cost_log.py for billed reconcile. Smallest complete: subprocess over the documented command instead of importing Modal locally (no modal client installed); one module, no new deps/config. Skipped: live SAM dispatch (F1), a live segment CLI, contract doc edits (policy already covers stages).

## Fresh checks
- `python -m unittest tests.pipeline.test_gpu_stages` -> 5 OK (validated reconstruct bundle; INVALID_INPUT vs PROCESSING_FAILED readable; SPEND_PAUSED guard; segment accept/reject; JobRunner: segment fails once -> retried -> ready, job-2 same input reuses every out:<key>: SAM calls 2, scene_job launches 1, unchanged).
- All pipeline modules: `python -m unittest tests.pipeline.test_gpu_stages tests.pipeline.test_jobs tests.pipeline.test_contracts tests.pipeline.test_keyframes tests.pipeline.test_understand tests.pipeline.test_uploads` -> 43 OK (6 in test_gpu_stages incl. sam_call glue).
- Segment validator vs REAL recorded SAM3.1 output (zero cost, no dispatch): accepted S07b `evidence/S07/S07b/orch14/result.json` (stages preflight/checkpoint/model_loaded/tracked, 19 stream frames) passes -> `Run-System/Runs/S13f-orch30/replay/segmentation.json` sha 54798a33bbd54e650eaf7309b936875869f66d16e78326c54e7dad44dd50e4e1 (replay of existing evidence, not a new run).
- Live bundle re-check: `python contracts/scene/validate_scene.py Run-System/Runs/S13f-orch30/live/bundle/scene.json` -> PASS rm04-mapanything-s06d synthetic=False.
- Live budget guard: a third `python -m Build.pipeline.gpu_stages RM04 ...` -> `SPEND_PAUSED retryable=False: GPU budget guard: 2 jobs, reserved USD 1.00`, rc 1, refused before any Modal call.
- Live Modal (standing auth evidence/owner/S05/GPU-AUTHORIZATION.md; RM04 approved per evidence/owner/S02/APPROVAL.md line 6; same SHA-verified S05c frames as S06f, manifest .worktrees/S05c-orch19/evidence/S05/S05c/input.json, read-only):
  - pre: containers [] (15:49:31Z), billing-pre.json read.
  - Job 1 (15:49:49Z, app ap-m9eoiasur296tPH8QzLfvg): rc 1 in ~10 s, **0 tasks, no GPU container, 0 billing rows**. Error message was an unreadable Rich border line -> fixed (_tail strips borders; failure log kept). Root cause hypothesis (not proven): piped Modal CLI on Windows cp1252 crashed printing glyphs (Rich used ASCII legacy box); fix = UTF-8 child env. Client exit left the ephemeral app until Modal stopped it at 15:52:58Z (0 tasks).
  - Job 2 (15:52:18Z, app ap-RJiTvMGO3RGcMEFJ1DHgqS): rc 0, A10G, round trip 53.2 s, cold start 25.2 s, inference 1.46 s; bundle validated, 20000 points; `live/reconstruction.json` sha returned. Same idempotency key as job 1 (no out recorded for job 1, so redispatch was correct).
  - Billed (read-only `modal billing report` 15:54:32Z, `python Build/gpu/cost_log.py`): **$0.01141** (A10G $0.00920, mem $0.00107, CPU $0.00079, egress $0.00035); est $0.01040; GPU s billed 30.1. Report may still accrue; latest read wins. Total reserved $1.00 (2 rows) = cap; spent ~$0.011. retries 0 (entry point).
  - post: containers [] ; both apps stopped, tasks 0.

## Findings for owning lanes (no edits made outside Owns)
- **F1 (S07 lane, blocks live segment):** Build/measurement/runtime/modal_track.py is hardwired to ST03 frames 58-76, OBJECT_ID 2, prompt "apple", and its local entrypoint writes `evidence/S07/S07b/orch14/result.json` (would overwrite accepted evidence). It returns ids/boxes/tracking record, **never masks**. Needs clip/frames/out parameters (and a mask/RLE output if masks are required) before the pipeline can run segment on a room clip. Also only room IDs run in scene_job, so both GPU stages cannot run on "one approved clip" today. Live segment was therefore not dispatched; budget was also fully reserved.
- **F2 (S06 lane / infra):** README command assumes an interactive console; when piped from Python on Windows it can fail (job 1). gpu_stages sets PYTHONIOENCODING/PYTHONUTF8; consider documenting.
- F3: clips.csv still marks RM04 `owner_approved NO / UNAPPROVED_CANDIDATE` while APPROVAL.md approves RM04 — control drift for the S02 lane.

## Evidence (committed small JSON only; npz/ply media stay local, untracked)
`Run-System/Runs/S13f-orch30/live/`: reconstruction.json, bundle/scene.json, bundle/RM04-scene-log.json, gpu-ledger.jsonl, billing-pre.json, billing-post.json.

## Limits / not claimed
No masks produced; no live SAM; no Gate R/M, calibration, physical scale or real-scene correctness claim (MapAnything nominal scale, gravity unknown). Not merged to main (controller integrates). Communication: silent; one completion message to controller.
Skipped/unchecked: live segment; real-Redis lease; billed figure may still accrue. Risk: ledger counts reservations, not billed, so a failed no-GPU attempt still consumes a job slot (conservative by design).
