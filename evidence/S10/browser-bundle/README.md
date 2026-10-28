# R11 local production bundle verification

Source: `694df9a0fd1fd1949cedec396de69a73ff1bad35`; isolated `run/R11-bundle-check` worktree. No authored product/config/control changes.

## Fresh commands (from isolated repository root)

```powershell
Push-Location Build/web
npm run build # existing next build --webpack
Pop-Location
node --test tests/lab/browser-simulator.test.mjs tests/lab/ui-contract.test.mjs
node evidence/S10/browser-bundle/inspect-bundle.mjs
node Build/web/src/auth/bundle-check.mjs
node evidence/S10/browser-bundle/probe-production.mjs
```

- Build exit **0**, complete compilation/page generation/optimization/traces: `build-output.txt`, `build-result.json`. Next 16.4.3, Node v24.18.0, npm 11.16.0.
- **19/19** narrow source tests pass: `source-tests.txt`, `source-tests-result.json`. These execute the existing actual four-template engines and compare engine/server traces; not a visual browser test.
- **32** emitted JS/map assets scanned and hashed: `bundle-inspection.json`. Normal-only validation, RK4 engine and UI markers belong to the manifested lab client entry. Recursive browser simulator source imports are only the trajectories/extended-templates/RK4 graph, not the session service or Mystery secret producer.
- Existing auth bundle check passes. App server bridge/session/Mystery-private markers, child_process, randomsecret/randomSecret and credential-shaped server keys absent in emitted assets. This is targeted evidence, not an exhaustive security audit.
- **18** production HTTP probes pass: `production-probes.json`. /lab returns 200 and its actual emitted simulator chunk returns 200; /library 200; missing-key sign-in/sign-up explicitly unavailable; unauthenticated and forged-header private workspace return 404. Three POSTs (normal start, malformed JSON, fit) all return 403 `local_lab_disabled`, `cache-control: no-store`. Production route intentionally not enabled.
- Production process bound only `127.0.0.1:3102`, launched directly with Next start; owned PID and SIGTERM receipt saved. No browser, external account or deployment used. `production-server-output.txt` is local stdout/stderr.
- `process-preflight.txt`: no competing Next production build; existing parent/other worktree dev processes left untouched. `dependency-junction.json` records reused canonical node_modules. Junction itself is not an ACL-enforced read-only mount; this run issues no install/dependency mutation command. Build output is isolated .next. Parent .next root timestamp before/after is unchanged (not a recursive tree integrity proof).

## Inspection corrections / material caveat

The first evidence-script attempt had an incorrect relative root. The next assumed a separate LabClient manifest entry, but webpack concatenates it under the client lab page. Both evidence-only assertions were corrected and freshly passed; no product code was changed.

An initial overbroad scan also rejected the **name** `CLERK_SECRET_KEY`. Inspection traced it to installed `@clerk/nextjs/dist/esm/server/constants.js`: webpack retains unused `.env.CLERK_SECRET_KEY`, `.env.CLERK_MACHINE_SECRET_KEY`, `.env.CLERK_ENCRYPTION_KEY` property references. The final scanner explicitly records these SDK name references rather than pretending every server-named SDK module is absent. No values/secret-shaped credentials found; own `server-config.js` stays server-only. This no-key build does **not** establish safety of a future credential-configured build, successful Clerk authentication, or runtime browser interaction. Authored normal gravity 9.81 is allowed, not treated as a Mystery secret.

No .env copied/read; no secrets retrieved. No install/new dependency, source edits, merges, deployment/public exposure, paid GPU, physical Gate M/S12 or real-scene work. Ignored isolated output/junction left for inspection. Cost/tokens unknown; OpenCodex-managed; not polled.
