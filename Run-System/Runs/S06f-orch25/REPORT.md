# S06f-orch25 REPORT — DONE

Lane CODEX-1; model anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). Issued 2026-10-29T15:23:14+00:00,
worker start 15:23:49Z, end 2026-10-29T15:39:55+00:00 (deadline 15:53:14+00:00). Base main ba5f668; branch run/S06f-orch25 (not merged; controller integrates).

## Result (acceptance: actual scene completes or failure evidence captured; target <=5 min incl. cold start)
- ONE A10G scene_job on RM04 (approved, Pexels "An Empty Classroom", Pavel Danilyuk; not RM02), app ap-yeKuf0FjgU0P0H8mB9lOvt,
  rc 0, retries 0, image not rebuilt: approved frames (4, SHA256-verified from the S05c manifest; same frames S05c already
  ran on Modal) -> MapAnything -> contract scene bundle -> validate_scene PASS rm04-mapanything-s06d schema=1.0.0
  synthetic=False (evidence/S06/S06f/validate.txt). 20000 points; peak GPU alloc 7.78 GB.
- Time: whole command 63.3 s incl. uv env + app create (15:27:12Z -> 15:28:15Z) — well inside the 300 s target.
  Scene log evidence/S06/S06f/RM04-scene-log.json: container boot 7.59 s, cold start 11.88 s, model load 18.81 s
  (ready 30.69 s), inference 1.51 s, function 20.92 s, round trip 43.64 s.
- Cost: GPU s est 27.21 / upper 45.64 / billed 25.96; est $0.01001 vs billed $0.00955 (cap $0.50; ledger
  evidence/S06/S06f/job-ledger.json). Containers [] and both apps stopped/0 tasks after (post-verify.txt).
- Failure evidence (honest): attempt 1 (ap-ltdA9yMPSJynaFT34T4Ent, 15:26Z) was refused in local preflight —
  clips.csv spells RM04's licence "Pexels License" but scene_job.LICENCES only had "Pexels". Refusal happened before
  scene_job.remote: no function call, no GPU container, no billed rows. Fixed (one allowlist entry, both map to contract
  "Pexels") + test, then the single GPU run above.

## Files
Build/gpu/scene_job.py (LICENCES +"Pexels License"), Build/gpu/test_scene_job.py (+1 test: every SCENE_IDS clip allowlisted);
infra/modal/README.md (S06f section: worktree command, licence spelling, RM04 timings);
evidence/S06/S06f/{.gitignore, job-ledger.json, RM04-scene-log.json, scene-RM04-gpu.json, run-log.txt, post-verify.txt,
billing-pre-today-hourly.json, billing-post-today-hourly.json, tests.txt, validate.txt}; media (npz, PLY) only in gitignored
evidence/S06/S06f/local/RM04/ (scene-RM04-gpu.json is the manifest copy; validate it beside its assets in local/).
Run-System/Runs/S06f-orch25/{PLAN.md, TIMEBOX.json, REPORT.md}.

## Checks (fresh)
- python -m unittest discover -s Build/gpu: 22 OK (was 21 + new allowlist test). contracts/scene: 11 OK. image_spec.py rc 0.
- validate_scene on RM04 bundle: PASS. Raw npz points finite; view0 median z +2.68 (OpenCV forward) before contract flip.
- Billing reconciled read-only with Build/gpu/cost_log.py (writes billed into the scene log); 15:33:27Z and 15:39:20Z
  reads identical ($0.00955325; billing-post*.json); attempt-1 app has no rows; container list [] again 15:39Z.

## Ponytail (applied, full)
- Reuse: S06d scene_job entry point + S06b RUNTIME_IMAGE unchanged; S06e scene log/cost_log reconcile; S06e documented uv
  command (+numpy +jsonschema, which avoided S06e's client failure); S05c manifest + frames in place (no re-extraction,
  no copy of media); S06e ledger/post-verify procedure.
- Smallest complete: root-cause fix is one dict entry in the shared allowlist (not a per-clip workaround / clips.csv edit
  outside Owns) + one test covering all room SCENE_IDS. No new deps, no image change, one GPU job.
- Skipped: RM05 (ISS, not an Earth room), viewer visual check, warm-start timing, SAM 3D, floor/gravity, AWS.

## Limits / risks
- Not Gate R, not calibrated scale, not physical evidence; vertical_fov_deg still placeholder 50 (S06d limit).
- Preflight runs inside the Modal local entrypoint, so a refused clip still creates (and stops) an empty app; no cost observed.
- Input manifest read from sibling worktree .worktrees/S05c-orch19 (frames are gitignored); if that worktree is archived the
  RM04 frames must be re-extracted per S05c.
- Billed figure may still accrue; latest read wins. Client/container clock skew possible (sub-second).
- Communication: silent; one completion line to controller only.

Next: controller integrates; S06g/S06h can reuse the same command for any approved room clip.
