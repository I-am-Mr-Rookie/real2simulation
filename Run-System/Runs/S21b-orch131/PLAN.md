# S21b-orch131 PLAN
- Objective: measure every gravity/scene-scale error that the S21a frozen manifest's pinned evidence supports (value, uncertainty, n); mark the rest UNAVAILABLE with evidence reasons.
- Owns (used): BENCHMARK.md; Build/benchmark/errors.py, Build/benchmark/test_errors.py; evidence/S21/S21b-errors.json; Run-System/Runs/S21b-orch131/.
- Dep: S21a DONE (manifest.json/manifest.py). No GPU/API, no installs, no unfrozen inputs.
- Checks: python -B -m unittest Build/benchmark/test_manifest.py Build/benchmark/test_errors.py; python Build/benchmark/manifest.py check.
