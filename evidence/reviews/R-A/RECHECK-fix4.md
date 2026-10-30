# R-A fix4 recheck — CHANGES_REQUIRED

Baseline `fd65aa22460c3a697de2f70f0629034de9272df3`; reviewed fix `1481912`. Assigned `gpt-6.1-sol/high`, CLAUDE cross-vendor lane reviewing Opus work. Offline, read-only product review; $0. Review DONE is not Gate A acceptance.

## Closure decisions

| Finding | Result |
|---|---|
| F1-R: a/an/single + time/angle units | **Original reported examples CLOSED. Numeric-enforcement invariant remains OPEN: P1 F1-R2 below.** |
| F3-R: numeric-contract fixtures labelled Gate A MET | **CLOSED as a reporting/acceptance defect.** Fresh fix4 replay is PROVISIONAL: numeric-contract 10/10, real setup validator 0/10. No owner amendment inferred. |
| Original F2/F4 | No reopening: joined-visible validation and exact saved-response/tool-output replay remain covered. This is not a new physical or provider attestation. |

## F1-R2 — [P1] Common quantity modifiers evade both display validation and the independent oracle

Run from the review worktree:

```powershell
python -B evidence/reviews/R-A/recheck-fix4/probe.py
```

These ordinary, definite unit-valued claims pass `validate_response -> check_trial -> safe_reply`, and the actual evidence runner `S14g_fix_gate_a.turn` reports **one attempt, model_reply_shown=true, invented=null**:

- `The elapsed time is a full second.`
- `The period is one whole minute.`
- `The angle is one full radian.`
- `The distance is one full metre.`

Each response cites a legitimate **gravity** tool quantity as a separate number segment; that reference does not source the asserted duration, period, angle or distance. The new text is displayed unchanged. The first claim also passes every visible-field entry point (segments, question prompt, chip label, candidate rationale).

Root cause: `contracts/agent/validate.py:44–46` requires a quantifier immediately followed by whitespace and a unit. `evidence/S14/S14g_fix_oracle.py:45–46` likewise only recognizes a quantifier whose next token is a unit. Inserting ordinary `full`/`whole` breaks both. The oracle is implementation-independent (no contracts.agent imports) but shares this conceptual gap. Its 40-case self-check passing is not evidence that these additional replies are safe.

**Required:** return numeric-language enforcement to the S14 owner; cover these bounded, concrete regressions at all visible surfaces and the independent oracle, preserving benign pronoun `one` and `double-check`. A constrained/code-owned narrative or existing tool-only response is the safer fallback where open prose cannot be validated. This is **not** a demand for a universal blacklist or unlimited English-language coverage.

Diagnostic asymmetries (same finding, not extra gate requirements): `This is a one-second delay.` and `a single-second interval` pass runtime display, although the oracle catches them; `one g`/`one N` are blocked by runtime but missed by the oracle. They show that neither detector can stand in for the other.

## Original F1-R examples and fail-closed fallback verified

The exact `a second`, `a minute`, `a radian` claims now fail both detectors. Also checked `an hour`, `a single second`, `one rad`, `a millisecond`, `a degree`. All eight repeated bad replies exhaust four offline adapter attempts and return the existing code-owned tool-only response, without showing the rejected prose. The actual gate runner independently confirms fallback for the three original examples.

Benign `This one fits the scene.`, `Please double-check the fit.`, `in radians`, and `metres per second` remain accepted. Fresh corpus-driven agent suite: **52 tests pass**; oracle agrees on **40/40 corpus cases**. Those passing checks do not negate F1-R2.

## F3-R closure and current Gate A evidence

Fresh `S14g_fix4_gate_a.run()` was called as a function, **not its CLI**, so no S14 packet was overwritten. The replay uses the saved ten recorded Wonder responses, saved scene/keyframe inputs and thirty exact saved live accepted trial replies/tool outputs. It preserves all thirty rendered replies and matches the saved fix4 summary exactly:

- `summary.gate_a = PROVISIONAL`.
- Ten distinct recorded scenes; numeric-contract specs **10/10**.
- Real `interview.answers_to_spec -> validate_setup` path **0/10**; all ten actual validator calls were observed, with `scene=None`, and no validator substitution claiming success. The original binding is restored afterward.
- Saved accepted live turns **30/30** valid with unchanged rendering; detector-flagged residual invention **0** for this **saved packet**, not the new adversarial probes.

`S14g_fix4_gate_a.py:40–55,83–91` gates MET on at least nine real setup successes plus thirty clean unchanged turns. Six explicitly labelled **synthetic summary-logic tests** check setup counts 0/8/9/10, a missing turn and an invented turn. Their mocked success counts test branching only; they are not setup-success evidence. Production setup-validation tests separately pass **14/14** on labelled synthetic safety fixtures.

`S14g_fix3_gate_a.py:152–153` now relabels numeric-only MET as PROVISIONAL; the function was checked with saved fixture rows (no random fresh simulation needed). Historical `S14g-fix3-live.json` and `S14g-fix3-offline.json` remain byte-unchanged, retaining their old MET labels **for custody only**, superseded by fix4. They are not current gate receipts.

## Pending owner amendment — no decision made here

Q16 remains with Koushik; do not silently amend it in a review or infer an answer from silence.

- **A: accept numeric-contract validation on recorded scenes with unverified scale.** The existing 10/10 can satisfy that **amended spec arm**, explicitly labelled “scale unverified, not setup-validated.” This grants no execution/scene-fit, metric-scale or physical-success approval. It does **not** resolve F1-R2 or itself authorize Gate A MET.
- **B: retain setup-validated specs.** Current evidence remains PROVISIONAL at 0/10 on the real path. At least nine recorded-scene specs must pass the normal authoritative-bundle/known-matching-scale/geometry/stability validation; no paid rerun can substitute for missing inputs. This review adds no new calibration criterion beyond that contract.

## Evidence, checks and limits

- `recheck-fix4/probe.py`, `results.json`, `probe-stdout.txt`: twenty bounded text probes, seven actual gate-runner trials, all four visible-field paths, forty-case oracle self-check, ten real setup-call observations, threshold/relabel tests, and SHA256 immutability of 66 protected input files.
- `recheck-fix4/fix4-replay.json`: fresh replay output; synthetic interview answers and synthetic-room tool outputs remain labelled, not user or physical evidence.
- `recheck-fix4/agent-tests.txt`: 52 passed; `setup-tests.txt`: 14 passed; `understand-tests.txt`: 7 passed.

The runner denies sockets, live-post adapters, new frame extraction, .env access, and Python file writes outside its owned review directory. One initial attempt stopped because tempfile tried a system-temp write-probe; the audit hook prevented that write. The runner was then pointed at the existing TEMP cache explicitly and scratch kept under owned `tmp/`; the final run succeeds. No product, tests, S14 evidence, canonical controls, dependencies, credentials, provider settings or owner decisions changed.

Skipped live calls/spend, browser/UI/physical integration, new media extraction, full build and universal-language claims. Risk: open prose still displays definite unsourced quantities; the saved packet's zero oracle findings cannot clear that counterexample. Return F1-R2 to the original S14 owner; keep Gate A PROVISIONAL and Q16 pending.
