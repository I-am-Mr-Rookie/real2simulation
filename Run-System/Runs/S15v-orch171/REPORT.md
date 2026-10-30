# S15v-orch171 REPORT — DONE

Lane CLAUDE; model anthropic/claude-opus-5-5 high; coding quota OpenCodex-managed, not polled. UTC 2026-10-30T23:40:59Z – 2026-10-30T23:51:46+00:00. Tokens/cost: unobservable. No GPU/Modal/Meta/AWS call, no video read or upload, no secrets.
Branch run/S15v-orch171, code commit **d195f270e74af29f817835130d0eeac7946245f9** (rebased on main daffaee2); this PLAN/REPORT commit follows. Not merged to main (controller acceptance).

## What changed
- `Build/api/workspace/jobs.py`: `owner_clips()` = clips.csv rows with status OWNER_RECORDED + owner_approved PRIVATE_PROCESSING_ONLY + file_fps 30/1, hashes from tracked `owner_clips.json`; merged into `approved_shas()` so the existing upload allowlist accepts OWN01–OWN12 by checksum (same 422 for anything else). On upload complete, owner clips get `provenance.measurement` from `owner_measurement()`: OWN01 → status recorded, label "RECORDED replay of a MEASURED result", g 10.96 ± 0.77 m/s^2, source `evidence/S07/S07i/result-own01.json` (+sha256), measured_label verbatim from S07i, caveat "Held-out prediction FAILS (RMSE 23.0 px >> 2 px): a MEASURED value with a failed held-out check, not a validated measurement."; other owner clips → status abstain, "UNCERTAIN: no measurement … (abstain, not an error)". Both carry input_label "OWNER_RECORDED / RECORDED" and scale {book cover edge, 0.2028 m, "user-declared, not verified"}.
- `Build/api/workspace/owner_clips.json` (new): tracked copy of OWN01–OWN12 sha256/fps/size from `evidence/S07/S07g/clips-sha256.json` + the S07i OWN01 result summary. Needed because the API image (stage.py, outside Owns) ships `Build/` but not `evidence/S07`. A test re-derives every value from the evidence files (drift fails the suite).
- `Build/api/workspace/analysis.py`: `/questions` appends one free-text `known_size` question (digit-free prompt; only when < 3 questions, web limit). `/spec` strips the known_size answer before answers_to_spec and returns `user_scale` = {declared, object, length_m, label "user-declared, not verified"} or {abstain, "UNCERTAIN: no usable known size; metric scale unknown"} — never a 422.
- Web: `controller.mjs` joins user_scale into the existing verbatim specLabel (already shown through run/fit/report); `view.mjs` renderProvenance renders the measurement block (g ± u, labels, source, caveat or abstain message, scale label). Text only.

## Checks (fresh, after rebase)
- `python -B -m unittest discover -s tests/api-workspace -t tests/api-workspace` → 23 OK (3 new: owner clip recorded/abstain via route + GET persistence; owner_clips.json == S07g/S07i evidence and approved_shas contains OWN01; known_size declared/abstain/absent).
- `node --test tests/workspace tests/shell-workspace tests/web-private tests/web-workspace-api` → 119/119 pass (2 new in spec-body.test.mjs). node_modules junction to canonical created, removed afterwards (canonical intact).
- `npm run build` (Build/web) → exit 0.

## Deploy (Railway DEV)
- `python infra/railway/dev/stage.py api %TEMP%\s15v-api-orch171` → 88 files (owner_clips.json included); `stage.py web %TEMP%\s15v-web-orch171` → 111 files; both source_revision d195f270…; `railway up --detach` with project b07b0d66 / env c5823a28 / service ids.
- api deployment **85c23646-2e35-4c25-af0d-cbe38a52c524** SUCCESS (previous 81a74b99 REMOVED); /health/live, /health/ready (postgres/redis/bucket ok), /api/version → 200, revision d195f270e74af29f817835130d0eeac7946245f9; /internal/workspace/jobs/… → 401 without token.
- web deployment **20e728a2-e0f5-45f1-90b8-4734d2e00bfb** SUCCESS (previous 1f827ca0 REMOVED); https://web-dev-cd80.up.railway.app/ → 200.
- For controller (deployments.json not edited):
  - api {deploymentId 85c23646-2e35-4c25-af0d-cbe38a52c524, previousDeploymentId 81a74b99-ef55-4f69-8459-384ff306b390, sourceRevision d195f270e74af29f817835130d0eeac7946245f9} — update verify.py pin.
  - web {deploymentId 20e728a2-e0f5-45f1-90b8-4734d2e00bfb, previousDeploymentId 1f827ca0-2cf6-4ace-99ac-f9f9f6e689ee, sourceRevision d195f270e74af29f817835130d0eeac7946245f9}.

## Ponytail (full) applied
Reuse: existing approved_shas allowlist/UploadService/422 path, provenance channel (complete → store → GET job → renderProvenance), specLabel channel through run/fit/report, test harness finish()/walk(). Smallest: one tracked JSON instead of editing stage.py (outside Owns); user_scale as a sibling of the validated spec rather than a new spec key (would need Build/agent + contracts validator changes, outside Owns). No new deps, no runtime tracking, no new endpoints.
Skipped: Build/pipeline, PrivateWorkspace.mjs, tests/pipeline, tests/shell-workspace (no change needed); rm04-questions.json fixture not regenerated (pins Build.agent output, unchanged).

## Limits / risks
- Owner-clip jobs still end failed DEPENDENCY_UNAVAILABLE at validate (no in-product tracking; honest — stages did not run); the result shows beside it as the measurement block. The interview (and so known_size) is reachable only for scenes with a recorded understanding (RM04 today), not for owner-clip jobs; owner clips carry the clips.csv book-edge scale labelled user-declared instead.
- user_scale is returned alongside the spec and in the label; the validated spec object itself is unchanged (not used as a fitter scale).
- OWN02–OWN12 abstain until a measured result is added to owner_clips.json (and its evidence test).
- Live signed-in walk with an owner clip upload not done (controller's job); only health/version/401/200 probes verified.

Communication: silent; one completion message to controller only.
