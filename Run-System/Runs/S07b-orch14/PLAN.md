# S07b-orch14 PLAN

- Issued 2026-10-29T11:27:38Z; deadline 11:57:38Z (Dhaka 17:57:38); minute-25 cutoff 11:52:38Z. Work start ~11:28:50Z.
- Model anthropic/claude-opus-5-5 high; OpenCodex-managed, not polled. Branch run/S07b-orch14, worktree .worktrees/S07b-orch14.
- Objective: root-cause and fix SAM3.1 multiplex propagate_in_video 0-batch RuntimeError (orch13), then bounded Modal A10 job(s) to emit a sanitized ST03-prefix track (frame/time coordinates + provenance). Not calibration, not Gate M.
- Owns: Build/measurement/tracking.py; Build/measurement/TRACKING.md; Build/measurement/runtime/; tests/measurement/test_tracking.py; evidence/S07/S07b/; Run-System/Runs/S07b-orch14/.
- Budget: <=$2 all-in, retries 0, max 1 container, stop + containers [] after each job. Secret by name only.
- Checks: test_tracking.py passes; Modal job stages include "tracked" with a sanitized record; containers [] after.
