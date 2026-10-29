# S07b-param (orch38) live receipt — RM04 SAM3.1, FAILED at container import
- Run 1 (only allowed): app ap-VxrG31RSO35uNDi9IcVHNH, launched 20:50:34Z: `modal run Build/measurement/runtime/modal_track.py --clip RM04 --first 0 --last 11 --prompt chair --object-id 0 --out evidence/S07/S07b-param/RM04-chair/result.json --masks` (PYTHONUTF8=1).
- Outcome: container crashed importing /root/modal_track.py: `REPO = MEASUREMENT.parents[1]` -> IndexError (orch36 WIP bug). No model load, no tracking, no result.json. Log: RM04-chair-launch.log.
- Stopped: `modal app stop` 20:53:03Z; containers before [] (containers-before-orch38.json), after [] (containers-after-orch38.json).
- Cost: reserved $0.50 (gpu-ledger.jsonl); billed (read-only billing report 20:59:59Z, re-read 21:11Z unchanged; Build/gpu/cost_log.reconcile) **$0.00147352** (A10G $0.00122552 ~4.0 GPU-s, CPU $0.00010539, Mem $0.00014261) -> RM04-chair-run1-cost.json, billing-post-orch38.json. May still accrue; latest read wins.
- Fix (offline-tested, not live-verified): REPO falls back when the file sits at a shallow path. Retry requested from controller as nonterminal blocker 20:53Z; controller declined after cutoff (separate bounded rerun after acceptance). Containers [] re-checked 21:11Z.
- billing-month-pre.json / containers-before.json: orch36 pre-snapshots (kept).
No masks/media committed. Not calibration, not Gate M, no physical claim.


# S07b-param (orch40) live rerun — RM04 SAM3.1 "chair" f0-11, SUCCEEDED
- Single run: app ap-c9idzNVYv1w3koKIhkGQyP, 21:20:38Z-21:22:36Z, same command with `--out evidence/S07/S07b-param/RM04-chair-orch40/result.json --masks` via `uv run --offline --no-project --python 3.11 --with modal==1.6.3 --env-file ../../.env modal run ...` (PYTHONUTF8=1). EXIT 0. Log: RM04-chair-orch40-launch.log.
- GPU NVIDIA L4 (function allows ["L4","A10G"]); checkpoint facebook/sam3.1 sam3.1_multiplex.pt rev daa6319..., sha256 0567debe...; load 35.5 s, track 9.3 s, remote 77.0 s, peak VRAM 14.3 GB. Container preflight_exit 2 (setuptools 80.9.0 vs lock 84.2.1; recorded, tracking ran).
- result.json 187,943 B (12 frames, 1 object id [0] per frame, COCO RLE masks 3840x2160). Masks decoded offline and re-run through accepted tracking.sanitize_responses: 12 frames, centroids+PTS identical to the record (RM04-chair-orch40-mask-check.txt; Run-System/Runs/S07b-param-orch40/check_masks.py).
- Caveat: stream box widens at f2 (x 0.366, w 0.196 vs 0.090 elsewhere) — obj 0 mask may merge adjacent chairs on that frame; centroid not validated as one physical chair.
- **Timestamp errata:** this run's frame_map f11 = 0.48 s is wrong (true 0.44 s): same decode-order read_intervals bug as ST03 orch14. Corrected map: evidence/S07/S07b-errata/RM04-orch40-frame_map.json. Code fixed after the run (`_pts`), not re-run live.
- Cost: reserved $0.50; billed $0.02535615 (L4 $0.01778, CPU $0.00265, Mem $0.00284, egress $0.00209), read-only 21:25Z, may still accrue -> RM04-chair-orch40-cost.json, billing-post-orch40.json, gpu-ledger.jsonl. Containers [] before (containers-before-orch40.json) and after (containers-after-orch40.json).
Not calibration, not Gate M, no physical claim. No media committed.

