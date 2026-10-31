# S07n — system-derived fall time t and drop height h (owner clips)

**Label: MEASURED (conditional: user-declared scale 0.2028 m, phone clock unverified, rolling shutter assumed).** Every number below is output of `fall_time_height.py` (`results.json`, `table.md`). No tracking, video decoding, GPU, Modal or Meta call; inputs are the existing SAM 3.1 tracks (`evidence/S07/S07g/track-own01.json`, `S07i/track-own02..06.json`, `S07j/track-own07..11.json` via S07k `measure_v2.TRACKS`) and stored fits (`S07h/results.json` v1, `S07k/results.json` v2). 9.79 is comparison only.

Run: `python -B evidence/S07/S07n/fall_time_height.py [--self-check]` from repo root.

## Rules (reused S07k v2 thresholds: MOVE 4 px, STATIC 6 px, SCALE_N 5 / MIN 3, WIDTH_TOL 10 %, DECEL 0.5)
- Release = last static frame before two consecutive steps > 4 px; ±1 frame.
- Impact = last frame before the first velocity collapse (step < 0.5× previous); ±1 frame. Floor y = max y of that frame and the collapse frame.
- t = (impact − release)/30 s; u_t = √2 · (1/30)/√3 (each endpoint uniform ±1 frame: quantisation + ambiguity) ⊕ 0.1 % clock.
- h = (floor y − median static y) px × m/px; m/px = 0.2028 m / mean SAM box width over ≤5 static frames ending at release (S07i formula: ±2 px box edge, ±0.5 mm edge). u_px = 2 px·√2 ⊕ change of centroid-minus-box-centre y between release and floor.
- g_ht = 2h/t², u by first-order propagation. Asserts: t = n/30, PTS span within 1 % of n/30, h = ½ g_ht t², all u > 0; synthetic self-check recovers g.
- Abstain when release or impact is not inside the track; for impact-missing clips the script reports LOWER BOUNDS only (no g_ht).
- Post-first-run fix (recorded, not tuned to g): OWN01's release-frame SAM box includes the hand (421 vs 291 px), so scale frames whose box width is > 10 % off their median are dropped. This changed OWN09 h (0.635 ± 0.161 → 0.851 ± 0.010 m) and OWN01's lower bound only.

## Results

| clip | release f | impact f | t (s) | h (m) | g_ht = 2h/t² (m/s²) | rel u t/h/g | fit v1 g ± u | fit v2 g ± u | z(g_ht−v1) | z(g_ht−9.79) |
|---|---|---|---|---|---|---|---|---|---|---|
| OWN01 | ABSTAIN: impact not in track: track ends f54 still falling (release f46; LOWER BOUNDS only: t ≥ 0.267 s, h ≥ 537 px ≈ 0.374 m) | | | | | | 10.96 ± 0.77 | — | | |
| OWN02 | 45 | 59 | 0.467 ± 0.027 | 0.911 ± 0.008 | 8.36 ± 0.98 | 6%/1%/12% | 9.29 ± 0.32 | 7.27 ± 3.07 | -0.90 | -1.46 |
| OWN03 | 44 | 56 | 0.400 ± 0.027 | 0.781 ± 0.012 | 9.77 ± 1.34 | 7%/2%/14% | 9.54 ± 0.63 | 9.56 ± 0.63 | +0.15 | -0.02 |
| OWN04 | ABSTAIN: impact not in track: track ends f55 still falling (release f45; LOWER BOUNDS only: t ≥ 0.333 s, h ≥ 913 px ≈ 0.615 m) | | | | | | 10.39 ± 0.46 | 10.40 ± 0.46 | | |
| OWN05 | ABSTAIN: impact not in track: track ends f52 still falling (release f43; LOWER BOUNDS only: t ≥ 0.300 s, h ≥ 580 px ≈ 0.409 m) | | | | | | 8.62 ± 1.28 | 9.62 ± 0.74 | | |
| OWN06 | ABSTAIN: release not in track: fewer than 3 static tracked frames before motion at f46 | | | | | | 7.12 ± 1.02 | — | | |
| OWN07 | 45 | 58 | 0.433 ± 0.027 | 0.923 ± 0.010 | 9.84 ± 1.24 | 6%/1%/13% | 8.72 ± 0.21 | 9.51 ± 0.93 | +0.89 | +0.04 |
| OWN08 | ABSTAIN: release not in track: pre-motion frames f31-f35 not static (y range 8.2 px) | | | | | | 8.82 ± 0.27 | 8.82 ± 0.27 | | |
| OWN09 | 8 | 21 | 0.433 ± 0.027 | 0.851 ± 0.010 | 9.07 ± 1.14 | 6%/1%/13% | 6.74 ± 1.77 | — | +1.10 | -0.63 |
| OWN10 | ABSTAIN: release not in track: no sustained centroid-y motion | | | | | | — | — | | |
| OWN11 | ABSTAIN: release not in track: no sustained centroid-y motion | | | | | | — | — | | |

## Plain verdict
- **OWN01 (01_demo_hero): the system CANNOT derive t or h from the existing track.** The S07g track stops at f54 while the book is still accelerating (step 113 px/frame), so impact is outside the track. Only lower bounds: t ≥ 0.267 s, h ≥ 0.374 m. Getting real values needs the track extended past f54 (new SAM run = GPU; out of S07n scope).
- Release and impact are both inside the track for **OWN02, OWN03, OWN07, OWN09**: t ≈ 0.40–0.47 s (±0.027 s, 6–7 %), h ≈ 0.78–0.92 m (±1–2 % stat.), g_ht 8.4–9.8 m/s² (±12–14 %). g_ht agrees with the stored v1 fit within 1.1 u in all four.
- **Robustness: approximate, not precise.** t is limited by ±1-frame release/impact ambiguity at 30 fps (≈ ±27 ms). h's small stated u excludes unquantified systematics: declared scale & release-plane assumption (floor depth not verified), perspective, rolling shutter, motion-blur elongation of the box near impact (S07l). For the demo, show t and h as "≈ system-estimated" with these u, e.g. OWN03 or OWN07; do not present them as calibrated measurements. g_ht is a cross-check from the same tracks, not independent evidence of g.
- OWN04/OWN05: impact outside track (lower bounds only). OWN06: track starts mid-fall. OWN08: pre-release frames not static (8.2 px > 6). OWN10/11: no fall.

