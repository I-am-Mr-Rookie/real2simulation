# S02c Opus-high continuation — new-source vetting and original-frame evidence (2026-10-27 UTC)

Scope of every "verified" entry: **local image-space tracking / scene-motion feasibility only**. Not physics,
calibration, timebase, owner approval, product use, publication or public-repo redistribution clearance.
All files are UNAPPROVED_CANDIDATE, owner_approved=NO. Frame times are file PTS, not capture time.

## Source vetting (read, not search summaries)

Commons API `imageinfo/extmetadata` read for 16 titles → `S02c-opus-commons-metadata.json` (licence, artist,
credit, description, URL, SHA-1). NASA Image Library `asset` + `metadata.json` read for 3 NASA IDs
(`S02c-nasa-RM05-metadata.json`; FF05/RM06 metadata kept with rejected files). Excluded before download:
simulations/animations (3-double-pendulums, Elastic Pendulum), YouTube-sourced "Bouncing Ball" (ScienceCOLA),
all sports/military/parachute results. Downloads were ordinary GETs; Commons SHA-1 matched for every file
received (`S02c-opus-download-log.json`).

**Rights finding:** Rhetos uploads (FF01/FF02/FF03/BN02/BN03/PJ02/PD01/PD09) are Mathe-AC Lernwerkstatt Aachen
productions; their end card states CC BY 4.0 crediting "Mathe-AC Lernwerkstatt Aachen", while Commons lists
CC BY-SA 4.0 / Rhetos. Attribution for any Rhetos clip should credit both; S02d/S02e should record this.

## Verified (narrow) — new this continuation

| ID | Source / licence | Evidence | Result |
|---|---|---|---|
| PD04 | Commons, MikeRun, CC BY-SA 4.0, 1280×720 | all 600 decoded frames; template track seeded f199 (box 34 px @960w), ±30 px search; `S02c-PD04-track.csv`, 48 inspected crops `S02c-PD04-crops.jpg` | Bob identifiable in all inspected crops; match median 0.89, min 0.49 (1 frame <0.5, hand-occluded release f0–~89). Pivot visible. Dashed overlay line drawn on video. Slow-motion factor unknown. |
| PD06 | Commons, Spheroidite, CC BY-SA 4.0, 1920×1080 | all 280 decoded frames; template track seeded f130 (box 56); `S02c-PD06-track.csv`, `S02c-PD06-crops.jpg` | Bob in every inspected crop; match median 0.93, min 0.83. Top-down view, long pendulum: partial period only; projection/length unknown. |
| PD03 | Pexels, Engin Akyurt (already local, never frame-verified) | all 1793 decoded frames; median-background moving-blob centroid; `S02c-PD03-blobtrack.csv`, 48 crops `S02c-PD03-blobcrops.jpg` | Active end ball centred in all 48 inspected crops (alternates left/right ball; consumer must assign identity). f0 ball partly out of frame. Pexels public-repo redistribution unresolved. |
| RM05 | NASA JSC "Step Inside the Station (4K Clean)", PD-USGov-NASA; local *small* rendition | 60–90 s, every decoded frame (901), LK flow fwd/back check @640×360; `S02c-RM05-flow-60-90s.csv` (adjacent), `-k10.csv` (10-frame baseline); overview `S02c-RM05-60-90s.jpg`; FFmpeg scene>0.25 cuts in window: 0 | 10-frame baseline: 796 moving pairs, single-homography inlier median 0.48 vs fundamental-matrix 0.96; 683 pairs H<0.6 → non-planar, translation/parallax-consistent motion. Adjacent pairs H≈0.98 (baseline too short). Some frames lose all features (close pass ~81 s). Astronauts visible: NASA media guidelines, no endorsement. Microgravity interior, not an Earth room. No scale/reconstruction. |

Previously verified (unchanged hashes): PD02, RM04 → total **6/10**.

## Reviewed and rejected (files moved out of repo to `%TEMP%/s02c-rejected/`, recoverable; not recorded as local)

| ID | Source | Why rejected (from full-decode review sheets) | SHA-256 |
|---|---|---|---|
| FF04 | Commons cup fall, CC BY-SA 4.0 | 201 frames; dark; cup visible falling only ~f20–35 with blur; mostly shattering | ad512d22…1ae7 |
| BN03 | Commons/Rhetos Flummiversuch | camera at floor, ball top cropped, heavy overlays; end card | fa07870b…a7ed8 |
| PD08 | Commons "Pendulum in controlled gravity" | 854×480 mixed edited segments, bob indistinct | 3f4fc06e…f552 |
| PJ02 | Commons/Rhetos Senkrechter Wurf | 10× slow-mo of only 8 original 25 fps frames; overlays; ruler visible | 0268137a…048 |
| FF03 | Commons/Rhetos Zeitsymmetrie | split-screen, reversed, 5× slow-mo; tiny ball | ba2d0284…d60d |
| PD07 | Commons COSI Foucault | bob leaves frame top repeatedly; bystanders | 80516ba1…99cd |
| PD05 | Commons Griffith Foucault, CC0 | handheld camera; bob out of frame after ~f190 (245/343 frames match <0.5) | 14bbfbbf…5833 |
| FF05 | NASA GRC Zero-G Drop Tower | multi-cut documentary; no continuous tracked drop segment seen | 4fa60648…c3f8 |
| RM06 | NASA GRC Space Experiments Lab tour | talking-head/cut-heavy; person-dominated | ef2afe37…5e37 |
| PJ03 | Commons/Rhetos Ballistische Kurve | **not reviewed**: review process killed (memory, 4.8 GB); open | 8a24c5f3…aacf |

Existing locals triaged this run (not flagged): PD01 heavily edited lecture (close-up ruler segment only);
BN01 handheld camera, depicted minor-looking person, small ball. Not verified usable.

## Access limits

Commons `upload.wikimedia.org` returned HTTP 429 for BN03 (once, then OK after 45 s) and PD09 Wagenpendel twice
(Retry-After 600 s); Commons API search then returned 429. Stopped; no bypass, mirror or retry churn. Unfetched
leads: PD09 Wagenpendel; Newton cradle (Kugelstoßpendel TSD CC BY-SA 4.0; "Newton's - Balls" CC BY 3.0;
"Pendolo di Newton" CC0); "Model of Foucault's pendulum 1–3" CC BY 4.0; "Mechanical movement of pendulum clock" CC0.

## Reproduction

`python evidence/clips/s02c_opus_review.py CLIP OUT [width]` → full decode, blob track, sheet;
`s02c_opus_track.py CLIP OUT SEED BOX [margin] [cx cy]`; `s02c_opus_blobcrops.py CLIP OUT WIDTH HALF`;
`s02c_opus_flow.py CLIP CSV START END [STRIDE]`; `s02c_opus_record.py` updates clips.csv/receipt.


## RM02 update (existing local, new measurement)

Earlier adjacent-frame probe (H inlier ≈0.92) could not separate pan from translation. This run: `s02c_opus_flow.py`
on all 426 decoded frames, 10-frame baseline → 416 moving pairs, single-homography inlier median 0.45 vs
fundamental-matrix 0.86; 390 pairs H<0.6 (`S02c-RM02-flow-k10.csv`). Non-planar motion consistent with camera
translation/parallax, narrow flag only; F inliers lower than RM05; no reconstruction/scale; Pexels redistribution unresolved.
Verified total after this flag: **7/10** (PD02, RM04, PD03, PD04, PD06, RM05, RM02).
