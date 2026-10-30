# Real2Simulation — 3:00 demo script — DRAFT v2 (S24a-orch146)

**Status: DRAFT.** S21 benchmark is DONE and every number below is quoted from it or from a cited evidence file. S23 (judging deploy) is NOT done: every deployed-URL / live-screen beat is **PENDING S23 / S24c-f**. Do not publish a recording until the PENDING register is empty.

Rules: lead with measurement. Every number = a generated value copied from [BENCHMARK.md](../../BENCHMARK.md) (row id given) or a cited evidence JSON; none authored. Honest labels are burned into the frame, not only spoken. Paths are relative to this file.

## Labels that must appear on screen verbatim

| Item | On-screen label | Source |
|---|---|---|
| Gate A | `MET_AMENDED_Q16 — scale unverified, not setup-validated` (never "MET") | [GATE_A.json](../../evidence/S14/GATE_A.json) `/verdict`, `/label` |
| Gate M | `Gate M: NOT_MET (input readiness — no calibrated scale or capture clock)` | [BENCHMARK.md](../../BENCHMARK.md) Gates; [actual-gate-m.json](../../evidence/S07/S07f/actual-gate-m.json) |
| Gate RS | `Gate RS: NOT_MET — diagnostic only, 7/466 frames scored` | [gate-rs.json](../../evidence/S12/gate-rs/gate-rs.json); BENCHMARK `gate_rs_median_heldout_error` = UNAVAILABLE |
| Library | `SIMULATED · playable` / `SIMULATED · practice setup` | [library-copy.mjs](../../Build/web/src/app/(public)/library/library-copy.mjs) `TAG` |
| Mystery-g | `Mystery-g practice shape at Earth g. This is not a blind test.` vs `/lab`: server draws a hidden g per session | [library-copy.mjs](../../Build/web/src/app/(public)/library/library-copy.mjs) `MYSTERY_COPY` |
| Meta usage | `One live Baseten Muse Open call · 1,176 tokens · cost UNKNOWN` | BENCHMARK `meta_s16e_total_tokens`, `meta_s16e_cost_usd`; [S16e-orch108-live.json](../../evidence/S16/S16e-orch108-live.json) |
| Scale | `Metric scale: ABSTAINED (unverified)` | BENCHMARK "What is unavailable"; [S05d RESULT.json](../../evidence/S05/S05d/RESULT.json) |

## Meta models actually used

| Model | Use | Evidence | Claim limit |
|---|---|---|---|
| SAM 3.1 (`facebook/sam3.1`) | per-frame object tracking, Modal A10G | [modal_track.py](../../Build/measurement/runtime/modal_track.py), [PD02-summary.json](../../evidence/S07/S07-chunktrack-orch67/PD02-summary.json) | tracking only |
| MapAnything (`facebook/map-anything`) | scene reconstruction / floor plane | [image_spec.py](../../Build/gpu/image_spec.py), [S05d RESULT.json](../../evidence/S05/S05d/RESULT.json) | scale abstained |
| Muse Open (`meta-models/muse-spark-open-1026`, Baseten) | sidebar `library.search`, **one** live call | [S16e-orch108-live.json](../../evidence/S16/S16e-orch108-live.json), [S16h-CHECKPOINT.md](../../evidence/S16/S16h-CHECKPOINT.md) | local dev adapter, not deployed routing; cost UNKNOWN |
| Muse Spark 1.3 / Muse Wonder 1.0 | interview turns / scene spec in recorded Gate A run (30 Spark, 10 Wonder calls) | [S14g-fix3-live.json](../../evidence/S14/S14g-fix3-live.json) `/summary`, [S14g-fix3-ledger.jsonl](../../evidence/S14/S14g-fix3-ledger.jsonl) | synthetic-room tool outputs; Gate A checkpoint = S14h replay; dollar cost not in BENCHMARK |
| SAM 3D Objects | not used — **do not claim** | — | cut |

## Beats (total 3:00)

