# S24a-draft-orch84 REPORT — DONE (draft scope)

- Lane/model: CLAUDE, anthropic/claude-opus-5-5/high. Coding quota: OpenCodex-managed; not polled.
- UTC: issued 2026-10-30T05:47:23+00:00; work stopped 2026-10-30T06:00:30+00:00. Base main dc742610ef4b2134b00a2ccfddd7c6f49aa239c0.
- Deliverable: media/script/DEMO_SCRIPT_DRAFT.md — 8 beats, 3:00, shot/caption/VO/evidence per beat, truths table, Meta-models table, PENDING register, cut list. Marked DRAFT pending S21/S23.

## Evidence values verified this run (read from files, not memory)
- Gate RS NOT_MET, ST03 7/466, threshold 0.05: evidence/S12/gate-rs/gate-rs.json (result, shortfall_reasons).
- Gate M NOT_MET: candidate 8, eligible 0, metric_approved 0: evidence/S07/S07f/actual-gate-m.json.
- Gate A summary gate_a MET, 10/10 scenes, spark_calls 30, wonder_calls 10, invented_shown_oracle 0: evidence/S14/S14g-fix3-live.json; script labels it "under review" (STATE: S14g PARTIAL pending R-A recheck orch77).
- Muse models: ledger model fields muse-spark-1.3 x30, muse-wonder-1.0 x10 (S14g-fix3-ledger.jsonl); muse-wonder-1.0 x4 (S14b-ledger.jsonl).
- SAM 3.1: facebook/sam3.1 in Build/measurement/runtime/modal_track.py; PD02 frames_observed 439/439 on A10G (S07-chunktrack-orch67/PD02-summary.json).
- MapAnything: facebook/map-anything in Build/gpu/image_spec.py; mapanything_metric_scaling_factor + metric_scale ABSTAIN for RM02/RM04/RM05 in evidence/S05/S05d/RESULT.json.

## Checks (fresh)
- Link resolver (python): 12 unique evidence links, 0 missing.
- Timing assert: 15+30+20+30+25+30+15+15 = 180 s PASS.
- DRAFT marker on line 1: True.
- python Run-System/worker_timebox.py check TIMEBOX.json: TIMING PASS (first attempt failed on empty timestamps from a slow shell read; fixed and amended).

## Ponytail (applied)
- Reuse: one Markdown file; cited existing evidence JSON/ledgers directly instead of new summaries or a generator script. Link check = one-off inline python, no new test file (prose deliverable, no logic shipped).
- Smallest complete: no video, captions file (SRT) or shot list split; tables in one file carry beats/shots/captions.
- Skipped: SRT/caption export, storyboard images, PD02/ST03 clips.csv licence-row verification beyond a count match, S13 SAM 3D evidence (marked do-not-claim/PENDING S18), Modal total cost figure (only per-job ledger linked).
- Risks: Gate A wording must change only after R-A recheck; beat 4/8 have no numbers until S21; judging URL requires separate owner go-ahead (S23). Clip licence rows for PD02/ST03 not individually re-verified.

## Communication
Silent; one completion message to controller chat as authorized. No canonical controls edited. No installs, no secrets read.
Next: after S21/S23, replace PENDING items, re-run link check, then S24c capture.
