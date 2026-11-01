# S15bf-orch243 REPORT — DONE
Lane CLAUDE; model anthropic/claude-opus-5-5 medium (assigned); coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (not observable); $0 spend.
UTC start 2026-11-01T08:12:29+00:00 (issue), work stopped 2026-11-01T08:19:09+00:00. Branch run/S15bf-orch243 from main b4ae52b7.

## Changes
- Build/api/workspace/analysis.py
  - F1: KNOWN_SIZE is now chips_and_free_text with two standard-reference chips (A4 paper short edge 0.21 m, bank card long edge 0.0856 m); chip labels contain no digits because web parseQuestions rejects untraced numerals, so the length lives server-side and applies only when the user picks that chip. Owner clips with a recorded owner-declared length get an extra first chip owner_recorded (uses that recorded value_m).
  - New owner_spec(answer, m): typed text parsed by existing user_scale (units mm/cm/m -> metres) wins; else chosen chip; else plain 422 INVALID_INPUT with the existing error shape ("spec did not validate"). Range check 0 < length <= 10 m (typed 0 or 12 m -> 422).
  - Owner-clip /spec branch now validates first, then returns spec {kind: owner_clip_scale, object, length_m, unit m, label "user-declared, not verified"}, setup_validated false, label "scale user-declared, not verified; not setup-validated" (Q16 style), plus the existing measurement/user_scale/live_fit. Missing or unusable answers no longer silently fall back to the recorded scale.
  - F5: _u_total recorded_total branch is used only when the declared length equals the recorded value_m; otherwise u = fitter u only, u_rule fit_only_legacy, u_label "fit residual scatter only; combined uncertainty unavailable for this older job at this scale".
- Build/web/src/workspace/controller.mjs: owner result stage only when d.setup_validated === false and d.spec.length_m > 0; otherwise falls through to the existing spec-rejected path. Chips render through the existing interview chip component (view.mjs ws-chip), no web change needed there.
- Tests: test_jobs (chips list, digit-free labels, spec fields, five 422 cases, A4 chip, owner_recorded chip, OWN10 with typed size); test_live_fit (F5 regression: no-budget OWN05 at 40.56 cm -> u == u_fit, fit_only_legacy); owner-clip.test.mjs (mock mirrors new API shape, chip-submit path, no-spec reply never reaches report.owner).

## Checks
See evidence/S15bf/CHECKS.md: 28 Python OK (+4 q16 OK), 133/133 node, npm run build EXIT 0.

## Ponytail (full) applied
- Reuse: user_scale parser/units, existing error() shape, existing interview chip reducer/view (chips_and_free_text already supported), existing controller spec-rejected path; no new framework, no new dependency.
- Smallest complete: chips map server-side instead of adding a web prefill feature; one guard line in controller; one branch in _u_total.
- Skipped: chip "pre-fills editable free text" in the web reducer (web submits chip id only; typing free text instead is the editable path; adding prefill would change the generic interview reducer for all questions). Book-cover chip skipped (no standard length; it stays the free-text example). Non-owner scene known_size path unchanged (still abstain, not 422).
- Risks: a 422 on the owner spec goes through the existing failWith path; not browser-verified that the user can re-answer without restarting. Live deployed API not exercised (controller deploys). tests/workspace/fixtures/live-fit-own05.json not regenerated (budget-present values unchanged by this fix).

## Communication
Silent run; one completion line to controller only.

## Next
Controller: merge, deploy dev, CODEX-2 S22 retest of Gate D 3.4 with chips; S22j verdict update per R-D.

