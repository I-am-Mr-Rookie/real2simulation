# S07d — explicit clock ambiguity and uncertainty propagation

Fresh CODEX-1 gpt-6.1-sol/medium <=30m, no new implementation after25m.
S07c implementation accepted; S07b live runtime still PARTIAL. Synthetic
uncertainty implementation is independently ready, NOT a physical-gate unlock.
Read current canonical instructions/budget/queue and actual accepted inputs,
fitter, docs/tests/reports. Apply Ponytail full, TDD/debugging and verification.

Owns ONLY Build/measurement/uncertainty.py, Build/measurement/UNCERTAINTY.md,
tests/measurement/test_uncertainty.py, evidence/S07/S07d/, Run-System/Runs/S07d/.
Shared inputs/fitter/tracker/README/dependencies/controls/main read-only. Leave
scoped commits UNMERGED; controller alone updates controls/integrates. No fanout.

Implement honest slow-motion/timebase classification and planned uncertainty
propagation around the actual deterministic fitter. Reuse existing validation;
unknown capture clock MUST abstain, delivered fps alone cannot establish it,
and no Earth-g-derived clock/scale. Known clock ratio alone does not prove
acquisition facts. Document exactly which evidence/correlation/noise assumptions
the result requires. Existing fields carry absolute one-standard uncertainty
for scale and capture ratio. Include these and timestamp/detection precision
only through explicit supported inputs/assumptions, never invented defaults.
Any introduced public input schema is local to this owned module and documented.
Do not relabel residual RMSE as calibrated g uncertainty or expose a guaranteed
coverage interval from three exact points. Unknown systematic components or
inadequate sample/rank must be explicit insufficiency/abstention. Fit/calibrate
training prefix ONLY; held-out suffix cannot tune noise, filtering or bounds.

Acceptance: real red/green synthetic tests demonstrate clock ambiguity held,
unit/sign and scale/clock sensitivity, honest known/unknown uncertainty and
conditioning/sample-size behavior, held-out isolation and malformed/numeric
boundary rejection. Run full measurement regressions; record fresh results,
concrete skills/files/limits/costs in REPORT. No real footage/model/API/GPU,
new downloads/installs, physical metric approvals, g measurements or GateM pass.
S07e/S12 remain scientifically gated. Questions via REPORT for STATE fallback;
no canonical writes/optional narration; final one status/absolute REPORT pointer.
