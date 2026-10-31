# S13j-orch213 REPORT: PARTIAL

- Lane CODEX-1; model anthropic/claude-opus-5-5/high (coding quota: OpenCodex-managed; not polled). Tokens unknown (not observable). GPU/API spend $0 (refused before dispatch).
- UTC: issued 2026-10-31T13:53:31Z; worker start 13:57:46Z; work stopped 14:23:31Z (deadline). Base main 061484b; branch run/S13j-orch213; worktree .worktrees/S13j-orch213; project 91e441f8-e40c-4ec4-bea2-de7fa1582d97.

## What happened
1. Guardrail call, not bypassed: `python -B -m Build.pipeline.gpu_stages RM04 <.worktrees/S05c-orch19/evidence/S05/S05c/input.json> evidence/S13j/reconstruct evidence/S13j/gpu-ledger.jsonl` (manifest sha256 b3fe96a5..., same as S13h; frames exist only in that S05c worktree). gpu_stages.reserve -> reserve_gpu -> `SPEND_PAUSED retryable=False: GPU job count or all-in reservation cap reached` at 14:01:01Z. No ledger row, no Modal call, no container; billed $0 vs reserved $0.
2. Cause (read-only, evidence/S13j/admission-preflight.json): 3 unsettled Modal reservations in canonical evidence/S20/runtime/reservations.json, $1.40 liability; gpu_stages MAX_JOBS=2, CAP_USD=$1.0.
3. Nonterminal blocker sent to controller 14:01Z. Controller decision 14:02Z: no GPU dispatch this run even if settled (DEV cannot display bytes); write the plan below; finish PARTIAL at deadline.
4. No Build/pipeline/recorded/ manifest written: no bytes exist to describe (a manifest without bytes would be fake). No DEV browser check (nothing to show; viewer path not wired).

## Plan 1: settle the 3 open reservations (operator/controller action, outside S13j Owns)
| request_id (canonical journal) | app (evidence/S07/S07j/ENVELOPE-2.md, S07j/RETRACK-RUN.md) | reserved |
|---|---|---|
| evidence/S20/runtime/standalone-gpu-ledger.jsonl:segment:modal-track:OWN01:24e8a04900af4ad49611ad152039ba07 | ap-9SEBfxKkipzckSWGcQRGvt | $0.60 |
| evidence/S20/runtime/standalone-gpu-ledger.jsonl:segment:modal-track:batch:OWN02,OWN03,OWN04,OWN05,OWN06,OWN07,OWN08,OWN09,OWN10,OWN11:004ccb39a68e4e86bcce42e10b61c5d2 | ap-7qnUtLNN8xQy534jpuXcQs | $0.40 |
| evidence/S20/runtime/standalone-gpu-ledger-2.jsonl:segment:modal-track:batch:OWN07,OWN08,OWN09,OWN10,OWN11:5626a16bf9844ea58231a3b666e21d22 | ap-HTu3CU7IfNE1A9Q6T9EyvL | $0.40 |

