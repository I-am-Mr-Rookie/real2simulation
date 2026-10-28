# S11h-swarm report

- RID: S11h-swarm; status DONE; UTC 17:30:14Z-17:35:00Z; OpenCodex-managed; not polled.
- Added `Build/fitter/api.py`: pure request -> validated simulated quantities -> existing fitter -> strict JSON adapter.
- Added focused tests: actual synthetic stopwatch/ruler -> fit -> sourced response; invalid/degenerate/provenance/options; unavailable covariance null/status; strict NaN/inf JSON.
- Explicit response assumptions: iid residual noise, fixed clock and scale, input quantity uncertainty not propagated. Unsupported uncertainty models reject. Exact AIC -inf serializes null with explicit unavailable status.

## Ponytail / reuse

Reused `validate_quantity`, `fit_motion`, `jacobian_covariance`, `gravity_quantity`, and `select_model`; no new dependency, HTTP, auth, UI, config, or duplicated fitter math. Skipped live/physical/deployment work.

## Fresh checks

`python -m unittest -v tests/fitter/test_api.py` — 4 passed. `python -m py_compile Build/fitter/api.py tests/fitter/test_api.py` — passed. Test setup temporarily used read-only peer snapshots of pending `core.py`, corrected `quantity.py`, and `synthetic.py`; none are committed.

## Limitation / integration

Parent must integrate after corrected fitter and instrument/quantity commits, then rerun. This leaf does not establish physical calibration, measured metrics, Gate M, or a product endpoint. Communication compliance: canonical report/evidence only.
