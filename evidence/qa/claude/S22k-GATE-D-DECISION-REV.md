# S22k revision of the S22j Gate D decision (per R-D review)

Judge: S22k-orch245, anthropic/claude-opus-5-5/medium, CLAUDE lane, from main b4ae52b7. Documentation only: no product
code, deploy, browser run, account or paid call. Revises evidence/qa/claude/S22j-GATE-D-DECISION.md (S22j, left
unchanged except a pointer line) per evidence/reviews/R-D/REVIEW.md (R-D, verdict "AGREE WITH CHANGES", F1 to F7).
Inputs also read: evidence/qa/claude/GATE_D_PROTOCOL.md, evidence/qa/claude/GATE_D_CHECKLIST.md,
Run-System/Runs/R-D-orch241/numeric-probe.json, Run-System/Runs/S15bb-orch233/REPORT.md, the S22i/S22j TIMEBOX.json
files, clips.csv, STATE.md, evidence/owner/S24/OWN07-PUBLIC-SNIPPETS-2026-10-31.md.

## Verdict of record (supersedes the S22j "Overall" line)

**Gate D: PASS on DEV with the scoped deviations listed below, conditional on S15bf + S15bg + S22l retest and the S23
judging URL.** Until all four conditions are met, Gate D of record stays NOT MET / PENDING (R-D: "Gate D of record is
NOT MET / PENDING"). This is a rehearsal result, not a protocol-conforming 3/3 PASS: step 3.4 and the streak are PARTIAL.

- Conditions: (1) S15bf: chips plus a validated owner spec on the owner-clip branch, and the legacy-budget limit (F1,
  F5). (2) S15bg: fixture-announcer recheck (F6). (3) S22l: fresh 3/3 streak + guest pass on the frozen build with the
  receipts required in F3. (4) S23: Koushik's written judging approval (S23a), promote (S23b), verify (S23c).
- Library-only fallback rule unchanged (QUEUE.md:606): "Fallback: If Gate D fails at freeze, the demo video uses the
  library path and the README states the upload limits honestly."

## Claim-by-claim disposition

| Item | S22j verdict | Revised verdict | Basis |
|---|---|---|---|
| 3.1 to 3.3, 3.5, 3.7, 3.8 | MET (scoped) | Unchanged, scoped as in S22j | R-D confirms the fitter runs; route caveat F4 applies to all. |
| 3.4 Agent interview; valid spec | MET (free text; chips not evidenced) | **PARTIAL** | F1 below. |
| 3.6 Sidebar patch/search | N/A | Unchanged | Not in signed-in UI. |
| streak 3/3 | MET on DEV | **PARTIAL** | F1 (3.4 not met) + F3 (receipts). |
| 2.1, 2.2, 2.4 to 2.6 | MET (DEV) | Unchanged | Not re-run since S22g; S22l / S23c re-run. |
| 2.3 Demo scene renders | MET (trajectory viewer, not a 3D scene) | **MET under GATE_D_CHECKLIST; scoped deviation from protocol 2.3** | F2 below. |
| env (judging URL) | NOT MET | Unchanged | S23 not done. |

## Findings disposition

### F1: step 3.4 and the full streak are PARTIAL

Exact owner-clip scope tested: OWN05, one known-size free-text question (answer "book cover horizontal edge 20.28 cm",
S22i/RUN.md:7); the answer sets a user-declared scale and the fitter runs live on the RECORDED track. The owner question
has `chips: []` and the owner branch returns before `interview.answers_to_spec` or numeric validation (R-D F1, citing
Build/api/workspace/analysis.py:35-36, :187-190, :193-203 and Build/web/src/workspace/controller.mjs:145-151). So no
validated experiment spec and no chips were exercised. No invented fitter number was found (R-D F1).
- 3.4: PARTIAL (free-text known-size answer drives a live fit; no validated spec; no chips by design).
- Streak: PARTIAL (3 scripted runs passed 3.1 to 3.3 and 3.5 to 3.8 on DEV; 3.4 PARTIAL in all three).
- Pending: S15bf (chips + validated owner spec), then retest S22l. "Valid spec" is not redefined here.

### F2: criterion 2.3 governed by GATE_D_CHECKLIST, recorded as a scoped deviation

GATE_D_PROTOCOL.md:50 says "3D scene renders within 15 s; controls respond." GATE_D_PROTOCOL.md:5 says the checklist
supersedes the dependency table, not expressly 2.3 (R-D F2). Decision: the newer GATE_D_CHECKLIST.md (lines 33, 37 to 40,
which accept playable traces) governs 2.3, because it is the later document and matches the top-level Gate D definition
(open/run a library demo). 2.3 is recorded as a **scoped deviation**: the library replay is a **SIMULATED side-view
trace** ("viewer (SVG, no canvas)", S22g/RUN.md:13), **not a 3D scene**. Label verbatim: "SIMULATED trajectory:
simulator output, not a measurement" (Build/web/src/viewer/trajectory-replay.mjs:7). No 3D geometry work is requested.
Guest playback is rechecked on the frozen build in S22l / S23c.

### F3: prose times reconciled to receipts

Actual receipts (no per-flow times invented; all times 2026-11-01 UTC):

| Run | Prose time | TIMEBOX | Evidence commit |
|---|---|---|---|
| S22i-orch237 | RUN.md:3 07:14 to 07:30Z; REPORT.md:2 stopped 07:24Z | issued 07:13:12Z; work_stopped_at = reported_at = 07:20:52Z | 341bc50c authored 07:20:53Z, committed 07:21:13Z |
| S22j-orch238 | heading 07:22Z-07:52Z | issued 07:22:03Z; work_stopped_at = reported_at = 07:27:46Z | 59e864f8 authored 07:27:48Z, committed 07:32:07Z |

The prose end times are later than the receipts; the receipts govern. S22j's "07:52Z" is its deadline, not its work
end. S22i keeps only cumulative timings (21.2 s, 19.5 s, 21.5 s), no per-flow UTC starts/ends and no protocol run.json
(R-D F3). This is a documentation inconsistency, not evidence of fabrication (R-D F3).
- Required in S22l: per-flow UTC start/end (plus monotonic durations), safe account aliases, build SHA read from the
  version endpoint, redacted console/network records, and one protocol run.json per flow. No retroactive logs.

### F4: browser route and footage limit

- Disclosed route: **headed Playwright bundled Chromium with Clerk development test accounts** (+clerk_test, code
  424242), because workers cannot drive the owner's in-app browser ("Browser is not available: iab" in worker chats;
  controller decision, STATE.md 2026-10-31T14:40Z entry). Protocol :21 and checklist :16 name the ChatGPT in-app
  browser; this route is a controller decision, not a recorded owner exception, so it is disclosed as a deviation.
