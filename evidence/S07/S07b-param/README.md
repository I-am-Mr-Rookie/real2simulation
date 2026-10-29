# S07b-param (orch38) live receipt — RM04 SAM3.1, FAILED at container import
- Run 1 (only allowed): app ap-VxrG31RSO35uNDi9IcVHNH, launched 20:50:34Z: `modal run Build/measurement/runtime/modal_track.py --clip RM04 --first 0 --last 11 --prompt chair --object-id 0 --out evidence/S07/S07b-param/RM04-chair/result.json --masks` (PYTHONUTF8=1).
- Outcome: container crashed importing /root/modal_track.py: `REPO = MEASUREMENT.parents[1]` -> IndexError (orch36 WIP bug). No model load, no tracking, no result.json. Log: RM04-chair-launch.log.
- Stopped: `modal app stop` 20:53:03Z; containers before [] (containers-before-orch38.json), after [] (containers-after-orch38.json).
- Cost: reserved $0.50 (gpu-ledger.jsonl); billed (read-only billing report 20:59:59Z, re-read 21:11Z unchanged; Build/gpu/cost_log.reconcile) **$0.00147352** (A10G $0.00122552 ~4.0 GPU-s, CPU $0.00010539, Mem $0.00014261) -> RM04-chair-run1-cost.json, billing-post-orch38.json. May still accrue; latest read wins.
- Fix (offline-tested, not live-verified): REPO falls back when the file sits at a shallow path. Retry requested from controller as nonterminal blocker 20:53Z; controller declined after cutoff (separate bounded rerun after acceptance). Containers [] re-checked 21:11Z.
- billing-month-pre.json / containers-before.json: orch36 pre-snapshots (kept).
No masks/media committed. Not calibration, not Gate M, no physical claim.
