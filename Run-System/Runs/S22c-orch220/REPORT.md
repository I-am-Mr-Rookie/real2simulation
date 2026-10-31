# S22c-orch220 REPORT
Status: DONE. Lane CODEX-2 run by anthropic/claude-sonnet-5-5 medium (OpenCodex-managed; not polled). UTC 2026-10-31T14:36:46Z to 2026-10-31T14:51:18+00:00.

Result: fresh DEV account (Clerk test email +clerk_test, code 424242) -> private workspace -> OWN05 upload -> interview answer -> result chart with labels in 29.3 s (63 s incl. Report). PASS vs <5 min (scripted). Full timings, verbatim labels, defects: evidence/qa/browser/S22c/RUN.md (Run 2 section). Key defects: P2 Run/Fit never executed (precomputed owner-clip result, no scene); P3 404 /api/workspace/jobs/s04o-probe; P3 375 px panel auto-open; P3 Report click 33.5 s undiagnosed; P3 redirect to /library. ENV: headless Chromium stalls on Cloudflare Turnstile at sign-up, headed passes.

Ponytail: reused existing playwright-core and Clerk test-email code; throwaway scripts in Temp, not committed; no code changes. Fresh checks: 3 full scripted passes plus 375 pass, screenshots viewed.
Skipped: Google sign-up, real email OTP, human usability pass, Gate D runs 2-3. Risk: timings are scripted and exclude human time; Report delay cause unverified.
Communication compliance: silent; no mid-run blocker needed (Turnstile resolved by headed mode).

