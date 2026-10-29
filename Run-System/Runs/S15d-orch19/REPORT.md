# S15d-orch19 REPORT
Result: **DONE** (fixture-level UI/state evidence only). Lane CLAUDE, anthropic/claude-sonnet-5-5/high; OpenCodex-managed, not polled. Tokens/cost: unobservable.
UTC: issued 2026-10-29T11:50:41, started 11:52:19, work stopped 12:02:19 (deadline 12:20:41; verified fully DONE, early finish allowed). Branch run/S15d-orch19, worktree .worktrees/S15d-orch19.

## Changes (all inside Owns)
- Build/web/src/workspace/interview.mjs (new, pure, no imports): `parseQuestions` (fail-closed re-check of an already-validated S14a agent-response question set; number segments render only from a labelled tool-output quantity), `reduceInterview` (Q_LOADED/Q_CHIP/Q_TEXT/Q_SUBMIT/Q_BACK/Q_RESET; illegal events return same state), `interviewView`, `interviewAnswers` (ids + user text only).
- view.mjs: `renderInterview` + optional 6th arg of `renderWorkspace`; react.mjs: optional `interview` prop; workspace.css; README.md (S15d section).
- tests/workspace/interview.test.mjs (8 tests) + tests/workspace/fixtures/interview-responses.json.
- evidence/S15/interview_fixtures.py (builds/drift-checks fixtures; every response passes contracts/agent/validate.py::validate_response), react-ssr-check.mjs (+S15d block), interview-preview.html, *-s15d.out.txt.

## Acceptance: question and answer transitions against validated fixtures
- Fixtures: 5 responses (recorded S14b muse b/c/d, authored 3-kinds incl. a number-segment chip, authored no-questions) all validated by S14a Python validator (`python evidence/S15/interview_fixtures.py` then `--check` exit 0).
- Transitions tested: chips -> free_text -> chips_and_free_text -> complete; toggle/unknown chip/ignored-kind events; empty/whitespace submit rejected with message and position kept; back restores answer; complete->reopen; new round only after complete (mid-answer reload illegal); rounds append; reset; 500-char cap and control-char strip; 15 malformed/untraced inputs rejected (wrong scene, digit in text, unresolved/unlabelled number ref, kind/chips mismatch, >3 questions, >6 chips, extra key, bad kind, duplicate ids, bad id, empty prompt, null).
- Markup tested via injected `h`: toggle chips aria-pressed, labelled textarea maxLength 500, onAction payloads, disabled without onAction, panel only in interview.active, interview never advances the S15a graph.

## Fresh checks
- `node --test tests/workspace/*.test.mjs`: 34 tests, 34 pass, 0 fail (26 existing + 8 new) -> evidence/S15/workspace-tests-s15d.out.txt.
- `node evidence/S15/react-ssr-check.mjs <Build/web/node_modules>` (React 19.3.1 SSR): S15d ok, user text `<b>` escaped -> evidence/S15/react-ssr-check-s15d.out.txt.
- In-app browser (ChatGPT IAB, via temporary localhost server, now stopped; file:// is blocked by policy): preview renders; chips, textarea, Back/Finish, escaped text visible at desktop width. Not tested: narrow breakpoint, real clicking/hydration, keyboard flow.

## Ponytail choices
Reused: S15a/b/c reducer+view+react patterns, S14a validator (as fixture gate, no JS reimplementation of numeric-word rules), S14b recorded fixtures, existing CSS vars, `h`-injection. Smallest complete: no new deps, no new state lib, one pure module, panel hook is one optional prop. Skipped: JS port of Python number-word check (host must pass validated responses; JS only blocks digits), transport to agent, spec building (S15e), autosave of drafts.

## Limits and risks
- Number-word/Unicode checks live only in Python; JS re-check is digit + structural only, so a host that skips Python validation could show number words.
- Duplicate question ids are rejected in JS (schema allows them) - stricter than S14a; note for S14.
- Submit uses aria-disabled (not disabled) when empty so the reason is announced; some AT may still read it as dimmed.
- Back cannot cross into a previous finished round (by design).
- Fixture validity is synthetic contract evidence only: not Gate A, real-scene, calibration or physical evidence. No live model calls, installs, deploys, or edits outside Owns. Canonical controls untouched.
- Communication compliance: silent; only the one authorised completion message to the controller.
