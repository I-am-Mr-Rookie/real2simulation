# S18g-orch120 — DONE (metadata loading + validated viewer-request boundary)

## Result / open scope boundary

Implemented and verified metadata-only library loading for every current guest
entry. Real scene descriptors produce an exact validated viewer request; setups
and challenges remain metadata, not fabricated scene-v1 bundles. **All current
entries return `canMount: false`**, because S18f exposes no render bytes or replay
trajectories. No playable library or parent S18/Gate D completion is claimed.

Controller receipt in this worker chat explicitly approves **DONE for
metadata-only loading + validated viewer-request boundary**, because the QUEUE
criterion is consumption of the viewer interface without editing CLAUDE modules.
Playable asset/replay wiring is explicitly deferred to a controller follow-up row.
No approved scoped acceptance remains unfinished; fully verified DONE may end early.

## Contract / custody

- CODEX-2 / S18; assigned gpt-6.1-sol / medium. Backend identity/effort, tokens
  and subscription cost are not independently observable. **OpenCodex-managed;
  not polled.** New GPU/Meta/API/model spend: $0.
- Parent project `91e441f8-e40c-4ec4-bea2-de7fa1582d97` supplied by delegation;
  no chat, launcher, project, provider or permission setting was created/changed.
- Canonical root: `C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.
- Created requested plain Git worktree `.worktrees/S18g-orch120`, branch
  `run/S18g-orch120`, FIRST from main `de2bdaed6c7cea0cc2cd206f41635ff380233499`.
  Initial worktree clean. No unrelated changes imported or staged.
- Issued 2026-10-30T09:22:34+00:00; implementation cutoff 09:47:34Z;
  deadline 09:52:34Z / 15:52:34 Dhaka. Final actual timestamps in TIMEBOX.json.
- Only Owns changed. Canonical controls, app, viewer/workspace modules, fixtures,
  credentials and dependencies untouched. Controller owns acceptance/merge.

## Implementation and acceptance evidence

1. `Build/library/loader.mjs` exports one framework-free async
   `loadLibraryEntry(entry, { signal, fetch })`. It snapshots input before async
   transport to prevent selection mutations changing checked safety defaults.
   Reuses viewer `readCapped`, `DEFAULT_LIMITS`, `checkManifest`,
   `checkViewerRequest`, `ViewerError`, scale-unverified banner and `deepFreeze`.
2. Before fetch: require metadata-only/display-only/scale-unverified labels,
   autoplay/physics off, prediction WITHHELD and empty parameters; allowlisted
   kind, JSON declaration, exact hash endpoint, lowercase SHA and safe integer
   size. Metadata cap is existing 256 KiB manifest limit, stricter than generic
   server artifact limit. No arbitrary URL, source path, redirect or credentials.
3. During fetch: forwarded cancellation, streamed and Content-Length caps,
   exact byte length, WebCrypto SHA-256, fatal UTF-8 then JSON. Unknown kinds,
   hash mismatch, oversize and malformed data refuse with authored readable
   errors; stream/network errors do not expose upstream exception messages.
4. RM02/RM04 descriptors pass the existing viewer manifest/point/asset/path gate
   and yield exact guest/inspect/public-library/reconstructed viewer requests,
   preserving SCALE_UNVERIFIED display-only banner, source attribution, gates,
   limitations and safe defaults. Actual asset bytes are not exposed by S18f.
5. Free-fall/projectile/pendulum setups require exact answer-free keys, supported
   templates and finite positive source timing. Mystery-g requires exact
   answer-free keys, `withheld-until-fit`, and existing `/lab` target. No gravity,
   extra answer fields or fixture substitution. Both remain SIMULATED metadata;
   a setup is never passed to the PLY decoder. Apollo/bounce/RM05 never fetch.
6. `evidence/S18/S18g-LOADER-INTERFACE.md` documents exact one-call web import,
   current return shape/kind mapping, safe plain-text display, and the unchanged
   future `createThreeViewer().mount(..., { loadScene, signal, onState, onError })`
   boundary. Current `canMount: false` must gate that call. The README links it.
   Its deferred-input section lists exact RM02/RM04 declared PLY paths, byte
   counts/hashes and decoder layout; existing free-fall/projectile/pendulum
   simulator trace/sample shapes; and the missing replay/geometry adapter.
   Mystery-g has no accepted viewer trajectory DTO and must use server-redacted
   /lab challenge/fit, never expose answer-bearing raw replay records. Apollo
   remains unavailable. These are follow-up inputs, not produced assets.

## Fresh verification

- `python -B -m unittest discover -s tests/library -t tests/library -v`:
  **73 PASS** (72 existing + 1 wrapper executing the Node contract suite),
  52.472s. Log: `evidence/S18/S18g-library-tests.txt`.
- Fresh current `guest.load_guest()` projections piped to
  `node --test-reporter=tap tests/library/loader.test.mjs`: **16 PASS**, no skips;
  all 18 entries plus malformed/unavailable inputs, URLs, hash/byte/stream limits,
  JSON/UTF-8, unsafe defaults, answer leaks, viewer contract limits, mutation,
  errors and cancellation. Log: `evidence/S18/S18g-loader-node-tests.txt`.
- Read-only `node --test tests/viewer/viewer.test.mjs
  tests/viewer/artifact-loader.test.mjs tests/viewer/real-scenes.test.mjs`:
  **19 PASS, 3 SKIP** (RM02/RM04/RM05 real media absent). Existing fixture PLY
  decoding, banners, loader+adapter mount/disposal and errors remain green.
  Log: `evidence/S18/S18g-viewer-tests.txt`.
- Node dynamic import resolved the documented relative import from the future
  `/library` page directory successfully, without importing Three/package deps.
- Documentation self-check compared all four deferred asset SHA/byte declarations
  against fresh accepted guest scene descriptors: PASS. Values are declarations,
  not downloaded media verification. Scoped product verification stopped at
  2026-10-30T09:39:04+00:00; subsequent receipt/staging/commit is bookkeeping.
- Initial Python wrapper failed only because Node chose spec rather than TAP
  reporter (all underlying 15 Node tests passed). Pinned the test reporter, not
  product behavior; subsequent focused and full suites passed. Final suite adds
  malformed-unavailable and in-flight-cancellation coverage, now 16 Node tests.
- Final named staging, `git diff --cached --check` and
  `python -B Run-System/worker_timebox.py check Run-System/Runs/S18g-orch120/TIMEBOX.json`:
  PASS (timing arithmetic separately from controller acceptance). No broad
  force-add, outside-Owns paths or bytecode staging.

## Skills/plugins: Ponytail full applied

Read `C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.3/skills/ponytail/SKILL.md`.
Reused public viewer validation/stream/limit/error/banner/freezing helpers instead
of copying their logic or changing CLAUDE-owned modules. One loader function,
no wrapper service, renderer, decoder, transport resolver, schema migration,
dependency, cache or extra fixture. Tests consume actual guest projections rather
than creating a second catalogue. Existing callers/config/exports need no changes.
Only browser-native SHA/UTF-8/JSON handling and minimal kind safety checks are new.

## Skips / risks / next

- Skipped app hookup, browser/Next build, live guest HTTP deployment, actual scene
  asset mounting, simulation replay, GPU/API/model work, installs, secret access,
  canonical controls, main rebase/merge, remote push/publication. No authority for
  new media redistribution, missing geometry or gate promotion was inferred.
- Structural blocker is **metadata versus render bundle**, not a missing decoder.
  Do not replace SIMULATED with SYNTHETIC fixture claims. No measured scale,
  physical accuracy, Gate M/RS/R/D or lunar result follows from loader success.
- WebCrypto/fetch/structuredClone require the existing modern browser/runtime;
  verified here on Node 24.18.0, not a live bundled page. Integrity is not rights
  approval/authenticity; the guest server still validates current source custody.
- Next: controller reviews branch and scopes the deferred playable row. Later app owner can
  use the documented single loader call to show metadata now; playable rendering
  requires separately accepted/exposed asset bundles or replay inputs.

Communication: one mandatory initial tool-work/Ponytail notice; two necessary
nonterminal controller messages (upstream finding, focused scope question). No
optional progress, owner question, quota polling or other-chat messaging. Final
skip/risk disclosure and one authorized completion callback follow final receipt.