- Footage: only **OWN07 short face-free snippets** are approved for public use (public demo video beat 5b; receipt
  evidence/owner/S24/OWN07-PUBLIC-SNIPPETS-2026-10-31.md, scope "Nothing else."). **OWN05 and all other owner clips stay
  private** (clips.csv: PRIVATE_PROCESSING_ONLY (Oct31)). QA screenshots of OWN05 (frames CSS-hidden) are not
  publication approval. The Gate D streak used OWN05, so its frames must not appear publicly.

### F5: legacy-job uncertainty limit disclosed, pending S15bf

Jobs without `u_budget` return the recorded total unchanged while g is recomputed for the new length (R-D F5, citing
analysis.py:130-132). R-D fallback probe: 40.56 cm gives g 17.24374723863895 with u still 1.28; with the budget u is
2.574546958037049. Fresh S22i uploads carry the budget. Disclosed as a limit until S15bf fixes it or abstains.

### F6: fixture announcer stays OPEN, pending S15bg

role=alert "Private development fixture" (Build/web/src/auth/dev-scenes.mjs:19) was not fixed or browser-verified by
S15be (R-D F6). Status: **OPEN**. S22j's expectation that S15be resolves it is withdrawn.

### F7: erratum to S15bb report numbers

Run-System/Runs/S15bb-orch233/REPORT.md reports "10 cm: g = 4.2514 +- 0.6348". Current code output
(Run-System/Runs/R-D-orch241/numeric-probe.json, 10 cm): g 4.2514169720510075, **u 0.6350844502877578, displays 0.64**.
The 20.28 cm value (g 8.621873619319475, u 1.2874051062222112, display 8.62 ± 1.29) agrees. S22j quoted only g = 4.25,
which is correct. Fitter unchanged; this is receipt hygiene.

