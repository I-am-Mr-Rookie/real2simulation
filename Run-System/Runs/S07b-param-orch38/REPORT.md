# S07b-param-orch38 REPORT — PARTIAL
Model anthropic/claude-opus-5-5/medium (OpenCodex-managed; not polled). UTC start 2026-10-29T20:46:16Z, work stopped 2026-10-29T21:15:54Z (full window; 21:00-21:11 waited on controller retry decision, re-read billing/containers). Branch run/S07b-param-orch38 from run/S07b-param-orch36 (3a941b1). Tokens: unknown (unobservable).

## Result
- Code DONE (offline): Build/measurement/runtime/modal_track.py track/main take clip, first/last frame, prompt, object_id, out, masks (opt-in COCO uncompressed RLE per frame per obj id). Defaults = accepted orch14 ST03 f58-76 "apple" obj 2; metadata derived from clips.csv equals accepted record; out opened with mode "x" + pre-GPU FileExistsError => never overwrites accepted evidence. plan() validates approval ID (evidence/owner/S02/APPROVAL.md), ints/>=3 frames, nonempty prompt, clips.csv row, before frames/GPU.
- Live: PARTIAL. The single allowed Modal run (RM04 f0-11 "chair", masks) crashed at container import (WIP bug below); $0.0015 billed; containers []. No result.json. See evidence/S07/S07b-param/README.md.

## WIP review (orch36 3a941b1)
Kept: parameterization, plan() validation, mask_rle, tests. Fixed: (1) REPO = MEASUREMENT.parents[1] crashed in the container (/root/modal_track.py) -> guarded fallback; regression test test_imports_at_container_root (fails before fix, passes after). (2) object_id now validated locally before frame extraction/GPU (was only checked remotely by tracking._context).

## Checks (fresh)
- PYTHONPATH=root;tests/measurement python -m unittest tests.measurement.test_tracking test_modal_track test_sam_runtime: 26 OK (1 skip) after fixes; container-import regression test fails without the fix; object_id pre-GPU subtests (remote/_frames not called).
- Dry run S07B_DRY=1 RM04 f0-11: 12 frames, PTS map ok (f11 at 0.48 s: source frame gap, recorded as-is).
- Billed reconcile read-only via Build/gpu/cost_log.reconcile; $0.00147352 (20:59Z and 21:11Z reads identical, ~4.0 A10G-s); ledger evidence/S07/S07b-param/gpu-ledger.jsonl; containers [] before 20:50Z, after 20:53Z/20:57Z/21:11Z.
- Controller reply ~21:11Z: no retry this run; separate bounded rerun after acceptance.

## Ponytail
Reuse: orch36 WIP, track_training/_context sanitizer unchanged (tracking.py untouched), cost_log.reconcile (no new cost code), clips.csv/APPROVAL as metadata source, existing ffmpeg _frames. Smallest: 2-line fix + 1 regression test; no new deps/config. Skipped: masks as PNG (RLE only), Build/pipeline wiring (S13f), second live run (contract cap 1; controller declined retry after cutoff).

## Risks / next
- Fix not live-verified; next run: same command (README) once authorized; ~2 min wall, est < $0.05.
- RLE at 3840x2160 with many chair instances may make result.json large; first live run should check size.
- RM04 object ids unknown until a prefix stream is inspected (orch14 needed obj-id selection).
- Communication: one nonterminal blocker message to controller (authorized); one final line.
