# S02c2 REPORT — round 3 (STOCK continuation) — DONE (bounded STOCK shard investigation complete)

- Status clarification (controller acceptance at `78e2317`, recorded ~23:27Z): DONE means the bounded STOCK shard assessment is complete per QUEUE S02c2 (source/rights/frame evidence or concrete no-usable-result). It is NOT a measured/calibrated g, NOT S02c parent success, NOT a usable-clip count increase and NOT owner/S02e approval. ST05 remains HOLD and ST04 REJECT with all limits below unchanged. No further searches needed for this shard. Status was PARTIAL in commits 2eace70–78e2317; history kept.

- Lane/model: CODEX-2 ownership, S02c owner exception; requested Opus 5.5 high (runtime identity not independently observable). Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No subagents, no GPU, no uploads, no secrets read.
- UTC: start 2026-10-27T23:17:36Z (fresh session); stop-new-work 23:42:36Z; end: see last commit time.
- Base `d6eedf5` (not amended); branch `run/S02c2`; same isolated managed worktree. Round-2 preserved first as [PLAN-round2.md](PLAN-round2.md), [REPORT-round2.md](REPORT-round2.md), [candidates-round2.json](candidates-round2.json) (scaffold commit `2eace70`, before any search). Owned writes only under `evidence/clips/shards/STOCK/`; media kept outside Git in `%TEMP%/s02c2/media/`.

## Result

**One new real source family/creator frame-reviewed and tracked (ST05), verdict HOLD — not counted as usable.** Zero usable clips added; not S02c success; target of 10 unchanged. Details: [candidates.json](candidates.json).

