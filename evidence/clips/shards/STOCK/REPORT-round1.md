# S02c2 REPORT — STOCK shard (Pexels/Pixabay), PARTIAL: no usable result

- Lane/model: CODEX-2 ownership, S02c owner exception; requested Opus 5.5 high (runtime identity not independently observable). Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No GPU, no uploads, no secrets read (only key-name filter for PEXELS/PIXABAY in .env: none present).
- UTC: start 2026-10-27T22:46:30Z; end ~23:01Z (inside 23:16:30 timebox; no implementation after 23:11:30).
- Base `8c6e486`, branch `run/S02c2`, worktree `C:/Users/HP/.codex/worktrees/s02c2/2026-10-26 - Meta Global AI Developer Hackathon`. Owned writes only: this directory; `test-data/public/shards/STOCK/` was used for provisional downloads, then emptied (media moved to `%TEMP%/s02c2/media/`, hashes below).

## Result

Verdict: **zero usable real Earth fall/bounce/projectile clips from this shard.** It is not S02c success and does not weaken the target of 10 clips. Details, hashes and metadata: [candidates.json](candidates.json).

| ID | Source (page read in browser) | Local file / review | Verdict |
|---|---|---|---|
| ST01 | [Pexels 7237100](https://www.pexels.com/video/girl-tossing-up-a-red-exercise-ball-7237100/), Alena Darmel, Pexels License | sha256 `704327eb…62ded4`, 3840x2160 25 fps, 162 frames 6.48 s; all 162 frames in [ST01-allframes.jpg](ST01-allframes.jpg) | REJECT: ball leaves top edge by ~f55 and never returns; no apex/descent/landing; identifiable minor; gym context |
| ST02 | [Pexels 7034149](https://www.pexels.com/video/dropping-black-balls-on-white-background-7034149/), Tima Miroshnichenko, Pexels License | sha256 `366d0991…7ed5b0d`, 3840x2160 25 fps, 234 frames 9.36 s; [all frames](ST02-allframes.jpg), [f180–233 at 400 px](ST02-f180-233.jpg) | REJECT: many overlapping blurred marbles; balls stay apparently static above floor for 20+ frames (depth on backdrop or edited playback, unresolved); page says "timelapse" so timebase unknown |
| — | Pexels 2469774 (Limpheart Motions, "Indie Game Developer") | not downloaded | REJECT: page says "softbody Tetris shapes" = simulation/render |
| — | Pexels 8798814 (RDNE Stock project) | not downloaded | REJECT: paddle-and-ball catch (sport context) |

[Pexels License](https://www.pexels.com/license/) read 22:57Z: free use, no attribution required, modification allowed; forbids offensive depiction of identifiable people, selling unaltered copies, implied endorsement, redistribution on other stock/wallpaper platforms. Public-repo redistribution of unaltered originals remains unresolved (S02e).

## Checks run (fresh)

- `curl` ordinary GETs of Pexels pages 2469774/7237100/8798814 and a Pixabay search page: **HTTP 403 Cloudflare "Just a moment..." challenge** (22:56:13Z). No retry or bypass attempted.
- Same public pages opened once each in the Codex in-app browser (normal page view, no challenge shown) to read creator/licence/description; the Pexels search page `/search/videos/ball%20dropping/` was viewed once to pick ST02.
- Download endpoints: HTTP 200 video/mp4 for both; `Get-FileHash` re-run after recording = match; `ffprobe` metadata as above.
- Reused `evidence/clips/s02c_opus_review.py` (full decode, PTS check, median-background blob sheet): ST01 162 frames, PTS monotonic, gap 0.04 s. Outputs `ST0x-sheet.jpg`/`ST0x-track.csv` are probe output only; with a moving person or many marbles the blob is NOT a tracked object.
- `ffmpeg tile` full-frame sheets (`drawtext` frame labels failed: Fontconfig missing; sheets are unlabelled, row-major frame order, 14 or 16 per row).

## Ponytail (applied: `C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.2/skills/ponytail/SKILL.md`, full)

- No new scripts or dependencies: reused `s02c_opus_review.py`, curl, ffprobe, ffmpeg, Get-FileHash. No new nontrivial logic, so no self-check needed; candidates.json is data that `python json.load` parses.
- Smallest complete route: read pages, then download only the 2 page-vetted real non-sports leads, then full-rate sheets. Sports/simulation leads were cut at page-read time without download.
- Kept: rights reads before downloads, hashes, original-frame evidence. Rejected media were removed from the branch rather than committing 47 MB of unusable files.
- Skipped: per-frame object tracking (no viable single trajectory to track), Pixabay page vetting (curl 403; no time for a browser pass), "apple falling" and other queries.

## Communication failure and root cause (systematic-debugging applied)

The first session ended after a search-only chat handoff with no REPORT, no page reads and no commit. Evidence: the tool outputs show no failed tool call at that point; the web_search had returned. **Root cause: an agent process error (stopping after search instead of continuing), not a tool or runtime failure.** The only real access failure found is the curl 403 Cloudflare challenge above, observed in this continuation; allowed alternative used: normal in-app browser page view. The chat summary was not run evidence; this file is.

## Limits, risks, next action

- Search snippets and thumbnails were not used for acceptance. ST02 frame interpretation is visual only at 200–400 px.
- Browser page reads are not saved as HTML; the read text is summarized in candidates.json with UTC times.
- Owner question: none.
- Next: Pexels/Pixabay keyword search produces mostly CG, sports or multi-object clips. Better lead: a static-camera single-ball drop or bounce on a plain background (e.g. queries "ball bounce slow motion white background", "rubber ball drop floor"), vetted page-first in the browser. Pixabay still needs a browser-based page read.

Communication compliance: this continuation used no optional narration beyond the required final pointer line; no canonical controls, parent edits, clips.csv, subagents or auto-merge.
