# S02d — file metadata and scale audit

Checked 2026-10-27 UTC, against `clips.csv` and the local original files, not source-page metadata. Values below are ffprobe average video FPS and **container** duration, matching the manifest. Container FPS is not proof of capture rate or real-time playback; per-clip timebase warnings remain in `clips.csv`.

| ID | Video fps | Container duration s | Scale / disposition |
|---|---:|---:|---|
| FF01 | 25/1 | 98.960000 | No verified physical dimension; scene-only pending scale |
| FF02 | 25/1 | 167.560000 | Fall-time-derived height is circular; scene-only pending independent scale |
| FF03 | not acquired | unknown | Ball size undocumented; scene-only; edited/time reversal risk |
| FF04 | not acquired | unknown | Cup size undocumented; scene-only; slow-motion factor unknown |
| AP15 | 2997/100 | 82.816149 | ~1.6 m release-height source prior is not an in-plane reference; scene-only; LOCATED_NOT_TRACKABLE |
| PJ01 | 30/1 | 121.188000 | No verified physical dimension; scene-only pending scale |
| BN01 | 240/1 | 41.443000 | Ball diameter unknown; scene-only; capture fps not established |
| PD01 | 25/1 | 132.680000 | Source claims 60 cm pendulum length; numbered physical ruler visible near 70 s; physical plane, uncertainty and applicable segment unverified |
| RM01 | not acquired | unknown | Room; scene-only |
| RM02 | 24/1 | 17.750000 | Room; scene-only |
| RM03 | not acquired | unknown | Room; scene-only |
| BN02 | 50/1 | 40.588000 | Ball diameter unknown; scene-only; slow-motion factor unknown |
| RM04 | 25/1 | 9.240000 | Room; scene-only |
| PD02 | 30/1 | 14.633333 | No verified physical dimension; scene-only pending scale |
| PD03 | 30000/1001 | 59.826433 | No verified physical dimension; scene-only pending scale |
| PD04 | 30/1 | 20.000000 | Length undocumented; scene-only; source labels slow motion, factor unknown |
| PD06 | 29992/1021 | 9.532000 | Dial tick dimensions unknown; scene-only |
| RM05 | 30/1 | 896.833333 | Hatch/handrail dimensions unverified; scene-only |
| PJ03 | 200/1 | 73.405000 | Chalkboard grid size unknown; scene-only; creator's 200 fps / 20x label and timer unverified |
| N1 | 30/1 | 141.909000 | Rig/backdrop dimensions unknown; scene-only; edited documentary timebase unverified |
| N2 | 30/1 | 146.091000 | Rig/backdrop dimensions unknown; scene-only; edited documentary timebase unverified |
| N3 | 30/1 | 147.477000 | Rig/backdrop dimensions unknown; scene-only; edited documentary timebase unverified |
| ST03 | 30000/1001 | 18.133333 | Apple size assumed, not known; scene-only; repeated frames and slow-motion factor unresolved |

`SCENE_ONLY_UNTIL_SCALE_VERIFIED` is a conservative restriction on metric-physics use, not evidence that a clip contains no motion; the existing 10 narrow visual-usable flags do **not** establish a calibrated clip. PD01 is a physical reference candidate only, not a verified metric calibration. The ruler was visually inspected from frame 1750 (~70 s); the wider view at frame 2500 (~100 s) explicitly says `Zeitlupe` (slow motion). Those different views do not establish a common plane, reference size in the motion segment, or known timebase. Do not infer g or other calibration from this note.

The four MP4s N1/N2/N3/ST03 additionally have shorter video-stream durations 141.866667/146.066667/147.433333/18.116667 s, respectively; the manifest records container durations, so use video timestamps/stream duration for frame-level work. Other rows used stream duration when available, otherwise format duration; their checked values matched container/manifest. FF03/FF04/RM01/RM03 have no local file: source duration labels are not file metadata. No download attempted.

