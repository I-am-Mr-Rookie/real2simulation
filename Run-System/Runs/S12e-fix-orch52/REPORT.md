# S12e-fix-orch52 — REPORT

**Status: DONE.** R-RS F1–F4 fixed in S12 code; every reproduction now refused; Gate RS measured result unchanged (NOT_MET, 0/3 categories eligible); Gate M NOT_MET everywhere.

- Lane/model: CODEX-1, assigned anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed, not polled. Tokens/cost: unknown (unobservable); $0 services (no Modal/Meta/AWS jobs).
- UTC: issued 2026-10-29T22:05:53Z; worktree created 22:06:20Z; work stopped/reported 2026-10-29T22:10:51+00:00. Branch run/S12e-fix-orch52 from main 4b950c6; not merged (controller integrates; cross-vendor re-review still required before clearing Gate RS).

## Changes (Owns only)

| Finding | Fix | File |
|---|---|---|
| F1 score | Before load_observations(): prediction clip_id + training_sha256 must equal boundary; trace (frame, PTS) identities must hash to boundary.suffix_identity_sha256 with len == suffix_count == len(sealed); predicted y finite. Coverage/sealed_frames now use boundary.suffix_count. | Build/real2sim/score.py |
| F1 overlay | build() also requires suffix_identity_sha256 == boundary's and complete-seal identity hash/count; contract validate() requires each trace's suffix_identity_sha256 == hash of its own [[frame,PTS]...] rows (catches 64-zero forgery). VERSION unchanged (no format change; stricter check only). | Build/real2sim/overlay.py, contracts/overlay/validate.py, CONTRACT.md |
| F2 | gate() recomputes eligibility per category: kind == category, provenance == "image-derived" (score() now carries provenance, default "synthetic" = ineligible), clip_id not SYNTHETIC*, int sealed/scored frames, coverage == scored/sealed and >= 0.8, finite nonnegative RMS, scored is True, distinct clip and prediction per category. Median policy unchanged. | score.py |
| F3 | Broad except fallback deleted. Only StageError (validate_segment rejection) is caught -> returns {} + "validate_segment rejected (unscored): ..." -> 0 scored frames, unscored shortfall. Relative-to-source index mapping kept. Other exceptions propagate. | score.py |
| F4 | score() rejects non-finite/non-numeric (pts, y) observations (ValueError) before alignment; gate() treats NaN/Inf/negative RMS as shortfall. | score.py |

Digest format NOT changed: v1 prediction digest [kind, model, trace] kept, so committed ST03 prediction c81e0f94… and S12 overlays regenerate byte-identically; no commitment rewritten or re-versioned.

## Regressions (tests/prediction/test_score.py)
- test_f1_wrong_clip_wrong_training_and_precommitted_subset_refused_before_read (loader never called)
- test_f1_overlay_forged_suffix_hash_refused (build and validate)
- test_f2_one_synthetic_projectile_aliased_three_times_is_shortfall (+ same real clip aliased, + forged coverage)
- test_f3_wrong_record_object_is_unscored_shortfall (real ST03 track copy, object_id 999)
- test_f4_nonfinite_observations_and_metrics_rejected (NaN/Inf PTS and y; NaN/Inf/negative category RMS)
- test_gate_needs_every_category updated to eligible-shaped results (old bare {scored, rms} dicts are now correctly ineligible).

## Fresh checks
- `python -B -m unittest discover -s tests/prediction -v` (worktree): 35 run, 33 pass; 1 fail + 1 error both test_params simulator (worktree lacks ignored simulator Node deps — same as R-RS review; files untouched). Output: evidence/S12/tests-prediction-S12e-fix.txt.
- Same test_params in canonical checkout (byte-identical params.py/test_params.py): 6/6 OK. Output: evidence/S12/tests-params-canonical-S12e-fix.txt.
- `python -B evidence/reviews/R-RS/reproduce.py` (read-only, not edited): now stops at line 46 AssertionError — its pre-defect sanity line expects bare {scored, rms} dicts to give MET, which F2 now refuses. Because that script asserts defects exist, its probes were replayed unchanged in Run-System/Runs/S12e-fix-orch52/refusals.py -> refusals.json: all 10 refused (wrong clip+training, wrong training same clip, precommitted subset, overlay forged suffix build + validate, one synthetic projectile x3, NaN PTS, Inf y, NaN category metric, wrong record object 999).
- Regenerated `python -B -m Build.real2sim.score`: gate RS NOT_MET, median null, projectile RMS 0.1981633916341227, 7/466 (1.502%), scored false, "validate_segment OK". Only diff in gate-rs.json: additive `"provenance": "image-derived"` in clips.projectile. `Build.real2sim.overlay` and `Build.real2sim.predict` regenerate byte-identical evidence (git diff empty). gate_m == NOT_MET in all 6 S12 JSON documents.

## Ponytail (full) applied
- Reuse: boundary._sha, existing verify()/check(), existing validate_segment + its StageError, existing reproduce.py fixture copied verbatim into refusals.py; no new module/abstraction/dependency.
- Smallest complete: metadata + identity-hash checks instead of a v2 digest (avoids re-versioning committed evidence); fail-closed return {} instead of a new exception class; one _eligible() helper.
- Skipped: v2 digest covering custody metadata; clips.csv licence lookup inside gate(); S12e shortfall-reason wording ("three categories gate-ineligible"); UI/new tracking.

## Risks / limits
- v1 digest still excludes clip_id/training_sha256: a caller who hand-edits those fields onto another clip's committed trace with identical (frame, PTS) identities and supplies that other commitment would pass F1 metadata checks. Close with a versioned v2 digest on the next new commitment if needed.
- "image-derived" provenance is caller-declared (plus SYNTHETIC* name check); not cross-checked against clips.csv approval.
- Not re-reviewed cross-vendor; Gate RS remains NOT_MET; no calibrated/physical claim. Communication: silent; one completion line to controller.
