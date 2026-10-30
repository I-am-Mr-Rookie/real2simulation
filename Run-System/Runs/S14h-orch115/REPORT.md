# S14h-orch115 REPORT — DONE

Lane CODEX-1 (native Claude); model anthropic/claude-opus-5-5/high. UTC start 2026-10-30T09:12:12Z; work stopped 2026-10-30T09:16:23+00:00 (deadline 09:41:24Z). Base main d3a1343 (includes fix7 3b07b4e). Coding quota: OpenCodex-managed; not polled. Tokens: unknown (unobservable). API/compute spend $0; offline, no Meta/Muse/Baseten calls, no installs, no .env reads.

## Result
- **Gate A checkpoint**: [GATE_A.json](../../../evidence/S14/GATE_A.json) + [GATE_A.md](../../../evidence/S14/GATE_A.md): MET_AMENDED_Q16, label "scale unverified, not setup-validated", never plain MET; numeric 10/10, setup-validator 0/10 shown; replay 30/30, 0 fallback, 0 invented; oracle 84/84; R-A CLEAR pointer + sha256; P2/P3 residuals carried.
- **Fallback**: already code-owned/tool-only (`safe_reply` -> `tool_backed`; also `trial.tool_only`, `muse.ask_user` template chips) and every fallback returns non-empty issues for logging. No Build/agent edit; proved by new `test_fallback_card_is_code_owned_and_model_invariant` (5 distinct invalid replies -> identical card).
- **P2 tiny fix**: `_UNIT` adds micro/nano-second -> "one microsecond"/"a few nanoseconds" now refused via the fix7 clause rule; "in microseconds: <q>" still binds. Unitless "one", count nouns, other unlisted units stay OPEN (documented).
- Review packet: [S14h-review-packet.md](../../../evidence/S14/S14h-review-packet.md).

## Fresh checks
- 8 suites: **60 tests OK** ([S14h-unittest.txt](../../../evidence/S14/S14h-unittest.txt)); oracle corpus **84/84**.
- Offline replay via S14g_fix5_gate_a.run(): 30/30 unchanged, 0 fallback, 0 invented, 10/10, 0/10 ([S14h-replay.json](../../../evidence/S14/S14h-replay.json)).
- P2 probe on main vs branch: main accepted all 6; branch refuses exactly the 2 micro/nano cases ([S14h-p2-probe.txt](../../../evidence/S14/S14h-p2-probe.txt)).
- timebox check: see below.

## Ponytail
Reuse: existing safe_reply/tool_backed fallback (no new code), existing fix7 clause rule (one regex token instead of new rule), existing S14g_fix5_gate_a.run() for replay (no new gate script), test helpers from test_reply. Smallest: 1-line validator diff + 1 test. Skipped: count-noun/unitless-"one" closure (would refuse legit prose/pronouns; not tiny), oracle/corpus edits, re-baselining reviewer verify.py (exits 1 on stale protected hashes, documented).

## Risks / next
Finite vocabulary, not a language guarantee; P3 conservative refusals and live fallback rate unmeasured. Cross-vendor review of the micro/nano diff advisable (packet). No scale, setup-validation or physical claim. Communication: silent; one completion message to controller.
