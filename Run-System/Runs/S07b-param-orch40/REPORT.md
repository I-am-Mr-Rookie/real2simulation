# S07b-param-orch40 REPORT — DONE
Model anthropic/claude-opus-5-5/medium (OpenCodex-managed; not polled). UTC start 2026-10-29T21:17:52Z. Work stopped 2026-10-29T21:25:51+00:00. Branch run/S07b-param-orch40 from main 6fbc095. Tokens unknown (unobservable).

## Task A — live rerun: DONE
- One Modal run, app ap-c9idzNVYv1w3koKIhkGQyP, EXIT 0, GPU L4. Output evidence/S07/S07b-param/RM04-chair-orch40/result.json (187,943 B; 12 frames; obj ids [0] each frame; RLE masks). Container-import fix from orch38 verified live.
- Masks decoded offline -> accepted tracking.sanitize_responses: 12 frames, centroids+PTS == record (evidence/S07/S07b-param/RM04-chair-orch40-mask-check.txt).
- Billed $0.02535615 (read-only 21:25Z via Build/gpu/cost_log.py; may still accrue) vs $0.50 reservation; ledger appended; containers [] before/after. Details: evidence/S07/S07b-param/README.md (orch40 section).

## Task B — ST03 errata: DONE
- Fresh ffprobe on hash-verified ST03 (sha 7239da80...df051): f76 = 2.535867 s; 2.569233 s = f77. Confirmed S12a finding.
- Root cause (code bug in Owns): modal_track._frames ffprobe `-read_intervals %+#(last+1)` counts packets in decode order; with B-frames the trailing B-frame was never decoded, so f77 slid into f76. Old method reproduces the recorded map exactly.
- Fix: new `_pts` reads last+1+32 packets, keeps first last+1 frames, asserts strictly increasing. Regression test test_pts_presentation_order_st03 fails before fix, passes after.
- Errata: evidence/S07/S07b-errata/ST03-orch14-frame_map.json (+ RM04-orch40-frame_map.json: same bug hit this live run, f11 0.48 -> 0.44 s; orch38 "source frame gap" note was this bug). README.md there. Accepted orch14 untouched.

## Checks (fresh)
- PYTHONPATH=root;tests/measurement python -m unittest tests.measurement.test_tracking test_modal_track test_sam_runtime: 27 OK (1 skip).
- Regression test with fix stashed: FAILED (errors=1); restored: OK.
- check_masks.py on live result: centroids_match_record true.

## Ponytail
Reuse: existing modal_track/track_training/sanitize_responses, cost_log reconcile CLI (no new cost code), uv+modal command from S06h report. Smallest: one ~10-line `_pts` helper + 1 test; mask check is a 35-line run-local script, not product code. Skipped: second live run to regenerate RM04 with fixed PTS (errata file instead; contract cap 1); adding L4 to cost_log RATES (Build/gpu outside Owns — gpu-s not back-solved, billed $ still exact); Build/pipeline wiring.

## Risks / next
- Live result.json frame_map f11 is wrong; consumers must use the errata map (or rerun with fixed code).
- f2 box width doubles: obj 0 mask may merge chairs on that frame; not validated as single object.
- Container preflight_exit 2 (setuptools 80.9.0 vs lock 84.2.1) recorded; tracking unaffected.
- Other S07 outputs produced by the old _frames (any clip with B-frames) may carry the same tail-PTS error; audit recommended. cost_log RATES lacks L4 (owner of Build/gpu).
- Billing may still accrue; latest read wins. No gate/physical claim.
- Communication: silent; one final line to controller.

