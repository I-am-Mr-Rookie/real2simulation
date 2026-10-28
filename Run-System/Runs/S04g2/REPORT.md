# S04g2 — DONE (local staging safety)

Replaced optimization-removable safety assertions with runtime exceptions and
exclusively claims a fresh destination after validating all selected paths.
Existing files/directories and concurrent creators cannot be overwritten by this
stager. No deployment/upload, credentials, model job or paid operation.

## Scope / authority / checks

Routine reversible CODEX-2 follow-up to F-CODEX-2-2's reproduced P2 within the
owner's direct sole-worker authorization until16:30Z. Requested managed Sol/medium;
actual backend/effort/tokens/coding cost unavailable; OpenCodex-managed; not polled.
Same existing project/chat, no fanout. Branch run/S04g2, base2124001, canonical
claim bc77084. Owns stage.py/test_stage.py/README.md, this run/evidence and serialized
controls only. Full timebox16:15:28–16:45:28Z; earlier owner stop16:30Z controls.

1. Red stage suite5 tests:9 subcase failures/3 errors before fix, red-stage.txt.
   Invalid service, existing destination, missing committed inputs and forbidden
   selected path guards failed in optimized mode; some normal paths raised only
   AssertionError. No real user data involved.
2. Existing Git committed-source/service allowlists, source revision, Dockerfile
   ARG stamping and SHA256 manifests retained. Explicit ValueError/FileExistsError
   replaces four assertions; prevalidate paths, then target.mkdir(exist_ok=False)
   closes the creation race. Partial failed contexts are retained, not deleted or
   silently retried into existing directories. Caller command unchanged.
3. Fresh full staging+verifier14/14 PASS on default3.14.5, actual optimized default
   process, and target3.11.15, each30s parent cap. checks.json records commands and
   normalized source hashes; *-final.txt logs. Tests cover directory/file refusal,
   concurrent creator, missing inputs, forbidden paths and all3 service manifests.
4. Real Git local staging (actual `python -O stage.py`) succeeds for web42/api9/
   worker6 committed files, hashes checked, then rejects every same-path retry
   without Dockerfile mutation. All outputs in verified temporary directory,
   removed by its standard-library owner; only sanitized counts/SHAs saved in
   real-git-staging.json. No context uploaded. Revision2124001 is the actual
   pre-fix source HEAD used for staged application bytes, not claimed deployment.

## Ponytail / limits

Applied installed Ponytail full/default: repaired root safety seam in existing
35-line script, no framework/dependency/config flag; reused standard library and
actual script compiled in both modes with synthetic Git. No application refactor,
provider/auth/settings change or speculative feature. Historical filler stager
reproduction is frozen evidence for its baseline and intentionally expects old
failure; use new test_stage.py for current regression, not that historical oracle.

No fsync/crash durability, malicious concurrent filesystem writer protection,
dependency/image locking, live health/auth/deployment, billing or physical proof.
The global health environment still lacks typing_extensions; no installation or
unrelated repair. Existing$2.85/$30/gates/S12 remain unchanged. No fixed timer or
background continuation. Mandatory changed-finding update only; no other narration.
Final rebase/FF/source audit/timing receipt recorded at canonical closeout below.

## Canonical acceptance

Verified FF9e3bf48; fresh main optimized staging/verifier14/14 PASS and normalized
source hashes match tested worktree. Source-only diff whitespace check PASS.
Raw red unittest log contains four trailing-space lines; an all-evidence diff
check reported those, not a clean result. Raw failure evidence retained verbatim.
Work stopped16:20:02Z; all local acceptance complete, report/control bookkeeping
afterward. TIMEBOX checker required before closure. Queue now57/204: two leaf
closures this session plus one justified new safety-fix leaf; recovery10 remains
a supporting child, not a fabricated leaf or parent S05b completion.
