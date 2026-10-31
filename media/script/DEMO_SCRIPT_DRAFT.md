# Real2Simulation — 3:00 demo script — DRAFT v5 (v4 + S24m system-measured t/h in beat 5b, no stopwatch)

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
| Meta usage | `One live Baseten Muse Open call · 1,176 tokens · Meta cost UNAVAILABLE` | BENCHMARK `meta_s16e_total_tokens`, `meta_s16e_cost_usd` (UNAVAILABLE); [S16e-orch108-live.json](../../evidence/S16/S16e-orch108-live.json) |
| Scale | `Metric scale: ABSTAINED (unverified)` | BENCHMARK "What is unavailable"; [S05d RESULT.json](../../evidence/S05/S05d/RESULT.json) |
| Library size | `"4 public clips" library fallback: NOT met (2 SIMULATED traces + Mystery-g practice)` | STATE S18j acceptance (content/approval blocker) |

## Meta models actually used

| Model | Use | Evidence | Claim limit |
|---|---|---|---|
| SAM 3.1 (`facebook/sam3.1`) | per-frame object tracking, Modal A10G | [modal_track.py](../../Build/measurement/runtime/modal_track.py), [PD02-summary.json](../../evidence/S07/S07-chunktrack-orch67/PD02-summary.json) | tracking only |
| MapAnything (`facebook/map-anything`) | scene reconstruction / floor plane | [image_spec.py](../../Build/gpu/image_spec.py), [S05d RESULT.json](../../evidence/S05/S05d/RESULT.json) | scale abstained |
| Muse Spark Open (`meta-models/muse-spark-open-1026`, Baseten) | sidebar `library.search`, **one** live call | [S16e-orch108-live.json](../../evidence/S16/S16e-orch108-live.json), [S16h-CHECKPOINT.md](../../evidence/S16/S16h-CHECKPOINT.md) | local dev adapter, not deployed routing; Meta cost UNAVAILABLE; **open-weight bonus NOT claimed** (S16h `meta_bonus_claimed=false`) |
| Muse Spark 1.3 (`muse-spark-1.3`) / Muse Wonder 1.0 (`muse-wonder-1.0`), Meta Model API | interview turns / scene spec in recorded Gate A run (30 Spark, 10 Wonder calls) | [S14g-fix3-live.json](../../evidence/S14/S14g-fix3-live.json) `/summary`, [S14g-fix3-ledger.jsonl](../../evidence/S14/S14g-fix3-ledger.jsonl) | synthetic-room tool outputs; Gate A checkpoint = S14h replay; Meta cost UNAVAILABLE |
| SAM 3D Objects | not used — **do not claim** | — | cut |

## Beats (total 3:00)

