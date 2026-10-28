# S07c — deterministic free-fall fitter, synthetic verification

Fresh CODEX-1 gpt-6.1-sol/medium <=30m, no new work after25m. Controller explicitly
decoupled implementation from S07b using accepted frozen S07a frame/input schema;
not a physical-gate or approval change. Read QUEUE/STATE/DECISIONS and
evidence/S07/S07a-controller-acceptance.md plus actual inputs.py/README/tests.

Isolated managed worktree/branch run/S07c. Owns ONLY:
Build/measurement/free_fall.py; Build/measurement/FITTING.md;
tests/measurement/test_free_fall.py; evidence/S07/S07c/; Run-System/Runs/S07c/.
Frozen inputs.py, shared README/dependencies/controls read-only. S07b owns tracking
module/test/docs; no duplicate adapter work or messages. Leave commits UNMERGED;
controller integrates and serializes controls. Questions/dependency changes REPORT.

Implement planned deterministic least-squares free-fall fit with explicit units,
sign convention, initial position/velocity, residuals and failure/abstention.
Use only training prefix to fit; immutable held-out suffix for separate evaluation.
Input source-pixel coordinates/PTS require verified scale and capture mapping for
metric conversion; call existing validation, refuse metric-ineligible data.
Synthetic test records may explicitly declare synthetic calibration, never forge
actual-media approval. Unknown real calibration/capture clock cannot become9.81
or an assumed slowdown factor. Do not fit Earth g to recover the clock. Preserve
origin/conditioning/numeric stability, enough distinct samples, finite values and
degenerate/rank-deficient/noisy cases. No silently fabricated uncertainty intervals;
S07d owns full propagation. Document diagnostics that are not calibrated intervals.
Respect planned smoothing where justified without leakage or gratuitous framework.

Acceptance: reproducible synthetic g recovery plus units/residuals/held-out
isolation and invalid/abstaining-input tests. No real tracking/g/inference/GPU or
Gate M pass/failure. S12 stays locked. No downloads, uploads/secrets, model calls,
accounts/terms/purchases/provider/global-policy changes or quota polling.

Read/APPLY Ponytail full; TDD for nontrivial fitter, systematic-debugging and fresh
verification. Reuse existing numeric/library patterns; smallest complete robust
implementation. No heavyweight installs/new framework or ceremonial tests.
Concrete red/green/checks/skills/limits in concise REPORT. Silent default, final
one status/absolute REPORT pointer. No extra agents for this bounded task.