| # | Time | Beat | Shot (footage / screen) | Caption (burned in) | Voice-over | Evidence | Status |
|---|---|---|---|---|---|---|---|
| 1 | 0:00–0:12 | Hook: measure, don't guess | PD02 clip, SAM 3.1 track dot drawn over the bob | Real video → measured track → simulation → honest error | "Real2Simulation measures physics from real video — and tells you exactly what it could not measure." | clip credit row PD02 | footage PENDING owner public-use OK; capture PENDING S24c |
| 2 | 0:12–0:40 | Measurement: tracking | PD02 full swing with per-frame mask/track overlay; small "A10G" tag | SAM 3.1 · 439/439 frames tracked · Modal A10G | "Meta's SAM 3.1 segments and tracks the object in every frame on a Modal GPU." | [PD02-summary.json](../../evidence/S07/S07-chunktrack-orch67/PD02-summary.json) `frames_observed`, `frames_total`, `gpu` | capture PENDING S24c |
| 3 | 0:40–1:00 | Reconstruction + gravity direction | RM02 classroom → MapAnything point cloud, floor plane, badge "scale: ABSTAINED" | Floor-normal spread 0.04393° (bootstrap 1 sd) · Metric scale: ABSTAINED (unverified) | "MapAnything rebuilds the room and finds the floor. When metric scale can't be sourced, the system abstains instead of guessing." | BENCHMARK `rm02_gravity_direction_bootstrap_sd`, `rm02_gravity_vs_camera_down_prior` (11.05°); [S05d RESULT.json](../../evidence/S05/S05d/RESULT.json) | viewer capture PENDING S24c |
| 4 | 1:00–1:25 | Fit with uncertainty | ST03 apple drop; fitter panel: track points + fitted parabola + 1σ band | Image-space g fit: ±0.07367 relative (1σ, n=19) · precision, not accuracy | "A deterministic fitter — not a language model — fits the fall and reports its uncertainty. It's image-space only: the clip is probably slow motion, so this is not g in metres per second squared." | BENCHMARK `st03_g_image_relative_uncertainty`; clips.csv ST03 suitability note | capture PENDING S24c |
| 5 | 1:25–1:50 | Predict, then check | ST03: committed prediction drawn before suffix is revealed; suffix frames overlaid; error meter | Gate RS: NOT_MET — diagnostic RMS 0.1982 image heights, 7/466 frames scored | "We seal a prediction before seeing the rest of the clip. Today it misses: the full tracking job ran out of GPU memory, and the ballistic fit has no floor — the apple lands, the prediction keeps falling." | BENCHMARK `st03_heldout_normalized_rms`, `st03_range_error` reason; [gate-rs.json](../../evidence/S12/gate-rs/gate-rs.json) | capture PENDING S24c |
| 6 | 1:50–2:15 | Muse interview, numbers from tools | Workspace chat: Muse asks setup questions; every number chip tagged "tool" | Gate A: MET_AMENDED_Q16 — scale unverified, not setup-validated · numeric contract 10/10 · setup validator 0/10 | "Muse Spark interviews you about the setup, but every number it shows comes from a tool. Our checker flagged zero invented numbers across 30 replayed turns — on recorded scenes, not validated setups." | [GATE_A.json](../../evidence/S14/GATE_A.json) `/counts` (10/10, 0/10, 30/30, 0) | capture PENDING S24d |
| 7 | 2:15–2:35 | Virtual lab + library | /library card tagged SIMULATED; Mystery-g practice card copy; cut to /lab blind round; sidebar search result | SIMULATED library traces · Mystery-g practice ≠ blind /lab · Muse Open: 1 live call, 1,176 tokens, cost UNKNOWN | "The library holds simulated experiments, clearly labelled. The Mystery-g card is practice at Earth g; the lab draws a hidden g each session for a real blind test. Sidebar search ran one live Muse Open call — cost unknown." | [library-copy.mjs](../../Build/web/src/app/(public)/library/library-copy.mjs); BENCHMARK `meta_s16e_total_tokens`, `meta_s16e_latency_s` (2.52345 s), `meta_s16e_cost_usd`; [lab-375.jpg](../../evidence/S10/ui/lab-375.jpg) (reference only) | deployed screens PENDING S23 + S24e |
| 8 | 2:35–2:50 | Cost + honest misses | Checklist card (static, project-authored) | Modal billed to date: $0.599594 · Gate M ✗ · Gate RS ✗ · Gate A amended · scale unverified | "The whole Modal bill so far is under a dollar. And here is what we have not proven: no calibrated metric source, so no physical-accuracy claim." | BENCHMARK `modal_month_to_date_billed_usd`, Gates | card PENDING S24f |
| 9 | 2:50–3:00 | Close | Judging URL + repo + BENCHMARK.md | Built Oct 27 – Nov 4 · every number links to BENCHMARK.md | "Every number you saw is a pointer into the repo's benchmark. Try it." | [BENCHMARK.md](../../BENCHMARK.md) | URL PENDING S23 (written go-ahead); public repo PENDING owner |

