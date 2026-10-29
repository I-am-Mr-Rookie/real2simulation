# S05d-orch21 REPORT — DONE (contract scope; Gate R NOT run, no physical calibration)

Lane CODEX-1, anthropic/claude-opus-5-5/high. UTC start 2026-10-29T12:17:18+00:00 (worktree 12:19), work stopped 2026-10-29T12:34:12+00:00. Coding quota: OpenCodex-managed; not polled. Tokens: unknown. Cost: $0 (CPU only; no GPU/Modal/network job).
Base main 87cb6bb; branch run/S05d-orch21.

## Result per clip (evidence/S05/S05d/RESULT.json; units = MapAnything model-metric, NOT calibrated)
| Clip | Floor plane | Inlier frac | RMS / p95 residual | Normal 1σ bootstrap / sensitivity (9 variants) | Mean cam height (model units) | Gravity dir | Metric scale | A4 normal |
|---|---|---|---|---|---|---|---|---|
| RM02 | FIT, visually confirmed floor; 11.1° from camera-down prior | 0.069 | 0.0081 / 0.0146 | 0.044° / 8 of 9 ≤1.75°, 1 outlier 18.2° (seed2, band 0.04) | ~1.18 | estimated = floor normal; magnitude null | ABSTAIN | ABSTAIN |
| RM04 | FIT, visually confirmed floor; 3.6° from prior | 0.057 | 0.0062 / 0.0109 | 0.020° / all 9 ≤0.50° | ~1.39 | estimated = floor normal; magnitude null | ABSTAIN | ABSTAIN |
| RM05 | UNRELIABLE (overlay shows scattered equipment, no deck; 3/9 variants no fit, up to 33.7°) | 0.037 | 0.0115 / 0.0190 | — | — | ABSTAIN: ISS, not under gravity | ABSTAIN | ABSTAIN |

Missing references (exact, from evidence/clips/S02d-metadata-scale-audit.md): RM02 "Room; scene-only" — no source-documented object dimension and no annotated endpoints (desk papers visible but their size is not source-backed as A4); RM04 "Room; scene-only" (Pexels classroom) — no source-documented desk/door/A4 size; standard door height not source-backed for this room; RM05 "Hatch/handrail dimensions unverified". No A4 sheet annotation for any clip, so A4 plane-normal agreement is ABSTAIN everywhere. Magnitude of g never assumed. Bootstrap σ is statistical only; sensitivity.json (seeds 0–2 × inlier bands 0.01/0.02/0.04) is the systematic spread. Camera heights are model-metric only (MapAnything metric_scaling_factor 1.375/1.710/0.876), not a calibration claim. RM02 desk top is ~0.79 model units above the fitted floor — plausibility only, not evidence.
Inputs: npz hashes match evidence/S05/S05c/RESULT.json (4ce3c82c…, 1a06953f…, a3bebfeb…); read from gitignored local dirs in .worktrees/S05b-orch14 and .worktrees/S05c-orch19 (canonical root lacks these local/ copies). Visual overlay checked only locally in %TEMP% (derived from licensed frames; not committed).

## Files
- Build/reconstruction/spike/scene_frame.py — RANSAC floor: normal within 35° of mean camera-down, every camera above plane, image-local triplet hypotheses, LOWEST plane with ≥3% support, LS polish, bootstrap; known_object_scale() requires length_m + source + pixel endpoints; CLI manifest→RESULT.
- Build/reconstruction/spike/test_scene_frame.py — 4 synthetic tests (plane/gravity recovery with a higher distractor plane, reproducibility, abstain paths, cited-reference scale + uncertainty).
- evidence/S05/S05d/manifest.json, RESULT.json, sensitivity.json.

## Checks (fresh, final code)
- `python -m unittest test_scene_frame` → 4 tests OK.
- RESULT.json rerun SHA256 identical both runs: DA03599D…406E.
- Visual overlay of floor inliers: RM02/RM04 floor regions correct; RM05 not a deck.
- Two root-cause fixes during the run: (1) global random triplets gave P(hit)≈f³ for 6%-inlier floors → seed-dependent RM04 (32° spread); image-local triplets fixed it (≤0.5°). (2) Max-inlier plane picked RM02's desk top (59% support, seen in overlay) → now lowest plane with ≥3% support.

## Ponytail (full) applied
Reuse: numpy/PIL only (installed), unittest like existing spike tests, existing npz keys and cam-to-world pose, schema scale/gravity semantics (unknown → null, magnitude never assumed). Smallest complete: one module + one test file; no new deps, no Open3D, no detector. Skipped: A4/door detection or annotation tooling (`shortcut:` comment in code), scene.schema.json emission, contracts/scene edits, Gate R. Risks: OpenCV cam-to-world convention inferred (consistent with synthetic + overlay); RM02 floor is a small visible area with one 18° sensitivity outlier; 3% support/35° prior are heuristics.

## Next
S05e/Gate R cannot pass known-object-10% or A4-5° with these inputs: needs source-backed reference objects with pixel annotations per clip (or the plan's planes/boxes fallback). RM05 needs a gravity-free frame convention.

Communication: silent; one completion message to controller only.
