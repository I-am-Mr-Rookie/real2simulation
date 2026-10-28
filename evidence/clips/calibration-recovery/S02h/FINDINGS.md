# RP03: editor clock recovered; metric trajectory not qualified

**One April18,2025 drop and its replay; zero metric-qualified trials.**
Negative technical qualification is not a measured-g result or a physical gate.

## Custody

Reused S02f's ignored media, no new downloads:
`C:/Users/HP/.codex/worktrees/s02f-research/2026-10-26 - Meta Global AI Developer Hackathon/evidence/clips/calibration-recovery/S02f/media/RP03-impact-240p.webm`.
SHA256 `e72d5406cd74f02dd76ad310adda42b4f1bdff0ec0953efa45b46069faa5fa7c`.
Fresh ffprobe and complete OpenCV decode agree:6,496 frames, first PTS0,
last108.250s. Adjacent PTS deltas16/17ms reflect60fps presentation rounded to
millisecond timestamps, NOT camera capture cadence.
[Full frame diagnostics](frame-diagnostics.csv), [summary](clock-summary.json),
[reproducible script](audit_clock.py). The310x240 left crop excludes the timer;
MAD descriptors are80x60. Whole-film4,868 adjacent identical crop hashes include
slates/holds and must not be counted as duplicate sensor frames.

## What the clock evidence resolves

