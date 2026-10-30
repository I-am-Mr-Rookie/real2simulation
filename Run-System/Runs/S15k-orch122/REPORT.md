# S15k-orch122 REPORT
Lane CLAUDE; anthropic/claude-sonnet-5-5/high (OpenCodex-managed; not polled). Branch run/S15k-orch122.
Windows: ORIGINAL issue 2026-10-30T09:37:43Z, deadline 10:07:43Z (lapsed; worker stalled on the Claude 5h quota after finishing the first walk at ~09:48Z). RESUME (controller receipt): resume_issued_at 2026-10-30T10:53:46Z, resume_deadline_at 2026-10-30T11:23:46Z, cutoff 11:18:46Z. Branch fast-forwarded to main 67e299a at resume.
**Status: PARTIAL** — deploy + auth + private-route boundaries verified live on BOTH deployments; upload, interview, run, fit, report are NOT-WIRED in the deployed app, so "Upload, interview, run, fit and report complete in browser" is NOT met.

## Resume re-walk (main 67e299a, includes S04i + S09k + S18k; excludes S04j)
Redeployed web only: deployment da4b03e9-659e-4966-8f12-8003199f7be5 SUCCESS 10:59:26Z (prev e4cc427a). Same results: signed-in own fixture workspace PASS (user menu shows Koushik Sadhak; 0 buttons/inputs; "No uploads are enabled"); other-scene and garbage ids 404; logged-out 404 (0.25-0.30 s, no hang); /, /library, /lab, /sign-in 200; /library still EMPTY/NOT CONNECTED (S04j not merged); 375px scrollWidth 375 for workspace/library/lab; tests/workspace 79 pass; verify.py 9/10 (stale text only). Nothing new is wired: PrivateWorkspace.mjs is unchanged by S09k/S18k, so no stage beyond Upload is reachable. In-app browser CDP was intermittently timing out (details in evidence JSON).

## Deploy (approved dev web only)
stage.py web (98 files, rev 27a1197) + `railway up` to web service; deployment e4cc427a-6b36-49c2-b269-278d90c42b8e SUCCESS 09:40:58Z (previous 61d3a805 REMOVED). No new services/variables/credentials; no prod/judging. Receipt: infra/railway/dev/deployments.json (IDs only). Logs: start, Ready in 291ms, Clerk telemetry notice only.

## Loopback finding (S04i handoff)
NOT reproduced on Railway: server binds `--hostname 0.0.0.0`; signed-in `/workspace` redirected to own fixture scene without hang; logged-out `/workspace/x` 404 in 0.36 s; no localhost self-request errors in deploy logs. (HTTP-level proof only; no Clerk-side config touched.)

## Per-stage results (in-app browser, https://web-dev-cd80.up.railway.app; details evidence/S15/s15k-orch122.json, shots evidence/S15/s15k-orch122/*.png)
| Stage | Result | Evidence |
|---|---|---|
| Deploy | PASS | above |
| Sign-in (/sign-in) | PASS | Clerk form had browser-saved credentials prefilled; I pressed Continue only (no typing, no auth changes) -> signed in, avatar menu visible |
| /workspace -> own fixture | PASS | /workspace/dev-fixture-cffb56aa…3e715; "FIXTURE / SYNTHETIC — empty private development scene"; rail Upload/Interview/Run/Fit/Report; viewport EMPTY · NO SCENE (workspace-desktop.png) |
| Logged-out access | PASS | curl /workspace, /workspace/x, own URL: 404 |
| Other-scene access | PASS | signed-in dev-fixture-000…0, not-a-scene, ..%2Flibrary: "Page unavailable", no private content (other-scene-404.png) |
| /library, /lab, /, /sign-in | PASS | 200, unchanged; `/api/health`,`/health/live` 404 on web (not web routes; API/worker health via verify.py) |
| 375px | PASS | workspace/library/lab scrollWidth 375 = no horizontal scroll (*-375.png); desktop shots too |
| Upload | NOT-WIRED | no file input or button anywhere; banner "No uploads are enabled" |
| Interview | NOT-WIRED | rail items are plain `<li data-status=todo>`; no interview props/actions |
| Run | NOT-WIRED | no run props; Railway has no Python/simulator bridge (/lab Run trial = local_lab_disabled) |
| Fit | NOT-WIRED | no fit props/endpoint |
| Report | NOT-WIRED | no report props/endpoint |

## Exact missing wiring (not faked; no fixture stages injected)
1. `Build/web/src/shell/PrivateWorkspace.mjs` renders `<Workspace state adapter audience>` only. `createWorkspace` already accepts onAction, interview, template, run, instruments, fit, report, navigate, loadScene, but nothing supplies them. Needed: a client controller holding `workflow.mjs` reduce() state and supplying those props (shell/app = S04 lane, outside this run's Owns; the controller itself could live in Build/web/src/workspace/ = S15 lane).
2. Upload: no browser upload UI and no web->pipeline HTTP route (Build/pipeline S13a-h exist; S13g "stream job progress" has no web endpoint). Owner: new S04-lane route under Build/web/src/app/api/ + S15 upload control; private scene storage replacing the empty read-only fixture (auth/dev-scenes.mjs shortcut).
3. Interview: S14 agent is Python/provider-bound; no web route. Owner: S14/S04 bridge.
4. Run/fit: simulator JS modules are staged, but no workspace->simulator/fit wiring; fitter is Python (Build/fitter) with no Railway runtime (S04/S19 lane).
5. Report: Build/reports is Python; no web route.
Smallest honest next step: one S04 row that gives PrivateWorkspace a controller + a single guest-safe local-only upload-to-state path, then S15k re-walk.

## Checks
- `node --test` on tests/workspace/*.test.mjs: 79 pass, 0 fail (fresh).
- `python infra/railway/dev/verify.py`: 9/10 pass. The 1 failure is STALE verifier text, not a defect: web `/workspace/private-check` still expects "Private workspaces remain unavailable"; it now returns the S04i 404 page ("Private workspaces require sign-in and scene ownership."). Fix is a one-line edit in infra/railway/dev/verify.py + test_verify.py (outside Owns; not edited).

## Ponytail
Reused stage.py/railway up, verify.py, existing 79 tests, existing in-app browser + CDP viewport override (cleared after use). No code/dependency added; no defect inside Owns found, so no source edit. Skipped: accessibility/keyboard pass (S15l), real GPU/API/uploads, Chrome. Risks: sign-in used browser-saved credentials (account identity not confirmed as Koushik's; no auth change made); Clerk real-key behaviour proven only for this one session; `.tmp-s19d-ctx/` still untracked at event root; staging context in %TEMP%\s15k-ctx-orch122.
Communication: silent; one final line to controller.
