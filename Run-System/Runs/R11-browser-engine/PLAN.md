# R11-browser-engine

- Parent project: `91e441f8-e40c-4ec4-bea2-de7fa1582d97` (inherited user handout;
  inline exception, no claim of a newly verified app-chat binding).
- Lane/model: CODEX1, managed Sol / medium, as assigned; no route changes.
- Branch: `run/R11-browser-engine`; starting SHA `d4f615d70e7cbc02e79d34237b72aaefe7582e20`.
- Issued: 2026-10-28T20:12:01.767Z. Deadline: 2026-10-28T20:42:01.767Z
  / 2026-10-29T02:42:01.767+06:00. Minute25 cutoff: 20:37:01.767Z.
- Objective: smallest standalone NORMAL browser adapter/component using exactly
  the existing four RK4 engines, bounded at2000 samples, with actual fixtures and
  deterministic current-engine/server parity. Static full-engine trace is enough.
- Owns only: new `Build/web/src/lab/browser-simulator.mjs`, new
  `Build/web/src/lab/BrowserSimulation.jsx`, new
  `tests/lab/browser-simulator.test.mjs`, `evidence/S10/browser-simulation/`, this
  run's report directory. No parent integration or shared controls.
- Checks: four-template exact parity + invalid/bounded-input tests; fresh Node
  syntax/related tests; JSX parse + scoped component element/hook checks.
- No physical M/S12, real scene, paid GPU, deployment, publication, accounts,
  terms, secrets, browser controller or merged main. Parent integrates later.