NASA specialist report: `shards/NASA/REPORT.md`; ST05 is not in `clips.csv`, remains HOLD per `shards/STOCK/REPORT.md` (unknown scale and slow-motion factor). AP15 remains NOT_TRACKABLE, not a lunar-g measurement. All entries remain unapproved; S02e requires the owner. Stock raw-file redistribution remains unresolved.

## Continuation — 2026-10-28 (supersedes only four rows above)

FF03 and FF04 are **rejected**, not accepted or in the repository. Their previously retained copies in `%TEMP%/s02c-rejected/` were probed without moving or uploading them; each SHA-1 matches `S02c-opus-commons-metadata.json` and each SHA-256 matches the prefixes/suffixes of the prior rejected-media review. `local_path` stays blank. Manifest fps/duration now identify the measured original copies, not availability or approval.

| ID | SHA-1 | SHA-256 | Video avg/r fps | Container duration | Dimensions |
|---|---|---|---|---:|---|
| FF03 | 1703408fb065a893476fc595f881e2a2833783bc | ba2d02848d7e5035ea6a5d23cb96e8498a5ee0052376815e7e21b738a42cd60d | 60/1 | 44.117000 s | 1920x1080 |
| FF04 | 180d75e27afdb1dd35038f10459b0a2c3430a82c | ad512d2293238ce0cd394979d0e22b74f91be31041793bd6884e0ac32f0d1ae7 | 25/1 | 8.046000 s | 480x308 |

Neither stream reported duration; values are container duration, not capture timebase. Existing scene-only/time-reversal/slow-motion cautions remain; rejected review reasons in `S02c-opus-frame-evidence.md` still apply. No physical size or metric calibration inferred.

RM01: [Pexels source page](https://www.pexels.com/video/a-classroom-interior-8342688/) exposes 25 FPS and 0:14 as page labels, not a probed rendition; actual file FPS/duration remain blank. RM03: [Pexels source page](https://www.pexels.com/video/an-empty-room-7056737/) provided no FPS or duration in the bounded page read; no file is retained. Both remain scene-only, unapproved, and missing actual file metadata. Page evidence does not establish redistribution permission. No downloads or access-control bypass.

## RM01/RM03 file probes — 2026-10-28 (Opus 5.5 high continuation)

Under Q2 bounded provisional download: each source page (HTTP 200, plain fetch) lists the normally provided `videos.pexels.com/video-files/<id>/...` renditions. Downloaded only the smallest useful rendition per row to `%TEMP%/s02d-rm/` (outside repository, not retained as accepted media; `local_path` stays blank), then ffprobe; header-only remote ffprobe of the largest rendition cross-checked fps/duration.

| Row | Downloaded rendition | Bytes | SHA-256 | Video fps (r/avg) | Frames | Stream / format duration s | Largest rendition probe |
|---|---|---|---|---|---|---|---|
| RM01 | `8342688-sd_426_240_25fps.mp4` (h264 426x240) | 390782 | `3BD4F2B3CDCA06160E8802609F619B968242BEF3E321E110FDF7A81A7EA18B0D` | 25/1 | 342 | 13.680000 / 13.680000 | uhd 3840x2160: 25/1, 342 frames, 13.680000 s |
| RM03 | `7056737-sd_640_310_30fps.mp4` (h264 640x310) | 1080848 | `1CB017EA6A4D76FCEEEB43B57864755DDBBA82CE84D7AB11AE75ACBA42BCA5FB` | 30000/1001 | 380 | 12.678333 / 12.693333 | uhd 4096x1974: 30000/1001, 380 frames, 12.678333 / 12.693333 s |

Manifest now records file_fps and container (format) duration, as for other rows; RM03 frame-level work should use stream timestamps. Timebase status changed from LOCAL_METADATA_UNVERIFIED to CAPTURE_TIMEBASE_UNVERIFIED: these are delivered-rendition measurements, not capture rate; Pexels may re-encode originals. Page JSON-LD labels (14 s / 13 s) are not used as measurements. RM03 `source_resolution` left blank (largest provided rendition 4096x1974 noted here only). Both rows remain scene-only, UNAPPROVED_CANDIDATE, no scale reference, no redistribution or final-use approval inferred.
