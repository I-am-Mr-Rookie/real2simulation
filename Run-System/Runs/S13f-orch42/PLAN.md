# S13f-orch42 PLAN — wire pipeline segment stage to parameterized SAM3.1 tracker

Lane CODEX-1 contract, assigned anthropic/claude-opus-5-5/high; OpenCodex-managed, not polled. Base main 03e6c2f; branch run/S13f-orch42; worktree .worktrees/S13f-orch42.
Issued 2026-10-29T21:27:26Z; deadline 21:57:26Z (Dhaka 03:57:26); minute-25 cutoff 21:52:26Z.

Objective: segment stage of Build/pipeline/gpu_stages.py calls the F1-fixed parameterized Build/measurement/runtime/modal_track.py (clip/frames/prompt/object_id/out, --masks) and validates its output (ids/boxes/centroids/COCO-RLE masks, frame_map PTS); failures readable + retryable. Replay accepted live RM04 orch40 result offline with errata frame_map; at most one bounded live RM04 segment run (<=$0.50, retries 0) under evidence/owner/S05/GPU-AUTHORIZATION.md.

Owns: Build/pipeline/; tests/pipeline/; contracts/jobs/; evidence/S13/S13f/; Run-System/Runs/S13f-orch42/. No Build/measurement edits, no installs, no gate/physical claims.
Checks: tests/pipeline unittest; offline replay of orch40 result -> segmentation.json; one live pipeline segment run, containers [] after, ledger + cost log.
