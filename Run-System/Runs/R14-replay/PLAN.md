# R14-replay — independent replay integrity audit

- Lane/model: CODEX-1 / managed gpt-6.1-sol, high (assignment; no independent runtime model introspection).
- Parent project: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; inherited contract/root, child UI membership not independently verified.
- Canonical root: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
- Isolated baseline: `74c886f9b2cc1322dde152f5be5813f813904bc6`; branch `run/R14-replay`; clean initial status.
- Issued: 2026-10-28T21:37:28.000Z; deadline: 2026-10-28T22:07:28.000Z (2026-10-29T04:07:28+06:00); implementation cutoff: 22:02:28Z.

## Objective / acceptance

Audit actual simulator replay hashes, canonicalization, seed/parameter/schema binding and malformed/tampered records, with independent expected oracles and frozen counterexamples. DONE denotes bounded audit completion, not product acceptance. No RK4 numeric audit.

## Exact Owns

- `Run-System/Runs/R14-replay/`
- `evidence/S10/replay-invariants/`
- `tests/simulator/r14-replay-invariants.test.mjs`

No product/control edits, merges, fanout, heavy builds, installs, browser actions, paid GPU, real scenes, physical gates or deployments. Existing Node/Python helpers only. Full Ponytail: smallest standard-library tests; reuse actual template factories/engines without copying physics; preserve failing expected oracles instead of fitting tests to bugs. Send confirmed input/expected/actual/root-cause findings nonterminal for parent integration, continue independent checks. Start no new implementation after minute25; verified fully DONE may finish early.
