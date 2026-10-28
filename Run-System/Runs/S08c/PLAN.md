# S08c plan

- UTC start: 2026-10-27T17:52:44Z; stop by 18:22:44Z; no new implementation after 18:17:44Z.
- Authorization: Complete run S08c, orchestrator mode; questions to STATE fallback.
- CODEX-1, planned Sol medium; runtime model/effort unavailable, no settings change.
- Objective: reject out-of-scene and numerically unsafe experiment setups against an authoritative validated scene bundle.
- Owns: contracts/experiment/; Build/templates/; tests/spec/. Serialized run receipts/control files only outside that set.
- Dependency S08b DONE. Initial main 12e4d62; claim b3361d8.
- Checks: test-first negative geometry/stability cases; complete experiment and scene regressions; fresh post-rebase/main tests and diff check.
- Budget: offline only, no Meta/service/GPU spend. 30-minute timebox.
- Skills: read Superpowers test-driven-development and verification-before-completion; apply red/green tests and fresh verification. Other tools only when relevant.
