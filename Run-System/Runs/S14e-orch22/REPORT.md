# S14e-orch22 REPORT — DONE

- Lane/model: anthropic/claude-opus-5-5 high; coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable). Meta/Muse calls: **0** (offline; billing hold respected). GPU/spend: none.
- UTC issue 2026-10-29T12:26:31+00:00 (worktree 12:28:55) — work stopped 2026-10-29T12:37:14+00:00. Branch run/S14e-orch22 from main 0ca50f2; code commit 681b65b. Worktree .worktrees/S14e-orch22.
- Communication: silent; one authorized completion line to controller. Canonical controls untouched.

## Result
Acceptance "Trial claims reference actual fitter/simulator output": met offline, on real S10 simulator + fitter runs inside the tests, with hand-written SYNTHETIC Spark replies.
- `Build/agent/trial.py` (new, ~100 lines): `trial_outputs(trial_id, start, fit)` turns S10 session-bridge start/fit results into validated tool outputs `<trial>-sim` (simulator duration/drop = last simulated observation) and `<trial>-fit` (fitter gravity); `trial_context` (what Spark sees, values included); `build_check_request` (model `muse-spark-1.3`); `validate_check` (S14a validation against THIS trial's outputs + must cite >=1 quantity + no questions/candidates); `check_trial` (1+3 bounded retries with fed-back issues; transport errors propagate); `tool_only` code-owned fallback with no model claim.
- `Build/agent/muse.py`: `build_request` got an `instructions` keyword (default unchanged; Wonder callers and S14d mutation harness unaffected).
- `contracts/agent/CONTRACT.md`: S14e section. `tests/agent/test_trial.py`: 10 tests.

## Ponytail (full) applied
- Reuse: S10 `Build/lab/session-bridge.py` `handle` start/fit (actual node simulator + `Build.fitter.api.handle`) for trial data; S14a `fit_tool_output`, `validate_tool_output`, `validate_response`, `render`; S14b `build_request`/`output_text`/schema; S14d `MAX_RETRIES` and loop shape.
- Smallest complete: one module + one keyword arg; no new schema (agent-response reused), no verdict field, no recorder, no config.
- Decision: retry loop duplicated (~8 lines) instead of refactoring accepted S14d `understand_with_retry`: keeps S14d code and its mutation harness byte-stable (re-run: 7/7 still killed). Fallbacks differ (ask_user vs tool_only).
- Skipped (named): live Spark run/recorder (billing hold); verdict/pass-fail field (not asked; numeric pass/fail stays code-owned later); S14f general reply enforcement; UI wiring (S15 lane); ramp/pendulum trials (bridge fit path is vertical drop; free_fall + projectile probed).

## Fresh checks
- `python -m unittest discover -s tests/agent -p 'test_*.py' -v` -> 40 OK (evidence/S14/S14e-unittest.txt).
- `python -m unittest discover -s tests/spec -p 'test_*.py'` -> 93 OK (regression).
- Mutation spot checks 8/8 killed (evidence/S14/S14e-mutation.txt via evidence/S14/S14e_mutation.py): uncited claim, questions/candidates, non-trial-specific fitter id, fabricated simulator value, retry count, feedback dropped, fallback untraced claim, transport retried. S14d harness re-run 7/7 killed (not re-saved).
- Probe (evidence/S14/S14e-probe.txt): free_fall + projectile actual trials; rendered check shows fitter gravity 9.81 ± 7.4e-05 m/s^2 (simulated), drop 0.1962 m, duration 0.2 s exactly from tool outputs; number-word reply rejected then retried; 4 rejects -> tool-only fallback.

## Limits / risks
- Fixture-only for the model side: no live Spark output; whether `muse-spark-1.3` honours the schema/minimal reasoning is unverified. Not Gate A, real-scene, calibration or physical evidence.
- Spark sees tool values (needed to check); it can only cite them by ref, but a wrong qualitative judgement ("consistent") is not machine-checked.
- `SIM_UNCERTAINTY` mirrors bridge INSTRUMENTS (1e-6) by hand; drift risk if the bridge changes. Tests need `node` on PATH.
- Budget: worst case 4 Spark calls per trial.

