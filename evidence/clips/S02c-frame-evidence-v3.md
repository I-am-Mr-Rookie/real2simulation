# S02c original-frame review v3 — 2026-10-27, run start 22:00:42 UTC (recorded); end not recorded

Requested routing: CODEX-2 ownership, owner override Opus 5.5/medium; runtime
identity not independently observable. Local original files only; nothing
uploaded. Evidence of visual suitability only; no calibration, physics fit,
rights clearance, owner approval or gate pass. Derived images/CSVs are in
`%TEMP%/s02c-v3/` (regenerate: `python evidence/clips/s02c_v3_analysis.py DIR`
plus ffmpeg sheets below). FFmpeg scene-score >0.3: no cuts in AP15, BN02, PJ01.

| ID | Original-frame evidence | Verdict for real fall/bounce/projectile |
|---|---|---|
| PJ01 (projectile) | Decoded all 3635 frames (568×320, 30 fps). Frame differencing finds live motion only at frames ~456–491 (PTS 15.2–16.4 s); rest of clip is title cards and annotated stills (diff 0). Viewed all 42 frames 15.2–16.6 s full-rate: rocket is a few-pixel blob; small moving blobs at e.g. (97,140) f461 → (158,102) f463 → (312,55) f469 → (509,137) f471 are consistent with an arc but interleave with noise/hand motion. | **Not usable as tracked trajectory**: ≈1 s, ~12 frames, object ≈3–15 px. Source overlay coordinates (x|y in m, poles 1 m apart) are creator-authored, not our measurement. At most a narrated reference, not a fit input. |
| BN02 (bounce) | Decoded all 2029 frames (1920×1080, 50 fps file; source text says 240 fps capture, unverified). Viewed 50 full-rate frames at 13–14 s: ball top cropped by frame edge throughout; floor-contact region visible. HSV-green mask unusable (green floor lighting/reflections saturate bottom edge = 269 every frame). | **Not usable for bounce height/restitution**: apex and top edge out of frame; only contact deformation visible. Timebase is a source claim. |
| AP15 (lunar drop) | Full 1-fps overview (83 s) and 4-fps sheet 28–50 s reviewed at 720×480: astronaut, LM leg, camera view change near 48–49 s not flagged by scene score. No falling hammer/feather identifiable at sheet scale. | **Unresolved**: drop segment not located; needs full-rate review of every candidate window before any claim. |

Moving camera: RM04 (prior run, frame-tracked) and RM02 (provisional, not
tracked) unchanged; no new moving-camera evidence this window.

Conclusion: the local pool contains **no individually verified real
fall/bounce/projectile clip** suitable for fitting. Remaining route: new
rights-cleared footage specifically showing a whole, high-contrast object
trajectory in frame from a static camera (e.g. Pexels/Pixabay ball drop or
toss against plain background) — must be selected by full-rate frame review,
not thumbnails.