Timing: 12+28+20+25+25+25+20+15+10 = 180 s.

## Shot list — footage, licence, credit

| Shot | Source | Creator / licence | Credit line (end card) | Rights status |
|---|---|---|---|---|
| PD02 (beats 1–2) | clips.csv `PD02` (Pexels 35640361) | Alexandre Henry Alves · Pexels License | Alexandre Henry Alves - Foucault Pendulum Swing in Grand Hall - Pexels | S02e approval = local pipeline only; people/depicted rights review noted |
| RM02 (beat 3) | clips.csv `RM02` (Pexels 6671552) | Andy Barbour · Pexels | Andy Barbour - Tracking shot of empty classroom - Pexels | S02e local only |
| ST03 (beats 4–5) | clips.csv `ST03` (Pexels 12723966) | Roman Odintsov · Pexels License | Roman Odintsov - Woman dropping apple on ground - Pexels (Pexels License); no endorsement implied | S02e local only; depicted person |
| Workspace, /library, /lab, sidebar, cards (6–9) | project-authored screen capture | own event work | — | needs S23 deploy or local dev capture (S24c-f) |

**Rights hold:** [APPROVAL.md](../../evidence/owner/S02/APPROVAL.md) approves these clips for local pipeline work only and retains the hold on *public raw media redistribution*. Showing clip frames in a public demo video needs a separate owner go-ahead (PENDING owner). Fallback if refused: replace beats 1–5 footage with track/fit plots only (no raw frames).

## Captions (copy-paste, one line per beat)

```text
[0:00] Real video → measured track → simulation → honest error
[0:12] SAM 3.1 · 439/439 frames tracked · Modal A10G
[0:40] Floor-normal spread 0.04393° (bootstrap 1 sd) · Metric scale: ABSTAINED (unverified)
[1:00] Image-space g fit: ±0.07367 relative (1σ, n=19) · precision, not accuracy
[1:25] Gate RS: NOT_MET — diagnostic RMS 0.1982 image heights, 7/466 frames scored
[1:50] Gate A: MET_AMENDED_Q16 — scale unverified, not setup-validated · numeric contract 10/10 · setup validator 0/10
[2:15] SIMULATED library traces · Mystery-g practice ≠ blind /lab · Muse Open: 1 live call, 1,176 tokens, cost UNKNOWN
[2:35] Modal billed to date: $0.599594 · Gate M ✗ · Gate RS ✗ · Gate A amended · scale unverified
[2:50] Built Oct 27 – Nov 4 · every number links to BENCHMARK.md
```

## PENDING register

- PENDING S23 — judging deploy URL (beats 7, 9); needs separate written owner go-ahead.
- PENDING S24c — clip/viewer/fitter captures (beats 1–5).
- PENDING S24d — workspace interview capture (beat 6).
- PENDING S24e — /library, /lab, sidebar captures on the deployed build (beat 7).
- PENDING S24f — edit, end-card, checklist card (beat 8) and final timing.
- PENDING owner — public use of PD02/RM02/ST03 frames in the video (rights hold above); public repo.
- Re-quote check: if any BENCHMARK/evidence value changes, re-run the number check in [REPORT.md](../../Run-System/Runs/S24a-orch146/REPORT.md) before recording.

## Cut list if over time
Beat 3 VO → caption only (−8 s); merge beats 8+9 (−10 s); drop sidebar clause from beat 7 (−5 s).

