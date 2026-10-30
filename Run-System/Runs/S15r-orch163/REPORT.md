# S15r-orch163 REPORT — DONE

Lane CLAUDE; assigned and actual anthropic/claude-opus-5-5/high. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No Meta/GPU/paid call, no secrets read, no Chrome, no auth change.
UTC issued 2026-10-30T21:19:08Z; work 21:19:47Z–21:29:30Z. Branch run/S15r-orch163, commit 0b0f980c (rebased on main 07825ca5). Ponytail full read and applied.

## What changed (Owns only; Build/simulator/*.mjs untouched)
- Build/api/workspace/analysis.py: spec route now returns as `validated_setup` (a) for setup-validated scenes the S10 artifact in exactly export_validated_setup's shape {artifact_version s10-validated-setup-v1, validation validate_setup, producer, spec, scene (the resolver's scene, unchanged)}; (b) for Q16 scenes a distinct artifact {artifact_version s15r-what-if-setup-v1, validation numeric_contract_only, what_if true, label = verbatim Q20 label, spec, scene {id, schema_version copied from spec.scene, synthetic:false, scale_verified:false}} plus top-level what_if_label. Existing `label` (Q16) and `setup_validated:false` kept. Report route accepts optional `label` only if it equals the exact what-if label (else 422), inserts it as the first report text line and returns what_if_label.
- Build/web/src/lab/browser-simulator.mjs: new explicit `mode:'what-if'` path that accepts only that artifact (all marker fields checked; free_fall/projectile), runs the existing freeFallTrajectory/projectileTrajectory engine with inputProvenance 'image-derived' (never 'synthetic'), returns {...trajectory, whatIf:true, label}. Normal mode code is byte-identical.
- Build/web/src/workspace/controller.mjs: browserSimulate selects 'what-if' only when validated_setup.what_if===true; snapshot.whatIfLabel; report request passes the label.
- Build/web/src/workspace/view.mjs + react.mjs: stage panel shows the verbatim what-if label in run.*/fit.*/report.* phases; any *.failed phase shows "CODE: reason" in the stage panel (was only "Run failed.").
- Build/web/src/shell/PrivateWorkspace.mjs: the SIMULATED page note leads with the verbatim what-if label when present; passes whatIf to Workspace.
- Build/web/src/shell/AccountNav.jsx: renders nothing until Clerk is loaded (was "Sign in" while the session loaded). ShellFrame.jsx footer: "Uploads are limited to approved licensed clips in the signed-in workspace." (was "No uploads are enabled").
- infra/railway/dev/stage.py: api allowlist adds evidence/S14/S14g-fix3-ledger.jsonl (jobs.py reads the sibling ledger for the understand UTC; it was not staged -> "time not recorded" on DEV). test_stage.py updated.

## Checks (fresh)
- python -m unittest discover -s tests/api-workspace (PYTHONPATH .;tests/api-workspace): 21 OK (incl. what-if artifact markers, S10 artifact shape, report label pass-through + wrong-label 422).
- python -B -m unittest infra.railway.dev.test_stage infra.railway.dev.test_verify: 16 OK.
- python -m unittest discover -s tests/pipeline: 53 OK.
- node --test tests/workspace tests/simulator tests/shell-workspace (node_modules junction, removed afterwards): 213 tests, 208 pass, 5 fail — all 5 pre-existing/environmental: 4 R14/clean ramp+pendulum oracle tests fail identically on canonical main 8df90794 (217 tests, 4 fail), and contacts.test.mjs needs @dimforge/rapier3d-compat (root node_modules absent in worktree). New: tests/simulator/what-if.test.mjs 3/3 (what-if accepted only in what-if mode; 8 bad variants rejected incl. synthetic:true, scale_verified:true, S10 envelope, pendulum; normal mode still rejects non-synthetic S10 scene); controller.test.mjs what-if test (real simulator via browserSimulate -> run.done, report request carries label, panel label + failure reason, what_if:false -> normal-mode rejection).
- node --test tests/web-private tests/web-workspace-api: 15/15. tests/lab/browser-simulator.test.mjs: 10/10 unchanged.
- npm run build (Build/web): exit 0.
- Real RM04 end-to-end (evidence/S15r/rm04_spec.py + rm04_run.mjs): RM04 Q16 path with the web answer body -> 200, what-if artifact (scene synthetic:false, scale_verified:false) -> real browser simulator what-if mode -> 555 samples. Files: evidence/S15r/rm04-spec-response.json, evidence/S15r/rm04-what-if-run.json. Numbers are SIMULATED from the described setup, not measured.

## Deploy (Railway DEV, after rebase onto main 07825ca5)
- stage.py api (87 files) / web (111 files) at source revision 0b0f980c5519c6c2394e9f801e6786e91a83746e; staged api context contains the S14g-fix3 ledger. Contexts: %TEMP%\s15r-api-orch163, %TEMP%\s15r-web-orch163.
- api deployment 81a74b99-ef55-4f69-8459-384ff306b390 SUCCESS (previous a2777e67 REMOVED); https://api-dev-6091.up.railway.app/api/version -> revision 0b0f980c5519c6c2394e9f801e6786e91a83746e; /health/live 200.
- web deployment 0144fdf3-5747-4979-ba23-0fd8a2f91a6d SUCCESS (previous 4ad6b82c REMOVED); / serves the new footer text.
- For the controller (not edited by me): deployments.json api {deploymentId 81a74b99-ef55-4f69-8459-384ff306b390, previous a2777e67-be64-4455-9d71-c8c5803c40a0, sourceRevision 0b0f980c5519c6c2394e9f801e6786e91a83746e}; web {deploymentId 0144fdf3-5747-4979-ba23-0fd8a2f91a6d, previousDeploymentId 4ad6b82c-7b39-4ef4-96ab-8a674989f883, sourceRevision 0b0f980c5519c6c2394e9f801e6786e91a83746e}. verify.py api revision pin -> 0b0f980c5519c6c2394e9f801e6786e91a83746e.

## Ponytail (reuse / smallest complete)
- Reused export_validated_setup's exact artifact shape (no new S10 format); reused existing RK4 freeFall/projectile engine and its existing 'image-derived' provenance instead of touching Build/simulator; reused the controller's existing failWith/RUN_FAIL error (reducer already carried the reason; only the panel didn't render it); reused stage.py/railway up procedure and existing test harnesses (fakeFetch, toRunReady, test_analysis fixtures).
- Skipped: ramp/pendulum what-if (would need Build/simulator/extended-templates.mjs, which only accepts synthetic provenance — fails closed with a clear reason; shortcut comment in browser-simulator.mjs); fit-table per-row label (label sits in the same stage panel above fit rows); browser walk (controller's job); deployments.json/verify.py edits (not owned).

## Risks / limits
- DEV browser walk of Run/Fit/Report not done by me (IAB bound to controller). Main not merged by me (dispatcher-style acceptance by controller).
- what-if provenance label 'image-derived' is the simulator's only non-synthetic option; the UI/API label makes the what-if status explicit.
- AccountNav: if Clerk never loads, nav shows no account link (truthful, but no Sign in fallback).
- Communication: silent; one completion line to controller. The codex_app thread-messaging tool namespace was removed from this session mid-run, so the completion message may need to be relayed by the owner/controller from this chat's final line.
