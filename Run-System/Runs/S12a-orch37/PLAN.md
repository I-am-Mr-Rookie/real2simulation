# S12a-orch37 PLAN
- Lane CODEX-1, assigned anthropic/claude-opus-5-5/high; OpenCodex-managed, not polled. Project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.
- Issued 2026-10-29T20:43:22Z; deadline 21:13:22Z (Dhaka 2026-10-30 03:13:22); cutoff 21:08:22Z. Base main d131047.
- Objective: calibration/withheld-frame boundary. Split by frame index (reuse Build/measurement validate_input), hash+freeze suffix before any fit, fitter sees prefix only, evaluation only against committed suffix, scale-free normalized error; Gate M NOT_MET in every output (Q15=A).
- Owns: Build/real2sim/; tests/prediction/; evidence/S12/; Run-System/Runs/S12a-orch37/.
- Checks: tests/prediction unittest; live Gate M via gate_m.evaluate_sources; regression tests/measurement + tests/fitter.

