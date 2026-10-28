# S11abc-swarm plan

- **Owns:** `Build/instruments/`, `contracts/fit/`, `tests/instruments/`,
  `evidence/S11/instruments-swarm/`, this run directory.
- **Objective:** implement S11a quantity contracts, S11b seeded stopwatch
  noise, and S11c camera/ruler/light-gate quantization.
- **Ponytail choices:** stdlib only; reused existing finite-number conventions;
  one shared quantity validator instead of fitter-specific copies; no
  dependency, sensor framework, calibration default, or physical integration.
- **Checks:** focused unittest discovery, compileall, diff check.
