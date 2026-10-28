# S08d plan

- Objective: validated free-fall template and deterministic analytic oracle.
- First retained UTC clock receipt: 2026-10-27T18:04:05Z; initial reads preceded
  this receipt by approximately two minutes. Exact initial-read UTC unavailable.
- Initial main observed: ba5a198803e9d5ac8728c4126399df1e1154a7d0; claim 1455964.
- Owns: contracts/experiment/; Build/templates/; tests/spec/.
- Dependency: S08c DONE. CODEX-1, planned Sol medium; runtime ID unavailable.
- Budget: <=30 minutes, no new implementation after minute25; offline only.
- Checks: factory passes validate_setup; independent closed-form cases and signed
  velocities; invalid inputs fail closed; spec/scene regressions after rebase/main.
- Serialized controls/receipts follow manual protocol; fallback questions in STATE.
