# S22g-orch229 REPORT
Status: DONE. Start 2026-10-31T16:25:09Z, end 2026-10-31T16:35:53+00:00. Model anthropic/claude-sonnet-5-5 medium; OpenCodex-managed; not polled. Tokens/cost unobservable.

Result: all three checks PASS (logged-out 375/1280, auth boundary incl. cross-account 404 and sign-out 401, signed-in 375). Details, exact codes/text: evidence/qa/browser/S22g/RUN.md (+5 screenshots). Observations O1-O4 (P3) proposed to owner lanes, e.g. panel stays open over result after Finish at 375; logged-out /workspace -> bare 404.

Ponytail: reused S22e route/script pattern and Clerk test-account flow; no new code, throwaway scripts in %TEMP%; context.request for API probes (no browser needed); one owner-positive control added so B's 404 is proven ownership not dead route.
Checks fresh: yes (all above run this session). Skipped: sidebar patch/search; in-app browser/real Chrome. Risks: headed Chromium only (D10); test accounts kept.
Communication compliance: silent; no mandatory exception.

