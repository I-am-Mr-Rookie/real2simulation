# S04i-orch118 — DONE (local implementation child only)

## Result and explicit acceptance boundary

The private route now mounts S15's public React workspace after the existing
Clerk-session/owner policy authorizes a server-only development fixture record.
Guests, nonowners, malformed/unknown IDs, missing configuration and unavailable
identity deny uniformly. Public `/library` remains unchanged.

**Controller receipt in chat 01a1882d-3481-7ce3-8f88-45c942e341cd explicitly
narrowed this child to local implementation and bounded HTTP proof, and moved
signed-in real-key HTTP verification to S15k on Railway dev. DONE is only that
child acceptance, not live authentication E2E, a complete workflow or a gate.**
The same receipt authorized finishing early rather than waiting/filler work.

## Important S15k handoff: loopback rewrite finding

The initial standard Clerk proxy reproduced the historical timeout when Next
was started with `--hostname 127.0.0.1`. Node diagnostic channels recorded
repeated **localhost `/workspace`** HTTP requests, not an external Clerk/JWKS
host. Standalone standard `clerkMiddleware()` with noncredential synthetic keys
returned a same-URL rewrite. Merely changing the client URL was insufficient;
using **both `--hostname localhost` and a localhost request origin** removed
the self-proxy loop. The deployment's **`--hostname 0.0.0.0` also passes** the
same bounded synthetic-config smoke. No SDK patch, version, provider, Clerk
configuration, credential or deployment change was made.

Evidence: `evidence/S04i/synthetic-network-trace.txt` preserves the failed
diagnostic run; `sdk-standalone.txt` records the independent SDK response;
`http-smoke.txt` records all three final passing production-server modes.
This narrows the observed local failure; it does not prove Railway real-session
behavior. S15k must verify that after its approved dev redeploy.

## Changes / concrete Ponytail application

- `auth/dev-scenes.mjs`, `scene-repository.js`: reused Node SHA256 and existing
  S15 `initialState`; one deterministic, read-only, empty fixture container per
  verified user. No database/bucket application helper existed, so no new storage
  client, dependency, persistence, mutation, upload or asset service was invented.
  Exact scene/user pairing is checked for both metadata and payload reads.
- Repository scope is local NODE_ENV development/test or the existing Railway
  environment named exactly `dev`; unlabelled production or a named non-dev
  environment denies. This uses existing environment names, not a new enable
  flag, and never bypasses authentication/ownership.
- `auth/server-access.js`: retained `authorizePrivateScene` and session-token
  `auth()`; added an authenticated own-fixture entry lookup and guarded view
  retrieval. The client DTO excludes owner ID and access metadata. Errors return
  the same Next notFound outcome, not provider/storage diagnostics.
- Private layout now composes children/CSS instead of unconditionally denying;
  each leaf remains its own authorization boundary. `/workspace` derives the
  current user's fixture ID and redirects to `/workspace/[sceneId]`.
- `shell/PrivateWorkspace.mjs`: uses `createWorkspace(React)` and the public
  `createThreeViewer()` adapter without editing **any S15 or S09 file**. The
  empty fixture honestly stays `upload.idle`, with no scene artifact, run, fit,
  invented physics value or fake success. Its visible FIXTURE / SYNTHETIC notice
  explicitly says uploads/live workflow services are not connected.
- Signed-in account navigation includes a non-prefetched private-workspace
  link. Generic 404 text no longer incorrectly says integration is absent.
- `src/proxy.js`: standard Clerk middleware, exact workspace-only matcher;
  missing config proceeds to the denying leaf, middleware errors deny with
  private/no-store 404. Standard SDK session-refresh handshakes are preserved.
- Extended the existing shell smoke, not a duplicate server harness; allowed
  only the owned composition stylesheet in its source-isolation check. Added
  bounded wrapper, focused tests and reproducible synthetic-only diagnostics.

## Fresh verification

