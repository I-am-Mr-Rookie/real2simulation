# S05a — DONE

## Objective and routing

Review reconstruction code/weight licences; freeze a scene artifact and synthetic
fixture for downstream work. Owner authorized this manual run explicitly.
Lane CODEX-1; planned GPT-6.1 Sol / medium; actual manual Codex chat, exact runtime
model/effort not exposed. No provider, credentials or settings changed.

- Claim/start UTC: 2026-10-27T17:15:47Z; preflight preceded claim.
- Implementation/final product verification end UTC: 2026-10-27T17:25:13Z.
- Main before claim: 32539dbe2cb8da8c5fd03488d06b7872ba63af1e.
- Merged task SHA: b32fc267a65f8fa8915b7e36bbc9e2f47ea0d482, `run/S05a` -> `main`, fast-forward only.
- Concurrent main commit `1c0c749` claimed CODEX-2 S02a. Initial fast-forward
  correctly refused divergence; rebased onto main, reran checks, then fast-forwarded.
  S02a work/status and all four unrelated untracked research/concept paths preserved.

## Changes (20 task-owned files)

- `Build/reconstruction/spike/README.md`: Apache-only candidate and spike boundary.
- `contracts/scene/`: JSON Schema2020-12 v1.0.0, integration/coordinate/codec docs,
  offline structural/semantic/integrity validator, pinned existing jsonschema4.23.0,
  11 tests, local LF attributes. No shared/web manifest changed or install performed.
- `test-data/synthetic/scene/`: original 8-point PLY scene, surfaces/box colliders,
  camera path, labels, explicit unknown gravity and synthetic warning; binary-byte
  preservation for PLY avoids checkout hash drift. Not model/fitter/simulator output.
- `evidence/S05/`: licence decision, reproducible public text capture, immutable
  code/weight revisions, five licence/model-card/README snapshots with source and
  saved hashes. Upstream trailing whitespace normalized only; wording unchanged.
- Serialized main updates: QUEUE/RUNS, STATE, DECISIONS_LOG, API_BUDGET, RUN_LOG,
  and this run's PLAN/REPORT receipts.

## Commands and actual results

| Command/check | Result |
|---|---|
| `python evidence/S05/capture_licenses.py` | Exit0; 5 immutable public snapshots, no weights/auth/inference |
| Public GitHub/HF revision/model metadata reads | Exact revisions recorded; Apache weights ungated; SAM weights manually gated |
| Standalone Apache weight `/LICENSE` read | HTTP404; documented; official model-card declaration is the weight evidence |
| `python -m unittest discover -s contracts/scene -p 'test_*.py' -v` | Exit0, 11 tests PASS, rerun after final rebase (11.896s) |
| `python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json` | Exit0, PASS; rerun on freshly checked-out main after merge |
| Five saved snapshot SHA256/byte-length assertions | Exit0, all5 PASS on fresh main |
| `git diff main...HEAD --check` after rebase | Exit0 |
| `git rebase main`; `git merge --ff-only run/S05a` | Successful after concurrent S02a claim; no conflict/no merge commit |

Negative coverage includes incompatible version/axes, unknown/zero scale, unknown
gravity pretending known, non-unit vectors/quaternions, non-finite values, duplicate
keys/IDs, unsafe paths, missing references/assets, asset size/hash tampering, malformed
PLY/count/colour/bounds, camera ordering, NC checkpoint identity and NC media licence.
One initial shell quoting error during evidence recapture was replaced by the
checked-in capture script. Initial upstream trailing-whitespace check failed;
normalization plus raw/saved hashes fixed it without relaxing whitespace checks.

## Licence result and limitations

Select **facebook/map-anything-apache** (Apache-2.0 code + declared Apache weights),
not the default NC checkpoint. Retain notices and audit actual dependencies before
installation/packaging. SAM 3D is custom licensed and gated: deferred pending owner
authorization/acceptance/access, not silently approved or used. See LICENSE_REVIEW.

S05a acceptance is satisfied; **S05 as a whole is not DONE**. Gate R and all runtime,
VRAM, metric accuracy, gravity/physics, browser/viewer and production performance
checks are NOT RUN. GLB/splat payload decoding is not validated here. Source metadata
fields do not authenticate real clip licences/owner approval; S02 remains mandatory.
No runtime resource/upload security gate or full dependency/legal audit is claimed.
Other-vendor Gate R review remains scheduled; no gate was passed on this fixture.

## Budget and next

- Meta/service inference/GPU calls: none; $0 spend in this run. Historical balance unknown.
- Tokens, task dollar cost, exact runtime model/effort and Claude quota: unavailable.
- Codex shared account before/after: used67%5h /49%weekly, remaining33% /51%; primary
  reset1793132283. Rounded snapshots include shared activity; no attributable task delta.
- No AWS, deployments, media/weight downloads, legal acceptance, accounts, remote,
  publication, personal files, archive imports or secrets read/copied.
- Next ready CODEX-1 run: **S08a**, Codex Sol medium. S05b/S07a wait for **all S02 DONE**,
  including approved clips. CODEX-2 S02a is already active; do not double-start it.
- No owner question needed for S05a; SAM is optional and deferred reversibly.
