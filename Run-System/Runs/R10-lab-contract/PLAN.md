# R10-lab-contract — round 1

- Project inherited from owner handout: `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; no new chat/project or delegation.
- Branch `run/R10-lab-contract`, baseline `f82ed85fd96c38f8fcee23322657e92e5f4f8e92`.
- Issued 2026-10-28T19:50:37.990Z; cutoff 20:15:37.990Z; deadline 20:20:37.990Z (02:20:37.990 Dhaka).
- Objective: reproduce and minimally repair bounded simulation-only lab session lifecycle defects.
- Owns: `Build/lab/session-service.mjs`, `tests/lab/*session*.test.mjs`, this run directory, `evidence/S10/session-hardening/`.
- Callers inspected: API POST route, LabClient start/fit requests and abort/reset guards, fit-contract parser, existing service tests; trusted handoff and Python bridge read only.
- Checks: existing real bridge/fitter integration; cold concurrent fit, expiry/eviction/reveal; controlled bridge lifecycle/abort/capacity/error regressions. Native Claude gate review is parent acceptance work, not delegated here.
- Ponytail FULL: reuse existing Map, bounded bridge, stable hash/handoff and test file; no new dependency, process abstraction, UI/Python/simulator changes or shared controls.
- No paid/live physical work, secrets, archived data, publication, merge/rebase or configuration changes. OpenCodex-managed; not polled. Costs unknown.
