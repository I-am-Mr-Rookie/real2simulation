# S16b-orch89 verification — synthetic offline only

Base main: `1dfc4e2ce76708aa39e998ecc385237c44877a0c`.

- Final `python -B -m unittest discover -s tests/sidebar-tools -t tests/sidebar-tools`:
  **38 tests, OK, 4.638 seconds**, exit 0. Raw receipt: S16b-orch89-sidebar.txt.
  This includes 23 existing S16a contract methods and 15 application methods.
- `python -B -m unittest discover -s tests/spec -t tests/spec`:
  **93 tests, OK, 50.632 seconds**, exit 0. Run directly; console receipt in this
  worker's tool output, no raw disk transcript captured. No duplicate rerun needed.
- `git diff --check`: exit 0 after the final application test addition and docs.
- New module imported by the exact sidebar discovery command; no install needed.

Application checks cover four valid templates, whole-section/multiple-section
replacement, preserved provenance labels, defensive copies, call/result correlation,
stale base and scene binding, bad envelopes/identity/sections, invalid units/numbers/
uncertainty/unknowns/nonfinite values, authoritative scene mismatch/asset hash/missing
files, geometry bounds, timestep/step-count limits and typed exception causes.
Mock downstream consumers are unreachable on rejection. The tool itself contains no
rebuild call, even for success: the successful return is the S16c handoff.

These are authored synthetic fixtures, not licensed real-clip, calibrated physical,
GPU, live provider, persistence, simulator execution, UI or deployment evidence.
