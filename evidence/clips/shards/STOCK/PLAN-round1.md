# S02c2 PLAN — STOCK shard (Pexels/Pixabay)

- Start (UTC): 2026-10-27T22:46:30Z. Timebox 30 min; no new implementation after minute 25.
- Lane/model: CODEX-2 ownership, S02c owner exception, requested Opus 5.5 high (runtime identity not independently observable).
- Base: retained `8c6e486`; branch `run/S02c2`; worktree `C:/Users/HP/.codex/worktrees/s02c2/...` (not `.worktrees/S02c`).
- Objective: find non-sports Pexels/Pixabay real Earth fall/bounce/projectile footage; read actual source/licence page before any provisional local download (Q2); full-rate original-frame review; record hash/metadata/attribution/limitations in a candidate manifest, or an explicit no-usable-result verdict.
- Owns ONLY: `evidence/clips/shards/STOCK/`, `test-data/public/shards/STOCK/`.
- Not touched: clips.csv, canonical controls, parent worktree, RM0x/PD0x/FF0x prior work, blocked sources (no retries/bypass).
- Reuse: existing `evidence/clips/s02c_opus_review.py`/`s02c_opus_blobcrops.py` patterns (median-background blob tracking + crop sheet) and ffprobe/ffmpeg.
- Acceptance: (1) every downloaded file has source/licence/creator read from the page + sha256 + ffprobe metadata; (2) each candidate has full-rate reviewed segment with frame evidence and limitations; (3) clean commit on run/S02c2.