**Source testimony:** title slate says DJI Osmo Action4 capture240fps,
editing200fps; replay explicitly says same fall at20x slowdown.
[Commons](https://commons.wikimedia.org/wiki/File:Impaktecholot_(Pilotversuch).webm)
also says240fps. [DJI specs](https://www.dji.com/osmo-action-4/specs) support BOTH
normal-video1080p200 and240fps: capability is not recording provenance.
Receipts: [Commons](commons-receipt.json), [DJI](dji-receipt.json),
[visible title/height/QR slates](provenance-slates.jpg).

**Actual decoded pixels, exact zero-based source indices:**

|Frame|PTS(s)|Burned-in editor time(s)|
|---:|---:|---:|
|1145|19.083|0.000|
|1151|19.183|0.005|
|1157|19.283|0.010|
|1163|19.383|0.015|
|1169|19.483|0.020|
|1319|21.983|0.145|
|1324|22.067|0.145|
|1325|22.083|0.150|
|1439|23.983|0.245|
|1445|24.083|0.250|

Read row-major [1145–1174](replay-origin-1145-1174.jpg),
[1320–1349](replay-frames-1320-1349.jpg) and [anchors](clock-anchor-frames.jpg).
These support `editor_time=.005*floor((frame-1145)/6)` in the inspected replay
windows. Six delivered frames per5ms editor increment gives10 editor-frame
advances per presentation second, consistent with200fps editing slowed20x.
Scene crop changes align at1319,1325,1331,1337,1343,1349; compression creates
small within-hold differences, so unequal hashes do not establish unique motion.
Do not extend this local formula through every later hold/card without checking.

The apparent real-time shot initially holds0.000, then moves around704 onward:
[690–719](realtime-frames-690-719.jpg). Thus even this shot cannot globally use
`physical_time=PTS-offset`. [Nearest-crop replay candidates](replay-correspondences.csv)
pair realtime714/720/726 with replay1427/1547/1667.
[Comparison sheet](exact-correspondence-frames.jpg) order is
714,720,726,1324 /1325,1427,1547,1667. Inspected hand/clod appearances support
same-event replay and approximate20:1 editor stretch, NOT exact sensor-frame
identity: encoding differs; hand/background motion can dominate the matcher.

**Irreducible raw-clock alternatives:**

1.240fps capture resampled to200fps preserving wall time: editor seconds equal
physical seconds and20x replay is20x physical slowdown.
2.240fps capture reinterpreted frame-for-frame at200fps: one editor second is
200/240 physical seconds; replay is24x physical slowdown. Each5ms editor step
would represent1/240 physical second, not1/200.
3.Actual200fps capture, with240fps slate mistaken. Camera supports both.

All can yield this200-grid timer and60fps delivery. Native sensor timestamps,
an edit-project/source-frame mapping or an independent physical clock is absent.
The20% time-scale discrepancy is an unresolved systematic alternative, NOT a
small timestamp-jitter error bar. Do not pick one using expected Earth gravity.
Original Commons upload is an edited WEBM, not authenticated native DJI MP4.

[Creator article](https://www.rhetos.de/html/lex/impaktecholot.htm) reports
inconsistent optical/acoustic times and~0.03s timer resolution, unlike visible
5ms ticks. [Paraphrase receipt](creator-source.json) retains specifics.
Edited audio/soft-clod impact delay cannot independently certify the sensor clock.

## Rope height versus identifiable projection

Read/reused S02g FINDINGS/source evidence; did not repeat FF01/02 research.
It describes nonstretch packing rope with metal weight lowered **from railing
top to ground**, then laid horizontally and measured with folding rulers,
approximately9m. RP03's comparison slate says9.00m. This is a legitimate
non-gravity-derived physical-length claim, not calibrated metres-per-pixel.
RP03 hand/clod are above/outside the rail; neither rope endpoint/readout is
co-registered with clod centre at release/impact. Release height, ground point,
centre-of-mass offsets, transfer between dates and uncertainty are not supplied.
Do not silently substitute rail-to-ground length for actual clod travel.

Visible nearby silver rails, path below and vegetation establish top-down depth
variation, not known dimensions in the vertical fall plane. The clod shrinks
substantially and view/railing alignment changes with camera motion. A ground
homography maps ground points, not airborne height. Hand/rail dimensions are
unknown; lens distortion, pose and stabilization are uncalibrated.

Even granting matched projected endpoints on a fixed vertical line, two known
metric endpoints do not fix its1D projective map. For normalized image-line
coordinate x with endpoints0,1 and known height H, the family

`z_k(x)=H*x/(1+k*(1-x)), k>=0`

preserves both endpoint heights but changes interior positions/accelerations.
This is a mathematical ambiguity counterexample, NOT fabricated candidate
positions or physics output; the script self-checks distinct midpoint mappings.
A fixed pinhole camera restricts to a fractional-linear mapping on a line;
[OpenCV's primary camera model](https://docs.opencv.org/5.0/main_modules/calib.html)
documents perspective projection. A third independent collinear metric reference
or independently established vertical vanishing point can remove the remaining
1D freedom, with identified endpoints and lens/pose corrections. None is verified.

This does NOT prove every top-down method impossible. An endpoint-only method
could use independent H, release-to-impact time and verified initial vertical
speed without any pixel scale; **that particular method** needs corresponding
endpoints and clock, both missing here. A joint rational trajectory/projection
fit may impose constant acceleration along a fixed vertical line and use
independently anchored metric endpoints and clock to constrain the projective
freedom, without assuming numerical Earth g. Its identifiability/conditioning
and camera-motion model must be demonstrated, not presumed. No such fit was
run; this run forbids fitter/g output and current S07a v1 excludes this mapping.

## Actual contract and suitability

Read retained S07a `Build/measurement/README.md`: **continuous pre-impact
partial flight is allowed**; it does not mandate release-to-impact coverage.
Its scale schema requires an independent constant in-plane m/px and uncertainty;
homography/world mapping is explicitly outside v1. Capture mapping must be
verified. RP03 provides visible partial descent within one shot, potentially
useful for qualitative/pixel tracking subject to applicable approval. This
audit does not certify all contact/free-flight boundaries or supply a track.

**Current metric suitability: NO.** Conditional projective/endpoint research
is possible only after native/edit clock provenance, rope-to-motion endpoint
transfer/uncertainty and a validated camera/projection method are supplied.
Accepting creator testimony alone permits, at most, explicitly assumption-labelled
editor-time pixel-motion research, not independently calibrated gravity.
No held-out split, calibrated coordinates, g, three-trial claim, metric approval,
CSV change, S07a completion or Gate M is produced. Unknown uncertainty stays unknown.

## Rights

Rhetos / mathe-AC Lernwerkstatt Aachen, *Impaktecholot (Pilotversuch)*,
April18,2025; [Commons source](https://commons.wikimedia.org/wiki/File:Impaktecholot_(Pilotversuch).webm),
[CC BY-SA4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Embedded endcard says CC BY4.0: retain Commons' stricter file-specific BY-SA
condition, no relaxation inferred. Sheets are documentary frame-selection,
resizing/tiling adaptations credited here under CC BY-SA4.0; no endorsement.
No public redistribution approval inferred. Source receipts are paraphrases
and metadata, not copied full creator/manufacturer articles.