Per request (Build/guardrails/settlement.py final_amount/settle_gpu), all files inside the repo:
- MEASURED per-app billed (read-only `modal billing report --start 2026-10-30 --end 2026-10-31 -r h --json --show-resources`, read 14:06Z, saved evidence/S13j/modal-billing-report-2026-10-30_31.json, sha256 f25008b7...; all rows interval 2026-10-30T23:00, env main, 4 rows each: A10G, CPU, Memory, Network Egress; Oct 31 query returned 0 rows): OWN01 ap-9SEBfxKkipzckSWGcQRGvt $0.022284; batch1 ap-7qnUtLNN8xQy534jpuXcQs $0.101925; batch2 ap-HTu3CU7IfNE1A9Q6T9EyvL $0.035123; sum $0.159332 vs $1.40 reserved. This file can be the billing_report source (copy into main before settling; sha256 must match the receipt). Cross-check: ENVELOPE-2 $0.78 before + $0.159 = ~$0.94 vs owner page $0.93 (dashboard rounding/read-time difference; not reconciled further).
- billing_report JSON: rows from read-only `modal billing report --for 2026-10-30 -r h --json --show-resources` (pattern: Build/gpu/cost_log.py; shape seen in evidence/S13/S13h/live/billing-post.json: object_id, cost, resource, environment, interval_start, description). Needs >=1 row with object_id == app_id, no duplicate (environment, interval_start, resource).
- scene_log JSON: {app_id, cost: {billed: {status: "billed", total_usd: exact sum of that app's rows}}}.
- receipt (schema "modal-settlement/1"): request_id, status "completed", containers [] (no live container for the app), billing_final_verified true, reviewed_by (non-empty), app_id "ap-...", completed_at, billing_read_at (reserved utc <= completed_at <= billing_read_at <= now), scene_log + scene_log_sha256, billing_report + billing_report_sha256.
- Run: `python -m Build.guardrails.settlement "<request_id>" <absolute receipt path>` (main checkout; one atomic journal write).
- Owner's Modal page ($0.93 used Oct 1-31 in total; ENVELOPE-2 read $0.78 before these jobs) is only an aggregate cross-check (~$0.15 for all three). It is NOT per-app billing and cannot be a settlement receipt.
- VERIFIED gap (14:06Z, read-only reservations.project on main): all 3 projected requests have app_id None, app_ids None, billed None. settle_gpu would therefore fail "Billing needs one explicitly bound single-app reservation". First step: append one result event per request to its standalone ledger (append-only, old rows untouched), e.g. `{"provider": "Modal", "request_id": "<full request_id>", "app_id": "ap-..."}` (project_ledger matches by request_id and records app_id); re-run project to confirm one bound app each, then write receipts and settle. This is a canonical runtime write: controller decision, not done here.

## Plan 2: smallest wiring to show RM04 geometry on DEV
Root cause of LOAD_FAILED today: Build/web/src/shell/PrivateWorkspace.mjs (line 158) passes no `loadScene` to Workspace, so the viewer adapter fails before any fetch. Even with bytes, there is no API route serving bundle bytes, DEV has no bucket service (infra/railway/dev/resources.json: Postgres, Redis, api, worker, web; only Postgres/Redis have volumes) and .env has no BUCKET_* keys.

Bytes (from S13h scene.json; re-capture sizes/shas will differ): scene.json 3,395 B + points.ply 752,022 B + points-mobile.ply 188,109 B = ~0.94 MB, 20,000 points (viewer limit 2,000,000). GPU: S13h reconstruct estimated $0.0125 (estimate, not billed); reserve $0.50 via gpu_stages.reserve after Plan 1.

Storage (no new paid service):
- A (zero infra, needs owner licence decision): commit the derived bundle (or points-mobile.ply only, 188 KB) under Build/api/workspace/scenes/RM04/ and bake into the API image. Blocker: S05c approval_scope says "local scene/tracking ONLY; not final/public/raw-media redistribution or third-party upload", and the repo goes public at submission. Owner must approve redistribution of RGB-coloured derived points from the Pexels clip first.
- B (private, recommended without that decision): Railway volume on the dev api service mounted at /data; env WORKSPACE_SCENE_DIR=/data/scenes/RM04 (name only). One-time transfer of the 3 files and sha256 check on the volume (mechanism unverified: e.g. `railway ssh --service api` plus base64 decode). Volume storage cost for ~1 MB is usage-based and negligible; exact rate not checked. Never a public URL.

Code (one small run, dev deploy already approved):
1. Build/api/workspace/jobs.py: `GET /scenes/{job_id}/bundle/{name}` under the existing require_owner router; job owned by caller, status ready, input sha == RM04 approved sha (existing approved_shas); name allowlist {scene.json, points.ply, points-mobile.ply}; read from WORKSPACE_SCENE_DIR; serve only if file sha256 equals the asset sha in that scene.json (and scene.json sha recorded in the new Build/pipeline/recorded/ manifest); missing env/file -> 503 DEPENDENCY_UNAVAILABLE (viewer shows unavailable, never a fake mesh); cache-control no-store.
2. BFF Build/web/src/app/api/workspace/[...path]/route.js: no change (GET proxy already forwards segments scenes/<id>/bundle/<name> and passes content-type + arrayBuffer).
3. PrivateWorkspace.mjs: `import { createArtifactLoader } from '../viewer/artifact-loader.mjs';` and module-level `` const loadScene = createArtifactLoader({ bundleUrl: (s) => new URL(`${API_BASE}/scenes/${encodeURIComponent(s.scene_id)}/bundle/`, globalThis.location.origin) }); `` then pass `loadScene` next to `adapter` at line 158 (scene_id is the job_id per jobs.shell_scene).
4. Tests: tests/api-workspace (owner 404, allowlist, sha mismatch, missing dir) + one node test that PrivateWorkspace passes loadScene. Then dev redeploy api+web, set env, iab 375px check: RM04 viewer renders with labels verbatim (scale unverified, Display only, not a measurement).

## Ponytail (full)
- Reused: existing gpu_stages CLI + reserve/reserve_gpu/require_reconstruction guard (no new launcher); S05c manifest found by sha match, not rebuilt; existing BFF proxy needs no change; existing createArtifactLoader, shell_scene ids and approved_shas in the wiring plan.
- Skipped: GPU dispatch (guard refused; controller decision); settlement (outside Owns, needs per-app billing); recorded manifest (no bytes); DEV browser check (nothing wired); any code changes outside Owns.

## Fresh checks
- Binding append simulated on a TEMP COPY of standalone-gpu-ledger.jsonl (canonical untouched, git status clean): project_ledger then binds OWN01 -> ap-9SEBfxKkipzckSWGcQRGvt and batch -> ap-7qnUtLNN8xQy534jpuXcQs (app_ids None). Settlement itself not run.
- reserve refusal reproduced from code path (reconstruct-cli.txt); journal snapshot sha256 8eeceb14f358... recorded; `python Run-System/worker_timebox.py check Run-System/Runs/S13j-orch213/TIMEBOX.json` (see commit).

## Risks
- Re-captured MapAnything bytes may not match S13h shas; record new shas, do not reuse old ones.
- Settlement needs the app-binding append above first; event field handling past app_id (e.g. whether a bare result event without other fields is accepted) not exercised. Plan 2 option B transfer mechanism unverified.

## Communication
One nonterminal blocker message and one completion line to controller chat 01a1882d-3481-7ce3-8f88-45c942e341cd (owner-authorized). No owner questions; option A licence decision is for the controller to raise.

