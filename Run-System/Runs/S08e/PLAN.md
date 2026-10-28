# S08e — projectile template and analytic answer

- UTC start: 2026-10-27T18:19:17Z. Limit 30m; no new implementation after 18:44:17Z.
- Requested lane/model: CODEX-1, GPT-6.1 Sol / medium. Actual: delegated Codex;
  exact runtime model/effort unavailable. No routing changes.
- Initial main: 9abe3e4bbc07ceb8b1951005b99d19b9a82d7256; claim: 8876980.
- Dependency S08d DONE; reports read: S09a, S02b, S08d.
- Owns: contracts/experiment/; Build/templates/; tests/spec/; run PLAN/REPORT
  and serialized canonical control updates under manual protocol.
- Objective: explicit sourced-input horizontal +X projectile factory with existing
  authoritative setup validation; deterministic vacuum closed-form oracle.
- Checks: RED then GREEN projectile tests (exact trajectory/impact, zero speed,
  provenance, input isolation, time domain and unsafe/tampered setup rejection);
  full experiment + scene regressions; diff check and fresh-main verification.
- No general launch angles, integrator, UI, services, footage, spend or publication.
- Skills: TDD and verification-before-completion; apply existing free-fall pattern
  without refactoring unrelated code. Existing repeated bundle validation remains
  a cost bottleneck, retained for trust-boundary safety.
- Budget: no external inference/GPU calls ($0); coding tokens/cost unavailable.
  Shared quota before used70%5h/50%weekly, reset1793132283; no reset/purchase.
- Questions: none anticipated; owner-question fallback if approval becomes needed.
