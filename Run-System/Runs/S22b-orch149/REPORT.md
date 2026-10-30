# S22b-orch149 REPORT
Status: DONE for guest-library QA coverage, with one caveat (below). Lane CODEX-2 / army Claude, Sonnet 5.5 medium assigned; OpenCodex-managed; not polled. UTC 2026-10-30T11:54:35Z–12:02Z (cutoff 12:19:35, deadline 12:24:35). DEV pre-candidate rehearsal only; no judging-candidate claim; Gate D not assessed of record. Deploy: web aa539357.

## Caveat
IAB profile was already SIGNED IN as owner (user menu/Private workspace visible). I did NOT sign out (would change shared owner session) or sign in. Guest behaviour was confirmed with cookie-less curl (web /library 200, /workspace 404) and first-paint 'Sign in' nav; browser interaction results are guest-equivalent, not a fresh logged-out profile. Re-run L1/L4 in a clean profile if Gate D of record needs it.

## Results (details: evidence/qa/browser/S22b-guest-library.json; screenshots S22b-*.jpg)
- L1 PASS (caveat): /library 200, 2.3s IAB reload / 2.9s cold curl; 2 playable + 1 setup-only + 14 UNAVAILABLE cards; labels SIMULATED, SCALE_UNVERIFIED, UNAVAILABLE+reason present.
- L2 PASS on web, FAIL on API host (404; guest served by web snapshot).
- L3 PASS: 3/3 sha256+bytes match.
- L4 PASS: projectile and pendulum open/play/scrub at 1280 and 375; zero Modal/Meta/Baseten/Fireworks requests (same-origin + Clerk only).
- L5 PASS. L6 PASS (no answer/g field in any guest response; blind path is /lab).
- L7 PARTIAL: no leak, but web returns 400 invalid_artifact_id (checklist expects 404 artifact_not_found).
- Mystery-g /lab: FAIL functional - Run trial -> raw 'local_lab_disabled'; Fit & reveal disabled; no answer shown.
- 375px: no horizontal overflow. Console: Clerk JS load error once + dev-keys warning.
- Not applicable to guest: private workspace, upload, interview, run, fit, report, auth checklist sections.

## Defects for S22f
D1 P2 /lab raw local_lab_disabled / Mystery-g unusable on dev. D2 P2 API host lacks /api/library/*. D3 P3 400 vs 404 invalid id. D4 P3 replays 0.2-0.25 s. D5 P3 Clerk console error. D6 P3 desktop grid width. D7 P3 Mystery-g card shows Earth-g/spoiler wording.

## Ponytail
Reused IAB + curl + existing manifest; no code written/changed. Skipped: fresh-account x3 timing, 1280 /lab fit, video recordings (screenshots only; durations from replay timestamps). Risk: network log from one CDP capture; browser not signed out.

Communication compliance: silent; one completion message.

