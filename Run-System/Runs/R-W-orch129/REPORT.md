# R-W-orch129 — DONE — Verdict: CLEAR (no P1/P2 requiring change; P2 runtime item deferred to S15k)

Cross-vendor (Anthropic Opus 5.5 high; OpenCodex-managed, not polled) read-only review of Sol S04i-orch118 at main 67e299a. UTC start 2026-10-30T10:53:45Z (issue); work stopped 2026-10-30T11:04:42+00:00. Tokens/cost: unobservable; $0 spend.
Reviewed: Build/web/src/proxy.js; auth/{access.mjs,config.mjs,server-config.js,server-access.js,scene-repository.js,dev-scenes.mjs}; app/(private)/{layout,workspace/page,workspace/[sceneId]/page}.jsx; shell/PrivateWorkspace.mjs imports; tests/web-private/*; shell/smoke.mjs.

## Findings by check
| Check | Result |
|---|---|
| Owner-only, no existence leak | PASS. Leaf calls authorizePrivateScene (regex-checked id, Clerk session identity, metadata owner==user, access==private), all failures -> same notFound(). Other-user / unknown / malformed / logged-out / provider-throw / config-missing / non-dev all return identical null (own probe). Fresh HTTP smoke: 404 for /workspace, /workspace/<id>, forged ownerId/access query + forged identity headers, HEAD 404; RSC returns Next's standard 200 + NEXT_HTTP_ERROR_FALLBACK;404 digest, uniform for every denial. |
| Matcher scope | PASS. ['/workspace/:path*'] matches /workspace, /workspace/, nested, ?_rsc; not /workspaces, /library*, /api/*, /health/*, /sign-in* (Next unstable_doesMiddlewareMatch; S04i test + own edge cases). Smoke: /library, /sign-in, /sign-up 200 unaffected. |
| Fail-closed Clerk config | PASS. Proxy skips Clerk when config invalid -> leaf readIdentity returns null -> 404. Middleware throw -> 404 private,no-store. auth() throwing (middleware not run) caught -> 404. Own probe: missing sk, sk_live with pk_test, pk without '$', bad host, empty sk all unavailable. |
| Dev fixture cannot reach production | PASS. Enabled only for RAILWAY_ENVIRONMENT(_NAME)==='dev' exactly, else NODE_ENV development/test; production, unlabelled, 'Dev', staging, production-Railway-with-NODE_ENV=development all deny (own probe). Fixture is empty initialState, owner-bound by sha256(userId); DTO strips ownerId/access. |
| No secrets in client bundle | PASS. Fresh build bundle-check 35 assets PASS. Own scan of 46 .next/static files: no sk_test/sk_live, RAILWAY_ENVIRONMENT, dev-fixture-, readDevelopmentScene, scene-repository, ownerId. One hit for the NAME CLERK_SECRET_KEY inside the Clerk SDK chunk (process.env read; Next inlines only NEXT_PUBLIC_*, so no value) — informational. |
| Loopback rewrite (127.0.0.1 vs localhost) on Railway | P2 RISK, not a bypass. Failure mode is a self-proxy loop/timeout = availability, still denying. Railway start is plain `next start` (binds all interfaces, like the passing 0.0.0.0 mode). Real-key handshake behind Railway edge (Host/X-Forwarded-*) remains UNVERIFIED -> S15k must check signed-in /workspace on dev redeploy and watch for repeated self-requests/timeouts. No code change recommended now. |

## Lower-priority notes (no change required)
- P3: fixture sceneId = unsalted sha256(Clerk userId) appears in URL/history/logs; reveals a stable user-linked hash, not access. Replace with random ids when real storage lands (already a shortcut comment).
- P3: production has no real repository, so every private scene 404s there; fail-closed but functionally incomplete (known S04i boundary).
- P3: RSC denials are HTTP 200 with embedded 404 (Next default); consistent, so no oracle, but monitoring that counts HTTP 404 will miss them.
- P3: a future judging deploy placed in a Railway env named 'dev' would expose the (owner-only, empty, labelled synthetic) fixture; name production env distinctly.

## Fresh commands (this run)
| Command | Result |
|---|---|
| canonical: node --test tests/web-private/{repository,server-access}.test.mjs Build/web/src/auth/*.test.mjs | 18 pass / 0 fail (worktree first failed: no node_modules) |
| canonical: node tests/web-private/http-smoke.mjs | FAIL — canonical .next was stale (BUILD_ID 2026-10-29T12:40Z, before S04i source). Not a code defect; not used as evidence. |
| worktree (node_modules junction -> canonical, isolated .next): npm run build --prefix Build/web | PASS, /workspace, /workspace/[sceneId], Proxy emitted |
| worktree: node tests/web-private/http-smoke.mjs | PASS exit 0, all modes (missing-config, synthetic-config localhost, 0.0.0.0) |
| worktree: node Build/web/src/auth/bundle-check.mjs | PASS 35 assets |
| worktree: node --test evidence/reviews/R-W/probe.test.mjs | 4 pass / 0 fail |
| own .next/static pattern scan | see table |

## Ponytail application
Reused existing tests, smoke harness, bundle-check and Next's own matcher helper instead of writing a server harness; one 4-test probe file only for gaps (env matrix, cross-user known-id, config syntax matrix, matcher edges). Built in my worktree via a node_modules junction rather than rebuilding canonical .next (avoids racing other workers). No Build/tests edits.
Skipped: real Clerk keys / signed-in session (secret + S15k scope), Railway deploy, timing side-channel measurement, PrivateWorkspace render review beyond imports.
Risks: signed-in real-key and Railway-edge behaviour unverified; junction Build/web/node_modules + .next left in this worktree (ignored, untracked).
Communication: silent; one completion line to controller.

