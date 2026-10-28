# ORCH-RETRY-HOLDS — DONE

Owner-authorized orchestration-tool fix, not a product run or S02c completion.
UTC 2026-10-27 approximately 19:15–19:20; final verification at 19:20 UTC.

## Diagnosis and change

`runs_view.py` treated every dependency-ready PARTIAL as immediately resumable.
S02c's 20:10 UTC cooldown existed only in narrative STATE/checkpoint, so it was
absent from generated readiness. QUEUE also retained an obsolete Q2 approval stop.

- Added canonical QUEUE Retry holds table with S02c's existing deadline and
  source-specific HTTP 429/403 reason; no new network attempts or bypasses.
- Generator validates explicit UTC deadlines and known/nonduplicate run IDs,
  hides cooling tasks from Ready now, shows Waiting to retry with UTC/Dhaka
  rollover, and labels expiry as bounded-retry eligible/recovery unverified.
- Status remains PARTIAL. Ordinary partials, dependencies, DONE and owner gates
  retain their behavior. ORCHESTRATOR now requires honoring/renewing holds.
- Q2 remains approved for provisional local licensed downloads only; S02e still
  gates final use. Seven candidates are not ten verified usable clips.

## Verification

`python -m unittest discover -s Run-System/tests -p test_runs_view.py -v`:
red before implementation (8 tests, 7 assertion failures including subtests);
green after implementation (8/8). Covers pre-deadline/boundary, UTC-to-Dhaka
rollover, expired hold with unmet dependency, ordinary PARTIAL, DONE, malformed/
naive/non-UTC deadlines and unknown run. Tests execute real parsing/rendering
and filesystem writes; only time and temporary file locations substituted.

`python -m unittest discover -s Run-System/tests -v`: 25/25 PASS, including
existing harmless dispatcher fixtures. `git diff --check`: PASS. Generator
refreshed against canonical QUEUE: 24/193 accepted, 2 in progress, 0 ready;
S02c appears in Waiting to retry, not Ready now. No remote recovery/clip
usability claim; product dispatcher remains disabled and unchanged.

## Skills/plugins and communication

Read Superpowers using-superpowers + Codex tools reference, systematic-debugging,
test-driven-development + writing-good-tests reference, verification-before-
completion. Applied trace from STATE/report to QUEUE/parser/render boundary,
test-first failure then smallest behavior fix, fresh tests/output inspection.
Skill/reference reads were sequential; writing-good-tests was read after initial
red/green and before final review. No remote service/plugin needed: local Python
generator bug; no product, credentials, routing or global policy changes.

Optional worker chatter omitted; mandatory brief runtime update/skill announcement
retained. User receives concise requested result, not a duplicated report.
Actual controller model/effort, tokens, subscription dollars not observable;
no additional inference/GPU/service cost incurred by these offline checks.
