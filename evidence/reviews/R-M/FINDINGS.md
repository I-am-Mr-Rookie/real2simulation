# R-M findings — independent Gate M review (read-only)

Scope: Build/measurement/{inputs,free_fall,uncertainty,gate_m}.py at HEAD 090d55a (byte-identical to canonical, SHA256 checked). Synthetic reproducers only: [repro.py](repro.py), output [repro-output.txt](repro-output.txt). **Review completion is not Gate M pass; 0 eligible / 0 measured stands. S12 not unlocked.**

## Actionable defects (priority order)

| # | Sev | Where | Defect | Fresh evidence |
|---|---|---|---|---|
| F1 | High | gate_m.py:74-83 summarize | Pass decision trusts caller-supplied `relative_error` / `uncertainty_covers_reference`; never recomputes from `g_m_s2` vs REFERENCE_G. | 3 trials g=20.0, relative_error=0.0, covers=True -> `PASSED`, gate_passed=true, mean_g 20.0 |
| F2 | Med | gate_m.py:76-77 | Independence = distinct raw strings; `'A'`,`'A '`,`'a'` count as 3 independent capture groups (strip only tests non-empty). Groups are self-declared, not receipt-bound. | independent_measured_count=3, gate_passed=true |
| F3 | Med (integration, fails closed) | gate_m.py:23-27, 61-66 | `evaluate_record` never sets `capture_group` or `uncertainty_covers_reference` and always appends a coverage blocker -> its output can never pass summarize. Correct today (no coverage rule), but the S07f decision must define coverage (k, interval) + group binding before any real pass is possible; otherwise future callers will patch dicts by hand (see F1). | capture_group=null, covers=null, summary NOT_MET |
| F4 | Med | gate_m.py:61-64; inputs.py:113 | Held-out suffix is computed but never gates anything; a 1-frame suffix is accepted. A suffix shifted 1 m off-model leaves relative_error 0.0. Prefix/suffix split therefore provides no out-of-sample check for the gate. | held_out_rmse_m=1.0, rel_err=0.0; 1-frame suffix accepted |
| F5 | High (uncertainty honesty) | uncertainty.py:88-89, 124-126 | Declared `detection_std_px` is never compared with observed training residuals. Declared 0.001 px vs actual RMSE 5.44 px -> detection u_g 0.00028 m/s² while g=10.71 (9.2% off). A residual-consistency check (e.g. reduced chi² bound -> abstain `declared_noise_inconsistent_with_residuals`) is the smallest fix. | F5 block in output |
| F6 | Low-Med | inputs.py:33-35,73-82; uncertainty.py:129-130 | No upper bound / relative sanity on declared calibration uncertainty: u_s = 10x m_per_px accepted under self-declared `small_error_linearization`, u_g=98 m/s². Once any coverage rule exists, huge declared uncertainty would trivially "cover" 9.81. Suggest abstain when relative u_s or u_ratio (or total u_g/g) exceeds a documented linearization limit. | u_g 98.1, g 9.81 |

## Verified correct (no finding)

- Prefix-only fit: `fit_free_fall`/`propagate_uncertainty` read only `validated.training`; `evaluate_held_out` rejects changed prefix/identity (custody of suffix explicitly external, gated by `custody_verified`).
- Timing Jacobian incl. design-matrix residual term matches central finite difference: analytic 205.22323 vs FD 205.22323 (unit timestamp std, noisy record).
- Scale/clock sensitivities g/s and -2g/ratio correct; PSD factoring for rho in [-1,1] correct.
- Large PTS origin (1e6 s) + slow-motion ratio 0.25 recovers g=9.8099999991 (rel err 1e-10).
- Default-deny: `metric_authorized`/`custody_verified` default False; CLI never sets them; scene receipt hash-pinned (EOL-normalized only); unknown receipt fails closed.
- Existing suite: `python -m unittest discover -s tests/measurement` 59/59 OK.

## Notes / low

- inputs.py:33: negative PTS (valid in some containers after edit lists) is a hard ValueError, not an abstention; acceptable fail-closed.
- Approval/evidence strings and `metric_authorized` booleans are declarations; authentication remains with trusted caller (documented, not a defect).

