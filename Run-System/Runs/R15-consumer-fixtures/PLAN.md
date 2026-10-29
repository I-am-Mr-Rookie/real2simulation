# R15-consumer-fixtures

- Assigned CODEX-2, existing managed Sol/medium. Parent project `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; inherited binding, child UI not independently verified.
- Issued 2026-10-29T07:39:21.000Z; minute25 cutoff 08:04:21Z; deadline 08:09:21Z / 14:09:21 Dhaka (1800 seconds). Owner stop 10:00Z / 16:00 Dhaka. No early incomplete terminal report; verified fully DONE may finish early.
- Reused clean transport checkout at `9598213140b74db8be2fca2adc21aa408a73cbb5`, preserving `run/R15-transport`; created `run/R15-consumer-fixtures` from combined source `b37f7b8` without reset/deletion.
- Objective: refresh only derived CLI snapshots after independently checking unchanged artifacts against accepted S08 analytic oracles and unchanged 0.005 threshold; restore all ten browser consumer tests.
- Owns: `evidence/S10/browser-simulation/*.server-trace.json`, directly necessary derived provenance there, `evidence/S10/consumer-recovery/`, and this run directory only. No product source, frozen artifact, invariant suite, threshold or browser test edits. No main merge.
- Read current canonical AGENTS/STATE/QUEUE/timebox policy, full Ponytail, R15-numerics report/model justification, existing generator, consumer and accepted S08 oracle code. Existing generator rewrites artifacts: reuse its actual Node CLI invocation on original artifact bytes, not its artifact creation/writes. Reuse S08 analytic functions and characteristic scales from existing regression; no manual snapshot numbers or new dependencies.
- Acceptance: fresh 10/10 browser consumer suite, all four actual CLI traces independently within 0.005, old/new snapshot/source hashes and numerical deltas, immutable source/artifact isolation, scoped commit, truthful timing/report.
- Skip broad build/physics repeats, IAB (parent serialized), fanout, network/install/model/GPU/physical/real-scene/deploy/publication/auth/config/quota work. Tokens/cost unknown; OpenCodex-managed; not polled.
