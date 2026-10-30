# R-L cross-vendor review — guest library exposure & Mystery-g withholding

Reviewer: anthropic/claude-opus-5-5 medium (CLAUDE lane), read-only. Base main `67e299a`.
Scope: Build/library/{guest.py,loader.mjs,playable.py,generate-trace.mjs,mystery_g.py,validate.py},
test-data/library-artifacts/, reports S18e-orch110, S18f-orch113, S18g-orch120, S18k-orch123.

## Verdict: CHANGES_REQUIRED (one P2, two P3; no P0/P1 on the guest HTTP surface)

## Evidence (fresh)
- `python -B -m unittest discover -s tests/library -t tests/library` -> Ran 81 tests, OK (library-tests.txt).
- `probe_guest_exposure.py` (run from worktree root) builds `load_guest()` and scans the guest manifest + every served object:
  - 18 demos: 2 playable traces (projectile baseline-short, pendulum short-small-angle), 1 metadata-only
    challenge (141 B: source, mode, answer_visibility, duration_s 0.2, time_step_s 0.001), 15 UNAVAILABLE.
  - Free-fall baseline-short (= Mystery-g record `/cases/0`) is UNAVAILABLE ("Trace withheld ...").
  - Raw acceptance.json (sha 60e7437f97...) NOT served; replayHash/traceHash of /cases/0 absent from manifest+objects;
    no `gravity`/`seed`/`replay`/hash keys in any served object; literal "9.81" absent; manifest 8,903 B.
  - No other public trace shares the answer RECORD (withholding keyed by (evidence sha, pointer); only /cases/0 matches).

## Findings
**P2 — Mystery-g answer VALUE is indirectly obtainable; withholding gives no real secrecy.**
The challenge record is acceptance `/cases/0`: g = 9.81 m/s², seed 42. (a) The served projectile
baseline-short trace (/cases/4) has the same g 9.81, seed 42, duration 0.2 s, dt 0.001 s; a guest can fit
vertical acceleration from its 201 samples and recover 9.81 (pendulum trace also encodes 9.81 via its period).
(b) 9.81 is Earth g, guessable a priori. (c) Public-repo rule: `evidence/S10/acceptance/acceptance.json`,
its copy `test-data/library-artifacts/objects/sha256/60e7437f97...json`, the withheld free-fall trace
`objects/sha256/b88a55d132...json` and `free-fall.json` (contains 9.81) are committed and become public at
submission. Guest API enforcement is correct, but "answer withheld" is not true against a guest who reads
the repo or fits a sibling trace. Fix (smallest): either relabel the library card honestly (e.g. "teaser; reference
case uses standard Earth g — real blind challenge is the /lab server-owned Mystery-g") and drop
"answer withheld" wording, or source the challenge from a non-public, server-owned randomized g in /lab only.
Do not claim blind-challenge secrecy from this record.

**P3 — Per-request full revalidation.** Every `/artifacts/{id}` call reruns `load_guest()` (all catalogue
validation + sha256 of every artifact, incl. trace custody/producer hashes). Correct for revocation by design
(documented), but O(library) work per unauthenticated request; add a cheap mtime/sha memo or rate limit before
public exposure.

**P3 — `ARTIFACT_BYTES` = 64 MiB on guest projection** (`require(len(data) <= ARTIFACT_BYTES)`); traces are
separately bounded to 256 KiB in `load_trace`, and challenge payload is 141 B, so practical risk is nil today;
tighten to MANIFEST_BYTES for guest objects if new kinds are added.

## Checks passed (no change needed)
- Path traversal / ids: artifact route requires `^[a-f0-9]{64}$` before any work and only dict-lookups guest
  projection hashes (no path from user input); re-verifies sha + size; `file_under` rejects `\\`, `:`, leading `/`,
  empty/`.`/`..` segments and resolves within root; catalogue names fixed (CATALOGUES tuple).
- Size bounds: manifest <= 256 KiB enforced; `bounded()` reads limit+1; trace/setup/acceptance read with 256 KiB cap.
- Honesty labels: synthetic -> SIMULATED, else SCALE_UNVERIFIED; unavailable cases -> UNAVAILABLE with reason;
  scale_verified/scale_label/gates/limitations copied from accepted catalogue; trace regenerated-hash difference
  appended as limitation; scenes stay UNAVAILABLE (no PLY bytes).
- Numbers trace to accepted records: trace kind/dt/sample count rechecked vs acceptance record; accepted traceHash
  custody matched; challenge numbers allowlisted (`challenge_payload`) and pointer-sourced.
- No GPU/API/network on guest paths: guest.py imports only fastapi/hashlib/json/re + local modules;
  `subprocess node generate-trace.mjs` exists only in `playable.generate()` (build-time), not in `load_trace`/guest.
  rg for fetch/requests/urllib/modal/openai/torch/cuda/os.environ in the six files: none.
- Cache headers: manifest no-store; artifacts immutable by content hash; nosniff everywhere.

Not checked: deployed web route/UI (Build/web) rendering of these labels; /lab Mystery-g server internals;
loader.mjs runtime in a browser (covered only by existing node tests in the suite).

