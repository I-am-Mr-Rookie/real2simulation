# S14g-orch47 REPORT — Run Gate A fixture and thirty-turn suite — DONE

- Lane/model: CODEX-1, assigned anthropic/claude-opus-5-5 high (desktop worker). Coding quota: OpenCodex-managed; not polled.
- UTC: issued 2026-10-29T21:51:42Z; work start 21:52:09Z; work stopped 2026-10-29T22:01:30+00:00; deadline 22:21:42Z.
- Base main 7fbf29f; branch run/S14g-orch47 (worktree .worktrees/S14g-orch47). Not merged (controller integrates).
- Meta spend: 42 live calls (12 muse-wonder-1.0, 30 muse-spark-1.3), all HTTP 200, **estimated $1.1328** (cap $3.00);
  billed unknown. Ledger: [S14g-ledger.jsonl](../../../evidence/S14/S14g-ledger.jsonl). Model tokens of this worker unobservable.

## Gate A result (measured, live) — MET

Acceptance "9/10 valid specs and zero invented numeric claims across 30 turns":
[S14g-live.json](../../../evidence/S14/S14g-live.json) (stdout [S14g-live-stdout.txt](../../../evidence/S14/S14g-live-stdout.txt)).

| Metric | Live | Offline fixture |
|---|---|---|
| valid specs | **10/10** | 10/10 |
| turns | 30 | 30 |
| invented numeric claims in shown text | **0** | 0 |
| model replies shown / tool-only fallbacks | 30 / 0 | 24 / 6 |
| model attempts stating numbers in text (caught pre-display) | 0 | 36/36 caught |
| Wonder / Spark calls | 12 / 30 | 13 / 66 (replayed) |

- Spec case = Wonder `understand_with_retry` on SYNTHETIC room-v1 scene context -> first candidate -> S14c
  `questions` -> hand-written SYNTHETIC S14c answers -> `answers_to_spec` (S08 validator). Live: 2/10 needed one
  retry (model put a number-ref with unknown tool_output_id 'none'/'table-box' in a question; validator rejected, retry fixed).
- Turn = actual S10 session-bridge simulator start + actual fitter (free_fall/projectile, normal and mystery g)
  -> Spark `check_trial` -> `safe_reply` display. Invented-number check is an INDEPENDENT scan of the shown string
  (rendered tool quantities removed via `quantity_text`, remainder through `numeric_issue`), not the validator verdict.
- Offline: RECORDED S14b fixtures (incl. the rejected incomplete one) + SYNTHETIC Spark replies with planted
  digits/number words/"twice"/uncited claims: [S14g-offline.json](../../../evidence/S14/S14g-offline.json); script
  self-check asserts the detector flags a planted number.

## Changes

- `contracts/agent/validate.py` (STATE follow-up, S13e live video quirk): question `kind` normalised to the chips
  actually sent (no chips -> free_text; chips on free_text -> chips_and_free_text) on a copy; chip/prompt number ban unchanged.
  `tests/agent/test_contracts.py` asserts normalisation, no input mutation, and a number word in a chip still rejected.
  `contracts/agent/CONTRACT.md` line updated.
- `Build/agent/tools.py`: `quantity_text` extracted from `render` (single number format; reused by the gate scan).
- `evidence/S14/S14g_gate_a.py`: `offline|live` suite, per-call ledger, hard $3.00 cap guard (worst-case reservation).

## Fresh checks (this worktree)

- `python -m unittest -v tests.agent.test_contracts …test_muse …test_interview …test_retry …test_trial …test_reply`
  -> 49 OK: [S14g-unittest.txt](../../../evidence/S14/S14g-unittest.txt). `python -m unittest tests.pipeline.test_understand` -> 7 OK.
- Prior mutation scripts rerun serially: S14d 7/7, S14e 8/8, S14f 6/6 KILLED:
  [S14g-mutation-rerun.txt](../../../evidence/S14/S14g-mutation-rerun.txt); `git diff --stat` after: only intended files.
- `python evidence/S14/S14g_gate_a.py offline` -> MET; `… live` -> MET (above).

## Ponytail (full) applied

- Reuse: S14d `understand_with_retry`, S14c `questions`/`answers_to_spec` + its SYNTHETIC_ANSWERS, S08 `setup`,
  S14e `trial_outputs`/`check_trial`, S14f `safe_reply`, S10 session bridge, S14b ledger/price constants and env path.
- Smallest complete: one evidence script (no new Build module/schema/version), 8-line validator normalisation,
  3-line helper extraction. No deps installed.
- Skipped: real-scene (ST03 keyframe) spec cases via Build/pipeline (more cost/time; one synthetic scene only);
  number-word list extension (no live misses observed); web/JS mirror of normalisation (outside Owns).

## Limits / risks / next

- Gate A measured on ONE synthetic scene: all 10 specs chose free_fall; answers are scripted SYNTHETIC user input, so
  "valid spec" measures understanding->interview->validator plumbing, not user-answer variety. Not real-scene,
  calibration or physical evidence. Spark priced at Wonder list rate x1.5 (shortcut; Spark price unverified).
- Product risk for S14h/S10: mystery-g trials show the fitted (hidden) gravity in the Spark check text — may spoil Mystery-g.
- Render cosmetic: number segments abut text without spaces when Spark omits them (e.g. "gravity.9.81 ±").
- `Build/web/src/workspace/interview.mjs` may assume strict kind/chips pairing; unverified (outside Owns).
- Next: R-A cross-vendor review, then S14h checkpoint.

## Communication

Silent; no owner questions; one completion message to controller chat as authorized.

