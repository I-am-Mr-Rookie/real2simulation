# N13-orch267 REPORT
Status: DONE (QA only, no code changes, no deploy). Findings: C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon\.worktrees\N13-orch267\evidence\N13\FINDINGS.md
- 3 fresh accounts in parallel plus a 4th (agent chat, voice, 375 px) and a 5th (isolation probe) on DEV, headed Chromium, Pexels clips only.
- Findings: 2 P1, 4 P2, 4 P3. P1: Mode B without known size shows "No value reported" and no chart/band (3/3); SAMPLE project not shown in the UI (seeded hash row in Processing instead). P2: contributor screen skipped on first load after sign-up; MEASURED 2.70 +/- 0.30 vs g 9.81 overconfident; agent guard refuses a valid drop-ball prompt 1/3; A4 accepts any two clicks as MEASURED.
- Passed: Mode B with size (26 to 42 s), share logged out and revoke, redo in 3D, Mode A build 31 to 49 s, A4 and object wiring, agent physics and off-topic refusal, voice transcribe, files preview/download/delete, 25 MB upload (15 s), 21st upload refused (429), cross-account isolation (404), 375 px no horizontal overflow.
- Checks: qa.mjs x3, qa2.mjs, probe.mjs (no repo tests run, no code touched).
- Paid calls (estimate, UTC 13:58 to 14:08): 6 Mode B about $0.14, 3 Mode A about $1.0, 5 muse-spark turns plus 1 transcribe under $0.05. About $1.2, within cap.
- Skipped: raw B1 API payload (job cap used), 15-minute GPU idle sleep, yellow GPU state not sampled, over-quota only on A3.
- Risks: harness first run had a wrong selector for the agent drawer (rerun in pass 2); the voice WAV loops so the transcript repeats.
