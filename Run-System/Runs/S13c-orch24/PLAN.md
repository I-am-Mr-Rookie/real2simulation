# S13c-orch24 PLAN

- Run S13c (controller contract S13c-orch24); lane CODEX-1; assigned anthropic/claude-opus-5-5/high; OpenCodex-managed, not polled.
- Issued 2026-10-29T15:02:52+00:00; deadline 2026-10-29T15:32:52+00:00; minute-25 cutoff 15:27:52Z. Base main 57deb4b.
- Objective: extract keyframes + metadata with ffmpeg/ffprobe; every keyframe carries its original (ffprobe pts / best_effort_timestamp) time and clip provenance from the clips.csv licence row.
- Owns: Build/pipeline/; contracts/jobs/; tests/pipeline/; Run-System/Runs/S13c-orch24/.
- Checks: (1) synthetic VFR lavfi clip -> keyframe times equal the forced non-uniform times; (2) nonzero start offset preserved (not rebased to 0); (3) provenance copied from csv row, unlicensed/NC/ND/mismatched path rejected; (4) one approved clip (RM02) read-only, outputs in temp, never committed.
- No Modal/spend, no installs, no media committed.
