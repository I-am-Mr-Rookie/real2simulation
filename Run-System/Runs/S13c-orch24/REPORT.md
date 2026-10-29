# S13c-orch24 REPORT — DONE

- Task S13c: extract ffmpeg keyframes and metadata. Lane CODEX-1; model anthropic/claude-opus-5-5/high (as assigned); coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable); Modal/API spend $0.
- Issued 2026-10-29T15:02:52+00:00; work 15:03:22Z–15:09Z; deadline 15:32:52+00:00 (Dhaka 21:32:52+06:00). Base main 57deb4b; branch run/S13c-orch24; worktree .worktrees/S13c-orch24. Not merged to main (contract: no writes to canonical root; controller integrates).

## Acceptance: keyframes have original timestamps and clip provenance — MET (synthetic + 3 approved local clips)

- Synthetic VFR mp4 (lavfi, frame n at n²·10 ms, keys forced at n=0,5,12): manifest times exactly [0.0, 0.25, 1.44] s from ffprobe pts — not index/fps.
- Synthetic mkv with +3 s container offset: times [3.0, 4.0], start_time 3.0 (not rebased to 0).
- Provenance copied from clips.csv row; missing row, empty/NC/ND licence, or path ≠ row local_path rejected (INVALID_INPUT). >60 s clip and non-video rejected.
- Read-only approved clips (APPROVAL.md scope: local pipeline work), outputs in %TEMP%, deleted after; source SHA256 unchanged:
  - RM02 (Pexels, Andy Barbour): 6 keyframes [0, 3.042, 6.042, 9.083, 12.125, 15.167] s, 17.75 s, 24/1.
  - PD04 (CC-BY-SA-4.0, MikeRun): 600 keyframes (all-intra), 20 s.
  - PD06 (CC-BY-SA-4.0, Spheroidite): 280 keyframes, 9.532 s, avg 29992/1021.
  This is extraction evidence only: no scene, tracking, calibration, gate or physical claim.

## Files (Owns only)

- Build/pipeline/keyframes.py (new): provenance(), metadata(), keyframe_times(), extract(), CLI.
- tests/pipeline/test_keyframes.py (new): 5 tests, synthetic lavfi clips in temp dir.
- contracts/jobs/CONTRACT.md: "Keyframes stage output (S13c)" section (manifest fields, rejection rules, output_sha256 = manifest hash).
- Run-System/Runs/S13c-orch24/{PLAN.md,REPORT.md,TIMEBOX.json}.

## Fresh checks

- `python -m unittest tests.pipeline.test_keyframes tests.pipeline.test_contracts tests.pipeline.test_uploads` → Ran 20, OK (S13a/S13b tests still green).
- `python -m Build.pipeline.keyframes <ID> <canonical clip> <temp> <canonical clips.csv>` for RM02/PD04/PD06 → results above; temp removed.
- First VFR run failed (times 0.3/1.4): synthetic encoder timebase defaulted to 1/10; fixed the test fixture with `-enc_time_base 1/1000` (the extractor itself was correct).

## Ponytail (full) — reuse / smallest complete change

- Reused: UploadError (code semantics), POLICY max_duration_s and ROOT from contracts.py, sha256 streaming pattern from uploads.py, real clips.csv header for test rows; installed ffmpeg/ffprobe 8.1.1 via subprocess; stdlib csv/json. No new deps, no schema change (manifest documented in CONTRACT.md; jobs.schema.json untouched so S13a schema tests stay valid).
- One ffprobe decode (`-skip_frame nokey`) for times and the same flags for ffmpeg extraction with `-fps_mode passthrough`; frame-count equality asserted instead of a second matching pass.
- Skipped (not asked): sampling/max-keyframe cap, schema entry for keyframe_manifest, upload-sourced (non-clips.csv) provenance, rotation/attached-pic stream handling, PNG output.
- Shortcut comment: all ffmpeg/ffprobe failures map to INVALID_INPUT (never_retry); split transient IO codes in S13d.

## Risks / next

- Structural: all-intra clips yield every frame (PD04: 600 JPEGs). Paid `understand` (S13e) must sample/cap frames before spend.
- Provenance ≠ use approval; CSV flags still UNAPPROVED_CANDIDATE; scoped approval only via APPROVAL.md.
- `-select_streams v:0` assumes first video stream is the clip (cover-art mp4 unhandled).
- Communication: silent; one completion message to controller as authorized.
