# S07b-orch13 PLAN

- Issued 2026-10-29T10:56:09+00:00; deadline 11:26:09Z; cutoff 11:21:09Z. Work start 10:56:37Z.
- Model: anthropic/claude-opus-5-5 high (assigned). OpenCodex-managed; not polled.
- Branch run/S07b-orch13 @7303bc5, worktree C:/Users/HP/.codex/worktrees/s07b-orch13.
- Objective: one bounded private Modal GPU run: SAM3.1 source preflight -> gated checkpoint via provisioned secret name `real2simulation-hf-read` -> SHA/size verify -> existing adapter on approved ST03 prefix -> sanitized centroid track.
- Owns: Build/measurement/tracking.py; Build/measurement/TRACKING.md; Build/measurement/runtime/; tests/measurement/test_tracking.py; evidence/S07/S07b/; Run-System/Runs/S07b-orch13/.
- Budget: <=$2 all-in reservation; 1 GPU job (L4, A10G fallback), timeout 900s, retries 0, max_containers 1; ephemeral `modal run` only; verify stop.
- Ponytail: reuse tracking.py/preflight.py/lock unchanged; one new script modal_track.py; no new deps.

