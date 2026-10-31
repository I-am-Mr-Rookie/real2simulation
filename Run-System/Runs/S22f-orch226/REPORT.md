# S22f-orch226 REPORT

Status: DONE. Lane CLAUDE, anthropic/claude-opus-5-5/high (OpenCodex-managed; not polled). UTC start 2026-10-31T16:11:44Z (issued 16:11:14Z), end 2026-10-31T16:17:39+00:00.

Result: evidence/qa/claude/S22f-GATE-D-JUDGEMENT.md.
- Gate D (a) as written NOT MET: timing 3/3 scripted runs < 1 min to result, but protocol 3.5 (fit from fitter) NOT MET in every run and 3.7 (report body) PARTIAL; DEV only = rehearsal. Streak 0/3 as written, 3/3 on timing.
- Gate D (b) guest library MET on DEV (S22b + fresh HTTP probe 16:13Z: / 200, /library 200, manifest 18 demos, /api/lab start+fit ok); no judging URL exists.
- P2-1 -> P1 (D1): Gate D requires an executed fit. Smallest honest change S15az: run existing Build/fitter/core.py fit_least_squares/select_model server-side on stored RECORDED prefix points; not via POST /api/workspace/fit (fitter.api.handle rejects non-"simulated" inputs, probed). Reference pixel length for scale absent from owner_clips.json.
- New P1s: D2 no candidate env + private workspace gated on Railway env name "dev" (source-read); D3 report body never verified. P2: D4 allowlist-only uploads (disclose), D5 "Scene ready" for no-scene job, D6 "user-declared scale" before user declares. P3: D7 scene-geometry note on no-scene clip (controller candidate confirmed), D8 "Private development fixture" header (confirmed), D9 S22e RUN.md end time 16:20Z after its 16:10:29Z commit, D10 Turnstile headless, D11 untested steps.

Files: evidence/qa/claude/S22f-GATE-D-JUDGEMENT.md; Run-System/Runs/S22f-orch226/{PLAN.md,TIMEBOX.json,REPORT.md}. No product code, deploy, account or canonical control change.

Commands/checks (fresh): read S22c/S22d/S22e RUN.md + REPORT/TIMEBOX, S15ay REPORT, GATE_D_PROTOCOL; rg source (jobs.py, dev-scenes.mjs, server-access.js, PrivateWorkspace.mjs, status.mjs, controller.mjs, analysis.py); viewed 3 screenshots; node fetch guest probe (temp script, uncommitted); python fitter feasibility probes (temp script, uncommitted): api.handle rejects measured/recorded labels; core.fit_least_squares runs on 4 OWN05 prefix points.

Ponytail: reused S22a protocol table as the criteria list (no new rubric), existing evidence lines quoted instead of re-running browsers; fix rows reuse existing fitter core and S15/S22i/S25 rows instead of new subsystems; judged live SAM tracking per upload unnecessary for Gate D's fit step. Skipped: browser re-run, report body check, non-dev env runtime check, different-answer interview test. Risks: D2 is source-read only; S15az live g may differ from recorded 8.62 and has dof 1 on OWN05.
Communication: silent; one completion line to controller (app thread tool not exposed in this session; final line in chat).

