# S13m-orch221 REPORT — DONE

Lane CLAUDE, anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). UTC 14:43:42 -> 14:51:30. Branch run/S13m-orch221
from main e1a76ce6. No deploy, no GPU, no spend; bytes stay local (gitignored), nothing uploaded.

## What changed
- Build/api/workspace/jobs.py: GET /internal/workspace/scenes/{job_id}/bundle/{name} on the existing require_owner router.
  404 unless the caller owns the job, executor is recorded, approved_shas maps the input to RM04 and job status is ready;
  name allowlist {scene.json, points.ply, points-mobile.ply}. Reads WORKSPACE_SCENE_DIR, default ROOT/evidence/S13l/reconstruct/bundle
  (the path stage.py bakes); missing/unreadable -> 503 DEPENDENCY_UNAVAILABLE; serves only if sha256 == Build/pipeline/recorded/
  RM04-S13l-mapanything.json, else 503. cache-control no-store; header x-r2s-source-sha256.
- **Deviation from Plan 2 (found while wiring):** artifact-loader checkManifest requires manifest id == sceneRef.scene_id; scene_id
  is the job id (shell_scene) but scene.json id is rm04-mapanything-s06d, so the viewer would fail 'scene id does not match the
  request'. Fix: after the sha check the API serves scene.json with only 'id' re-bound to the job id (asset shas unchanged, so ply
  bytes are still client-verified). Served scene.json bytes therefore differ from c8574afb...; the header carries the verified source sha.
- Build/web/src/shell/PrivateWorkspace.mjs: loadScene = createArtifactLoader({bundleUrl: API_BASE/scenes/<scene_id>/bundle/})
  passed to Workspace; visible note when live: "Scene geometry: Display only, scale unverified, not a measurement."
- infra/railway/dev/stage.py: api context bakes evidence/S13l/reconstruct/bundle/{3 files} from the local repo root only when
  present AND sha-equal to the committed manifest (mismatch raises before any write); listed in context-manifest.json.
- BFF Build/web/src/app/api/workspace/[...path]/route.js: verified, no change (GET forwards segments, content-type, arrayBuffer, no-store).

## Fresh checks
- python -m unittest tests.api-workspace.test_jobs: 14 OK (new test: ready RM04 job 200 + no-store + id bound; other owner 404;
  allowlist 404 for npz/scene-log/SCENE.JSON; traversal 404; sha mismatch 503; missing dir 503; non-RM04 input 404).
- python -m unittest infra/railway/dev/test_stage.py: 9 OK (new: bakes only sha-verified present files; mismatch raises, no dest).
- node --test tests/workspace, tests/web-private, tests/web-workspace-api (*.test.mjs globs; bare dir form fails on node 24 here): 147 pass;
  tests/shell-workspace: 28 pass. New tests/web-private/scene-bundle.test.mjs: loadScene fetches /api/workspace/scenes/<job>/bundle/scene.json and is passed to Workspace.
- npm run build (Build/web): exit 0.
- Staged-API probe evidence/S13m/staged_probe.py -> evidence/S13m/staged-probe.json ok=true: stage.py api at dbe5d88c into %TEMP%,
  app imported from the stage, real RM04 clip (8231fbca...) uploaded with synthetic owner/token, job ready; points.ply and
  points-mobile.ply body sha == manifest; scene.json == verified file with id re-bound; other owner 404; missing dir 503.
- evidence/S13m/loader_probe.mjs -> loader-probe.txt: real createArtifactLoader accepts the served bundle (20000 points).

## Ponytail (full)
- Reused: owned()/require_owner/error, approved_shas, JobRunner.progress + shell_scene for readiness, recorded manifest as sha
  source, existing createArtifactLoader, existing BFF unchanged, stage.py manifest pattern, existing test setUp/finish helpers.
- Smallest: one route + 3 constants; one loader + one note in the shell; ~12 lines in stage.py. No new deps/options.
- Skipped: deploy and DEV viewer check (controller), Railway env WORKSPACE_SCENE_DIR (baked default suffices), mobile LOD selection (loader fetches main asset only), .npz.

## Risks / controller notes
- Deploy: run stage.py api from the CANONICAL checkout where the gitignored bundle exists; confirm context-manifest.json lists the 3
  evidence/S13l/reconstruct/bundle files, else DEV answers 503 (viewer unavailable, by design).
- API image now carries ~0.94 MB derived RGB points from the Pexels clip on private DEV only; never public (repo/judging scope unchanged).
- Only jobs whose input sha maps to clip_id RM04 get the bundle; other clips stay 404.
- Local web tests need Build/web/node_modules (junction to canonical, gitignored) in the worktree.

## Communication
One completion line to controller chat 01a1882d-3481-7ce3-8f88-45c942e341cd (owner-authorized).
