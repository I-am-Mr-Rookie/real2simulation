# R14-instrument-gate — DONE: no P0–P2 within reviewed scope

**Verdict: pinned `82791f3` `_quantize` passes the narrow S11 numeric gate.** No P0/P1/P2 findings. P3 notes below are pre-existing, non-blocking. Not Gate M/S12/physical/calibration/deploy acceptance.

## Identity / window
- Lane CLAUDE, Opus 5.5/medium via existing managed route (runtime identity not independently exposed). Costs/tokens unknown; OpenCodex-managed; not polled. No model/GPU/network jobs.
- Issued 21:48:02Z, start 21:48:29Z, work stopped 21:55:40Z, deadline 22:18:02Z (Dhaka 04:18:02). Verified fully DONE early (TIMEBOX.json). Owner 04:00 UTC stop not approached.
- Worktree `C:/Users/HP/.codex/worktrees/swarm14-instruments-audit/2026-10-26 - Meta Global AI Developer Hackathon`, branch `run/R14-instrument-gate` from `e4c9603` (audit commits `a78eb02`, `e4c9603` preserved). Owns only this run dir. No candidate/product/test edits, no main merge.

## Pin verified
- `82791f3` parent = `55a3d2e`; diff stat = only `Build/instruments/synthetic.py` +4/-2.
- Candidate worktree HEAD = `82791f3`; working `synthetic.py` blob `90469a6` == committed blob; SHA256 `3f216767…a78d` == snapshot the R14 audit verified (so audit's 22/22 + 312-observation result applies to this exact pin). Candidate has frozen `tests/instruments/test_r14_invariants.py` tracked-diff vs pin (parent's integration file) plus untracked evidence; not touched.

## Source/meaning review
New code: `whole = floor(ratio); magnitude = (whole + (ratio - whole >= 0.5)) * resolution`, ratio = binary64 `abs(value)/resolution`.
- Correctness: for finite ratio < 2^52, `floor` is exact and `ratio - whole` is exact (Sterbenz/same-ulp), so fraction>=0.5 test is exact on the binary64 quotient → no premature rounding (root cause of baseline `+0.5` drift fixed once in shared helper; all 6 instrument channels inherit). For ratio >= 2^52 ratio is integral, fraction 0, no spurious tick. `whole` is a Python int from a float → exact float conversion in the multiply.
- Overflow: `floor(inf)` raises OverflowError → existing ValueError; inf product caught by existing `isfinite`. Rejection envelope unchanged.
- Semantics: rounds the *binary64 quotient* (docstring updated accordingly), preserving fixture `test_synthetic.py:23` 1.25/res0.1 -> 1.3; exact-Fraction policy (1.2000000000000002) correctly rejected as a behavior change.
- Sign handling line unchanged.

## Fresh independent checks (pinned source, read-only import)
| Check | Result |
|---|---|
| `python Run-System/Runs/R14-instrument-gate/repro.py <candidate>` (own exact-Fraction half-away oracle; not product algorithm) → [repro.log](C:/Users/HP/.codex/worktrees/swarm14-instruments-audit/2026-10-26%20-%20Meta%20Global%20AI%20Developer%20Hackathon/Run-System/Runs/R14-instrument-gate/repro.log) | 14/14 edges OK: strict below-half 0x1.fffffffffffffp-2→0; ties ±0.5→±1, 2.5→3; lattice 2^52+1, 2^53, max float unchanged; 2^52-0.5→2^52; 2^51+0.5→2^51+1; subnormal lattice 0x1.0000000000001p-1022 and 1.5·2^-1074 @ min-subnormal res unchanged; 5e-324@1→0; -0.4→-0.0; -0.0→+0.0. Decimal fixture 1.3 (Fraction policy 1.2000000000000002). Rejects 1e308/1e-308 and max/0.5. Seeded 200 000-case dyadic sweep (res 2^-1074..2^60, signed, ties/integers/random fractions): **0 mismatches**. Camera (x=-0.0, y=-0.3, res1) → x 0.0, y -0.0. |
| `python -m unittest discover -s tests/instruments -p "test_*.py"` in candidate | Ran 22, OK. |
- Skipped (accepted parent/audit evidence, no blanket re-audit): lab 17 / fitter 45, audit's 312-observation verifier, covariance, non-dyadic grids beyond fixture.

## Findings
- **P0–P2: none within reviewed scope.**
- P3 (pre-existing, unchanged lines, no action required for gate):
  1. Signed zero inconsistent: input -0.0 → +0.0 (`if value else 0.0`), but -0.4@1 → -0.0 (copysign). Equal under ==, harmless to fitter; only matters if someone serializes/compares sign bits.
  2. Conservative rejection of some finite true answers (e.g. max_float/0.5, 1e308/1e-308) because quotient overflows; intentional per `test_synthetic.py:49`.
  3. Quotient-rounding policy means non-dyadic grids follow rounded quotient, not exact nearest stored-grid point; now documented in docstring; deliberate compatibility choice.

## Ponytail FULL application
Read full Ponytail. Reused audit's frozen FINDINGS/REPORT/TIMEBOX format and existing candidate suite; one ~40-line stdlib repro (Fraction oracle) as the single new check instead of re-running audit verifier/lab/fitter. No deps, no product/test edits, no new features. Smallest complete review: pin identity + source reasoning + targeted edges.
Skipped/not checked: lab/fitter rerun, non-dyadic exhaustive grids, physical/calibration. Risk: integration of frozen tests into main still parent-owned.

## Communication
Silent; only required final one-line pointer. No other chats/agents/model calls. Costs unknown.

