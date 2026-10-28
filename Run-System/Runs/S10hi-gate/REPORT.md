# S10hi-gate report

- Run: `S10hi-gate`; lane/model: `CODEX-1`, Sol high, inherited managed route.
- Base/branch: clean detached checkout was switched/repointed to `run/S10hi-gate` at `bd5df5f`; no destructive `git reset`/`reset --hard` was used and no rebase was needed.
- Issued: `2026-10-28T18:34:51Z`; original deadline: `2026-10-28T19:04:51Z`; minute-25 cutoff: `2026-10-28T18:59:51Z`; work stopped: `2026-10-28T18:57:39Z`; reported: `2026-10-28T18:57:45Z`. Timebox is 30 minutes; no early PARTIAL/BLOCKED exception used.
- Owns changed only: `Build/lab/acceptance.py`, `tests/lab/test_acceptance.py`, `evidence/S10/acceptance/`, and this run report/control folder.

## Result

Implemented the smallest complete acceptance orchestrator by reusing `Build.lab.regression.quantity`, S08 template factories and analytic oracles, `export_validated_setup.export`, the actual Node simulation transport, and `replay-check.mjs`. It authors 15 explicit cases across all four templates: gravity variations, short/long stable horizons, upward free-fall, zero-horizontal and tiny-height ballistic cases, positive-acceleration ramp endpoint preflight, multiple-period pendulum, and zero-answer equilibrium.

Fresh evidence: `evidence/S10/acceptance/acceptance.json` reports 15/15 passed, 0 failed, 0 rejected, actual seeded replay/determinism for every case, unchanged threshold `0.005`, dimensional characteristic scales, and `zero_answer_guard` for equilibrium. Endpoint values are only clamped when the fixed-step timestamp exceeds the oracle limit within a strict 4-ULP tolerance and are recorded as representational clamps; no measured case is filtered.

Contact diagnostic installed the already-pinned dependency with `npm ci --ignore-scripts --no-audit --no-fund` in `Build/simulator`, then measured the existing same-state Rapier adapter at dt `0.02`, `0.01`, and `0.005` for free-fall/projectile. All six rows observed contact at `0.62 s`; spread was `0`, max absolute sampled contact-time error versus the analytic `0.6223823880 s` was `0.0023823880 s`, and no jitter or rebound was observed. Fallback was not observed or applied; its machine-readable policy remains RK4-only with free dragging disabled if contact support becomes unavailable/jittery. No UI change was made.

The checkout does not expose a verifiable S10g UI transport/toggle path, and the required other-vendor R-P CLI review ended `ECONNREFUSED` per controller callback. Neither is claimed complete. This run is synthetic numeric readiness only, not Gate P, Gate M, physical, UI, or R-P evidence.

## Checks

- `node --test tests\\lab\\contact-integration.test.mjs` — 2/2 passed after install.
- `python -m unittest tests\\lab\\test_regression.py tests\\lab\\test_acceptance.py` — previously 3/3 passed; post-install acceptance rerun completed with 15/15 cases passing.
- `python -m Build.lab.acceptance` — completed and wrote fresh evidence.
- `git diff --check` — passed.
- Coding quota: `OpenCodex-managed; not polled`.

## Ponytail reuse / skips / risks

- Reused existing factories/export/oracles/transports; added no dependency, integrator, model-authored number, UI, manifest, or control edits.
- Skipped browser/paid builds, deployment, physical/real-scene claims, R-P reroute/retry, and any S10g UI implementation because they are outside Owns or explicitly held.
- Risk: contact evidence is synthetic and sampled at first contact only; the measured `0.0023823880 s` timing error is not a physical Gate-P result. Parent must not present the no-jitter sweep as broad physical validation.
- Communication compliance: one required nonterminal status callback; no optional worker chatter.
