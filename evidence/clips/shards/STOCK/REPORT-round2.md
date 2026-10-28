# S02c2 REPORT — round 2 (STOCK continuation) — PARTIAL

- Lane/model: CODEX-2 ownership, S02c owner exception; requested Opus 5.5 high (runtime identity not independently observable). Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No subagents, no GPU, no uploads, no secrets read.
- UTC: start 2026-10-27T23:07:48Z (original timebox, not reset); stop-new-work 23:32:48Z; work ended ~23:17Z, commit after.
- Base `3bbf2dc` (not amended); branch `run/S02c2`; isolated managed worktree. Round-1 preserved: [PLAN-round1.md](PLAN-round1.md), [REPORT-round1.md](REPORT-round1.md), [candidates-round1.json](candidates-round1.json). Owned writes only under `evidence/clips/shards/STOCK/`; media kept outside Git in `%TEMP%/s02c2/media/`.

## Result

**One new real Earth drop found and frame-reviewed (ST03), verdict HOLD — not counted as usable.** Zero usable clips added; not S02c success; the target of 10 is unchanged. Details: [candidates.json](candidates.json).

| ID | Source (page read in in-app browser) | Local file / review | Verdict |
|---|---|---|---|
| ST03 | [Pexels 12723966](https://www.pexels.com/video/woman-dropping-apple-on-ground-12723966/), Roman Odintsov, Free (Pexels License), orig 2160x4096 0:18 | 720x1366 rendition, sha256 `7239da80…53df051`, 5,457,582 B, 29.97p 543 frames. Release ~f57–58, free fall f58–f76, lands on pillow ~f76–77, small rebound f80–88. [all frames](ST03-allframes.jpg), [f54–113 crop](ST03-f054-113-crop.jpg), [f72–95 landing](ST03-f072-095-landing.jpg), [track](ST03-track.csv) | **HOLD**: static camera, single apple, continuous unoccluded descent, quadratic fit rms 3.64 px — but timebase is unresolved (25p→30p repeats + probable slow motion) |
| — | [Pixabay 105469](https://pixabay.com/videos/ball-coming-down-movement-105469/), Abdullah7 | not downloaded | REJECT: tag "3d"; player shows CG render |
| — | [Pixabay 108869](https://pixabay.com/videos/ball-beach-bounce-108869/), Nova2000 | not downloaded | REJECT: animated beach balls on black |
| — | [Pixabay 212586](https://pixabay.com/videos/glass-ball-falling-ball-drop-ball-212586/), Radiopodziemia247 | not downloaded | REJECT: creator bio "Animacje, grafika 2D/3D"; CG related media |
| — | [Pexels search "dropping ball"](https://www.pexels.com/search/videos/dropping%20ball/) (one view) | — | No new non-sports lead: volleyball/basketball/tennis/golf, balloons, 3D animation |

### ST03 measured facts and limitations

- Measured (ST03_track.py, f58–f76): 14 points, 3 exact-repeat frames dropped, monotonic-descent assert passed; a = **2521.9 px/s²** with unique frames at 1/25 s, rms 3.64 px; apple width median 61 px. With container 29.97 time and repeats kept, rms is 8.9 px (worse), which supports the 25p→30p cadence.
- Estimate, not measurement: if the apple is 7–8.5 cm wide, a ≈ 3.1–3.5 m/s² ≈ 0.32–0.36 g, which suggests ~1.7–1.8× slow playback. The apple size is assumed; there is no known-size reference.
- Other limits: hand release (v0 ≈ 0, ±1 frame); soft pillow landing partly hidden f77–79 (not usable for restitution); re-encoded rendition, not original; motion blur near the bottom (f73, f75 excluded); identifiable adult (Pexels: no offensive depiction/implied endorsement); portrait frame; public redistribution unresolved (S02e). f144–f230 (possible second handling) not reviewed.
- Possible use, for the integrator to decide: an "unknown timebase / Mystery-g" example only if the slow-motion factor is labelled as unknown. It cannot be a calibrated g measurement.

## Checks run (fresh, this round)

- In-app browser (normal page views, no challenge, no bypass): Pixabay 105469, 108869, 212586; Pexels 12723966; one Pexels search page. No curl page fetches, so there were no 403s this round.
- `curl` GET of the page-listed rendition URL: HTTP 200 video/mp4, 5,457,582 B (23:11:42Z). `Get-FileHash` SHA256 and `ffprobe -count_frames` as above.
- `python evidence/clips/s02c_opus_review.py <clip> %TEMP%/s02c2/st03 360`: 543 frames, PTS monotonic, gap 0.0334 s, no non-monotonic steps (person blob, not the apple; sheet kept in TEMP).
- ffmpeg `select/crop/scale/tile` sheets for the reviewed segments (unlabelled, row-major; frame ranges are in the file names).
- `python evidence/clips/shards/STOCK/ST03_track.py <clip> ST03-track.csv`: self-check assert passed; output above. candidates.json: `json.load` ok.

## Ponytail (read and applied: `C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.2/skills/ponytail/SKILL.md`, full)

- Reused `s02c_opus_review.py`, ffmpeg, ffprobe, curl and Get-FileHash. One new ~35-line script, `ST03_track.py`, was added only because the existing median-background tracker locks onto the person. It is scoped to this clip and has an assert self-check (point count and monotonic descent).
- Smallest route: page read before download; rejected renders/animations at page level without download; downloaded the 5.5 MB 720p rendition instead of the 4K original. The review is bounded to f50–f113 plus a whole-clip thumbnail pass.
- Kept: rights/creator reads, hash and metadata, original-frame evidence, explicit assumptions. Removed one redundant crop sheet of my own. Skipped: re-reading the Pexels licence page (round-1 read reused), the Pixabay licence summary page, Pexels 8212402 (water splash), Pixabay search pages, and the f144–230 segment.
- Risk: the ST03 slow-motion inference rests on an assumed apple size; treat it as a flag, not a number.

## Communication failure (systematic-debugging applied)

- Symptom: the first round-2 attempt (and round 1 before it) ended with a chat-only final. In round 2 there was no on-disk REPORT, no page read and no commit.
- Root cause (from evidence, Phase 1): no tool error preceded that final; web_search had returned leads. A search-quota limit on discovery was wrongly treated as a blocker for inspection, and the report went into chat instead of onto disk.
- Fix (verified this session): REPORT scaffold was written and committed first (`471a433`, 23:10Z). Known leads were then inspected with tools; this REPORT was updated with tool-backed results before the final commit. The final chat is one pointer line.
- Communication compliance this session: no optional narration in chat; the orchestrator's acceptance note was the only input. Owner questions: none.

## Next action

Integrator: decide whether ST03 has any role as a labelled unknown-timebase example; otherwise treat it as REJECT for g fitting. Further STOCK search should target Pixabay real-footage queries (e.g., "apple falling", "dropping object" with non-CG creators) and should check the slow-motion labels first.