| ID | Source (page read in in-app browser) | Local file / review | Verdict |
|---|---|---|---|
| ST05 | [Pexels 7117951](https://www.pexels.com/video/man-holding-a-orange-7117951/), Katrin Bolovtsova, Free (Pexels License), orig 2160x4096 0:18, page tag "Slow Motion Video" | rendition labelled 338x640 decodes as 226x426, sha256 `e0972b40…5d8b1c7e0`, 473,531 B, 30p 533 frames, 0 exact repeats. Six tosses of one orange; [f12–59](ST05-f012-059.jpg), [f278–309](ST05-f278-309.jpg), [track (all frames)](ST05-track.csv) | **HOLD**: static camera, plain background, single object, unoccluded parabolas; six trials a = 1102–1159 px/s² (mean 1128.6, sd 21.6, 1.9%), rms 0.16–0.32 px — but probable slow motion (page tag), playback factor and scale unresolved |
| ST04 | [Pexels 6287596](https://www.pexels.com/video/dropping-an-egg-on-a-wooden-tray-6287596/), Klaus Nielsen, Free | 640x360 25p, sha256 `1e72b639…3efd1e6`; [f0–11](ST04-f000-011.jpg) | **REJECT**: top-down camera (fall along optical axis), egg visible ~3 frames before crack |
| — | Pexels searches "ball bouncing floor", "falling to the floor", "dropping egg", "tossing ball in the air", "bouncy ball"; Pixabay search "dropping ball" (one view each, link lists only) | — | No other non-sports single-object lead: sports, CG/animation/flags, ball pits, coins, liquids. Pixabay 63040 "newton cradle pendulum" (collision/pendulum, not fall; unopened) and 18684 "tower ball drop abstract" (title suggests CG; unopened) noted only |

### ST05 measured facts and limitations

- Measured (ST05_track.py): per-toss quadratic fits on free-flight frames 22–44, 104–122, 192–214, 282–303, 373–395, 472–492: a = 1105.6, 1128.2, 1102.3, 1159.2, 1138.1, 1138.1 px/s² at container 30 fps; rms ≤ 0.32 px; 0 exact-repeat frames in the whole file.
- Estimate, not measurement (both scale and timing assumed): orange 6.5–9 cm over 28–31 px gives ~2.4–3.6 m/s² (~0.24–0.37 g). If that held, a hypothetical slow-playback TIME factor would be sqrt(1/fraction) ≈ 1.6–2.0× (the 2.7–4× in commit 62e31c1 was the acceleration ratio, not the time factor; see Errata). Consistent with the page's slow-motion tag only qualitatively. No known-size reference; capture rate undocumented.
- Other limits: hand toss (v0 ≠ 0) and catch; segment endpoints chosen by reviewer (sheets + second differences); depth motion unmeasured; small re-encoded rendition, not original; identifiable adult (Pexels: no offensive depiction/implied endorsement); public redistribution unresolved (S02e); portrait frame.
- Possible use, for the integrator to decide: stronger "unknown timebase / Mystery-g" candidate than ST03 (no cadence repeats, 6 consistent trials). While the playback factor is UNKNOWN, any g output from it must abstain; a calibrated g would require resolving BOTH the playback factor and the scale.

## Checks run (fresh, this round)

- In-app browser (normal page views, no challenge, no bypass): 4 Pexels search pages, Pexels 6287596 and 7117951 pages; rendition URLs read from page HTML. One scripted multi-search call timed out in the browser REPL ("js execution timed out; kernel reset") and one page read hit "CDP operation exceeded its deadline before command dispatch"; both recovered by a single normal re-read, no retry churn.
- `curl` GETs: 6287596 sd 640x360 → HTTP 200 video/mp4 884,333 B (23:20:17Z); 7117951 sd → HTTP 200 video/mp4 473,531 B (23:21:08Z). `Get-FileHash` SHA256 and `ffprobe -count_frames` as above.
- ffmpeg `select/scale/tile` sheets (row-major, frame ranges in file names).
- `python ST05_track.py <clip> ST05-track.csv 22-44 104-122 192-214 282-303 373-395 472-492`: self-check asserts passed for all six; first version (toss 1 only) gave the identical 1105.6 px/s² / 0.23 px, a regression check after generalising. candidates.json: `json.load` ok; `git diff --cached --check` clean.

## Ponytail (read and applied: `C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.2/skills/ponytail/SKILL.md`, full)

- Reused curl, ffmpeg/ffprobe, Get-FileHash and the ST03 tracker pattern; one ~35-line `ST05_track.py` added because ST03_track.py is hard-coded to the apple clip's frames/colour/ROI. It has an assert self-check; no new dependency.
- Smallest bounded work: small renditions only, no 4K/original download, ST04 rejected after a 12-frame crop. Skipped: no-search Pixabay this round, Pexels 7100101 (multi-egg), ST01–ST03 and rejected Pixabay IDs not revisited, primary ST03/NASA review not duplicated.
- Risk: both HOLD clips (ST03, ST05) are probably slow motion with unresolved factor and assumed scale; neither supports a calibrated g claim (abstain unless both are resolved).

## Communication compliance

Silent workflow followed; PLAN/REPORT scaffold committed before search; no control/canonical edits, no merge, no subagents; final chat is one pointer line.

## Next action

Integrator: decide whether ST05 (preferred over ST03) enters as an unknown-timebase Mystery-g example. Further STOCK work should target real-time (non-slow-motion) footage with a known-size reference.

## Errata (controller review, corrected in-timebox ~23:26Z; history kept in commits 62e31c1/14d31c8)

- Commit 62e31c1 stated "~2.7–4× slow playback" (and candidates.json said "consistent with e.g. 120->30 fps conform"). That was the acceleration ratio g/a, not the time factor. Correct hypothetical time factor: sqrt(1/0.37)–sqrt(1/0.24) ≈ 1.6–2.0×; the 120→30 fps (4×) remark is withdrawn. Scale and timing both remain assumptions, not measurements.
- It also said ST05 "cannot be a calibrated g measurement unless the slow-motion factor is labelled unknown". Wrong: labelling the factor UNKNOWN requires abstention; calibration requires resolving the factor and the scale.
- No new acquisition, search or script for this correction; fresh checks: `json.load` and `git diff --cached --check` only.
