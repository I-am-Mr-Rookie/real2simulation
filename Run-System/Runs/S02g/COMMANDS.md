# S02g command / operation receipt

All writes target the isolated managed worktree's two owned directories.
Canonical root below is read-only input:
`C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon`.

## Research / custody

- Read canonical DISPATCH and PARALLELISM_POLICY first, then AGENTS, relevant
  README/owner/plan/control/skills instructions; reviewed S05b, S02d and S07a
  reports and retained S07a audit/snapshot. No memory lookup was needed.
- Managed create_worktree from fedd9709; `git switch -c run/S02g`.
- Firecrawl search: `site:commons.wikimedia.org "Freier fall" "Rhetos"`, limit4.
  Four targeted live-request Markdown scrapes, not a broad crawl or agent job.
  Search feedback accepted/refund1. See retrieval-receipt.json.
- Web search: original rope method and 25fps claims; direct primary-source opens.
  No creator messages, login, accounts, contact forms, API-model/GPU calls.
- `Invoke-WebRequest` on original public article HTML extracted its video src;
  `Invoke-WebRequest -Method Head` on that WEBM recorded headers only.
- `Get-FileHash -Algorithm SHA256` and SHA1 on the two retained files;
  assert SHA1 equals original Commons checksum. All matched.
- ffprobe stream/container probe:
  `ffprobe -v error -show_entries format=duration,size:stream=index,codec_name,codec_type,r_frame_rate,avg_frame_rate,time_base,start_time,duration,nb_frames:stream_tags -of json FILE`.
- ffprobe decoded PTS:
  `ffprobe -v error -select_streams v:0 -show_frames -show_entries frame=best_effort_timestamp_time -of json FILE`.
  Python standard-library checks asserted first PTS0, strictly increasing PTS,
  current-source SHA1; counted all deltas. Results retained in JSON, no assumptions
  about physical capture cadence.

## Bounded local visual probes

From canonical media directory, OUT is the owned evidence folder.

~~~powershell
ffmpeg -hide_banner -loglevel error -i FILE -vf 'select=not(mod(n\,200)),scale=480:-1,tile=4x6' -frames:v 1 OUT-overview.jpg
ffmpeg -hide_banner -loglevel error -ss START -i FILE -t DURATION -vf 'fps=2,scale=480:-1,tile=GRID' -frames:v 1 OUT-detail.jpg
ffmpeg -hide_banner -loglevel error -ss TIME -i FILE -frames:v 1 -vf scale=960:-1 OUT-still.jpg
ffmpeg -hide_banner -loglevel error -ss 54 -i FF02.webm -t 10 -an -vf crop=800:700:0:300 -f framemd5 OUT-crop.framemd5
~~~

- Overviews select original frame0 then every200th video frame: nominal
  presentation times 0,8,16,... seconds; black cells are empty montage padding.
- Detail sheets, row-major: FF01 start10/grid4x4; FF02 start46/grid5x6,
  start108/grid4x6, start132/grid4x6. Sampling2fps with FFmpeg FPS rounding;
  these are visual search aids, **not an exact source-frame index receipt**.
  Grid sizes cap the sheet before the requested duration in longer cases.
- Exact-seek stills: FF01 13.20,13.52; FF02 113.20,118.20.
  FF02-113.2 and FF02-113.20 are the same requested time, not two observations.
- All sheets and key stills were actually viewed. Top-down perspective,
  nonuniform edits, step counters, labelled drops and end-card licence inspected.
- FFmpeg crop SSIM on FF01 13.52 and FF02 113.20: All0.876526. Not sufficient
  to certify duplication; no trial deduplication claimed from that scalar.
- Exact adjacent crop MD5 equality at FF02 54–64: 0 of249 pairs,250 frames.
  Rejected exact hashing as a robust detector of edited still/hold content.
- Initial time-label drawtext filter failed parsing the escaped hms expression.
  Corrected by removing optional labels, then extraction exit0; no global
  runtime change. One attempted image read preceded completion and failed;
  subsequent file existence and successful image reads confirmed outputs.

## Verification

- S07a snapshot's three source SHA256 values rechecked against current canonical
  CSV, approval and S02d audit: all3 MATCH, preserved in source-snapshot-check.json.
- Fresh JSON, reference-presence, local-link and owned-path checks recorded in
  verification.json. Git diff whitespace/scope checked before commit.
- Run-system report directory is globally ignored by this repo; force-add only
  this run's explicit PLAN/COMMANDS/REPORT files, never the whole ignored tree.
- No product test suite rerun: no product code/contract/runtime changed.