| # | Time | Beat | Shot (footage / screen) | Caption (burned in) | Voice-over | Evidence | Status |
|---|---|---|---|---|---|---|---|
| 1 | 0:00–0:12 | Hook: measure, don't guess | PD02 clip, SAM 3.1 track dot drawn over the bob | Real video → measured track → simulation → honest error | "Real2Simulation measures physics from real video, and tells you exactly what it could not measure." | clip credit row PD02 | clip frames PENDING owner Q19 (default B: track plot only); capture PENDING S24c |
| 2 | 0:12–0:34 | Measurement: tracking | PD02 full swing with per-frame mask/track overlay; small "A10G" tag | SAM 3.1 · 439/439 frames tracked · Modal A10G | "Meta's SAM 3.1 segments and tracks the object in every frame on a Modal GPU." | [PD02-summary.json](../../evidence/S07/S07-chunktrack-orch67/PD02-summary.json) `frames_observed`, `frames_total`, `gpu` | capture PENDING S24c |
| 3 | 0:34–0:48 | Reconstruction + gravity direction | RM02 classroom → MapAnything point cloud, floor plane, badge "scale: ABSTAINED" | Floor-normal spread 0.04393° (bootstrap 1 sd) · Metric scale: ABSTAINED (unverified) | "MapAnything finds the floor. When metric scale can't be sourced, the system abstains." | BENCHMARK `rm02_gravity_direction_bootstrap_sd`, `rm02_gravity_vs_camera_down_prior` (11.05°); [S05d RESULT.json](../../evidence/S05/S05d/RESULT.json) | viewer capture PENDING S24c |
| 4 | 0:48–1:13 | Fit with uncertainty | ST03 apple drop; fitter panel: track points + fitted parabola + 1σ band | Image-space g fit: ±0.07367 relative (1σ, n=19) · precision, not accuracy | "A deterministic fitter — not a language model — fits the fall and reports its uncertainty. It's image-space only: the clip is probably slow motion, so this is not g in metres per second squared." | BENCHMARK `st03_g_image_relative_uncertainty`; clips.csv ST03 suitability note | capture PENDING S24c |
| 5 | 1:13–1:38 | Predict, then check | ST03: committed prediction drawn before suffix is revealed; suffix frames overlaid; error meter | Gate RS: NOT_MET — diagnostic RMS 0.1982 image heights, 7/466 frames scored | "We seal a prediction before seeing the rest of the clip. Today it misses: the full tracking job ran out of GPU memory, and the ballistic fit has no floor — the apple lands, the prediction keeps falling." | BENCHMARK `st03_heldout_normalized_rms`, `st03_range_error` reason; [gate-rs.json](../../evidence/S12/gate-rs/gate-rs.json) | capture PENDING S24c |
| 5b | 1:38–1:58 | System measures fall time and drop height (no stopwatch) | OWN07 (private owner clip; owner approved short face-free OWN07 snippets for the public video (receipt evidence/owner/S24/OWN07-PUBLIC-SNIPPETS-2026-10-31.md); other owner clips stay private; OWN01 and other OWN clips: plot/table only, no raw frames): SAM track + release/impact markers + parabola, then [S07n table](../../evidence/S07/S07n/table.md) row OWN07; then OWN01 hero row showing ABSTAIN + lower bounds, and hero fit 10.96 ± 0.77 failing its held-out check | ≈ SYSTEM-ESTIMATED · MEASURED (conditional) · t 0.433 ± 0.027 s · h 0.923 ± 0.010 m · g 9.84 ± 1.24 m/s² (from t, h) · scale user-declared 20.28 cm · phone clock unverified · approximate, not calibrated · hero: lower bounds only t ≥ 0.267 s, h ≥ 0.374 m (track ends f54, before impact) · hero fit 10.96 ± 0.77 fails own check | "The system finds release and impact in the phone clip, with the scale you declare: fall time 0.433 plus or minus 0.027 seconds, height 0.923 plus or minus 0.010 metres, g 9.84 plus or minus 1.24. Hero take: the track ends before impact, so lower bounds only. Approximate, not calibrated." | [S07n README](../../evidence/S07/S07n/README.md), [results.json](../../evidence/S07/S07n/results.json) `OWN07`/`OWN01`, [table.md](../../evidence/S07/S07n/table.md); hero fit [S07h](../../evidence/S07/S07h/README.md), checks [S07k](../../evidence/S07/S07k/README.md), [S07l](../../evidence/S07/S07l/README.md), [S07m](../../evidence/S07/S07m/README.md) | other owner-clip frames stay private; capture PENDING S24c; no stopwatch (Q22 answered: system-estimated) |
| 6 | 1:58–2:23 | Muse interview, numbers from tools | Workspace chat: Muse asks setup questions; every number chip tagged "tool" | Gate A: MET_AMENDED_Q16 — scale unverified, not setup-validated · numeric contract 10/10 · setup validator 0/10 | "Muse Spark interviews you about the setup, but every number it shows comes from a tool. Our checker flagged zero invented numbers across 30 replayed turns — on recorded scenes, not validated setups." | [GATE_A.json](../../evidence/S14/GATE_A.json) `/counts` (10/10, 0/10, 30/30, 0) | capture PENDING S24d |
| 7 | 2:23–2:39 | Virtual lab + library | /library card tagged SIMULATED; Mystery-g practice card copy; cut to /lab blind round; sidebar search result | SIMULATED library traces · Mystery-g practice ≠ blind /lab · Muse Open: 1 live dev call, 1,176 tokens, Meta cost UNAVAILABLE | "The library holds simulated experiments, clearly labelled. The Mystery-g card is practice at Earth g; the lab draws a hidden g each session for a real blind test." | [library-copy.mjs](../../Build/web/src/app/(public)/library/library-copy.mjs); BENCHMARK `meta_s16e_total_tokens`, `meta_s16e_latency_s` (2.52345 s), `meta_s16e_cost_usd`; [lab-375.jpg](../../evidence/S10/ui/lab-375.jpg) (reference only) | deployed screens PENDING S23 + Gate D (S22f/S22j) + S24e; if Gate D fails, library path only |
| 8 | 2:39–2:50 | Cost + honest misses | Checklist card (static, project-authored) | Modal billed to date: $0.599594 · Gate M ✗ · Gate RS ✗ · Gate A amended · scale unverified | "Modal bill so far: under a dollar. Not proven: no calibrated metric source, so no physical-accuracy claim." | BENCHMARK `modal_month_to_date_billed_usd`, Gates | card PENDING S24f |
| 9 | 2:50–3:00 | Close | Judging URL + repo + BENCHMARK.md | Built Oct 27 – Nov 4 · every number links to BENCHMARK.md | "Every number you saw is a pointer into the repo's benchmark. Try it." | [BENCHMARK.md](../../BENCHMARK.md) | URL PENDING S23 (written go-ahead); public repo PENDING owner |

