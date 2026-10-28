# R-S10-extension review report

- Status: DONE; no owned review work remains.
- Model/lane: CODEX-1 Sol medium, managed route.
- Branch/head: `run/R-S10-extension`, rebased onto canonical integrated main `d50289f`; review evidence commit `f7d4647`.
- Owns changed only: `evidence/reviews/R-S10-extension/` and this report/timebox.
- Ponytail full applied: smallest source-only review, isolated repros, no peer edits or generated peer outputs.

## Final review

- Contacts latest `d02e726`: explicit `simulated/synthetic` labels, exact dense sample step/time, same-state Rapier mapping, cloned/frozen vectors; focused contacts tests 5/5 PASS.
- Templates integrated in main: fixed-step RK4 ramp and nonlinear pendulum from validated S08 artifacts; focused extended-template tests 7/7 PASS.
- Replay latest integrated source: exact-version replay records reject unsupported values before acceptance; actual S11-shaped fitter handoff binds exact observations; Mystery-g projection is allowlisted and browser-compatible. Replay/Mystery-g tests 5/5 PASS.
- Lab: `python -m unittest discover -s tests/lab -p 'test_*.py' -v` 5/5 PASS, including actual four-template seeded replay regression. Parent evidence records pendulum max relative error `0.00026645 < 0.005`.
- Final integrated Node set: contacts/templates/replay 17/17 PASS after local `npm ci --ignore-scripts` for the pinned Rapier dependency. Parent's new contact-integration tests and version rejection brought the targeted set to 7/7 PASS.

## Findings and limits

Earlier findings were re-reviewed and closed: contacts reject forged labels/timing and deep-copy vectors; replay rejects fake fitter shapes and binds actual observations; lab regression has the replay dependency integrated. No open P1/P2 source findings remain in Owns.

S10g public DTO/fit-reveal contract is implemented, but the viewer intentionally keeps Mystery-g unavailable; no UI toggle/integration claim. S10h remains numeric-child-only until proper g/R-P evidence. R-P, physical Gate P, and whole Gate M are not run or claimed. Evidence is synthetic/offline only. No secrets, spend, deployment, auth, publication, model/config change, or quota polling.

Exact historical findings and commands are in `evidence/reviews/R-S10-extension/REPORT.md`.
