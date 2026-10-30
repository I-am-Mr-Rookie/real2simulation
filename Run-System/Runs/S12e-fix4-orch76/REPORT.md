# S12e-fix4-orch76 REPORT — DONE

Lane CODEX-1; model anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable); $0 GPU/API (no Modal/Meta call).
UTC issued 2026-10-30T05:39:17Z; work 05:40–05:53Z; base main eddead8; branch run/S12e-fix4-orch76.

## Fixes (evidence/reviews/R-RS/RECHECK3.md)
- **F2-R3 [P1]** — new committed registry [evidence/S12/accepted-tracking.json](../../../evidence/S12/accepted-tracking.json), built only from existing accepted evidence: one entry `ST03-f58-83-S12e-orch45` binding clip ST03 + source sha256, artifact path + sha256, full seal identity (last_training_frame 76, training_sha256, suffix identity sha, 466), presentation map (S07b recovery3) path + sha256, frame range 58–83, Modal app ap-2Sbu8Pen5jJhHlNxAhuva6 / gpu-ledger, limits (7/466). `score.accepted_tracking()` requires exactly one entry matching artifact path+sha, then seal, presentation-map digest and exact frames/PTS. `Tracked` records `custody` (registry sha + entry) or `custody_error`; unknown artifacts are diagnostic-only: `score()` sets `ineligible_reason`, and `_tracking_ok()` (gate) re-derives custody independently and requires equality with the carried receipt.
- **F2-C [P1]** — `score()` refuses a `Tracked` whose `.boundary != boundary` (frozen dataclass equality: clip/source/training rows/digests/seal) before any artifact or suffix read. Tracking evidence now carries `seal_identity`; results carry the prediction's `training_sha256`; `_tracking_ok` requires evidence seal == result clip/source/training/suffix identity/count and after_frame == last_training_frame, and the registry entry binds that seal.
- Kept: explicit `synthetic` refusal, path-escape, artifact sha, observation digest, identity checks; F2-A/F2-L/F1 code untouched.

## Regressions added (tests/prediction/test_score.py)
- `test_f2r3_reviewer_forged_native_tracked_end_to_end_is_shortfall`: loads the reviewer's own recheck3/review.py fixtures + persisted *-SYNTHETIC-track.json (asserted equal to `tracker()`), native Tracked, unpatched score/gate: each scores and validates but is ineligible ("no accepted tracking custody"); gate NOT_MET, median None, all three shortfall (reviewer had MET on main 35c9a90).
- `test_f2c_tracked_bound_to_other_boundary_refused_and_not_eligible`: reviewer's genuine-ST03 0.01 H shifted boundary + real-bound loader -> ValueError "different boundary", loader never read; carried training_sha transplant and re-sealed evidence both fail `_tracking_ok`.
- Positive control in existing real-evidence test: custody entry present; custody=None evidence ineligible.

## Fresh checks
- `python -B -m unittest -v tests.prediction.test_score test_boundary test_predict test_overlay`: **38 OK** -> [evidence/S12/tests-prediction-S12e-fix4.txt](../../../evidence/S12/tests-prediction-S12e-fix4.txt).
- `python -B -m Build.real2sim.score` regenerated evidence/S12/gate-rs/gate-rs.json from the existing ST03 artifact: `gate RS NOT_MET median=None projectile=0.1981633916341227 coverage=0.015 gate_m=NOT_MET`; `result` identical to previous; only projectile `tracking_evidence` (seal, custody) and `training_sha256` added; ineligible_reason None (custody OK, still shortfall on 7/466 coverage).
- All gate_m fields in evidence/S12 JSON: NOT_MET.

## Ponytail (full) applied
- Reuse: registry entry generated from existing `st03_record`/`split`/`seal_identity` + existing ledger/presentation map; tests reuse the reviewer's review.py fixtures/`tracker()` and persisted synthetic tracks (read-only) instead of new fixture code; Boundary dataclass equality used for F2-C instead of a new hash scheme.
- Smallest complete: one JSON registry + ~40 lines in score.py; no new module/framework, no per-pixel attestation.
- Skipped: PD02 S07-chunktrack-orch67 f0-438 artifact NOT registered: no PD02 boundary/seal or committed pendulum prediction exists in evidence/S12 for an entry to bind, and it spans <1.25 periods; scorer format compatibility not checked. PD02 remains shortfall.
- Risks: registry is trusted because it is committed and controller-reviewed — a repo writer could still add an entry; acceptance must review registry diffs. Any registry edit changes registry_sha256 and invalidates previously carried custody (intended; regenerate gate-rs.json). Independent R-RS re-review still required.

## Limits
Measured Gate RS NOT_MET (projectile 7/466 coverage, bounce/pendulum not tracked). Gate M NOT_MET; no physical/calibration claim. No Modal/Meta/GPU, installs, secrets or canonical control edits.

Communication: silent; one authorized completion message to controller.
Next: R-RS recheck4 (cross-vendor) on this branch/merge.

