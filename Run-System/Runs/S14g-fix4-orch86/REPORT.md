# S14g-fix4-orch86 REPORT — DONE

Lane CODEX-1, step S14. Assigned/actual: anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). UTC 2026-10-30T06:13:43Z -> 2026-10-30T06:24:31+00:00. Base main `b2fc20b` (main since advanced to `68bff3e`, S24a-draft only; no overlap). Spend \$0; no Meta/provider calls; no installs. Tokens/costs: unknown (unobservable).

## F1-R (P1) — closed at display boundary + independent oracle
- `contracts/agent/validate.py`: replaced the split rule (`one|a/an` + spatial/mass units; time/angle only after `one`) with ONE quantifier rule `(one|a|an|single) + any unit` covering spatial, mass, force/energy, time (s/ms/min/h/hr, (milli)seconds, minutes, hours) and angle (degrees, radians, rad, deg). Fail-closed: "a second look" is also refused -> trial already falls back to the code-owned tool-only reply (`Build/agent/trial.py` fallback), so no new fallback code was needed.
- `evidence/S14/S14g_fix_oracle.py` (independent, does not import contracts.agent): TIME set gains radian(s)/rad/deg/ms/min/h/hr/millisecond(s); `a/an/single` + UNITS|TIME now flagged.
- Corpus `tests/agent/fixtures/adversarial-visible-text.json` 29 -> 40 cases: 8 expected-bad (`ra4-a-second`, `ra4-a-minute`, `ra4-a-radian` = the exact R-A strings; an hour, a degree, a single second, one rad, a millisecond) + 3 benign (in radians, metres per second, "One sees ..."). Existing benign `one`/`double-check` cases still pass.
- Regressions: existing corpus-driven `tests/agent/test_visible_text.py` runs every case through safe_reply, prompts, chips, rationales and the check_trial loop -> 52/52 OK (`evidence/S14/S14g-fix4-unittest.txt`). Oracle self-check 40/40 agrees. Direct: the three R-A strings -> `untraced_number_word 'a second'|'a minute'|'a radian'`; "This one fits the scene." and "Please double-check the fit." -> None. `tests/pipeline/test_understand` 7/7 OK.
- R-A probe copied unchanged to `ra-probe/probe.py`: it now fails its own line-86 assertion that these three still pass display/oracle (`ra-probe-stdout.txt`) = misses closed. This is a finite lexicon, not a universal guarantee.

## F3-R (P1) — Gate A honestly PROVISIONAL, not MET
- New `evidence/S14/S14g_fix4_gate_a.py` (sockets denied, extraction denied, \$0): replays the SAVED `S14g-fix3-recorded.json` responses via fix3 `spec_case` twice — (A) fix3 numeric `validate()` stand-in, (B) REAL `interview.answers_to_spec -> contracts.experiment.validate_setup` with the bundles that exist (none) — and re-validates the 30 saved LIVE fix3 turns under the fix4 boundary (exact render + residual oracle).
- Result (`evidence/S14/S14g-fix4-offline.json`, `-stdout.txt`): **summary.gate_a = PROVISIONAL**; numeric-contract 10/10; setup-validator **0/10** (`$.scene: invalid authoritative bundle: None is not of type 'object'`); 10 distinct recorded scenes; 30/30 live turns valid with unchanged render; invented_shown_oracle 0. MET is reachable only if >=9 pass path B.
- `S14g_fix3_gate_a.py` run() now relabels a numeric-scope MET as PROVISIONAL. Historical `S14g-fix3-{live,offline}.json` (which say MET) left byte-unchanged for custody; superseded by fix4 output.

## Owner question
Gate A (QUEUE S14: nine valid specs from ten recorded scenes) cannot pass the production `validate_setup` path because no scene bundle with verified scale exists for these clips (S05d abstained). Koushik, choose: **(A)** amend Gate A to accept numeric-contract validation on recorded scenes with unverified scale (current 10/10, labelled "scale unverified, not setup-validated"), or **(B)** keep Gate A requiring bundle-bound specs that pass `validate_setup` (stays PROVISIONAL until scale-verified bundles exist), or free text.

## Ponytail (full) applied
Reuse: fix3 `spec_case`/`recorded_post`/custody and its own `spec_only` hook swapped for the real validator (no re-implementation); existing corpus-driven tests instead of new test files; existing trial tool-only fallback instead of a new constrained mode. Smallest complete change: one regex alternation, one oracle line + set, 11 corpus rows, one summary relabel, one offline script. Skipped: live/paid rerun (forbidden, not needed), blacklist growth beyond the reviewer's unit families, record_muse.py/Build/pipeline (not owned). Risks: lexicon remains finite (e.g. "a moment", "an instant" are vague, not unit claims, and pass); "a second look"/"wait a minute" now refused -> tool-only fallback (fail-closed UX cost); synthetic interview answers and synthetic-room turn outputs are fixtures, not user/physical evidence.

## Files
contracts/agent/validate.py; evidence/S14/S14g_fix_oracle.py; evidence/S14/S14g_fix3_gate_a.py; evidence/S14/S14g_fix4_gate_a.py; evidence/S14/S14g-fix4-offline.json; evidence/S14/S14g-fix4-offline-stdout.txt; evidence/S14/S14g-fix4-unittest.txt; tests/agent/fixtures/adversarial-visible-text.json; Run-System/Runs/S14g-fix4-orch86/{PLAN.md,REPORT.md,TIMEBOX.json,ra-probe/probe.py,ra-probe-stdout.txt}.

Next: R-A recheck of fix4; owner answer above decides whether Gate A can move beyond PROVISIONAL. Communication: silent; one completion line to controller.

