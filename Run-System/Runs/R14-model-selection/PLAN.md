# R14-model-selection — independent bounded audit

- Objective: audit fitter API model-selection/AIC, residual semantics, supported degrees and sample counts using frozen independent expected oracles; no covariance/QR implementation audit.
- Requested lane/model/effort: CODEX-1 / existing managed gpt-6.1-sol / high. Runtime model identity is not independently exposed.
- Baseline: main `74c886f9b2cc1322dde152f5be5813f813904bc6`; isolated branch `run/R14-model-selection`, initially clean.
- Parent: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; canonical root `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`. Inherited association only; no independently verified child UI association.
- Owns: `Run-System/Runs/R14-model-selection/`; `evidence/S11/model-selection-invariants/`; `tests/fitter/test_r14_model_selection.py`.
- Window: issued 2026-10-28T21:37:28.000Z; minute25 cutoff 2026-10-28T22:02:28.000Z; deadline 2026-10-28T22:07:28.000Z (Dhaka 2026-10-29T04:07:28.000+06:00).
- Acceptance: exact-source counterexample or bounded clean conclusion; minimal independent oracle and fresh targeted CPU checks; honest evidence/limits. DONE means audit complete, not product pass.
- Method: reuse installed unittest/standard-library exact arithmetic and existing test style; no installs, product edits, controls, merges, deployments, UI, fanout, paid jobs or private/environment values. Nonterminal confirmed findings immediately sent to parent; keep auditing.
- Read/apply Ponytail full: smallest complete evidence/test-only change, reuse helpers where applicable, no new abstractions/dependencies or unrelated checks. Freeze expected behavior, never fit oracle to a bug.
- Coding usage: OpenCodex-managed; not polled. Tokens/costs unknown if unobservable.
