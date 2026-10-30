# S04k-orch133 REPORT — DONE

Lane CLAUDE, anthropic/claude-opus-5-5 high (OpenCodex-managed; quota not polled). UTC start 2026-10-30T11:13:57Z,
end 2026-10-30T11:22:26+00:00. Branch run/S04k-orch133 from main 4e59880; code commit afbdae4. Tokens/cost: unknown (unobservable); no paid calls.

## Change
- `Build/web/src/app/api/library/guest.mjs`: reads `<cwd>/library-snapshot/guest.json` (`R2S_GUEST_SNAPSHOT` override),
  4 MiB bound, verifies every object (64-hex id, <=256 KiB, sha256) and that every manifest artifact resolves; verified
  once per process (fixes R-L P3 per-request revalidation), failures sticky -> 503. Artifact sha rechecked on read;
  immutable + ETag kept; manifest gets no-cache + content ETag. Python spawn kept only when snapshot is ABSENT and
  NODE_ENV != production (local dev); corrupt snapshot never falls back. Routes unchanged.
- `infra/railway/dev/stage.py` (web only): refuses tracked edits under Build/test-data/evidence (`git diff --quiet HEAD`),
  runs existing load_guest() via the same one-liner, checks object hashes (all before the exclusive mkdir), writes
  Build/web/library-snapshot/guest.json into the context and records its sha in context-manifest.json. Also stages
  `Build/library/loader.mjs` (LibraryClient imports it; previously unstaged -> Docker build would fail).
- `web.Dockerfile`: WORKDIR /app/Build/web, `COPY Build /app/Build` — mirrors repo layout so ../simulator, ../lab,
  ../library and loader.mjs's ../web/src imports resolve; context still only holds stage.py's allowlist + snapshot.
- Tests: test_stage.py (web expects loader + snapshot; new rejection test: tampered/invalid snapshot and dirty tree ->
  no destination). tests/web-library/library.test.mjs now serves from a real load_guest snapshot + tamper/drop/bad-json/
  oversize 503, production-missing 503, dev fallback parity, broken-root 503, objects == manifest refs, no answers.

## Ponytail
Reused load_guest() as the only projection/answer-withholding logic (no JS re-implementation, no widening; snapshot
object set asserted equal to manifest refs). Reused the existing python one-liner and route files; snapshot = the exact
JSON shape the old spawn returned. One file, no new deps, no new config besides one env override mirroring R2S_REPO_ROOT.
Skipped: 304/If-None-Match handling, snapshot signing, a separate build script, Docker build itself.

## Fresh checks
- `python -B -m unittest discover -s infra/railway/dev -p "test_*.py"` -> 15 OK (evidence/S04k/infra-unittest.txt).
- `node --test tests/web-library/library.test.mjs` -> 5/5 pass (evidence/S04k/node-test.txt).
- `npm run build --prefix Build/web` -> exit 0 (evidence/S04k/npm-build.txt).
- Real stage.py web context build + production-mode HTTP probe without python: evidence/S04k/STAGING-PROBE.md.

## Risks / next
- NOT deployed. Next dev redeploy must stage from a clean committed tree (stage now fails on tracked edits under
  Build/test-data/evidence) and needs python+fastapi on the staging host. Docker build of the new layout unverified
  (staged-layout next build verified instead).
- `infra/railway/dev/verify.py` still expects /library text "No demos are published yet" (not owned; redeploy run should update).
- Snapshot is frozen at staging: custody revocation needs a restage/redeploy (intended trade-off of no runtime Python).
- Untracked files are not detected by the clean-tree check (load_guest reads tracked custody files).
Communication: silent; one completion message to controller only.
