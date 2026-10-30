# Real2Simulation — 3:00 demo script — DRAFT

**Status: DRAFT pending S21 (benchmark) and S23 (judging deploy).** Not a final script. Do not record from it until S21/S23 land and every `PENDING` below is replaced by a linked measured value or cut.

Rules used: every number links an existing evidence file (paths relative to this file). No number exists → PENDING <row>. Event-only work (built Oct 27 – Nov 4). Footage = licensed clips listed in clips.csv only. Numbers on screen come from fitter/simulator/ledgers, never from a model.

## Current truths (must be said, not hidden)

| Claim | Value | Evidence |
|---|---|---|
| Gate RS (prediction vs real suffix) | **NOT_MET**; ST03 scored 7/466 sealed frames; threshold 0.05 normalized RMS | [gate-rs.json](../../evidence/S12/gate-rs/gate-rs.json) |
| Gate M (calibrated metric inputs) | **NOT_MET**; 8 candidates, 0 eligible, 0 metric-approved (input readiness, not an accuracy failure) | [actual-gate-m.json](../../evidence/S07/S07f/actual-gate-m.json) |
| Gate A (interview never invents numbers) | MET at spec-contract scope: 10/10 recorded scenes, 0 invented shown numbers — **under review** (R-A recheck; S14g PARTIAL) | [S14g-fix3-live.json](../../evidence/S14/S14g-fix3-live.json) |
| Metric scale on real scenes | **Unverified** — scale abstained in floor/gravity/scale fit | [S05d RESULT.json](../../evidence/S05/S05d/RESULT.json) |

## Meta models actually used (from ledgers/code)

| Model | Role | Evidence |
|---|---|---|
| Muse Spark 1.3 (muse-spark-1.3) | interview turns (30 calls in Gate A run) | [S14g-fix3-ledger.jsonl](../../evidence/S14/S14g-fix3-ledger.jsonl) |
| Muse Wonder 1.0 (muse-wonder-1.0) | scene understanding/spec (10 calls in Gate A run) | [S14g-fix3-ledger.jsonl](../../evidence/S14/S14g-fix3-ledger.jsonl), [S14b-ledger.jsonl](../../evidence/S14/S14b-ledger.jsonl) |
| SAM 3.1 (facebook/sam3.1) | object tracking on Modal A10G | [modal_track.py](../../Build/measurement/runtime/modal_track.py), [PD02-summary.json](../../evidence/S07/S07-chunktrack-orch67/PD02-summary.json) |
| MapAnything (facebook/map-anything) | multi-view reconstruction (metric scaling factor recorded) | [image_spec.py](../../Build/gpu/image_spec.py), [S05d RESULT.json](../../evidence/S05/S05d/RESULT.json) |
| SAM 3D Objects | optional path only — **do not claim** unless S13/S18 evidence lands | [sam3d_option.py](../../Build/gpu/sam3d_option.py) — PENDING S18 |

## Beats (total 3:00)

| # | Time | Beat | On-screen shot | Caption (burned in) | Voice-over (draft) | Evidence / PENDING |
|---|---|---|---|---|---|---|
| 1 | 0:00–0:15 | Hook: measure, don't guess | Licensed clip (pendulum PD02) playing, track dots appear | "Real video → measured physics → prediction" | "Real2Simulation turns a real clip into a physics simulation — and tells you how wrong it is." | licence row in clips.csv; PENDING S24c (capture) |
| 2 | 0:15–0:45 | Measurement first | PD02 with SAM 3.1 masks + per-frame track overlay | "SAM 3.1 tracked 439/439 frames (A10G)" | "We segment and track the object frame by frame with Meta's SAM 3.1 on a Modal GPU." | [PD02-summary.json](../../evidence/S07/S07-chunktrack-orch67/PD02-summary.json) (frames_observed 439/439); per-job cost: [gpu-ledger.jsonl](../../evidence/S07/S07-chunktrack-orch67/gpu-ledger.jsonl) |
| 3 | 0:45–1:05 | Reconstruction + scale honesty | MapAnything point cloud in viewer, floor plane, "scale: abstained" badge | "Scale not verified on real scenes" | "MapAnything rebuilds the scene. When floor and scale can't be pinned down, the system abstains instead of guessing." | [S05d RESULT.json](../../evidence/S05/S05d/RESULT.json); viewer shot PENDING S24c |
| 4 | 1:05–1:35 | Fit + uncertainty | Fitter panel: model selection, parameter with interval, residual plot | "Fitted by the fitter, not by an LLM" | "A deterministic fitter chooses the motion model and reports parameters with uncertainty." | numbers PENDING S21 (benchmark); lab UI ref [lab-375.jpg](../../evidence/S10/ui/lab-375.jpg) |
| 5 | 1:35–2:00 | Muse interview (Gate A) | Workspace chat: Muse asks setup questions; numeric reply visibly comes from tool output | "Muse Spark asks; tools supply every number" | "Muse Wonder reads the scene, Muse Spark interviews you — every number it shows comes from a tool, never the model." | [S14g-fix3-live.json](../../evidence/S14/S14g-fix3-live.json) (30 Spark / 10 Wonder calls, 0 invented); label "under review" until R-A passes |
| 6 | 2:00–2:30 | Predict, then check | Sealed-suffix prediction overlaid on ST03 real frames; RMS meter | "Gate RS: NOT MET (7/466 frames scored)" | "We commit a prediction before seeing the rest of the clip. Today it misses: tracking ran out of GPU memory and the ballistic fit has no floor." | [gate-rs.json](../../evidence/S12/gate-rs/gate-rs.json); improved result PENDING S12e/S21 |
| 7 | 2:30–2:45 | Honest misses | Checklist card: Gate M ✗, Gate RS ✗, Gate A (review), scale ✗ | "What we have not proven yet" | "No calibrated metric source passed yet, so we claim image-plane agreement only — not physical accuracy." | [actual-gate-m.json](../../evidence/S07/S07f/actual-gate-m.json), [gate-rs.json](../../evidence/S12/gate-rs/gate-rs.json) |
| 8 | 2:45–3:00 | Close + live link | Judging deploy URL, repo, "built Oct 27 – Nov 4" | "Event-only work · licensed clips · open repo" | "Every number you saw links to evidence in the repo. Try it live." | URL PENDING S23; benchmark headline PENDING S21 |

Timing check: 15+30+20+30+25+30+15+15 = 180 s.

## PENDING register

- PENDING S21 — benchmark numbers (fit accuracy, coverage, runtime) for beats 4 and 8.
- PENDING S23 — judging deploy URL (beat 8). Judging deploy needs separate written owner go-ahead.
- PENDING S12e/S21 — any improved Gate RS result (beat 6); if none, keep NOT_MET wording.
- PENDING S24c — screen captures for beats 1–4.
- PENDING S18 — demo library content / SAM 3D Objects (cut from script if absent).
- Gate A wording: switch "under review" → "MET" only after R-A recheck accepts S14g.

## Cut list if over time
Beat 3 voice → caption only (−10 s); merge beats 7+8 (−10 s).
