# S10fg-extension plan

- Objective: add deterministic replay records and Mystery-g public projection/fit-reveal contracts.
- Owns: `Build/simulator/replay.mjs`, `Build/simulator/mystery-g.mjs`, their tests, `evidence/S10/extension-replay/`, and this run folder.
- Checks: Node test files; timebox checker; inspect diff for only owned paths.
- Boundary: caller supplies the already-integrated private runner; this run does not claim template integration or a physical/fitter result.
