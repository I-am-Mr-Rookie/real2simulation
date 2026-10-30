# S16a-orch80

- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
- Objective: offline typed sidebar request/result contracts, validator-first spec patch, rebuild and licensed-library search; no execution/provider wiring.
- Assigned: CODEX-2, gpt-6.1-sol / medium; OpenCodex-managed; not polled.
- Issued: 2026-10-30T05:45:52+00:00; implementation cutoff 06:10:52Z; deadline 06:15:52Z (12:15:52 Dhaka).
- Base: main dc74261; branch run/S16a-orch80; isolated plain Git worktree .worktrees/S16a-orch80.
- Owns: Build/sidebar-tools/; tests/sidebar-tools/; evidence/S16/; Run-System/Runs/S16a-orch80/.
- Reuse: contracts.experiment.validate_experiment.validate + parse_json; contracts.agent.validate.validate_tool_output; jsonschema already required by contracts.
- Checks: offline positive/negative request and result validation, no mutation, stale digest/scene rejection, licence/provenance completeness, existing spec/agent regressions.
- Dependencies S12/S14 remain PARTIAL; controller explicitly pulls contracts forward against their main interfaces. No gate claims. S18 unmerged work excluded; define stable source/provenance projection and document adapter boundary.
- No canonical controls, merge, dependencies, secrets, network, spend or provider calls.
