# S07d plan

Start: 2026-10-28 approximately 08:00 UTC; first recorded clock 08:07 UTC.
CODEX-1, requested gpt-6.1-sol/medium; backend identity not independently exposed.
Base: 2bd54c60329f146d61021ed7e3e763e29feb61a9. Precreated checkout was
clean/detached; create local run/S07d here, never merge or change controls.

Objective: explicit capture-clock classification and conditional first-order
uncertainty around accepted deterministic fitter, synthetic tests only.

Owns: Build/measurement/uncertainty.py, Build/measurement/UNCERTAINTY.md,
tests/measurement/test_uncertainty.py, evidence/S07/S07d/, Run-System/Runs/S07d/.

Use Ponytail full: reuse validator/fitter and standard library, no dependencies,
smoothing, noise estimation, external calls or callers outside Owns. TDD red/green;
debug failures from observed evidence; fresh full measurement and repository tests.
Unknown clock/systematics/noise abstain. Prefix-only explicit precision inputs;
no confidence interval, empirical coverage, physical readiness or Gate M claim.
Stop new implementation by 08:25 UTC, finish by 08:30 UTC conservatively.
