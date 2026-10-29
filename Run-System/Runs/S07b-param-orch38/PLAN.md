# S07b-param-orch38 PLAN
Started 2026-10-29T20:47:55+00:00 (issued 2026-10-29T20:45:54+00:00; deadline 21:15:54Z; cutoff 21:10:54Z). Model anthropic/claude-opus-5-5/medium; OpenCodex-managed, not polled. Project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
Objective: review/fix orch36 WIP parameterizing modal_track.py (clip, frames, prompt, out, object_id, opt-in RLE masks; defaults = accepted ST03; never overwrite evidence), offline tests, then <=1 bounded Modal SAM3.1 run on approved RM04 (cap $0.50, retries 0, ledger, billed reconcile, containers [] after).
Owns: Build/measurement/runtime/; Build/measurement/tracking.py; tests/measurement/; evidence/S07/S07b-param/; Run-System/Runs/S07b-param-orch38/.
Checks: unittest test_modal_track + test_tracking; dry-run frame extraction; live run receipt.
