# S04b — DONE

## Scope / receipt
- Objective: Next.js shell and isolated route layout. Requested CODEX-2,
  GPT-6.1 Sol / medium; actual delegated Codex model/effort not exposed.
- UTC start 2026-10-27T18:27:27Z; initial main 2045c55; claim ea615b4.
  Final verification receipt 2026-10-27T18:39:00Z (11m33s).
  Task 8847965 rebased onto S08f main e8e99ed, then fast-forwarded as
  e8ae0b5b925c4dc9b6c7b44a5086e3e73fada013. No lane/settings changes.
- Managed worktree C:/Users/HP/.codex/worktrees/s04b/2026-10-26 - Meta Global AI Developer Hackathon.
  Archive requested once after merge; refused: "The task's primary checkout
  cannot be removed." Retained clean; no manual deletion/bypass.

## Changes
- Pinned next16.4.3/react19.3.1/react-dom19.3.1; Node>=20.9.
  Documented webpack build/start/smoke scripts. Added three0.186.1 for S09b's
  explicit renderer dependency request, without viewer imports or edits.
- App Router root + public/private groups; public landing and honestly empty
  /library. Private layout AND workspace leaf deny with 404; no scene/job/asset
  reads, session acceptance or workspace implementation. Generic 404 includes
  missing-auth explanation. Route groups are not security boundaries.
- Semantic frame, skip link, local responsive CSS, authored labelled schematic
  and icon, sanitized error boundary. No remote fonts/media or invented results.
- Deterministic production HTTP smoke, source isolation check and setup docs.
  No API/worker/infra changes, lockfile or root configs outside Owns.

## Checks / evidence
- RED before implementation: smoke failed "root HTML layout must exist".
- Initial HTTP run exposed Next's layout notFound using the ancestor boundary,
  not the group's own not-found; removed that unused boundary, used generic
  root fallback and guarded the leaf too. Final tests exercise real HTTP.
- Browser initially reported missing favicon; added /icon.svg assertion,
  observed 404 !=200 RED, then authored icon and rebuilt GREEN.
  A failed-run Windows Node cleanup assertion was also emitted; response bodies
  are now drained before status assertions. No such warning in passing runs.
- Worktree production build PASS; smoke PASS before commit and after rebase:
  /, /icon.svg, /library 200; private workspace, unknown entry and unknown page
  404; forged session cookie/user header still 404. Server is loopback-only and
  smoke terminates it. Isolation checks pass.
- Shell DTO tests7/7 and viewer regression11/11 PASS before commit, after rebase
  and on main; git diff --check PASS. Viewer files unchanged.
- Playwright inspected desktop1280x800 and mobile375x812: no horizontal overflow
  (document width375), main/skip/navigation present, public library empty.
  After icon fix, fresh home navigation console: 0 errors/0 warnings.
  Local screenshots/snapshots in browser/ beside this report (ignored);
  servers stopped. This is shell QA, not auth E2E, physics or Gate evidence.
- Canonical main fresh npm install (22 packages, audit0 vulnerabilities),
  production build and smoke all PASS; no server left running. Main verification
  checkout 1b7c11b includes the S08g claim; task files are the merged e8ae0b5.

## Skills / plugins
- Read and applied Superpowers test-driven-development + writing-good-tests:
  initial missing-shell RED, real HTTP tests, favicon RED/GREEN, no mocks.
- verification-before-completion: fresh build, HTTP and regression evidence;
  using-git-worktrees: baseline7/7, native managed isolated branch and ff merge.
- frontend-design: token/type/layout plan reviewed before implementation;
  subject-specific labelled bench illustration, no fabricated science/dashboard,
  desktop/mobile screenshot critique, local fonts and visible focus.
- Actually used native worktree and usage-limit app tools, Playwright browser
  tools, official Next.js docs and npm registry. Railway/GitHub/Clerk tools skipped:
  deployment, publication and auth wiring are later tasks. No native UI requested.

## Limits / next
- S04b only: no Clerk, Google/OTP E2E, scene playback, upload, API/worker health,
  storage, Railway deployment or gates. All gates remain NOT RUN.
- Direct dependencies pinned; transitive resolution not locked because the
  root package-lock is outside Owns. Future ownership should include it before
  deployment/reproducibility claims. No .env values accessed or copied.
- Next authorized run: S04c CODEX-2 Sol medium; S09b now has its requested
  three dependency. Existing clip approval-order question Q2 is unchanged;
  no new owner question.
- Shared quota before/after used70%5h /50%weekly; not task attribution.
  Tokens/subscription task dollars unknown; Meta/service inference/GPU $0.
