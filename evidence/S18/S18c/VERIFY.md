# S18c verification

- `python -B -m unittest discover -s tests/library -t tests/library -v`:
  **36 tests PASS** (28 existing, eight projectile/availability tests).
  Raw output: [library-tests.txt](library-tests.txt).
- Projectile validator: **VALID, four local-only demos**;
  [projectile-validation.txt](projectile-validation.txt).
- Existing free-fall validator: **VALID, five local-only demos**;
  [free-fall-regression.txt](free-fall-regression.txt).
- [custody.json](custody.json): exact acceptance bytes, every numeric pointer,
  original run-report hash, hashed bounce shortfall sources and all inspected
  S11 JSON refs. No new object; free-fall and original manifest remain unchanged.
- `git diff --check` and `git diff --cached --check`: PASS.
- Final 06:59Z audit: every saved custody reference still has its recorded hash.
- Final timebox arithmetic: [timebox-check.txt](timebox-check.txt), generated at
  the original deadline before the authorized post-deadline bookkeeping commit.

## What this does not verify

No trajectory or media playback, guest route, calibrated real-clip result,
held-out real-clip comparison, uncertainty, physics gate or parent S18 acceptance.
Bounce is UNAVAILABLE: no accepted source to index. The existing S10 acceptance
metrics are simulated pre-contact analytic comparisons, **not held-out real data**.
No API/GPU/spend, installs, deployment, secrets, auth changes or canonical controls.
