# R12-covariance-review — follow-up (first P3 only)

Status: **DONE** — first P3 (REPORT.md, `core.py:278` lost floor vs subnormal declared noise) **RESOLVED**; no new P0–P2. REPORT.md remains unchanged provenance.
Same original window (issued 2026-10-28T21:05:41.128Z, deadline 21:35:41.128Z); follow-up work stopped 2026-10-28T21:13:35.4070385Z. Model as assigned `anthropic/claude-opus-5-5` native. Quota OpenCodex-managed; not polled. Cost unknown.

**Final reviewed pin:** parent `run/R12-covariance-fix` = `9d240b05549199f49f0be0ca13285653778180a3` (only product commit after 7708494). Cherry-picked locally as `585123e` for testing only; `git diff --stat 9d240b0 HEAD -- Build tests` empty (identical product tree). Parent must NOT take 585123e; take only the report commit.

## Change reviewed
`Build/fitter/core.py:288-290`: when `sigma2 is None and dof>0`, require `min(variances) > ulp(0)·n/dof`. README bound text matches. New test `test_uncertainty.py:85-91`.

## Bound arithmetic (evidence/followup_probe.py → followup-probe.txt, PROBE PASS)
- RSS = `fsum(e*e)`; under round-to-nearest a nonzero square becomes 0 only if exact e² ≤ u/2 (u = ulp(0)=5e-324); probe confirms at 1e-162, 2^-538 (→0, exact<u/2) and 2^-537 (→u). Hence lost RSS < n·u, true floor RSS/dof < n·u/dof = bound: strictly-greater declared variance dominates it. Sound and conservative (factor 2 slack).
- Parent case n=3,dof=1: bound 1.5e-323. Declared var 5e-324 and 1.5e-323 → unavailable (None SE); nextafter 2e-323, 3e-323, 0.01 → valid with SE>0. One zero declared row with lost floor → unavailable (stricter than old `not any`; correct, its floor is unknown). `sigma=0` → valid SE 0. Original P2 underflow repro unchanged (default unavailable; declared .1 SE=0.05 exact).
- Guard unreachable on non-declared path (sigma2 None returns at `core.py:256-257`) and when residuals are exactly zero (`_sigma2` returns 0.0, not None) ⇒ no relaxation or change to normal fits.

## Fresh tests
`python -m unittest discover -s tests/fitter -v` → **Ran 45 tests, OK** (incl. new subnormal test, 13 frozen invariants). [evidence/followup-fitter-tests.txt](evidence/followup-fitter-tests.txt)

## Findings
No P0–P2. Remaining REPORT P3s (#2 condition estimate, #3 Gauss-Jordan R⁻¹) unchanged, notes only. Residual note: when rss>0 but some squares underflowed, floor error is absolute < n·u/dof — negligible, not a finding.

## Ponytail
Reused prior probe pattern/stdlib Fraction; ~35-line targeted probe; no product edits. Skipped broad sweep/audit, lab/IAB/Node checks (parent-owned, parent reports 84 Node/17 lab PASS — not re-verified here), merge. Risk: none new beyond REPORT.

