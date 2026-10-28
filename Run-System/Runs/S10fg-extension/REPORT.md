# S10fg-extension report

- **Result:** DONE. CODEX-1 / GPT-6.1 Sol medium, managed route. Branch `run/S10fg-extension`, rebased/started at `03d57f6`; no shared controls or manifests changed.
- **Clock:** issued `2026-10-28T18:04:15Z`; nominal deadline `2026-10-28T18:34:15Z`; work stopped/reported `2026-10-28T18:08:04.9963498Z` (Asia/Dhaka). `TIMEBOX.json` preserves the supplied contract times and actual completion time.
- **Changed:** `Build/simulator/replay.mjs` provides canonical JSON hashing, explicit version/seed/numeric parameters/trace, immutable records, hash-verified caller-supplied replay, and hostile/nonfinite/sparse rejection. `Build/simulator/mystery-g.mjs` provides an immutable public observation projection and single-use reveal only from an explicit successful fitter result; private gravity/seed/setup remain closure-only and are not returned by methods or errors.
- **Tests/evidence:** `node --test tests/simulator/replay.test.mjs tests/simulator/mystery-g.test.mjs tests/simulator/trajectories.test.mjs tests/simulator/simulator.test.mjs` — 15 passed. `git diff --check` passed. Evidence: `evidence/S10/extension-replay/contract-evidence.json`.
- **Ponytail applied:** reused existing Node/no-dependency style and caller runner boundary; no new package/dependency, UI, template integration, fitter execution, browser test, or model-authored numeric result.
- **Risk/limit:** this is a contract extension only; actual extended-template integration and real fitter/browser end-to-end remain parent scope. Public observations are intentionally exposed for fitting; reveal labels are metadata, not authentication.


