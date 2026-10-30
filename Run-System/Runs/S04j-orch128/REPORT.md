# S04j-orch128 REPORT — DONE
Lane CLAUDE, assigned anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No GPU/API/model/paid calls.
UTC: issued 2026-10-30T10:53:45Z, worker start ~10:58:32Z, stopped 2026-10-30T11:09:23+00:00. Branch run/S04j-orch128 from main 67e299a.

## Changed
- Build/web/src/app/api/library/guest.mjs — calls Build/library/guest.py `load_guest()` (single source of truth) via execFile; manifest no-cache;
  artifact: strict ^[a-f0-9]{64}$ id (400), unknown 404, size <=262144 + sha256 recheck (503), immutable cache + ETag + nosniff; any failure 503 fail-closed.
- api/library/manifest/route.js, api/library/artifacts/[id]/route.js — thin GET wrappers (force-dynamic).
- (public)/library/page.jsx + LibraryClient.jsx — cards sorted playable > setup-only > unavailable; tags SIMULATED·playable /
  SIMULATED·setup only / UNAVAILABLE + reason; SCALE_UNVERIFIED display-only line; Mystery-g card = setup only, answer withheld, link /lab;
  "Play simulated replay" -> Build/library/loader.mjs loadLibraryEntry (fetch+sha verify) -> viewer mountTrajectoryReplay (inspect mode). One replay open at a time.
- tests/web-library/library.test.mjs; evidence/S04j/{node-test.txt,build.txt,screens.mjs,screens.json,desktop.png,mobile-375.png,STAGING.md}.

## Fresh checks
- `node --test tests/web-library/library.test.mjs` -> 3/3 pass (labels, UNAVAILABLE reasons, mystery answer-free, 400/404, immutable, sha, traceFromBody for projectile + pendulum, broken-root 503). evidence/S04j/node-test.txt
- `npm run build --prefix Build/web` -> exit 0; routes /library, /api/library/manifest, /api/library/artifacts/[id] built. evidence/S04j/build.txt
- `next start -p 3417` + `node evidence/S04j/screens.mjs` (headless Edge over CDP, http localhost, not Chrome UI): desktop + 375px: 18 cards
  (2 playable, 1 metadata-only, 15 UNAVAILABLE), replay data-state=ready, no horizontal overflow, no answer text. evidence/S04j/screens.json, desktop.png, mobile-375.png
- /library and /api/library bypass auth: proxy matcher is only /workspace/:path* (unchanged).

## Ponytail (applied)
Reuse: guest.py logic called, not ported (no duplicated custody/answer-withholding rules); loader.mjs loadLibraryEntry for fetch+verify; viewer mountTrajectoryReplay;
house styles (.reading/.mount-note/.state-tag) + ~5 lines grid CSS. Skipped: client caching, filters/search, pagination, per-card routes, scene/PLY viewing.
## UI bar
myfront read: rule 1 "preserve existing brand" -> kept app's warm paper/offset-shadow theme, no restyle. Mobbin: one web search
("library gallery of cards with status badges": Arcade, Gamma, Airtable, Air, Tana) -> status-tag-first card grid, playable first. Superpowers: not used (no time; not needed).

## Limits / risks
- Structural bottleneck: each API request spawns python and re-validates custody (~4-8 s locally) — by guest.py's no-cached-authority contract. Upgrade: short-TTL memo keyed on file mtimes if latency matters.
- Deploy needs python+fastapi+library files in the image: evidence/S04j/STAGING.md for S15k (stage.py not edited). Not deployed.
- Pendulum replay mounted only via test (traceFromBody); screenshot shows one replay open (UI opens one at a time).
- Build used a junction Build/web/node_modules -> main's node_modules (untracked, not committed).

