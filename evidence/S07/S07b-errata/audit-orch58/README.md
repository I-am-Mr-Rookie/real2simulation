# Committed tracking PTS audit — S07-pts-audit-orch58

Snapshot: `ea0dcc9` (main at dispatch). Scanned all 1,664 committed files under
`evidence/`; recursively inspected structured JSON/JSONL and timestamp-bearing CSV
headers. A separate `git grep` of all committed text found no additional tracking
maps in logs/text (only code, reports, calibration research, and review diffs).

**23 tracking/timebase/derived-trace files: 18 OK, 5 WRONG.** Checked 2,641 timestamp
occurrences, including duplicate `record.frames` and `frame_map` values. Integer
PTS ticks in recovery3 custody/presentation maps and its first suffix PTS also agree.
`audit.json` lists every result, original SHA256, JSON pointer, excluded timestamp
candidate, and source/probe command. `checks.json` validates all five NEW errata
maps and reproduces the old and fixed methods at every distinct map endpoint.

## Sources / independent clock check

Fresh local FFmpeg 8.1.1 `ffprobe`, **entire stream, no packet count limit**:
`-select_streams v:0 -show_entries frame=pts,pts_time:stream=time_base,has_b_frames -of json`.
Saved full probe outputs here; timestamps strictly increasing; comparison tolerance
1 microsecond. This checks file presentation time, NOT physical capture time.

| Clip | Local source (canonical root) | SHA256, freshly verified | Frames |
|---|---|---|---:|
| ST03 | test-data/public/ST03.mp4 | 7239da801ff407cf5ff047fceb82351724ad35985be298ffcb0e4ba1a53df051 | 543 |
| RM04 | test-data/public/RM04.mp4 | 8231fbca041d030f2fc39bd4281af6112e476bf811f548fc9019db53f7cb87ec | 231 |

Correction to handout wording: **clips.csv has no SHA column**. Its clip IDs,
local paths and source URLs were bound to `evidence/clips/S02c-acquisition.json`,
which supplies the full expected SHA256. Existing output source hashes also match.
No media copied into this worktree or committed.

## Every audited file

Paths below are relative to `evidence/`. OK means PTS agrees, not successful tracking.
Failed GPU attempts remain failed even when their maps are OK.

| File | Result | Wrong frame / correction (seconds) |
|---|---|---|
| S07/S07b-errata/RM04-orch40-frame_map.json | OK | — |
| S07/S07b-errata/ST03-orch14-frame_map.json | OK | — |
| S07/S07b-param/RM04-chair-orch40/result.json | WRONG | f11: 0.48 -> 0.44 (map + record) |
| S07/S07b/orch13/result-run10.json | WRONG | f76: 2.569233 -> 2.535867 |
| S07/S07b/orch13/result-run11.json | WRONG | f76: 2.569233 -> 2.535867 |
| S07/S07b/orch13/result-run4.json | OK | — |
| S07/S07b/orch13/result-run5.json | OK | — |
| S07/S07b/orch13/result-run6.json | OK | — |
| S07/S07b/orch13/result-run7.json | OK | — |
| S07/S07b/orch13/result-run8.json | OK | — |
| S07/S07b/orch14/result-run1.json | WRONG | f76: 2.569233 -> 2.535867 (map + record) |
| S07/S07b/orch14/result.json | WRONG | f76: 2.569233 -> 2.535867 (map + record) |
| S07/S07b/recovery3/manifest.json | OK | — |
| S07/S07b/recovery3/presentation-map.json | OK | — |
| S12/gate-rs/ST03-f58-542/result.json | OK | — |
| S12/gate-rs/ST03-f58-83/result.json | OK | — |
| S12/overlay-ST03.json | OK | — |
| S12/prediction-ST03.json | OK | — |
| S13/S13f/live-orch42/raw-result.json | OK | — |
| S13/S13f/live-orch42/segmentation.json | OK | — |
| S13/S13f/replay-orch40/segmentation.json | OK | — |
| S13/S13h/live/segment/raw-result.json | OK | — |
| S13/S13h/live/segment/segmentation.json | OK | — |

One new `*-frame_map.json` here per WRONG file; `errata_for` and
`original_sha256` bind each correction to its accepted input. No accepted file,
existing README or original errata was edited. Previously corrected ST03/RM04
maps are independently confirmed, not replaced.

Old method reproduces f76/f11 exactly. Endpoint f70 happens to be correct; B-frames
do NOT imply every limited probe is wrong. Old ST03 f83 probing would shift f82
and f83, but the committed gate-rs map is already correct. Fixed `_pts` equals the
full-stream probe at RM04 last=11 and ST03 last=70,76,83,542.

## Downstream consumers / historical boundaries

- `Build/real2sim/predict.py::st03_record` explicitly applies original ST03 errata,
  validates its source/original-path/frame set, cross-checks against recovery3,
  then reseals. `prediction-ST03.json` records that errata input; its suffix is
  466 frames (f77 restored). `overlay-ST03.json` and `gate-rs/gate-rs.json` cite it.
- `Build/real2sim/overlay.py::st03_frame_map` uses the independently correct
  recovery3 presentation map. The current prediction/overlay/Gate-RS path already
  uses corrected presentation timestamps; no consumer rewrite needed here.
- `S13/S13f/replay-orch40/segmentation.json` explicitly cites and applies the RM04
  errata; f11 is 0.44. `Build/pipeline/gpu_stages.py::validate_segment` accepts a
  caller-supplied errata map. Its live S13f/S13h outputs have correct maps already
  (source=`live`), not evidence of applying an errata file.
- **Historical, not current corrected seal:** `S12/boundary-ST03.json` retains its
  old f76 diagnostic, 465-frame seal and f77 quarantine. `params-ST03.json` refers
  to that boundary and abstains. They were not silently repaired/resealed. New
  consumers must use the corrected prediction path, not resurrect these older
  boundary/parameter receipts. No old numeric physical result is promoted.
- New orch13/run1 correction maps are not wired into consumers: those are failed
  or superseded attempts, not the accepted orch14/prediction path.

## Exclusions / limits

- S06 `camera_path.time_s` is explicitly `float(i)` in `scene_job.py`, an export
  index clock, not `modal_track._frames` PTS. S05 input extraction is also separate.
  Do not interpret S06 camera index time as verified source PTS.
- Acquisition/research CSV tracks and S02 calibration maps predate or independently
  bypass `modal_track`; synthetic S10/S12 clocks and review reproductions are not
  real tracking outputs. Listed as exclusions, not falsely labelled PTS-verified.
- `S07/S07b/orch13/apps-before.json` is non-JSON CLI inventory text, not a track.
- Audit is exhaustive for **committed evidence at the dispatch snapshot** only;
  ignored/untracked/new concurrent outputs are not covered. Timing correction
  validates neither centroids/masks nor scale/capture clock or Gate M/R/RS.

## Reproduce (no GPU, installs, or network)

```powershell
python evidence/S07/S07b-errata/audit-orch58/audit.py --self-check
python evidence/S07/S07b-errata/audit-orch58/audit.py 'C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon'
python evidence/S07/S07b-errata/audit-orch58/check.py
```

`check.py` expects this snapshot's coverage (23 files / 5 corrections); a newer
snapshot needs an explicitly reviewed new inventory, not relaxed count asserts.
