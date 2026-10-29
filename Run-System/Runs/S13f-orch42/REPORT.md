# S13f-orch42 REPORT — Connect SAM masks and Modal reconstruction

Status: **DONE** — both GPU stages now live-verified through Build/pipeline with validated output (reconstruct: S13f-orch30 live A10G run; segment: this run, live RM04 via the parameterized tracker with masks). Failures readable + retryable (offline tests).
Lane CODEX-1 contract; assigned anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled.
Issued 2026-10-29T21:27:26Z; started 21:28:02Z; work stopped/reported 21:34:38Z (verified DONE, early finish allowed; TIMEBOX.json `worker_timebox.py check` TIMING PASS); deadline 21:57:26Z. Base main 03e6c2f; branch run/S13f-orch42. Not merged (controller integrates).
Process note: my first apply_patch resolved against the canonical checkout (turn cwd) and edited main's gpu_stages.py; within ~1 min I copied it to the worktree and `git checkout -- Build/pipeline/gpu_stages.py` in canonical (canonical status clean except the owner's pre-existing untracked PDF).

## Changed (Owns only)
- [Build/pipeline/gpu_stages.py](../../../Build/pipeline/gpu_stages.py)
  - `sam_call(clip, first, last, prompt, object_id, raw_out)` now shells out to the F1-fixed documented CLI `modal run Build/measurement/runtime/modal_track.py --clip --first --last --prompt --object-id --out --masks` (same subprocess + UTF-8 env pattern as reconstruct; replaces the old in-process `app.run()` glue that needed a local modal client and hardwired object 2). Idempotent: a clean raw result on disk is reused (no 2nd paid dispatch); an errored raw is moved aside (`raw-result.failed-<utc>.json`) and redispatched; rc!=0 -> `segment-failure.log` + INVALID_INPUT (approval/clip/overwrite/arg text, never retried) or PROCESSING_FAILED (retryable).
  - `validate_segment(raw, prompt, object_id, frame_map=None)`: stages checkpoint/model_loaded/tracked, 64-hex checkpoint sha, `record.tracking.object_id` == requested, frame_map indices == stream frames with strictly increasing PTS (optional errata override), every frame has the object's box + centroid + COCO-RLE mask of exactly height x width pixels. Any violation -> PROCESSING_FAILED retryable with a one-line reason.
  - `segment(key, call, out, ledger, prompt, object_id, frame_map=None)` keeps the S13d JobRunner/StageError contract + ledger reserve; writes `segmentation.json` (per frame: index, pts_s, box, centroid_px, mask_rle for that object).
  - CLI: `segment <clip> <first> <last> <prompt> <object_id> <out> <ledger>` (live) and `replay <result.json> <prompt> <object_id> <out> [errata.json]` (offline, no spend). Reconstruct CLI form unchanged.
  - `ENV_FILE`: uses `<ROOT>/.env` when present (main checkout), else `../../.env` (run worktree) — the old hardwired `../../.env` only worked from .worktrees/<run>.
- [tests/pipeline/test_gpu_stages.py](../../../tests/pipeline/test_gpu_stages.py): SYNTHETIC SAM fixture with masks/record/frame_map; segment validate/reject table (CUDA error, wrong object, bad RLE size, missing frame mask, non-increasing PTS, errata override); sam_call CLI args/reuse/move-aside-retry/INVALID_INPUT; JobRunner retry/no-duplicate test updated.
- contracts/jobs/ unchanged (policy already lists segment/reconstruct, retries, never_retry).

## Ponytail (applied)
Reuse: the orch30 reconstruct subprocess pattern, `_tail`, `_write`, `reserve`, BAD_INPUT, JobRunner/StageError idempotency (out:<key>), modal_track's own plan/frames/no-overwrite guard (not re-implemented), cost_log.cost/reconcile for the cost record. Smallest complete: subprocess to the documented CLI instead of importing modal locally; validation is one function shared by live + replay. Skipped: a jobs-schema change for segmentation docs (no consumer yet), mask decoding/area stats, an object-id auto-picker.

