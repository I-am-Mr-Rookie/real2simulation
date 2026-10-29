# S14a-orch14 REPORT — DONE (contract child; Gate A not run)

- Lane/model: CODEX-1 row, anthropic/claude-opus-5-5 high (controller assignment). Coding quota: OpenCodex-managed; not polled. Meta/API spend $0; no LLM/GPU calls.
- UTC: issued 2026-10-29T11:21:53Z, work start ~11:22Z, work stopped 2026-10-29T11:30:25Z. Branch `run/S14a-orch14` (base main `1430b38`), worktree `.worktrees/S14a-orch14`. Not merged; controller integrates.

## Objective / acceptance
QUEUE S14a: scene, question and tool-output contracts; structured response schema forbids untraced numeric claims (tests prove rejection). **Met** on visibly synthetic fixtures.

## Changes (Owns only)
- `contracts/agent/response.schema.json` — response v1: text/number segments; text pattern forbids ASCII digits; number segments are refs only (no inline value); ≤3 questions (chips/free_text/chips_and_free_text, ≤6 chips), ≤3 candidates; additionalProperties false.
- `contracts/agent/validate.py` — `validate_response` (strict JSON → schema → Unicode numerals/fractions + number words → ref resolution → scene binding → chip/kind consistency), `validate_tool_output` (tool fitter|simulator, status ok, quantities labelled measured|simulated).
- `contracts/agent/CONTRACT.md` — contract doc + limits.
- `Build/agent/tools.py` — `scene_context` (validated bundle → number-free model input), `fit_tool_output` (fitter api → tool output), `render` (value ± uncertainty unit (label)).
- `tests/agent/test_contracts.py` — 11 tests; `evidence/S14/` logs.

## Ponytail (full) — applied
- Reuse: S11 `contracts/fit/quantity.validate_quantity` for every tool quantity (relabelled copy so `measured` passes its simulated-only label gate, one-line comment); `contracts/experiment` `parse_json` for strict JSON; `contracts/scene` `validate` gates scene context; `Build.fitter.api.handle` + `Build.instruments.synthetic` give the end-to-end fixture (no new fixtures files, existing `test-data/synthetic/scene/room-v1`).
- Smallest complete: refs-not-values design makes "number absent from tool outputs" structurally impossible instead of regex-matching numbers against outputs; one schema file + one validator + one adapter module; jsonschema already installed (4.23.0); no new deps.
- Skipped (not asked / later rows): Muse calls (S14b), chip→spec mapping (S14c), retry loop (S14d), trial check (S14e), tool-only fallback reply (S14f), Gate A 30-turn suite (S14g), candidate template registry check, tool-output↔scene binding, user-number echo label.

## Commands / results (fresh)
- `python -m unittest discover -s tests/agent -p 'test_*.py' -v` → 11 OK (`evidence/S14/S14a-unittest.txt`).
- Negative controls: numeric check disabled → 10 failing results; segment semantics disabled → 5 failures (`evidence/S14/S14a-mutation.txt`).
- Regression `python -m unittest discover -s tests/fitter -p test_*.py` → 65 OK.
- Rejection cases proven: ASCII digits (schema alone + validator), Arabic-Indic/Roman/fraction/CJK numerals, number words, numbers in prompts/chips/candidates, unknown tool output/quantity, inline `value` smuggling, extra fields, non-measured/simulated label, empty evidence, NaN, bad unit, non-fitter/simulator tool, error status, duplicate ids, failed fit, >3 questions, wrong scene, duplicate-key JSON, NaN JSON.

## Limits / risks
- Number-word list is a shortcut ("one" allowed; Roman letters "XIV", ordinals not caught); Gate A must extend it. Fail-closed false positives (`m/s²`, "half").
- Fixture-only: no gate, real-scene, calibration or physical claim. Tests need run from repo root (namespace packages, like tests/fitter).
- Communication: silent; one completion message to controller as authorized.

## Next
S14b consumes `scene_context` + response schema for Muse structured output; S15d can bind to `$defs/question`.