Timing: 12+22+14+25+25+20(5b)+25+16+11+10 = 180 s (3:00). Beat 5b added by trimming beat 2 (−6), 3 (−6), 7 (−4), 8 (−4).

## SWAP BLOCK — beat 5b numbers (FINAL analyses S07h v1 + S07k v2 + S07m v3; edit only here)

Label: **MEASURED** (real SAM 3.1 tracks; user-declared scale 0.2028 m book edge; phone clock NOT externally verified; rolling shutter assumed). Reference g = 9.79 m/s² (local, comparison only). **Caveat to say/show:** v2 and v3 are second/third analyses chosen after v1 failed (forking paths), same scene/operator/phone; low power. Sources: [S07h](../../evidence/S07/S07h/README.md) (v1, frozen, 11 clips: 9 measured, 2 abstain; OWN12 excluded; held-out 0/9 at the old 6 px rule), [S07k](../../evidence/S07/S07k/README.md) (v2), [S07l](../../evidence/S07/S07l/README.md) (the 6 px rule was miscalibrated; blur/rotation and centroid drift present), [S07m](../../evidence/S07/S07m/README.md) (v3 pre-registered predictive chi-square).

Show on screen (numbers copied from the S07m table, g ± u in m/s²):

| clip / window | g ± u | v3 predictive check | on-screen status |
|---|---|---|---|
| OWN01 hero, v1 | 10.96 ± 0.77 | FAIL (p 0.0065); v2 abstains (7 < 8 frames) | **not validated** |
| OWN05, v1 | 8.62 ± 1.28 | PASS | conditional |
| OWN05, v2 | 9.62 ± 0.74 | PASS | conditional |
| OWN07, v2 | 9.51 ± 0.93 | PASS | conditional |
| OWN08, v2 | 8.82 ± 0.27 | PASS — but ~3.6 u below 9.79 | conditional; passing ≠ accurate |
| OWN02, v2 | 7.27 ± 3.07 | PASS (20.5 px held-out; low power) | conditional; huge u |

Not shown as results: OWN06 (release misdetected), OWN03/04/09 (v3 FAIL), OWN10/11 (abstain), OWN12 (excluded). Repeat drops 05 v1 (OWN05/07/08): 8.62/8.72/8.82, about 1 m/s² low (S07h).

Spoken summary (20 s): the system finds release and impact itself — OWN07 t 0.433 ± 0.027 s, h 0.923 ± 0.010 m, g 9.84 ± 1.24 (conditional, approximate, not calibrated); hero track ends before impact → lower bounds only (t ≥ 0.267 s, h ≥ 0.374 m) and its 10.96 ± 0.77 fit fails its own check; scale is user-declared. Never say "validated", "accurate" or "matches g"; the only permitted word is "conditional" (S07m: no clip is an unconditionally validated measurement of g). No stopwatch: Q22 answered (Oct31) — the demo shows the system's own estimate; never invent a stopwatch or tape-measure reading.
Owner-clip rights: Owner approved short face-free OWN07 snippets for the public video (receipt evidence/owner/S24/OWN07-PUBLIC-SNIPPETS-2026-10-31.md); other owner clips stay private (CLIPS.md; trims local, gitignored).

## Shot list — footage, licence, credit

| Shot | Source | Creator / licence | Credit line (end card) | Rights status |
|---|---|---|---|---|
| PD02 (beats 1–2) | clips.csv `PD02` (Pexels 35640361) | Alexandre Henry Alves · Pexels License | Alexandre Henry Alves - Foucault Pendulum Swing in Grand Hall - Pexels (Pexels License); no endorsement implied | S02e approval = local pipeline only; people/depicted rights review noted |
| RM02 (beat 3) | clips.csv `RM02` (Pexels 6671552) | Andy Barbour · Pexels License | Andy Barbour - Tracking shot of empty classroom - Pexels (Pexels License); no endorsement implied | S02e local only |
| ST03 (beats 4–5) | clips.csv `ST03` (Pexels 12723966) | Roman Odintsov · Pexels License | Roman Odintsov - Woman dropping apple on ground - Pexels (Pexels License); no endorsement implied | S02e local only; depicted person |
| Workspace, /library, /lab, sidebar, cards (6–9) | project-authored screen capture | own event work | — | needs S23 deploy or local dev capture (S24c-f) |

