# S14g-fix6-orch100 REPORT — DONE

Lane CODEX-1, step S14. Assigned anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled.
UTC issued 2026-10-30T06:59:33+00:00; work started ~07:00:58Z; stopped 2026-10-30T07:06:59+00:00. Base main d64bf86 (main since advanced
to 1ffb4b7 with unrelated library/orch commits; rebase before merge). Offline only, spend $0, no model calls, no installs.

## Fix (R-A RECHECK-fix5 F1-R3, P1)
Root cause: fix5's bare label-chain binding (`<units>: <q>` / `<units> = <q>`) masked a unit chain whenever a citation
followed, so "The period is one whole minute: <gravity q>" laundered an invented amount.
Structural fix (deletion, both detectors, independently):
- contracts/agent/validate.py: `_BOUND` keeps only (1) unit chain directly after a cited quantity, (2) unit chain
  directly after "in" with no amount. The second alternative (bare label chain before `:`/`=` + CITE) is removed.
  "in metres: <q>" still passes (the "in" phrase binds; ":" and CITE are not unit words).
- evidence/S14/S14g_fix_oracle.py: `_bound` forward label branch deleted; back-walk to CITE/"in" only. No
  contracts.agent import (probe's import check still passes).
- Any amount/quantifier word (one/a/full/whole/more/number words...) between binder and unit breaks the chain ->
  unit unbound -> refused -> existing code-owned tool-only fallback. No word blacklist, no dimension system.
- tests/agent/fixtures/adversarial-visible-text.json: +10 cases (56 -> 66): the disclosed string, the four further
  results.json variants (full-second/gravity, full-radian =, full-metre:, full-second/duration), comma/period/
  one-more-minute variants, "in whole minutes: <q>" (refused), and benign "Drop time in seconds = <q>." (allowed).
  Benign "This one fits the scene." / "Please double-check the fit." unchanged and passing.
- Code-owned prompts: no rewording needed. Run-System/Runs/S14g-fix6-orch100/prompt_scan.py checks every string
  literal in Build/agent and Build/pipeline (with a worst-case trailing citation): fix5-accepted but fix6-refused = 0
  (prompt_scan.txt).

## Fresh checks
- `python -B -m unittest tests.agent.test_visible_text tests.agent.test_contracts tests.agent.test_reply tests.agent.test_trial
  tests.agent.test_retry tests.agent.test_interview tests.agent.test_muse tests.pipeline.test_understand` -> 59 tests OK
  (evidence/S14/S14g-fix6-unittest.txt). Oracle self-check: 66/66 agree.
- Reviewer probe, read-only: copied unchanged into evidence/S14/fix6-reviewer-probe/run/probe.py (evidence/reviews not
  written; its audit hook confines writes to its own dir). Only edits in the copy: the five F1-R3 gap expectations
  flipped to refused, the 7th gate turn now asserted to fall back like the other six, corpus 56 -> 66, replay compared
  to the fix6 packet (minus scope). Result: all 8 gap probes refused at runtime + oracle (4 trial rejections each ->
  tool-only fallback), all 32 gap-surface checks agree, all 7 actual gate-helper turns attempts=4 / model reply not
  shown / invented=null; 427 protected files unchanged; network denied. Its `verdict: CHANGES_REQUIRED` and
  `fix5-replay.json` filename are hardcoded literals of the reviewer script, not a fix6 verdict.
- Offline replay `python -B evidence/S14/S14g_fix6_gate_a.py` (thin wrapper reusing S14g_fix5_gate_a.run()):
  saved live turns **30/30 shown unchanged, 0/30 fall back**, 0 oracle-flagged invented shown numbers.
  gate_a = **MET_AMENDED_Q16**, verbatim label "scale unverified, not setup-validated"; numeric-contract 10/10,
  production setup-validator **0/10** shown alongside. Never plain MET. Final clearance needs the next R-A recheck.
  (evidence/S14/S14g-fix6-offline.json, S14g-fix6-offline-stdout.txt)

## Ponytail (full) applied
- Reuse: fix is two deletions in existing binders; replay reuses fix5 run() via a ~10-line wrapper; probe reused
  as-is with minimal expectation flips; fallback is the existing trial.tool_only path.
- Smallest complete: no new detector, word list, dimension matching or prompt rewording (scan proved none needed).
- Skipped: test_setup/validator suite, new live model calls, UI/physical integration, edits to record_muse.py/pipeline.
- Risks: fail-closed — bare unit labels without "in" (e.g. "Drop metres: <q>") are now refused and fall back to tool-only
  if a live model emits them (0/30 saved turns did). English coverage remains finite; the "in <units>" binder is the only
  remaining label path (amount words break it). Live retry behaviour not re-measured (offline).

## Files
contracts/agent/validate.py; evidence/S14/S14g_fix_oracle.py; tests/agent/fixtures/adversarial-visible-text.json;
evidence/S14/S14g_fix6_gate_a.py, S14g-fix6-offline.json, S14g-fix6-offline-stdout.txt, S14g-fix6-unittest.txt;
evidence/S14/fix6-reviewer-probe/run/{probe.py,results.json,fix5-replay.json,probe-stdout.txt};
Run-System/Runs/S14g-fix6-orch100/{PLAN.md,TIMEBOX.json,REPORT.md,prompt_scan.py,prompt_scan.txt}.

Communication: silent; one authorized completion line to controller. Tokens/cost: unobservable; $0 spend.
Next: R-A recheck of fix6 (cross-vendor) for numeric-language clearance.