## Fresh checks
- `python -m unittest tests.pipeline.test_gpu_stages tests.pipeline.test_jobs tests.pipeline.test_contracts tests.pipeline.test_keyframes tests.pipeline.test_understand tests.pipeline.test_uploads` -> **43 OK** (rerun after the ENV_FILE edit).
- Offline replay (zero cost) of accepted live S07b-param-orch40 RM04 result + errata frame_map: `python -m Build.pipeline.gpu_stages replay evidence/S07/S07b-param/RM04-chair-orch40/result.json chair 0 evidence/S13/S13f/replay-orch40 evidence/S07/S07b-errata/RM04-orch40-frame_map.json` -> [segmentation.json](../../../evidence/S13/S13f/replay-orch40/segmentation.json) sha 97fb6d51…d1df, 12 frames, f11 pts 0.44 (errata; original recorded 0.48).
- Negative replay: same result with object_id 2 -> `PROCESSING_FAILED retryable=True: segment: record tracks object 0, expected 2`, rc 1.
- **Live** (standing auth evidence/owner/S05/GPU-AUTHORIZATION.md; RM04 approved in evidence/owner/S02/APPROVAL.md; retries 0 = modal_track `retries=0, single_use_containers`; PYTHONUTF8=1):
  - pre 21:30:14Z `modal container list --json` -> `[]`.
  - 21:30:18Z `python -m Build.pipeline.gpu_stages segment RM04 0 11 chair 0 evidence/S13/S13f/live-orch42 evidence/S13/S13f/live-orch42/gpu-ledger.jsonl` -> rc 0 at 21:32:00Z, sha de4b1368…01b1. App ap-xI2mj9VGKy9OOcRAbUQFv8 (s07b-orch14-sam31-track) created 21:30:21Z, stopped 21:31:59Z, tasks 0. NVIDIA A10G (L4/A10G fallback list), remote 58.3 s, load 22.5 s, track 8.4 s.
  - Output [segmentation.json](../../../evidence/S13/S13f/live-orch42/segmentation.json): 12 frames, object 0 box+centroid+2160x3840 RLE each. Raw [raw-result.json](../../../evidence/S13/S13f/live-orch42/raw-result.json): `frame_sha256` identical to orch40 and `frame_map` identical to the errata (F1 PTS fix confirmed live: f11 0.44).
  - post 21:32:08Z containers `[]`; app stopped.
  - Ledger [gpu-ledger.jsonl](../../../evidence/S13/S13f/live-orch42/gpu-ledger.jsonl): 1 job, reserved $0.50 (cap $0.50). Cost [cost-log.json](../../../evidence/S13/S13f/live-orch42/cost-log.json): upper-bound estimate $0.0360 (98 s app lifetime x A10G+2 CPU+16 GiB list rates). Billed (read-only `modal billing report --for today -r h --json --show-resources` -> billing-post2.json, `python Build/gpu/cost_log.py cost-log.json billing-post2.json`, 21:34:17Z): **$0.02628** (A10G $0.01894, egress $0.00312, mem $0.00220, CPU $0.00201), GPU s billed 61.9. First read 21:32:40Z had no rows (billing-post.json). May still accrue; latest read wins. Post-reconcile containers `[]` (21:34:23Z).

## Findings (no edits outside Owns)
- F4 (S07 lane): live raw shows `preflight_exit 2`, `preflight.ok/dependency_ok/runtime_ok false` while the model loads and tracks (same as orch40). Preflight is reported, not gating; the validator does not require it. Worth reconciling in the S07 lane.
- F5: wrong-object output is classed PROCESSING_FAILED retryable (output doesn't match request); the CLI never returns that in practice since object_id is passed through.
- orch30 F3 (clips.csv RM04 owner_approved drift) not rechecked.

## Limits / not claimed
Segmentation of one chair (object 0) on RM04 f0-11 only; no Gate R/M, calibration, metric scale or physical claim. No combined segment+reconstruct JobRunner run live (each stage live-verified separately; JobRunner chaining offline-tested). Media (frames/npz) stay local; only JSON committed.
Communication: silent; one completion message to controller chat.
Skipped/unchecked: later billing accrual (re-run cost_log on a fresh report); real-Redis lease. Risk: `raw-result.json` reuse trusts the on-disk file (owned evidence dir only); ledger rows keep billed_usd null (billed lives in cost-log.json).
