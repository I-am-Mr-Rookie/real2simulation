# S02c visual triage — 2026-10-27 UTC

This is **not continuous playback or individual usability verification**. Local
originals were decoded into 2-frame/second contact sheets at 240-pixel width,
20 samples per sheet, chronological left-to-right/top-to-bottom. This covers
each file on disk but misses frames between samples and can hide cuts, repeated
frames, blur, occlusions and edits. I visually reviewed every sheet for RM04,
PD02, PD03 and BN02; only selected sheets for the other six. Approximate times
below identify review windows, not capture time or calibrated measurements.
Originals were not changed. Sheets are local temporary evidence at
`%TEMP%/s02c-review-20261028/`; regenerate with
`ffmpeg -i INPUT -vf "fps=2,scale=240:-2,tile=5x4" -q:v 5 -vsync 0 ID-%03d.jpg`.
Contact sheets are not committed or licensed for publication by this review.

| ID | Visual evidence and provisional disposition |
|---|---|
| RM04 | Entire 9.24 s sampled. Foreground desks enter and grow relative to rear board and shelving; some apparent depth-dependent movement, but optical zoom/perspective and actual translation are not distinguished. Promising room lead, not verified parallax/reconstruction; no measured scale. |
| PD02 | Entire 14.63 s sampled. Contrasting gold bob visibly crosses patterned floor and reverses; pivot above image and pedestrians near frame edge. Candidate for 2-D bob tracking, not yet tested; timebase/scale unknown. |
| PD03 | Entire 59.83 s sampled. Newton cradle, moving outer bob(s), static view; amplitude becomes very small later and similar reflective spheres overlap. Source labels slow motion; factor, pivot geometry and scale unknown. Not independent simple-pendulum validation. |
| BN02 | Entire 40.59 s sampled. Large green ball with person partly visible, educational text, repeated/stepwise bounce images, crossfade to end card around 35 s. Source claims high-speed capture; physical cadence cannot be inferred from file fps, ball deforms and size unknown. End card says CC BY 4.0 while manifest records Commons CC BY-SA 4.0: reconcile source-specific declarations before final use. |
| BN01 | Reviewed samples 0–10, 20–40 s. Small red ball, dark backlighting, person and camera angle changes, some ball exits frame; poor unambiguous continuous tracking candidate. Depicted-person rights, scale and timebase unknown. Remaining sheets unreviewed. |
| FF01 | Reviewed samples 20–30 and 50–60 s. Educational captions and prolonged held/annotated frames in drop sequence; overhead view; small moving object. Time labels are edited source annotations, not validated timebase; independently measured scale absent. Remaining sheets unreviewed. |
| FF02 | Reviewed samples 20–30 and 70–80 s. Overhead stairwell, source graphics and scene changes; potentially overlaps FF01 and cannot count as independent experiment. Timebase and scale not verified; remaining sheets unreviewed. |
| PJ01 | Reviewed samples 0–20 and 40–50 s. Text intro, tiny matchstick rocket on cluttered background, overlaid coordinates/held frames. Difficult tracking and edits require original-speed review; reference rods/source claims are unverified, capture cadence unknown. Remaining sheets unreviewed. |
| AP15 | Reviewed samples 0–10 and 30–70 s. Low-resolution lunar footage; small objects and astronaut, exposure/occlusion make trajectory ambiguous at thumbnail scale. Exact release/landing segment, temporal fidelity and scale need full-resolution continuous review. Remaining sheets unreviewed. |
| PD01 | Reviewed samples 10–20, 50–60 and 90–100 s. Chalkboard scene and closeups with ruler, text, transitions and source-described slow motion. Pendulum pivot and full trajectory not established in sampled sections; scale/timebase source claims remain unverified. Remaining sheets unreviewed. |

No clip is marked usable or approved. Need continuous original-frame playback or
tracking across candidate intervals, cuts/occlusion checks, and distinct real
experiments; S02d owns calibration and S02e final-use approval. Pexels raw-file
public-repository distribution and third-party rights remain unresolved.

Replacement search: [RM02, Andy Barbour's tracking shot of empty classroom](https://www.pexels.com/video/tracking-shot-of-empty-classroom-6671552/),
already listed in clips.csv but not locally downloaded, is described by the
source as 18 s and a tracking shot. Search-result metadata is not playback,
actual parallax, complete rights clearance or owner approval. A Wikimedia
[experiments category](https://commons.wikimedia.org/wiki/Category:Videos_of_experiments)
lists a cup drop, but individual source/licence/cadence were not reviewed and
it is not a cleared replacement. No blocked source request was repeated.
