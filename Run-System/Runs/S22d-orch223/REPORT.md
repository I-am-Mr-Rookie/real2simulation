# S22d-orch223 REPORT

Lane/model: CODEX-2, assigned anthropic/claude-sonnet-5-5/medium (OpenCodex-managed; not polled). UTC start 2026-10-31T15:39:59Z; end 2026-10-31T15:50:39+00:00 (deadline 16:09:38Z).

Result: Gate D run 2 PASS vs <5 min (scripted, ~58 s to result); RM04 viewer PASS (scene loads with "Display only, scale unverified, not a measurement."; no 503). Full detail, timings, labels, defect reproduction: evidence/qa/browser/S22d/RUN.md. S22c P3-1, P3-2, P3-4, P2-1 reproduced; P3-3 not reproduced (43 ms).

Files: evidence/qa/browser/S22d/{RUN.md,own05-result-1280.png,rm04-1280.png,rm04-375-closed.png}, this report, PLAN.md, TIMEBOX.json. No code changes. Scripts in %TEMP%/s22d (uncommitted). Test accounts kept.

Ponytail: reused S22c route, existing playwright-core runtime, Clerk test code; smallest scripted flow, no new code/deps. Fresh checks: 1 full OWN05 pass, 2 RM04 passes (1280, 375), screenshots viewed for privacy.
Skipped: 375 px OWN05 pass, RM04 interview answers/Run/Fit, Report body verification, human usability, Google/real-email sign-up, headless retry. Risk: scripted timings exclude human time; RM04 shows a recorded replay, not a live run.
Communication compliance: silent; one completion message to controller.


