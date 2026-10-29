# S14c-orch19 REPORT — DONE

- Lane/model: anthropic/claude-opus-5-5 high; coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable). Meta/Muse calls: **0** (offline; recorded fixture replay only). GPU/spend: none.
- UTC start 2026-10-29T11:49:14+00:00 (issue; work began 11:50:04) — end 2026-10-29T11:58:41+00:00. Branch run/S14c-orch19, code commit f6c78f3 on main 526ec0c. Worktree .worktrees/S14c-orch19.
- Communication: silent; one authorized completion line to controller. Canonical controls untouched.

## Result
Acceptance "Chips and free-text map into validated spec inputs": met on SYNTHETIC fixtures.
- `Build/agent/interview.py` (115 lines): `template_of` (validated S14b candidate -> template), `questions` (code-owned one to three questions per template, emitted as an S14a agent-response and run through `validate_response`, so number-free), `answers_to_spec` (chip/free text -> sourced quantities patched onto a same-template base spec, then S08c `validate_setup`; all issues aggregated in `AgentContractError`).
- Decision (S14a open item): user numbers enter the spec only, label `assumed`, evidence `user-input:<param>:<chip:id|free-text>`, uncertainty null; never echoed in agent text.
- `contracts/agent/CONTRACT.md`: S14c section. `tests/agent/test_interview.py`: 5 tests.

## Ponytail (full) applied
- Reuse: S14a `validate_response` for question number-freedom/schema; S08c `validate_setup` for all physics/range/bounds checks (no duplicated range logic); S14b `muse.understand` + recorded fixture `live-room-v1-d` for template choice; S08 test `setup()` fixtures as base specs; existing `AgentContractError`.
- Smallest complete: one data table (QUESTIONS) + one regex parser; no new schema, UI, state machine or dependency. Chips carry only exact meanings (at rest / frictionless = zero); no default physical numbers. Only conversion: deg -> rad (angles require an explicit unit).
- Skipped (named): mapping model-authored S14b question chips to spec inputs (free-form ids; shown as context only); asking gravity/body/origin/simulation inputs (base-spec provenance kept); web UI wiring (S15/S17 lanes); uncertainty entry for user input.

## Fresh checks
- `python -m unittest discover -s tests/agent -p 'test_*.py' -v` -> 23 OK (evidence/S14/S14c-unittest.txt).
- `python -m unittest discover -s tests/spec -p 'test_*.py'` -> 93 OK (regression; untouched).
- Mutation spot checks, 5/5 killed (evidence/S14/S14c-mutation.txt): skip validate_setup, accept Unicode digits, accept bare angle, digit in prompt, non-zero rest chip. First run exposed a weak test (bare angle "5" was rejected by the S08 range, not the parser); test fixed to "0.1".
- Real rejection messages + mapped ramp parameters: evidence/S14/S14c-probe.txt.

## Limits / risks
- Fixture-only: SYNTHETIC scene/specs and hand-written SYNTHETIC answers; not Gate A, real-scene, calibration or physical evidence.
- Free-text parser accepts plain decimal/exponent with contract units (+deg); "1.5 metres", fractions and locale commas are rejected (fail-closed; user retypes).
- Caller's base spec must already hold valid values for unasked fields.

## Next
UI lane: render `questions()` chips, post answers to `answers_to_spec`, show issues verbatim.

