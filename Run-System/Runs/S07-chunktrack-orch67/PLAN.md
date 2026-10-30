# S07-chunktrack-orch67 PLAN

Issued 2026-10-30T05:07:12Z; deadline 05:37:12Z; cutoff 05:32:12Z. Lane CODEX-1 (S07/S12); assigned anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled).
Branch run/S07-chunktrack-orch67 from main a2fa169.

Objective: smallest memory-bounded long-segment mode in Build/measurement/runtime/modal_track.py (--chunk N: one SAM session per
chunk, 1-frame overlap, re-seed by IoU>=0.5 of the text-prompt object against the previous chunk's last selected mask, fail closed;
per-chunk sealed source-frame/PTS/frame-SHA provenance; presentation-map PTS from existing _pts; RLE format unchanged), offline tests,
then real Modal jobs: PD02 f0-438 (whole clip; >=1.25 period coverage measured afterwards), BN01 one arc if time allows.

Owns: Build/measurement/runtime/; tests/measurement/test_modal_track.py; evidence/S07/S07-chunktrack-orch67/; Run-System/Runs/S07-chunktrack-orch67/.
Checks: python -m unittest tests.measurement.test_modal_track; validate_segment (call only) on each job result; modal app/container list [] after.
Budget: per job reservation <=$1 (timeout 1500 s x A10G+CPU+mem list rates = ~$0.55), run total <=$2.50, retries 0, stop on error.
No gate claims; Gate M and Gate RS remain NOT_MET.

