# S09a plan

- Objective: define viewer adapter (S04a contract) and synthetic fixture scene (S05a bundle).
- Start UTC: 2026-10-27T18:11:53Z. Initial main bef9476; claim 55ffcf9.
- Owns: Build/web/src/viewer/; tests/viewer/; evidence/S09/.
- Dependencies: S04a DONE, S05a DONE. Lane CLAUDE, planned Opus 5.5 / medium.
- Budget: <=30 min, offline, no package manifest (S04 owns deps), no renderer.
- Checks: uses S04a/S05a contracts; fixture marked synthetic, not Gate R evidence;
  node unit tests for lifecycle/validation; S05a validator still PASS.