## Merged disclosure list (README, video, judge note)

R-D checklist items 1 to 10 merged with S22j limits 1 to 9, deduplicated.

1. **DEV rehearsal only; no judging approval or pass.** Private workspace is gated on the Railway env name "dev"
   (dev-scenes.mjs:6-9, server-access.js:10). Record the frozen deployed SHA from the version endpoint; S15be changed
   Build files after the streak, so S22l must retest.
2. **Route and accounts.** Headed Playwright bundled Chromium (not the in-app browser), Clerk development test accounts
   (+clerk_test, code 424242), same OWN05 / 20.28 cm answer each run. Google, real-email OTP, human timing and other
   clips untested. Scripted timings (21.2 s, 19.5 s, 21.5 s) exclude human reading/typing; a human < 5:00 is not measured.
3. **Uploads limited to the clips.csv checksum allowlist** (jobs.py:247, 422 otherwise). UI copy verbatim: "This clip is
   not on the approved list. Try a demo clip from the library; your own videos cannot be processed in this build."
   A judge's own video cannot complete the flow.
4. **Track RECORDED, fit live.** "Track: RECORDED (precomputed SAM 3.1, not run live)"; no live SAM/GPU per upload.
   OWN05 has no reconstructed scene.
5. **Owner known-size branch: one free-text question, no validated experiment spec, no chips** (F1). Not the Gate A
   validated-setup path.
6. **Scale user-declared, unverified; phone clock not externally verified.** "Scale unverified; not a validated
   measurement." u = 1.29 combines fit scatter with recorded S07m budget terms (declared assumptions, not calibrated
   coverage). Legacy jobs without a budget keep the old-scale u at a new length (F5).
7. **Few points, large held-out errors.** Four fit points, dof = 1; held-out residuals 4.6, 9.6, 19.9 px vs fit rmse
   0.12 px. The displayed held-out PASS (chi2/dof 2.32/3, p 0.51) and prediction band belong to the stored post-hoc S07m
   third analysis (forking-paths caveat), not a fresh validated measurement.
8. **Recorded chart and live fit are separate.** A new scale does not redraw the stored chart: "Recorded reference (not
   affected by your scale)". Show measured/recorded/simulated labels verbatim.
9. **Guest playback is a SIMULATED SVG side-view trajectory, not a reconstructed 3D scene** (F2). Library counts: All 18,
   RECORDED 0, SIMULATED 3, what-if 0, UNAVAILABLE 15.
10. **No spend-cap demo.** SPEND_PAUSED/402 is not emitted by the API; no live spend-cap or failover claim; the
    owner-clip path runs no GPU/model.
11. **No download/PDF/accessible export.** Report is the page body; browser print is the fallback; no PDF generated.
12. **Evidence limits.** S22g-i kept RUN.md tables + screenshots; raw scripts/logs stayed in %TEMP%; no run.json; prose
    times differ from receipts (F3). Fixture role=alert text OPEN (F6). S15be copy fixes are source-only until rechecked.
13. **Footage.** Only OWN07 short face-free snippets may appear publicly (video beat 5b). OWN05 and all other owner
    clips stay private; do not publish their video or frames. Public-clip licence/credit boundaries apply separately.

## Next

S15bf, S15bg, then S22l retest on the frozen build; S23a (Koushik), S23b, S23c; S25 README limits from the list above.