**Rights hold:** [APPROVAL.md](../../evidence/owner/S02/APPROVAL.md) approves these clips for local pipeline work only and retains the hold on *public raw media redistribution*. Showing clip frames in a public demo video needs a separate owner go-ahead: **PENDING owner Q19** (STATE; default if silent = B). Under B (and until Q19 A): beats 1–5 use track/fit plots and overlays only (no raw frames); keep the source credits on the end card. All three video clips are Pexels License; no CC BY / CC BY-SA clip (BN01, PD04, PD06) appears — if one is added, use the [ATTRIBUTION.md](../../ATTRIBUTION.md) form: creator — title, licence name + link, source URL, "adapted" note.

End-card credit block (matches [ATTRIBUTION.md](../../ATTRIBUTION.md) and clips.csv `attribution`):

```text
Footage (Pexels License, no endorsement implied):
Alexandre Henry Alves — Foucault Pendulum Swing in Grand Hall · Andy Barbour — Tracking shot of empty classroom · Roman Odintsov — Woman dropping apple on ground
Models: SAM 3.1 (SAM License) · MapAnything (Apache-2.0 code) · Muse Spark 1.3 / Muse Wonder 1.0 (Meta Model API) · Muse Spark Open (Baseten)
```

## Captions (copy-paste, one line per beat)

```text
[0:00] Real video → measured track → simulation → honest error
[0:12] SAM 3.1 · 439/439 frames tracked · Modal A10G
[0:34] Floor-normal spread 0.04393° (bootstrap 1 sd) · Metric scale: ABSTAINED (unverified)
[0:48] Image-space g fit: ±0.07367 relative (1σ, n=19) · precision, not accuracy
[1:13] Gate RS: NOT_MET — diagnostic RMS 0.1982 image heights, 7/466 frames scored
[1:38] ≈ SYSTEM-ESTIMATED · MEASURED (conditional) · t 0.433 ± 0.027 s · h 0.923 ± 0.010 m · g 9.84 ± 1.24 m/s² (from t, h) · scale user-declared 20.28 cm · phone clock unverified · approximate, not calibrated · hero: lower bounds only t ≥ 0.267 s, h ≥ 0.374 m (track ends f54, before impact) · hero fit 10.96 ± 0.77 fails own check
[1:58] Gate A: MET_AMENDED_Q16 — scale unverified, not setup-validated · numeric contract 10/10 · setup validator 0/10
[2:23] SIMULATED library traces · Mystery-g practice ≠ blind /lab · Muse Open: 1 live dev call, 1,176 tokens, Meta cost UNAVAILABLE
[2:39] Modal billed to date: $0.599594 · Meta cost UNAVAILABLE · Gate M ✗ · Gate RS ✗ · Gate A amended · scale unverified · 4-clip library ✗
[2:50] Built Oct 27 – Nov 4 · every number links to BENCHMARK.md
```

## PENDING register

- PENDING S23 + Gate D (S22f/S22j) — judging deploy URL and deployed screens (beats 7, 9); needs separate written owner go-ahead. If Gate D fails at freeze: library path only, upload limits stated (QUEUE S22 fallback).
- PENDING S24c: captures done, gaps listed in [SHOTS.md](../capture/S24c/SHOTS.md) (no point-cloud viewer, no fit parabola or prediction overlay, DEV /lab disabled).
- PENDING S24d — workspace interview capture (beat 6).
- PENDING S24e — /library, /lab, sidebar captures on the deployed build (beat 7).
- PENDING S24f — edit, end-card, checklist card (beat 8) and final timing.
- PENDING owner Q19 — public use of PD02/RM02/ST03 frames in the video (rights hold above; default B = plots-only); public repo.
- Re-quote check: if any BENCHMARK/evidence value changes, re-run the number check in [REPORT.md](../../Run-System/Runs/S24a-orch146/REPORT.md) before recording.

## Cut list if over time
(Beat 3 VO and beat 7 sidebar clause already trimmed in v3.)
Beat 3 VO → caption only (−8 s); merge beats 8+9 (−10 s); drop sidebar clause from beat 7 (−5 s).

