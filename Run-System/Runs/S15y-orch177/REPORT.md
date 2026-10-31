# S15y-orch177 REPORT — DONE
Lane CLAUDE; anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97. UTC start 2026-10-31T00:02:38Z, end 2026-10-31T00:13:20+00:00. Branch run/S15y-orch177; code commit 6b9e16d9 (rebased on main e8d329fe).

## Change
- Root cause: `complete` ran the S13h recorded replay for owner clips, which has no recording -> validate failed DEPENDENCY_UNAVAILABLE -> web `upload.failed`.
- `Build/api/workspace/jobs.py`: owner clip (owners() hit) skips the runner; provenance executor `none`, label `no scene: owner clip, scene reconstruction not run`, stored measurement (S15v owner_measurement). Job = `{job_id, status: no_scene, label}` (deliberately not the shell job DTO: no fake scene/stage events). GET /jobs returns the same for polling. `scene_resolver` returns `({owner_clip: measurement}, None, None)` for those jobs (app.py wiring outside Owns, so no new router param). Caveat now: "held-out RMSE 23.0 px exceeds the 6 px pass threshold (S07h: 3 x the declared 2 px)".
- `analysis.py`: owner-clip scene -> questions = [KNOWN_SIZE] only (scene-free; drop height omitted = optional); spec -> `{ok, owner_clip, measurement, user_scale}`; missing/unparseable size -> abstain, never 422.
- Web: workflow edges `OWNER_CLIP` (upload.idle/failed/cancelled -> interview.active, scene null, owner.jobId) and `OWNER_RESULT` (-> new phase `report.owner`); controller skips polling on `no_scene`, uses owner.jobId for questions/spec, puts measurement+user_scale in provenance; view renders the result card in the stage panel at `report.owner` (+ "Your known size" line); layout labels owner interview "no scene (reconstruction not run)" and marks Run/Fit "(not run)"/skipped; PrivateWorkspace sceneId fallback and SIMULATED note no longer shown on report.owner. README graph/states/events updated.
- Licensed RM04 path untouched (same recorded_runner branch); its tests unchanged and green.

## Ponytail (full) applied
Reuse: S15v owner_clips/owner_measurement/user_scale/KNOWN_SIZE, existing provenance channel and renderMeasurement, scene_resolver injection point, interview reducer unchanged. Smallest: no contract/schema change (owner job is a separate tiny dict, not a new shell job status), no new endpoint, no app.py edit, no new deps. Skipped: drop-height question (optional per task), Run/Fit for owner clips, in-product tracking.

## Checks (fresh, after rebase)
- `node --test tests/workspace/*.test.mjs tests/shell-workspace/*.test.mjs tests/web-private/*.test.mjs tests/web-workspace-api/*.test.mjs` -> 121 pass / 0 fail (new tests/workspace/owner-clip.test.mjs: OWN01 upload -> interview.active, no /jobs poll, known_size only, body {known_size:{text}}, report.owner panel shows g = 10.96 ± 0.77, 6 px caveat, user scale; no "Upload failed|DEPENDENCY_UNAVAILABLE|needs attention|Start a new upload"; OWN02 abstain + size abstain). workflow.test updated for the new phase/events.
- `python -B -m unittest discover -s tests/api-workspace -t tests/api-workspace` -> 24 OK (new test_owner_clip_no_scene_job_then_known_size_interview_then_result incl. owner scoping 404s; caveat wording asserted; RM04 tests unchanged).
- `npm run build` (Build/web, node_modules junction to canonical, removed afterwards) -> exit 0.
- DEV deploy: see evidence/S15y/DEPLOY.md (api 88eb14d1 / web 75dcb815 SUCCESS, revision 6b9e16d9; health 200; internal 401 unauthenticated).

## Files
Build/api/workspace/{jobs.py,analysis.py}; Build/web/src/workspace/{workflow.mjs,layout.mjs,controller.mjs,view.mjs,README.md}; Build/web/src/shell/PrivateWorkspace.mjs; tests/api-workspace/test_jobs.py; tests/workspace/{owner-clip.test.mjs,workflow.test.mjs}; evidence/S15y/DEPLOY.md; Run-System/Runs/S15y-orch177/{PLAN.md,TIMEBOX.json,REPORT.md}.

## Limits / risks
- Live signed-in OWN01/OWN02 browser walk on DEV not done by this worker (controller's job). Unit tests mock fetch; API tests use the real routers.
- Owner-clip result is the stored S07i value (RECORDED replay of MEASURED) or abstain; no tracking runs. The declared known size is echoed, not used to recompute g.
- Stage strip shows Run/Fit "(not run)"; the Report step hosts the owner result.
- Controller must update deployments.json + verify.py pin (not edited here). Staged dirs left in %TEMP% (s15y-*-orch177).
- Communication: silent; one completion line to controller. Costs: Railway dev builds only; no GPU/Meta/paid calls, no secrets read.
