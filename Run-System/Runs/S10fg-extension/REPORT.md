# S10fg-extension report

- **Result:** DONE after reviewer correction. CODEX-1 / GPT-6.1 Sol medium, managed route. Branch `run/S10fg-extension`; no shared controls/manifests changed.
- **Corrections:** replay now uses browser-capable `globalThis.crypto.subtle` SHA-256, async stable hashes, accessor/cycle/sparse/unsupported-value/extra-array-property rejection, and deep-clones before freezing. Mystery-g exposes only allowlisted `{time_s, position_m}` samples; rejects arbitrary metadata and private/accessor-shaped inputs.
- **Trust boundary:** `createTrustedFitterHandoff` accepts the actual S11 Python response shape (`status: ok`, `gravity` quantity with `m/s^2`, finite value/uncertainty, `source.label: simulated`, available covariance, supported uncertainty model). `revealFit` requires the opaque handoff; source and uncertainty are preserved. A fabricated structurally similar object is rejected because it is not marked by the handoff factory. This is a tool-boundary marker, not cryptographic authentication.
- **Fresh checks:** `node --test tests/simulator/replay.test.mjs tests/simulator/mystery-g.test.mjs tests/simulator/trajectories.test.mjs tests/simulator/simulator.test.mjs` — 13 passed; Mystery-g test invokes `Build.fitter.api.handle` through Python and consumes its JSON response. `git diff --check` passed.
- **Evidence:** `evidence/S10/extension-replay/contract-evidence.json`.
- **Skipped:** no template/browser end-to-end integration; no model-authored success, spend, deployment, or shared-control edits.
