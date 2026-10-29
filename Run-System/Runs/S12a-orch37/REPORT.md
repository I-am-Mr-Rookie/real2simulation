# S12a-orch37 REPORT — DONE

Lane CODEX-1 · anthropic/claude-opus-5-5/high (as assigned) · coding quota OpenCodex-managed; not polled · tokens/cost: unknown (unobservable); no paid API/GPU/Modal/Meta calls.
UTC start 2026-10-29T20:43:22Z (issue) / work began 20:44:00Z · work stopped 2026-10-29T20:49:27+00:00 · base main d131047 · branch run/S12a-orch37.

## Result
Gate M: **NOT_MET_INPUT_READINESS** (fresh run of Build/measurement/gate_m.evaluate_sources on this worktree). No calibrated-g, metric or physical-accuracy claim anywhere.

Files (all in Owns):
- Build/real2sim/boundary.py — split(data, gate_m_status) -> (Boundary, held_out); fit_prefix(Boundary); evaluate(Boundary, PrefixFit, held_out); synthetic_fixture(); CLI `python -m Build.real2sim.boundary --output evidence/S12/S12a-boundary.json`.
- tests/prediction/test_boundary.py — 7 tests.
- evidence/S12/S12a-boundary.json — boundary record + live Gate M dict + synthetic evaluation; evidence/S12/S12a-tests.txt.

Acceptance:
1. Training prefix / held-out suffix immutable — frozen Frame tuples from S07 validate_input; suffix SHA-256 committed in Boundary at split time; input mutation after split has no effect (test_split_freezes...).
2. No evaluation leakage — Boundary has no suffix frames (only hash/count); spy on fit_motion proves fitter receives exactly the 12 prefix times, none of the suffix (test_fitter_never_sees_suffix); evaluate rejects modified/truncated/extended suffix, forged prefix, or fit from another split (test_tampered...). Receipt JSON carries no suffix coordinates.
3. Gate M result required — split() refuses any status not starting NOT_MET (None/""/MET/PASSED rejected); CLI feeds the live evaluator status; every record/evaluation carries gate_m_status + NOT_MET notice.
- Scale-free: error = Euclidean pixel error / training-prefix extent (dimensionless); test shows identical error at 0.5x pixel scale; exact quadratic extrapolates to <1e-9.

## Fresh checks (this worktree, Python 3.14.5)
- `python -m unittest discover -s tests/prediction -v` → 7 OK.
- `python -m Build.real2sim.boundary --output evidence/S12/S12a-boundary.json` → "Gate M NOT_MET_INPUT_READINESS; held_out=6"; synthetic max error 3.5e-16.
- Regression: tests/measurement 70 OK (1 skipped); tests/fitter 65 OK.
- `python Run-System/worker_timebox.py check Run-System/Runs/S12a-orch37/TIMEBOX.json` → TIMING PASS.

## Ponytail (full) applied
- Reused, not rewritten: validate_input (split/order/leak/≥3-prefix rules, blockers), Frame, FitAbstention, fit_motion, gate_m.evaluate_sources. New code = one ~150-line module; no new deps, no __init__ (namespace pkgs like Build/measurement).
- Smallest complete: ordering enforced by types (fit_prefix only takes a Boundary that has no suffix) instead of a custody service; hash commit via stdlib hashlib/json.
- Shortcut recorded in code: fitter only accepts "s"/"m" labels; values are PTS seconds + dimensionless normalized pixels.
- Skipped: select_model/degree choice (S12b+), parameter transfer, uncertainty, real-clip splits.

## Real clips
None split: Gate M evaluator states no real tracks exist (accepted S07 has no real tracking output). real_clips_used=[] in evidence. Fixture is labelled SYNTHETIC with zero source hash.

## Limits / risks
- Process-local custody only: caller still holds the returned suffix; external sealed storage is downstream integration.
- Time axis is presentation PTS, not capture seconds (timebase unverified); fine for scale-free extrapolation error, not physics.
- Cross-vendor review of S12 gate path still required per run system.

## Next
S12b (parameter transfer) can consume Boundary/PrefixFit; first real-clip boundary needs an accepted S07 track for an approved clip.

Communication: silent; one completion line to controller chat as authorized. No canonical controls edited.

