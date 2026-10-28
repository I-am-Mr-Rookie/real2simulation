# S10g-ui report

## Result
DONE — implemented the actual local `/lab` page and client UI on `run/S10g-ui` from `main` `bd5df5f`.

## Changes
- Added public route `Build/web/src/app/(public)/lab/page.jsx`.
- Added `Build/web/src/lab/LabClient.jsx` with:
  - accessible template radios for free fall, projectile, ramp, and pendulum;
  - ballistic-only Mystery-g toggle;
  - `start` and ballistic-only `fit` POST calls to `/api/lab`;
  - blank/reset state on template or mode changes;
  - abort plus request-version stale-response protection;
  - pending/error/status messaging without raw payload dumping;
  - sampled trajectory SVG, table, simulated badge, reveal uncertainty, and limitations.
- Added narrow responsive `Build/web/src/lab/lab.css`; no shared shell/layout/style/auth files changed.
- Added `tests/lab/ui-contract.test.mjs` for flow, trust-label, no-hidden-gravity, and narrow-layout contracts.

## Checks
- `node --test tests/lab/ui-contract.test.mjs` — 2/2 pass. Output: `evidence/S10/ui/ui-contract.txt`.
- `git diff --check` — pass.
- Base/branch check: clean checkout at `bd5df5f`, branch `run/S10g-ui`; only owned source/test/report/evidence paths are untracked/changed.

## Ponytail reuse and skips
- Reused existing public shell and CSS variables; native React/browser APIs only; no dependency or abstraction added.
- Skipped heavy Next build and live browser/API verification because the worktree has no `Build/web/node_modules`, and parent owns local server/browser integration and serialization.

## Risks / limits
- Live `/api/lab` response and rendered 375px browser behavior remain for parent integration verification.
- The component accepts the agreed fit variants (`fit`, `actualS11response`, `reveal`, or `gravity`) but cannot verify live service behavior offline.
- Coding allowance: OpenCodex-managed; not polled. No jobs, spend, deploy, auth, upload, or policy changes.
