# S02c original-frame visual evidence — 2026-10-27 UTC

Scope of the two verified entries is **local visual tracking/scene-motion
feasibility only**, not a physics benchmark, owner approval, production use,
rights clearance for public distribution, or reconstruction success. Original
videos remain local and unapproved. Times below are file presentation times,
not independently established physical capture times. S02d owns calibration.

## PD02 — gold bob, 2-D image-space tracking

- OpenCV 4.13 decoded all **439 original 1920×1080 frames**, zero-based
  0–438 (file PTS 0.000–14.600 s, 30 fps). Adjacent PTS gaps approximately
  1/30 s; this says nothing about the original capture/slow-motion rate.
- `s02c_frame_analysis.py` initialized a 111×111 pixel bounding box on the bob
  in frame 0, matched that original-frame template within a ±45-pixel local
  search on each successive frame, and recorded each match and box in
  `S02c-PD02-frame-track.csv`. All 439 contextual target crops, one for every
  decoded frame in ordered 50-frame sheets, were visually inspected: the gold
  bob remains identifiable inside the box through the entire window; from
  approximately frames 100–300 its edges sometimes extend beyond the fixed-size
  box. Thus a rough 2-D position is supportable, not precision segmentation.
  One-second full-frame annotations were also checked. Template-match minimum
  0.6099 occurs at frame 155 (5.166667 s); scores are similarity, not accuracy.
- Pedestrians are in the background and do not visibly occlude the bob in the
  reviewed crops. Reflective table produces a lookalike reflection below; this
  tracker followed the actual bob in the inspected crops. Frame 0–438 show a
  continuous apparent swing with a reversal. No FFmpeg scene-score >0.25 cut
  detected; that test cannot rule out subtle edits or synthesized content.
- Camera framing pans/shifts; image coordinates are **not world coordinates**.
  Pivot outside frame, unknown pendulum length/scale, camera motion and unknown
  real capture timebase make this insufficient for calibrated g or pendulum fit.
  People and venue rights need review; Pexels raw-file public-repo permissions
  remain unresolved. A consumer still needs its own tracking and stability tests.

## RM04 — static-room relative motion, not proven 3-D reconstruction

- OpenCV decoded all **231 original 3840×2160 frames**, zero-based 0–230
  (PTS 0.000–9.200 s, nominal 25 fps). Tracking was performed on half-resolution
  1920×1080 versions of every decoded frame, not a 2 fps sample. Initial rear
  board features were propagated frame-to-frame with forward/backward Lucas–Kanade
  checks; a RANSAC board homography is compared with four manually seeded near
  table corners and other scene features. `S02c-RM04-frame-flow.csv` contains
  the full trace; `S02c-frame-summary.json` records the result.
- At frame 100 (4 s), 200/200 board features and 82/84 context features remain;
  near-left table corner differs from board-plane homography by 20.90 half-res
  pixels. At frame 200 (8 s), 194/200 board correspondences are homography
  inliers, near-left residual is 35.44 pixels; by frame 230 it is 38.89 pixels.
  Near-right corner was lost at frame 109 (4.36 s): not every feature survives.
  A few feature points also belong to the cabinet behind the table, so the
  aggregate median is not a clean foreground-only measurement.
- Inspected annotated frame 0, 100, 200 and 225; the near table and wall/board
  remain recognizable. Feature flow survives across consecutive frames, and
  near/far features do not follow a single board-plane warp. This is evidence
  of relative depth-dependent motion consistent with parallax, **not proof of
  camera translation alone**: zoom/lens distortion and imperfect flow remain
  alternatives. No scene score >0.25 cut detected; subtle edits remain possible.
  Occlusion/entry of foreground desks and changing field of view matter. No 3-D
  geometry, absolute scale, camera calibration or reconstruction was verified.

## Provisional replacement RM02

On this continuation, one ordinary GET to
`https://www.pexels.com/download/video/6671552/` returned 200 video/mp4; local
file SHA-256 `9825020bbdcf650a272548275f27bb109dd7834d9db9dd3a69a067ff39219720`.
[Source](https://www.pexels.com/video/tracking-shot-of-empty-classroom-6671552/):
Andy Barbour, Pexels licence; restrictions/third-party rights and public raw-file
redistribution remain unresolved. Local copy is unapproved. ffprobe: 3840×2160,
24 fps, 426 decoded frames, 17.75 s file duration; full ffmpeg decode succeeded,
and no scene-score >0.25 cut was detected. Viewed 1-fps overview and frames 0,
96 and 192: lateral-looking camera motion across desks/window with foreground
occlusion and shallow focus; desk enters/exits view. **Not framewise-tracked or
individually verified.** File fps is not verified capture cadence; scale unknown.

## Reproduction and limits

From this worktree: `python evidence/clips/s02c_frame_analysis.py OUTPUT_DIR`;
OpenCV 4.13 and NumPy required. Output CSV/summary from this run are committed;
large annotated video-derived frames and full-rate crop sheets remain local in
`%TEMP%/s02c-frame-analysis-v2/` and can be regenerated. FFmpeg scene check:
`ffmpeg -i INPUT -vf "select=gt(scene\,0.25),showinfo" -an -f null -`.
FFprobe best-effort frame timestamps were inspected for monotonicity. No images,
files or metadata were uploaded. Re-running the acquisition recorder preserves
the narrow evidence flags only for identical file hashes.
