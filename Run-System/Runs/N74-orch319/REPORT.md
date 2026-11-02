# N74-orch319
Status: DONE; real signed-in Clerk-session verification remains unverified (synthetic header fixture used).
Changed: F2 flex nav can shrink/wrap, brand cannot shrink; F3 home labels imperfect scale with uncertainty.
Changed: F4 separate requesting/recording/transcribing states across all three voice controls; denial returns idle, retry works; lab form wraps the longer label at 375.
Changed: F5 toggling either room pick tool off clears its note and pending clicks.
O1: no race found. Synchronous localStorage write precedes state update; lab reads same authenticated-user key afresh on every ask. No speculative change.
Checks: 272 Node tests pass across workspace, lab-editor, web-private and shell-workspace; npm run build passes; git diff --check passes.
Browser: actual local production home at 320/375/1366, actual lab microphone-pending UI at 1366/375. Synthetic signed-in AccountNav fixture at 320/375/1366, all three voice controls denied/recovered.
Evidence: evidence/N74/QA.md, browser-results.json, voice-fixture-results.json, reproducible isolated UI fixture. Screenshots local only as linked in QA.md.
Paid calls: 0. No microphone permission granted, transcript, auth/account changes, uploads, private media, deployment or push.
Skipped: real Clerk signed-in local session (credentials absent), real microphone transcription and paid Wonder turns.
Risk: header actual Clerk UserButton integration should be rechecked after DEV merge; O1 single live observation not reproduced.
