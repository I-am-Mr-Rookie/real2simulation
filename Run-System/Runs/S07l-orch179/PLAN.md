# S07l-orch179 PLAN

- Issued 2026-10-31T00:09:37Z; deadline 00:39:37Z (Dhaka 06:39:37); minute-25 cutoff 00:34:37Z. Model: anthropic/claude-opus-5-5/high (OpenCodex-managed, not polled).
- Objective: diagnose why held-out prediction fails on every owner clip, from existing SAM 3.1 track JSONs + S07h/S07k results only (no tracking, video, frames, model, Modal/GPU/Meta).
- Owns: evidence/S07/S07l/ ; Run-System/Runs/S07l-orch179/.
- Method: evidence/S07/S07l/diagnose.py imports S07k measure_v2 (-> S07h, S07i, Build.measurement) for track paths, box widths, constants; pixel-space y(t) fits on the same v1/v2 windows and floor(2n/3) split. One statistic + verdict per hypothesis (a)-(g); verdict thresholds fixed in the script before the real run. Nothing chosen by closeness to 9.79.
- Checks: `python -B evidence/S07/S07l/diagnose.py --self-check`; real run writes results.json; reproduction of S07h/S07k held-out RMSE asserted; `python -B -m unittest discover -s tests/measurement -t tests/measurement`.