| Command | Result / evidence |
|---|---|
| `node --test tests/web-private/*.test.mjs Build/web/src/auth/*.test.mjs` | **18 PASS**, 0 fail; `evidence/S04i/unit-tests.txt` |
| `node --test tests/workspace/*.test.mjs` | **79 PASS**, 0 fail; `workspace-tests.txt` |
| `npm run build --prefix Build/web` | **PASS**, Next 16.4.3 webpack; both workspace routes and proxy emitted; `build.txt` |
| `node tests/web-private/http-smoke.mjs` | **PASS**: missing-config localhost, synthetic-config localhost, synthetic-config 0.0.0.0; 60s subprocess limit/mode, 3s requests; `http-smoke.txt` |
| `node Build/web/src/auth/bundle-check.mjs` | **PASS**, 35 emitted browser JS/map assets; `bundle-scan.txt` |
| `git diff --check` + changed-path allowlist | **PASS**, all tracked/untracked changes within Owns + exact proxy extension; `scope-check.txt` |

Tests exercise the **actual server facade and repository** with a mocked Clerk
transport: owner view/entry ID, nonowner/guest/unknown/invalid/config/provider
failure 404, no auth call for invalid IDs/missing config/non-development mode,
session-token-only call, no owner identity in view. The public S15 SSR contains
all four slots, an idle state and the honest fixture label. These are not real
Clerk session results. Actual Next matcher tests exclude `/library`, sign-in,
health, API and lookalike paths. HTTP smoke verifies library200, private404,
forged cookies/headers denied, RSC404 digest, public-query isolation and HEAD.
Web `/health/live` and `/health/ready` remain404 (no web health route exists);
the distinct API/worker health services and their code were untouched.

Node24 emits the existing typeless-package ESM warning during the source-level
server-facade test; it passes. No package type/config churn was added to silence
a test warning. Build used the existing installed dependencies via an ignored
node_modules junction; no dependency install, lockfile or manifest edit.

## Authority, custody and timing

- Parent project Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`;
  canonical root retained, no new chat/project, workers or schedules created.
- Own isolated worktree `.worktrees/S04i-orch118`, branch `run/S04i-orch118`,
  from main `74427f179e1c6e1d6533283a97903075124e4f4a`; initial status clean.
  Canonical controls and unrelated user changes untouched. Left unmerged for
  controller integration, as explicitly contracted.
- Controller granted exactly `Build/web/src/proxy.js` outside the original
  Owns and later narrowed child acceptance as described above.
- CODEX-2; assigned gpt-6.1-sol/high. Managed runtime identity not independently
  introspected. Coding quota: **OpenCodex-managed; not polled**. Observable token
  counts unknown. External inference/GPU/API spend **$0**; no model calls.
- Issued 2026-10-30T09:17:50+00:00; first observed worktree clock 09:18:50Z;
  implementation cutoff 09:42:50Z; original deadline 09:47:50Z (15:47:50 Dhaka).
  Product work/verification stopped **2026-10-30T09:33:56+00:00** after the
  controller's explicit local-acceptance/DONE receipt. Actual report time and
  full 1800s window are recorded in `TIMEBOX.json`; timing check saved on disk.

## Skips, risks and next action

No deploy, real-key login, Google/OTP, live session refresh, persistent private
data, geometry upload, live workflow services, production exposure or gate/
real-scene/physical claims. Fixture state is deliberately nonpersistent and
cannot complete a workflow by itself. No secrets/environment files were read,
copied or staged; test credentials are explicit noncredential sentinels only.
S15k must redeploy Railway **dev**, verify real owner entry/scene mount plus
other-user/logged-out/unknown denial, and wire/walk the live workflow separately.

Communication: mandatory initial skill/tool update, finding update and necessary
authorized controller callbacks only; no optional repetitive narration. Final
controller callback is the exact one-line report pointer.

Primary references consulted: installed Next16 proxy and server/client guides;
[Clerk standard middleware](https://clerk.com/docs/reference/nextjs/clerk-middleware),
[Clerk Next quickstart](https://clerk.com/docs/nextjs/getting-started/quickstart),
[Next proxy convention](https://nextjs.org/docs/app/api-reference/file-conventions/proxy).
