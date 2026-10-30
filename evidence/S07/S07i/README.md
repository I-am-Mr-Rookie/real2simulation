# S07i — OWN01 MEASURED g from the real SAM 3.1 track; one batched track job for OWN02–OWN11

## 1. OWN01 g — MEASURED (owner clip, user-declared scale, phone clock not externally verified)
Script: [measure_own01.py](measure_own01.py) (`--self-check`) → [result-own01.json](result-own01.json).
Input: controller's real SAM 3.1 track `evidence/S07/S07g/track-own01.json` (sha256 in result; A10, f40–60).
All rules are constants in code, fixed before the fit; nothing tuned toward 9.79.

| item | value |
|---|---|
| position | SAM binary-mask pixel centroid (area-weighted, from the track record). Box centre run as sensitivity |
| scale | SAM box width on held pre-release f40–44 (frames fixed in S07g run_sam_track.ps1 before tracking): 291.41 px (sd 0.92) → 0.2028 m / 291.41 = 6.959e-4 m/px; u = SEM ⊕ 2 px edge allowance ⊕ 0.5 mm ruler (assumed) = 0.75 % |
| fall window | release = first frame > held median + 8 px (S07g rule) → **f47**; end = last contiguous tracked frame **f54** (SAM lost the book f55–60: `missing_frames`) → 8 frames, **0.233 s** |
| split | train = first ⌊2n/3⌋ = f47–51 (5 frames, 2 dof); held-out f52–54 |
| **g (mask centroid)** | **10.96 ± 0.77 m/s²** (1σ) vs local 9.79 → +1.17 (+12 %), 1.5σ |
| budget | fit (2 px/frame declared) 0.67; scale 0.08; timing (0.1 ms PTS + 0.1 % clock) 0.06; model (centroid vs box centre) 0.37 |
| g (box centre, sensitivity) | 10.59 |
| train RMS | 0.89 px |
| **held-out residuals** | f52 −2.1, f53 −16.9, f54 −36.1 px (RMSE 23 px ≫ 2 px) → **held-out prediction FAILS** |

Reading: g agrees with 9.79 within its (large) uncertainty, but the 5-frame prefix does not predict the
next 3 frames; the uncertainty is dominated by the fit (0.13 s training span). Treat as a MEASURED value
with a FAILED held-out check, not as a validated measurement.

Why the window is short / what is in it (quantified, not corrected):
- Landing is NOT in the window: SAM loses the object after f54 (S07g colour landing was f58–60).
- f47 is release onset (S07g saw +5 px already at f47; hand contact may still push) → inflates prefix curvature;
  held-out residuals all negative and growing = prefix acceleration too high for the later fall.
- f54 box: width 286 → 261 px, height 215 → 237 px, x +21 px = out-of-plane rotation; the mask centroid of a
  rotating cover shifts vs the centre of mass (part of the f54 −36 px residual).
- Perspective: scale taken at the release depth; any depth change during the fall is unmodelled.

vs S07g colour DIAGNOSTIC 10.73 ± 0.41: (a) SAM scale 291.4 px vs colour 2–98 % width 270.8 px — the colour
estimator under-read the cover by 7 %, which alone moved the diagnostic up ~7 % (10.73 → ~9.97 at SAM scale);
(b) the SAM fit starts at f47 (release onset) and trains on only 5 frames, whereas the diagnostic trained on 8
frames f48–55 — the higher SAM pixel curvature comes from that shorter, earlier window; (c) diagnostic u
used residual-derived noise, SAM u uses declared 2 px detection error. Both agree within 1σ of each other.

## 2. Batch tracking job OWN02–OWN11 (NOT run by this worker)
- Windows fixed BEFORE any tracking: [fall_windows.py](fall_windows.py) → [fall-windows.json](fall-windows.json)
  (S07g yellow threshold, quarter res, `-fps_mode passthrough` numbering = modal_track). 176 frames total.
  v1 rule (no 4-frame run test) fired on hand jitter at OWN03/09/10/11 and default cfr decode shifted indices by 1;
  both fixed before tracking. **OWN12 excluded**: front cover (colour rule fails) and a contact sheet f24–63 shows
  the book stays in hand while the camera pans — no free fall to track.
- `modal_track.py --batch <json>`: plans + extracts every clip first (duplicate outputs/bad object ids fail
  before admission), ONE `admit_standalone("modal-track:batch:OWN02,…")`, ONE `track_batch.remote` (one container,
  clips sequential, per-clip errors isolated), one `track-ownNN.json` each (never overwrites).
- Bound: worst case (300 s startup + 780 s `BATCH_TIMEOUT_S`) × (A10 $0.000306 + 2 cores × $0.0000131 + 16 GiB ×
  $0.00000222)/s = **$0.397 ≤ $0.40** (Modal list prices, 2026-10-31; L4 is cheaper). Expected: OWN01 = 45 s
  remote for 21 frames (19 s load, 7.6 s track) → 10 clips × ~25 s load/preflight + 176 × 0.36 s ≈ 5–6 min ≈ $0.13.
- Dry run (S07B_DRY=1, fake modal, no GPU): [dry-run.txt](dry-run.txt) — 10 clips, 12–22 frames each.

Controller command (from canonical root, after merge; admission state controller-owned):
```powershell
$env:S20_MODAL_RESERVATION_USD='0.40'; uv run --python 3.12 --with modal==1.6.3 --env-file .env modal run Build/measurement/runtime/modal_track.py --batch evidence/S07/S07i/fall-windows.json --approval evidence/S07/S07g/OWNER-APPROVAL.md
```
Equivalent: `powershell -File evidence/S07/S07g/run_sam_track.ps1 -Batch` (root fixed: GetDirectoryName + Push-Location -LiteralPath).

Risks: peak VRAM was 16.0 GiB for OWN01's 21 frames on the 23 GiB A10 (OWN07 has 22; test caps windows < 24);
22.9 MB of JPEG frames (176, measured in the dry run) go in one call (larger than OWN01's; untested size); colour-rule windows
were not visually checked per clip.

