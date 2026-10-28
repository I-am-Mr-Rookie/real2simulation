# S07c plan

UTC start: 2026-10-28T07:26:30Z (initial repository inspection; approximate).
Base: 4bbae8ba9dbbb386794f050d4287eb21aea99d86. Branch: run/S07c.
Objective: deterministic, calibrated prefix-only quadratic free-fall fit with
separate held-out evaluation and explicit numerical/scientific abstention.

Owns ONLY Build/measurement/free_fall.py; Build/measurement/FITTING.md;
tests/measurement/test_free_fall.py; evidence/S07/S07c/; Run-System/Runs/S07c/.
Shared schema/README/dependencies/controls/main read-only. No integration/merge.

Apply Ponytail full, TDD, systematic debugging, verification-before-completion.
Use standard library orthogonal least squares, no new dependency, raw coordinates
without unjustified smoothing. Validate through frozen S07a boundary. Tests cover
known synthetic gravity, initial state, VFR/capture conversion, held-out isolation,
noisy residuals, malformed/ineligible and ill-conditioned data. No uncertainty
intervals or physical gate claims. No model/GPU/media/network work.

Stop <=30m; no new implementation after minute25. Record red/green evidence,
fresh relevant suites and exact limitations; commit owned paths, leave unmerged.
