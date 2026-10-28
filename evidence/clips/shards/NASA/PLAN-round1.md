# S02c1 PLAN — NASA real Earth drop/trajectory shard

- Start: 2026-10-27T22:46:36Z. Lane CODEX-2, Opus 5.5 / high (orchestrator-assigned). Base 8c6e486, branch run/S02c1, worktree .worktrees/S02c1.
- Objective: assess NASA Image and Video Library *real* Earth fall/drop/swing-release footage (not simulation/animation) for S02c coverage gap; record source/rights reads before any download, hashes/metadata, full-rate segment, original-frame evidence, limitations.
- Owns ONLY: evidence/clips/shards/NASA/, test-data/public/shards/NASA/.
- Not doing: RM05/FF05/RM06 repeats, clips.csv, canonical controls, merge, GPU, uploads, calibration/gate claims.
- Acceptance: (1) per-candidate metadata.json rights/credit read recorded; (2) local hash+ffprobe+scene-cut+frame sheet for any downloaded candidate; (3) verdict per candidate or explicit no-usable-result.
- Ponytail (full): reuse ffmpeg/ffprobe + existing evidence conventions; one small recorder script only if needed, with self-check.
