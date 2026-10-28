# S08a — experiment contract

- Authorized: Koushik's `Complete run S08a`; manual protocol, CODEX-1.
- Claim UTC: 2026-10-27T17:30:19Z; main before claim f0d64943d6487657c037e27cd04b51f55af827f4.
- Planned model: GPT-6.1 Sol / medium. Actual runtime model/effort unavailable.
- Objective: define a versioned structural experiment contract with explicit units,
  input provenance and scene constraints compatible with scene v1.0.0.
- Owns: contracts/experiment/; Build/templates/; tests/spec/.
- Dependencies: S03 DONE. No product gate, inference, deployment or footage needed.
- Checks: schema self-validation; valid structural fixtures for four template shapes;
  negative tests for missing provenance, unit identity, versions and scene structure.
- Budget: <=30m from claim, no new implementation after minute25; zero service spend.
- Evidence: unittest output, schema documentation, task diff and run report.
- Non-goals: S08b ranges/dimensions, S08c geometry/stability, S08d-g template
  generators/analytic oracles, S08h final bad-spec regression; all gates NOT RUN.
