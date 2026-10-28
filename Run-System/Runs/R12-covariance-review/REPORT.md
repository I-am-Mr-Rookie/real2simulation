# R12-covariance-review — narrow native Claude gate re-review

Status: **DONE** (narrow re-review; no P0–P2). Lane: other-vendor gate review; model as assigned `anthropic/claude-opus-5-5` native spawn (not Claude Code). Parent project 91e441f8-e40c-4ec4-bea2-de7fa1582d97 as assigned (UI binding not verified by worker).
UTC issued 2026-10-28T21:05:41.128Z; work stopped 2026-10-28T21:08:31.3553973Z. Reviewed pin `7708494` (fix) against frozen audit `eceee9e`. Coding quota: OpenCodex-managed; not polled. Cost/tokens: unknown.

## Scope
Only `git show 7708494 -- Build/fitter/core.py Build/fitter/README.md tests/fitter/test_uncertainty.py`, plus frozen `tests/fitter/test_invariants.py` and `evidence/S11/invariants/FINDINGS.md` (both unchanged between eceee9e and 7708494: empty diff).

## Verdict per reproduced P2
1. **Invalid full covariance (Gram / squared condition) — FIXED.** `core.py:265-270` builds physical transform × R⁻¹ factor before squaring; `core.py:283-284` declared influences = factor·Qᵀ column using stored `_q` (`core.py:87,122,149`) — algebraically correct (β = T R⁻¹ Qᵀ y). Covariance = Σ v·wᵢwⱼ via fsum (`core.py:295`) ⇒ diagonals are sums of nonnegative terms. All diagonals checked (`core.py:299-306`). Condition gate `‖R‖∞‖R⁻¹‖∞ > 1/sqrt(ulp(1))` only when positive noise (`core.py:291-294`); `sigma=0` known exact path stays valid.
2. **Residual-square underflow false zero — FIXED.** `_sigma2` `core.py:218-219` returns unavailable when rss==0 with nonzero residuals; timing-only stationary case caught by `core.py:288-289`; known `sigma=0` preserved.

## Fresh evidence
- `python -m unittest discover -s tests/fitter -v` → **Ran 44 tests, OK** (includes all 13 frozen invariants tests, which were written to expose the defects). [evidence/fitter-tests.txt](evidence/fitter-tests.txt)
- Independent exact-Fraction oracle sweep (own code, [evidence/probe.py](evidence/probe.py) → [evidence/probe.txt](evidence/probe.txt)): 3-pt (0,e,1) and 4-pt (0,e,2e,1), e=2^-1…2^-52, known and declared modes. Every VALID result has all diagonals >0 and worst correlation-scaled full-matrix error **1.86e-9**; FINDINGS repros (e=2^-28, 2^-30, 2^-36) now **UNAVAILABLE** with covariance/SE None (no finite invalid matrix); e≥2^-48 rejected as rank-deficient. Underflow repro: default, zero-declared and timing-only → unavailable; sigma=0 → valid SE 0; declared 0.1 → valid SE 0.05 (= exact σ/2). PROBE PASS.
- No threshold/noise-model/gate relaxation: change only adds abstentions; existing coverage/core/api tests unchanged and passing. Only one `FitResult(` constructor (`core.py:147`); `_q` defaults `()`, private, not serialized (rg: no asdict/replace) ⇒ public API/metadata unaffected.

## Findings
No P0–P2.
- P3 `Build/fitter/core.py:278`: when RSS underflows (floor lost) and a declared `sy²` is subnormal-but-nonzero, the true residual floor could exceed it; covariance stays "valid". Representation-limit corner, magnitude <1e-300; no action needed.
- P3 `Build/fitter/core.py:291-293`: ∞-norm condition is an estimate (factor ≤p of 2-norm) computed from computed R⁻¹; abstention is conservative at observed sweep (4-pt e=2^-26 valid, error 1.9e-9 — README "roughly half digits" holds). Note only.
- P3 `Build/fitter/core.py:258`: R⁻¹ via general Gauss-Jordan `_invert` instead of triangular back-substitution; pre-existing, accuracy fine in sweep.

## Ponytail (full) applied
Reuse: stdlib `fractions`/`math` only; reused existing fitter API and test discovery; no new deps. Smallest-complete: one ~60-line probe, no product edits. Checks: fresh full fitter suite + independent oracle sweep. Skipped: lab compatibility / IAB375 checks and merge (parent-owned), broad audit, physical M/S12/real scenes/GPU/deploy (locked). Risk: oracle covers zero-position synthetic designs only; real-scene conditioning untested here.

## Communication
Silent workflow; one final line only. Only own run files committed.

