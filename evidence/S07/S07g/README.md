# S07g — owner clips registered; OWN01 g measurement (SAM 3.1 BLOCKED, diagnostic only)

## 1. Registration (done)
`clips.csv` rows OWN01–OWN12 (free_fall, creator Koushik Sadhak Jeet, OWNER_RECORDED,
PRIVATE_PROCESSING_ONLY (Oct31), public use pending owner go-ahead). Per-file sha256, bytes,
fps, duration, resolution and PTS stats: [clips-sha256.json](clips-sha256.json), produced by
[register_clips.py](register_clips.py) (idempotent). Videos stay in the gitignored owner folder.
- All trims 30/1 fps, uniform PTS dt = 33.333 ms (trim re-encode). 1080x1920 except OWN11 478x850.
- Raw original `_raw/VID_20261031_035735.mp4` (read-only) over 13.5–17.2 s: 127 frames,
  dt 33.23–33.43 ms, mean 33.3333 ms → phone timebase ≈30 fps with ±0.1 ms PTS jitter.
  Phone clock is NOT externally verified.
- Approval receipt: [OWNER-APPROVAL.md](OWNER-APPROVAL.md) (OWN01–OWN12 only; no other clip widened).

## 2. Real pipeline (SAM 3.1 on Modal) — BLOCKED by the S20 GPU admission guardrail
Exact command: [run_sam_track.ps1](run_sam_track.ps1) (`--clip OWN01 --first 40 --last 60
--prompt "yellow book" --object-id 0`). `modal_track.py` gained an `--approval` receipt argument
(default unchanged: S02 APPROVAL.md) so owner clips are gated by their own receipt.
- Dry run (`S07B_DRY=1`, no GPU): plan/approval/clips.csv/frames OK, 21 frames f40–60,
  PTS 1.366341–2.033008 s.
- Live attempt 2026-10-30T22:45:58Z: `ReconstructionPaused: S20_MODAL_RESERVATION_USD all-in bound
  required`; with bound 0.60: `ReconstructionPaused: GPU admission state unavailable or invalid` —
  root cause `FileNotFoundError: <canonical>/evidence/S20/runtime/receipt.json` (and
  reservations.json absent). Build/guardrails/ADMISSION.md: a trusted operator must supply a fresh
  verified receipt.json + reservations.json; no agent bootstrap. Not fabricated.
- Modal: ephemeral app created and stopped locally before `track.remote`; no GPU container,
  no job; cost ≈ $0 (no ledger row because the admission refused before reserving).
- **No MEASURED pipeline g exists for OWN01.** Owner action: provide S20 runtime receipt/journal
  (or a controller-issued `S20_MODAL_REQUEST_ID`), then run run_sam_track.ps1 + fit.

## 3. DIAGNOSTIC (colour threshold; NOT the pipeline; NOT MEASURED)
[diagnostic_colour.py](diagnostic_colour.py) → [diagnostic-own01.json](diagnostic-own01.json);
`--self-check` asserts the fit/threshold. Rules fixed in code before the fit (no tuning to 9.79):
fall = centroid >8 px below held median through last increasing frame; train = first 2/3, held-out = rest.

| item | value |
|---|---|
| fall frames | 48–60; train 48–55 (8), held-out 56–60 (5) |
| scale | held frames 36–44 yellow-mask width 270.8 ± 1.1 px (sd) / 0.2028 m = 1335 px/m |
| g (DIAGNOSTIC) | **10.73 ± 0.41 m/s²** (1σ) vs local 9.79 → +0.94 (+9.6%), 2.3σ: MISS |
| budget | fit 0.38; scale 0.13 (SEM + 3 px edge/blur allowance); timing 0.09 (1 ms assumed, conservative vs ±0.1 ms PTS) |
| model | not quantified (rotation, drag, perspective) — see causes |
| train RMS | 2.9 px |
| held-out residuals | +6, −5, −18, −46, −234 px → held-out FAILS (f58–60 landing/bounce) |

Likely causes (not corrected, not tuned): hand/fingers occluding the cover at the held frames
(shorter px width ⇒ g too high; 9.79 would need ≈297 px); release impulse at f48; book rotation
and motion blur shifting the yellow-pixel centroid; out-of-plane motion (perspective scale
taken at release depth only); landing detection rule admitting f58–60. A SAM mask + the
free_fall.py held-out evaluation should be the judge, not this diagnostic.

Post-result inspection (reported, NOT applied; primary diagnostic value unchanged):
- Frame-44 crop: book held by fingertips at its top-left corner, cover tilted a few degrees.
  The 2–98 percentile width estimator under-reads a uniform span by ~4% by construction
  (visual edge-to-edge ≈ 290 px at f44), so this method's scale alone biases g high by ~4–7%.
- Mask width falls 270 → 223 px and yellow pixel count 46k → 25k during f50–58: the book
  rotates out of plane while falling, moving the colour centroid relative to the centre of mass.
- Centroid already moves at f47 (+5 px): release onset is f47/48; the fixed rule started at f48.

