# S13h-orch46 REPORT — Measure dev upload-to-scene path

Status: **DONE** — approved RM04 went upload -> validate -> keyframes -> live SAM3.1 segment -> live MapAnything reconstruct -> viewer-loadable scene in **144.4 s** (< 360 s policy job_deadline_s / 6 min). Retry tests pass (52 OK offline). Measured on the pipeline CLI path: there is no upload route in Build/api or Build/web (finding F1).
Lane CODEX-1; assigned anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled. Tokens: unknown/unobservable. Modal billed **$0.03641** (2 jobs); Meta $0.
Issued 2026-10-29T21:41:29Z; started 21:42:12Z; work stopped/reported 21:50:10Z (verified DONE, early finish allowed); deadline 22:11:29Z. Base main 1e052d4; branch run/S13h-orch46. Not merged (controller integrates).

## Measured timeline (evidence/S13/S13h/live/timing.json, UTC)
| stage | start | elapsed s | result |
|---|---|---|---|
| upload | 21:44:56.129 | 0.18 | UploadService, 4 x 8 MiB chunks, 25,336,829 B; complete() verified whole-file sha 8231fbca…87ec |
| validate | 21:44:56.313 | 0.07 | data.part sha == clips.csv RM04 file sha |
| keyframes | 21:44:56.385 | 1.04 | 4 keyframes + provenance manifest (Pexels License) |
| segment (Modal) | 21:44:57.425 | 74.48 | app ap-I8urJxSA6u5zks1vnroxDn, NVIDIA A10, chair object 0 frames 0-11; segmentation.json sha 95f5a778…0f3e, 12 frames with box/centroid/RLE |
| reconstruct (Modal) | 21:46:11.905 | 68.62 | app ap-DhO27sNHIL7LrJaS9F9Pjo A10G; cold start 29.0 s, model load 21.5 s, inference 1.7 s; reconstruction.json sha 1dd6f90b…e5c5 |
| viewable | 21:47:20.529 | 0.00 | scene rm04-mapanything-s06d, 20,000 points, synthetic=false |
Total 144.4 s; within_deadline true. GPU stages = 99% of time; cold start + model load dominate both (structural bottleneck: two sequential cold Modal apps; warm/combined container or running segment||reconstruct would cut ~60 s).

Viewable checks (fresh): `python contracts/scene/validate_scene.py .../bundle/scene.json` -> PASS (not Gate R evidence); `node evidence/S13/S13h/viewer_check.mjs evidence/S13/S13h/live/reconstruct/bundle` -> viewer's own buildSceneModel (Build/web/src/viewer, unedited) ok, 20000 points, SCALE UNVERIFIED banner, gateEvidence false, 40 ms ([viewer-check.txt](../../../evidence/S13/S13h/viewer-check.txt)).

## Changed (Owns only)
- [Build/pipeline/e2e.py](../../../Build/pipeline/e2e.py) (new): `python -m Build.pipeline.e2e CLIP FIRST LAST PROMPT OBJECT_ID RECONSTRUCT_MANIFEST OUT_DIR [CLIPS_CSV]` drives existing modules stage by stage, writes timing.json after each stage, stops at the first failure (measured failure record).
- [tests/pipeline/test_e2e.py](../../../tests/pipeline/test_e2e.py) (new, 2 SYNTHETIC tests): all stages -> viewable; segment PROCESSING_FAILED -> status failed, reconstruct never called.
- [evidence/S13/S13h/](../../../evidence/S13/S13h/): timing.json, gpu-ledger.jsonl (2 rows, $0.50 reserved each = $1.00 cap), segment raw-result/segmentation/cost-log, reconstruction.json + bundle scene.json + scene-log, keyframes manifest, upload meta.json, billing-post(2).json, containers-pre/post/post2.json, apps-post.json, viewer_check.mjs. Not committed: point-cloud PLYs/npz, keyframe JPGs; upload data.part (copy of the clip) deleted after the measurement.
- contracts/jobs/ unchanged (policy already defines the stages and job_deadline_s 360).

## Ponytail (applied)
Reuse: UploadService (chunking + sha verify), keyframes.extract, gpu_stages.sam_call/segment/reconstruct (ledger budget guard, UTF-8 Modal env, bundle validation), cost_log.py reconcile, contracts/scene validator, the viewer's buildSceneModel. Smallest complete: one ~90-line timing driver + 2 tests; no new route, store, dependency or retry code. Skipped: an HTTP upload/job route (Build/api|web outside Owns), live understand (Meta spend not in this run's budget), driving through JobRunner (its understand stage would need a live Meta call or a fake success; retry behaviour stays covered by tests).

## Fresh checks
- `python -m unittest tests.pipeline.test_e2e tests.pipeline.test_progress tests.pipeline.test_gpu_stages tests.pipeline.test_jobs tests.pipeline.test_contracts tests.pipeline.test_keyframes tests.pipeline.test_understand tests.pipeline.test_uploads` -> **52 OK** (50 prior + 2 new; retry/backoff/never-retry/no-duplicate-dispatch tests included). `python -O -m unittest tests.pipeline.test_e2e tests.pipeline.test_jobs` -> OK.
- Modal (standing auth evidence/owner/S05/GPU-AUTHORIZATION.md; RM04 approved evidence/owner/S02/APPROVAL.md; retries 0; PYTHONUTF8=1): 2 jobs, cap $1.00 / $0.50 each reserved in ledger. Billed (read-only billing report 21:48:33Z and re-read 21:49:15Z, unchanged; `python Build/gpu/cost_log.py`): segment **$0.02261** (A10G $0.01406, egress $0.00532, mem $0.00164, CPU $0.00160; 45.9 GPU s), reconstruct **$0.01380** (A10G $0.01148; 37.5 GPU s). Total $0.03641. Report may still accrue; latest read wins.
- Containers: pre 21:44:40Z showed ONE foreign container (app ap-cKH0R4xXlsZqus6i4Sk7wY s07b-orch14-sam31-track, started 21:44:21Z before this run — another worker); post 21:47:29Z showed another foreign one (ap-2Sbu8Pen5jJhHlNxAhuva6, created 21:46:42Z, after my segment app stopped). Both my apps stopped, tasks 0; final `modal container list` 21:49:25Z -> **[]**.

## Findings
- F1: no upload/job HTTP route exists (Build/web/src/app/api has only lab/; Build/api only health). The <6 min figure is the pipeline CLI path with local chunk upload (0.18 s), NOT a network upload to Railway dev; a 25 MB browser upload adds network time. Owner of Build/api|web should add POST upload chunks + GET job progress (S13g feed).
- F2: downstream binding is by clip id + sha, not by the uploaded file: keyframes.provenance requires the clips.csv path; modal_track reads the canonical test-data file; reconstruct used the existing S05c 518-px frame manifest (same source sha 8231fbca…). Bytes are identical (verified), but an unlisted user clip cannot flow through today.
- F3: understand (Meta) not in this measurement; S13e measured it separately. Add its latency for a full-pipeline figure.
- F4 (carried): segment default frame_map used (no errata override here); S07 preflight_exit drift not rechecked.

## Limits / not claimed
Single run, n=1, cold Modal both times; no Railway deploy touched; no gate, physical, metric-scale or real-scene-quality claim (MapAnything nominal scale). Communication: silent; one completion message to controller chat.
Next: Build/api|web owner wires upload + progress routes over UploadService/JobRunner and re-measures over the network.

