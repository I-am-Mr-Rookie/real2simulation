# S12b-orch39 REPORT — DONE

Lane CODEX-1 · anthropic/claude-opus-5-5/high · coding quota OpenCodex-managed; not polled · tokens/cost unknown; no GPU/Modal/Meta/paid calls.
UTC issue 2026-10-29T21:13:53Z · work started 21:14:22Z · work stopped 21:21:51Z (verified DONE, early finish allowed) · reported 21:22:30Z ·
base main 3ff3d53, rebased onto main bb76776 and tests/prediction rerun (13 OK) before final commit.

## Result
Gate M **NOT_MET** in every record/output. 'g' = fitted image-height/s^2 acceleration (never m/s^2); speed image-height/s;
friction/restitution dimensionless. Uncertainty = 1-sigma standard (fitter jacobian_covariance, residual-variance OLS).

Files (all new, Owns only):
- Build/real2sim/params.py — parameter() validated record {name, value, unit, uncertainty, provenance, gate_m}; abstain();
  from_fit(boundary, input_provenance) -> g=2*c2, speed=c1 from S12a fit_prefix, provenance = clip/source sha, boundary training +
  suffix-identity sha, fit sha, method; abstains if AIC picks degree 1 or covariance invalid. transfer() requires exactly one valid
  record per g/speed/friction/restitution, refuses missing/abstained/duplicate/non-finite/negative-uncertainty/no-provenance (no defaults).
  simulate(records, setup) feeds values to the EXISTING Build/simulator/contact-runs.mjs (RK4 + Rapier contacts) via node and returns
  parameters unchanged + parameter_set_sha256 + simulator input/output + gate_m + limitations. main() writes the real ST03 record.
- tests/prediction/test_params.py — 6 tests (5 on SYNTHETIC fixtures + committed ST03 record).
- evidence/S12/params-ST03.json — real ST03: all four params ABSTAINED (S12a fit withheld: S07 frame_map PTS conflict; no bounce
  observation for friction/restitution); transfer refused; simulated=false.
- evidence/S12/tests-prediction-S12b.txt — fresh test log.

Acceptance (g, speed, friction, restitution retain provenance and uncertainty):
1. Records leave transfer/simulate byte-identical to input (test asserts equality per param incl. uncertainty + provenance).
2. Simulator actually consumed them: RK4 samples match 1 - v t - g t^2/2 to 1e-9 (g, speed); restitution 1.5 surfaces the
   simulator's own "restitution must be finite in [0,1]" rejection (friction/restitution reach Rapier unaltered); contact reached.
3. Missing friction, abstained restitution, linear-only fit (abstained g/speed), NaN/None value, negative/None uncertainty,
   missing provenance key, duplicate -> ValueError; nothing defaulted.
Synthetic fit sanity (authored y=0.1+0.6t+2.7t^2 +/-0.5px): g 5.4000 ± 0.0461, speed 0.5991 ± 0.0072 image-height units.

## Findings (outside Owns; for controller)
- F1 Build/simulator trajectories/contacts accept only source='simulated', inputProvenance='synthetic'. Real image-derived params are
  therefore REFUSED by simulate() (no mislabeling). A real transfer needs a simulator provenance label (e.g. 'image-derived') — Build/simulator change.
- F2 Simulator fields are named *_m; here they carry image heights (labelled in output 'units'). Rename/unit field would be a simulator change.
- F3 friction/restitution have no measurement source in the codebase (no bounce/slide fitter); they can only be supplied as records with provenance.
- F4 ST03 real transfer stays blocked on the S12a/S07 frame_map errata (frame 77).

## Fresh checks (Python 3.14.5, Node v24.18.0, this worktree)
- python -m unittest discover -s tests/prediction -v -> 13 OK (7 S12a + 6 S12b) -> evidence/S12/tests-prediction-S12b.txt.
- python -m Build.real2sim.params -> "evidence/S12/boundary-ST03.json -> evidence/S12/params-ST03.json gate_m=NOT_MET refused=True".
- Env note: worktree lacked Build/simulator/node_modules (gitignored); created a local directory junction to the canonical
  Build/simulator/node_modules (no install, not committed). Delete the junction with the worktree.
- No fitter/lab/simulator code changed, so their suites were not rerun.

## Ponytail (full)
- Reused: S12a fit_prefix + _sha + GATE_M/LIMITS; fitter jacobian_covariance (no new uncertainty math); existing runContactAwareTrajectory
  via a 3-line node -e loader (no new JS file); plain dicts, stdlib only, no deps.
- Smallest complete: one module, records as dicts, validation at the transfer boundary; one shortcut comment (synthetic-only simulator label).
- Skipped: uncertainty propagation through the simulation (carried, not propagated — e.g. ±1σ ensemble is S12c/e scope), x-axis/projectile,
  friction/restitution estimation, Quantity contract reuse (its unit set is metric-only and label 'simulated'-only).

## Risks
- Uncertainty is OLS residual-based, clock/scale held fixed; PTS clock unverified. Not physics, not calibration.
- Cross-vendor review of the S12 path still required. Gate M/RS not run.

Communication: one completion line to controller (authorized). No canonical controls edited.
