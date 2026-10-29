# S14f-orch23 REPORT — Enforce tool-only numbers in replies — DONE

- Lane/model: CODEX-1 row, assigned anthropic/claude-opus-5-5 high (desktop worker). Coding quota: OpenCodex-managed; not polled.
- UTC: issued 2026-10-29T14:32:47Z; work start 14:33:24Z; work stopped 2026-10-29T14:47:12+00:00; deadline 15:02:47Z.
- Base main f37121c; branch run/S14f-orch23 (worktree .worktrees/S14f-orch23). Not merged: controller integrates
  (contract forbids writes to the canonical root).
- Tokens/cost: Meta API 0 calls, $0; model tokens unobservable.

## Result

Acceptance "Untraced number is blocked and replaced by tool-backed response" — met on SYNTHETIC replies against
actual S10 simulator + fitter outputs computed in-test.

- `Build/agent/tools.py`: `safe_reply(response, tool_outputs, scene_id) -> (text, blocked_issues)`: valid reply ->
  `render` text unchanged; any untraced number / contract issue blocks the whole reply and returns
  `render(tool_backed(...))` (code-built lead + every tool quantity as a ref). No outputs -> number-free block text.
  Invalid tool outputs raise (not masked). `tool_backed` guards quantity names containing digits ("value").
- `Build/agent/trial.py`: S14e `tool_only` now reuses `tool_backed` (same text/behaviour; S14e tests + mutants green).
- `contracts/agent/validate.py`: number-word list += ordinals third..twelfth, tenths/hundredths, "one point"/"point one",
  "single digit". "double" deliberately NOT added (blocks "double-check").
- `contracts/agent/CONTRACT.md`: S14f section + limits update. `tests/agent/test_reply.py`: 9 tests.

## Fresh checks (2026-10-29, this worktree)

- `python -m unittest -v tests.agent.test_contracts …test_muse …test_interview …test_retry …test_trial …test_reply`
  -> Ran 49 tests OK (40 existing + 9 new): [evidence/S14/S14f-unittest.txt](../../../evidence/S14/S14f-unittest.txt).
- `python evidence/S14/S14f_mutation.py .` -> 6/6 mutants KILLED (fallback removed, values dropped, digit name leak,
  "one point", ordinals, fallback without outputs): [S14f-mutation.txt](../../../evidence/S14/S14f-mutation.txt).
- `python evidence/S14/S14e_mutation.py .` (after trial.py refactor) -> 8/8 KILLED: [S14f-S14e-mutation-rerun.txt](../../../evidence/S14/S14f-S14e-mutation-rerun.txt).
- `git diff --stat` after mutation runs: only intended edits (sources restored).

## Ponytail (full) applied

- Reuse: S14a `validate_response`/`numeric_issue`/`render`, S14e fallback shape (moved into shared `tool_backed`,
  deleting the trial copy), S10 session bridge + test_trial helpers imported for real tool outputs, S14e mutation pattern.
- Smallest complete change: one function + one shared helper (~30 lines), regex extension, no new deps/schema/version bump.
- Skipped: partial redaction of bad segments (whole-reply block is safer/simpler); question/chip rendering in
  `render` (unchanged S14a scope); Roman numerals/"first"/"second" (false-positive risk); web wiring (outside Owns).

## Limits / risks / next

- Fixture-only: SYNTHETIC replies, 0 live Meta calls. Not Gate A, real-scene, calibration or physical evidence.
- `Build/web/src/workspace/interview.mjs` mirrors `render` in JS; any UI showing model text must go through
  `safe_reply` (server) or mirror it — not in Owns, unverified. Candidate follow-up for S15/S14g.
- Process incident (recovered): an earlier tool call lost its output while two S14e mutation runs overlapped; one
  restored a mutant into trial.py. Detected via `git diff`, repaired by patch, then all checks rerun serially green.
- Number-word list remains a shortcut; S14g thirty-turn suite should feed misses back.
- Next: controller review/ff-merge of run/S14f-orch23; S14g (needs S13).

## Communication

Silent; no owner questions; one completion message to controller chat as authorized.
