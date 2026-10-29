# S05f → cross-vendor re-review packet (for R-R follow-up; read-only reviewer)

Scope to check: F1–F6 repairs, Q-S05e annotation decisions, Fallback 2 record. Branch `run/S05f-orch25`.

| R-R finding | Fix (file) | Regression (Build/reconstruction/spike/test_gate_r.py) |
|---|---|---|
| F1 producer `calibrated` vs evaluator `FIT` | evaluator accepts producer contract `calibrated`; unknown statuses raise (gate_r.py) | `test_f1_actual_producer_calibrated_status` (real `scene_frame.analyse` output incl. new A4 fitter → PASS 3/3) |
| F2 no fixed cohort | `COHORT=(RM02,RM04,RM05)`; missing/extra ids raise | `test_f2_fixed_cohort`, `test_disjoint_criteria_do_not_combine` |
| F3 floor/values not prerequisites | orientation needs floor FIT + gravity estimated; finite bounded angle [0,90], mpu>0, durations ≥0 else ValueError | `test_f3_no_floor_fails`, `test_f3_invalid_values_error` |
| F4 rounding before GPU compare | compare unrounded seconds vs 240 | `test_f4_gpu_compared_before_rounding` (240.029 fails, 240.0 passes) |
| F5 abstained gravity → angle failure | kind `ineligible` with source reason | `test_f5_abstained_gravity_reason` |
| F6 float 10% boundary | `<= 0.10 + 1e-12` | `test_f6_inclusive_scale_boundary` (0.9/1.1 pass; 0.8999/1.1001 fail; 5° boundary kept) |

Also: `scene_frame.known_object_scale` validates view/pixel bounds, distinct endpoints, finite 3D sample and keeps endpoints/length/raw error in output; new `a4_plane` CPU fitter (bbox shortcut documented) — never runs when gravity ABSTAIN (`test_a4_plane_angle_to_gravity`).

Reviewer questions: (1) common-cohort policy acceptable vs per-criterion? (2) RM02 abstention reasoning (aspect excludes A4) sound? (3) anything in frames suggesting a cited standard object missed? (4) Fallback 2 labelling sufficient?

Note: `evidence/reviews/R-R/probe_gate_r.py` asserts the OLD defective verdicts; it now fails by design (defects fixed) — superseded by the regressions above.
Not done: no new GPU, no live billing, no external standard re-verification, no browser/visual UI.
