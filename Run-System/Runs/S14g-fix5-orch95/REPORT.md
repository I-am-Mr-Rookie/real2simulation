# S14g-fix5-orch95 REPORT — DONE

Lane CODEX-1 / S14; model anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). UTC start 2026-10-30T06:37:44Z (issue); work stopped ~06:46Z; well before deadline 07:07:44Z. Branch run/S14g-fix5-orch95 from main 2cd5747. Offline, network not used, spend $0. Tokens: unknown (not observable).

## What changed (R-A RECHECK-fix4 F1-R2, P1)
Structural rule replaces per-phrase lists: in visible text ANY unit word (length, mass, force/energy, time, angle, g, N, J, W, Hz, Pa, imperial…, incl. hyphen compounds such as `one-second`) is allowed only when **bound**:
1. right after a cited quantity (`<q> metres per second squared`), or
2. a label chain ending in `:`/`=` right before a cited quantity (`in metres: <q>`), or
3. a unit named with no amount after `in` (`in metres per second`, `in deg or rad`).
Chains pass only unit words, `per/squared/cubed/or` and spaces/symbols; any other word or `. ! ? ;` breaks the binding. Unbound -> refuse -> existing code-owned `trial.tool_only` fallback (fail-closed; "a second look", "second clip" now fall back — accepted).

- [contracts/agent/validate.py](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S14g-fix5-orch95/contracts/agent/validate.py): `CITE` placeholder (U+E000) for cited quantities in the joined visible run; per-segment check wraps neighbouring citations with CITE; `numeric_issue` adds `unbound_unit_word`; model text containing private-use chars is refused (cannot forge CITE). Old number-word/quantifier rules kept.
- [evidence/S14/S14g_fix_oracle.py](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S14g-fix5-orch95/evidence/S14/S14g_fix_oracle.py): same rule implemented independently (own token lexicon/walk, no contracts.agent import); closes asymmetries (`one g`, `one N` now caught by oracle; runtime now catches `one-second`/`single-second`). `visible()`/self-check use CITE.
- [evidence/S14/S14g_fix_gate_a.py](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S14g-fix5-orch95/evidence/S14/S14g_fix_gate_a.py): `visible_strings` marks citations with the oracle's CITE (was a space).
- [Build/agent/interview.py](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S14g-fix5-orch95/Build/agent/interview.py): two code-owned prompts "Type the angle with deg or rad." -> "in deg or rad." (rule 3).
- [tests/agent/fixtures/adversarial-visible-text.json](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S14g-fix5-orch95/tests/agent/fixtures/adversarial-visible-text.json): +16 cases (all six reviewer strings, `one g`, `one N`, unit-before-cite without label, `a second look`, `in one full second`; benign: This one fits the scene., Please double-check the fit., label, unit-after-cite, apostrophe/e.g.). `benign-double-check` ("second clip") flipped to invented=true (fail-closed by design).
- [tests/agent/test_reply.py](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S14g-fix5-orch95/tests/agent/test_reply.py): ordinary-words test uses "the other clip"; asserts "Use the second clip." is refused.
- New [evidence/S14/S14g_fix5_gate_a.py](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S14g-fix5-orch95/evidence/S14/S14g_fix5_gate_a.py) (reuses fix4 runner): refused saved replies counted as fallback, shown as tool_only, oracle-checked; Q16=A label.

## Fresh checks
- `python -B evidence/S14/S14g_fix_oracle.py` -> {corpus_cases: 56, oracle_agrees: True}.
- Agent suite + tests/pipeline/test_understand: **59 tests OK** ([S14g-fix5-unittest.txt](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S14g-fix5-orch95/evidence/S14/S14g-fix5-unittest.txt)). Corpus drives validate_response/safe_reply at segments, prompt, chip, rationale and the 4-attempt trial loop (every bad case ends in tool-only).
- Direct runtime spot-check: all six reviewer strings -> `unbound_unit_word`; `one g`/`one N` -> refused; benign pair -> None.
- Offline replay [S14g-fix5-offline.json](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S14g-fix5-orch95/evidence/S14/S14g-fix5-offline.json) / [stdout](C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/S14g-fix5-orch95/evidence/S14/S14g-fix5-offline-stdout.txt): **gate_a = MET_AMENDED_Q16**, label "scale unverified, not setup-validated"; numeric-contract 10/10, setup-validator 0/10 (shown alongside); 10 distinct recorded scenes; saved live turns **30/30 shown unchanged, 0/30 fall back**; invented (oracle) 0. Not plain MET; final Gate A clearance still needs the R-A recheck.

## Ponytail (full) applied
Reuse: existing `numeric_issue` path, `trial.tool_only` fallback, corpus-driven tests (no new test file), fix4 runner imported not copied. Smallest complete: one regex rule + CITE placeholder instead of extending phrase lists; prompt wording change instead of a code-owned bypass flag. Skipped: unit-dimension matching between a bound unit word and the cited quantity's unit; reviewer probe.py not run (writes into evidence/reviews, outside Owns) — its strings are in the corpus instead.

## Limits / risks
- Label form still trusts adjacency: "The period is one whole minute: <gravity q>" passes (unit bound as a label; no dimension check). Upgrade: compare bound unit word to the cited quantity's unit if R-A asks.
- More benign prose now falls back (any ordinal "second", "minute detail", "to some degree"); 0/30 saved live turns affected, live models may differ.
- Finite unit lexicon; not a universal English guarantee. Replay uses saved responses; not new model/physical evidence. Historical evidence/S14/S14c-probe.txt keeps the old prompt wording (unchanged history).
- Communication: silent; one completion line to controller as authorized. Canonical controls not edited.
