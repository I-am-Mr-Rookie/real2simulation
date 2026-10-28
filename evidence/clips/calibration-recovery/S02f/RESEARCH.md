# S02f replacement audit — 0/3 metric-qualified

Three new allowed-source **files audited**, not three usable or independent
benchmark trials. No S07a/Gate M pass, fitting, g estimate or owner approval.
Machine-readable review proposal: [candidates.json](candidates.json).

## Ranked disposition

| Rank | Candidate | New evidence | Unmet requirement / action |
|---|---|---|---|
| 1 | RP03 — [Impaktecholot (Pilotversuch)](https://commons.wikimedia.org/wiki/File:Impaktecholot_(Pilotversuch).webm) | April 18, 2025, Rhetos. Embedded slate explicitly distinguishes a **9.00 m nonstretch-rope measurement** from circular optical/acoustic estimates. Capture slate: DJI Osmo Action 4, **240 fps captured, 200 fps edited**; another slate explicitly labels a **20x replay**. These are source claims, not derived slowdown estimates. | HOLD. Camera looks downward; depth changes greatly through descent, so 9 m endpoint height is **not** an image-plane metres-per-pixel reference. No calibrated projection/reference plane or scale uncertainty. Delivery is 60 fps; mapping from capture to edit to replay/transcode has not been verified. Same single drop repeated, not two trials. Best next technical lead, but not fit-ready. |
| 2 | RP01 — [A-level Physics Core Practical](https://commons.wikimedia.org/wiki/File:A-level_Physics_Core_Practical-_Finding_a_value_for_g_using_a_free_fall_method.webm) | NUSTEM, 2016. Producer [notes](https://nustem.uk/activity/measuring-g/) identify a metre rule/bracket and independent g-ball release/impact timer, with 0.01 s display resolution. | HOLD. Reviewed g-ball release around 127–128 s is visible, but ball drops below the lower image before floor contact; no certified continuous release-to-impact segment. Ruler coplanarity/projective error and readable ruler endpoints unverified. 25 fps file cadence is not camera provenance. Apparatus timing is not per-frame mapping. Do not turn separate methods/cuts into independent trials. |
| 3 | RP02 — [Свободное падение](https://commons.wikimedia.org/wiki/File:%D0%A1%D0%B2%D0%BE%D0%B1%D0%BE%D0%B4%D0%BD%D0%BE%D0%B5_%D0%BF%D0%B0%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5.webm) | GetAClass, 2014; Commons cooperation provenance and CC BY 3.0. Actual HD file inspected: real paired-object studio drops near 65–73 s and 105–114 s, distinct from surrounding drawn animation. | REJECT for metric shortlist. No numbered ruler/known object dimension in reviewed drop views; dark objects, low contrast and undocumented slow motion. 24000/1001 delivered fps does not establish capture rate. Endpoints/independence not certified. Do not infer dimensions from wood, ball, backdrop or studio equipment. |

## Local files and custody

All three are downloaded directly from Commons under Q2 provisional research
permission; raw videos are retained only under ignored media/.

| ID | Local rendition | Bytes | Container duration / video cadence | SHA-256 |
|---|---|---:|---|---|
| RP01 | 426×240 VP9/Opus | 20,430,216 | 614.519 s / 25/1 | af01de83df6bd8e7d99ee617981d75e8981cc004acebb2d5014fd2687068b3aa |
| RP02 | Commons original 1920×1080 VP8/Vorbis | 21,092,042 | 229.188 s / 24000/1001 | 00c35bff1d0f5069739f10ac245478e16db1258a08f8f43182ae6f4811f78025 |
| RP03 | 426×240 VP9/Opus | 2,587,661 | 108.268 s / 60/1 | e72d5406cd74f02dd76ad310adda42b4f1bdff0ec0953efa45b46069faa5fa7c |

RP02 SHA-1 **d44ae167a983aacc360811f96cca352827c15a2e**
matches the live Commons original imageinfo response and byte count.
RP01/RP03 are transcodes, so their hashes must NOT be compared to original-file
hashes. Their derivative URLs are recorded by Commons videoinfo receipts.
Full decode of every acquired video returned exit0; this establishes integrity,
not physical suitability or timing truth.

See media-integrity.json, RP0*-ffprobe.json, *-videoinfo.json,
commons-original-imageinfo.json, and [attribution/licences](ATTRIBUTION.md).
The title-source480p image was streamed from RP03's API-listed 480p derivative
to disambiguate the exact 240-capture/200-edit statement; no second full video
was retained. Height slate comes from the local RP03 240p file at 72 s.

## Visual evidence and segment limitations

- RP01-contact-15s.jpg: one sampled frame every15 s, row-major. It is an
  overview, not proof of event continuity. RP01-gball-85-145s.jpg samples at1 fps;
  RP01-gball-126-129s.jpg samples at10 fps. Latter shows release followed by
  exit below frame. Approximate timing only; no event-coordinate annotation.
- RP02-contact-5s.jpg: every5 s. RP02-wood-62-76s.jpg and
  RP02-ball-103-116s.jpg sample at2 fps. They expose cuts, the drop set, and
  absence of an identified dimensional witness, not capture cadence.
- RP03-contact-4s.jpg: every4 s across108.268 s. It shows the real-time shot,
  explicitly repeated slow-motion shot, comparison and capture slates.
  RP03-title-source480p.png and RP03-height-slate-72s.png retain the decisive
  source text. Do not count these views as separate experiments.
- No continuous event has certified release/impact frame numbers, calibrated
  tracks, camera intrinsic/extrinsic parameters or quantitative uncertainty.
  Unknowns in candidates.json stay null/false, not guessed percentages.

## Precise hypotheses tested / stopped work

1. Original FF02's linked source might contain noncircular scale/capture data:
   it does describe rope measurement and25 fps Lumix capture. Preliminary
   summary/pointers retained; **S02g now owns all further FF01/FF02 forensics**.
   Nothing about current segment applicability or independent trials is proven
   here. Previously generated FF sheets are ignored and not used as conclusions.
2. NUSTEM's producer notes and visible ruler might qualify a replacement:
   apparatus is promising, but inspected framing loses the impact and no actual
   camera-clock mapping was found. Independent hardware total time alone is not
   a licence to infer a uniform slow-motion multiplier.
3. GetAClass's educational experiment might contain a calibrated studio shot:
   reviewed footage has real falls but no identified dimensional or capture-time
   witness. Rejected instead of inventing standard object dimensions.
4. New April2025 Rhetos capture might add a separate, high-rate trial: source
   supplies concrete capture/edit/rope information, but top-down projective
   geometry and edit mapping prevent metric qualification.

Firecrawl plus web searches were focused on ruler/size, capture cadence and
primary allowed-source educational footage. Searches returning stroboscopic
still photos, synthetic animations, lunar/ISS, rain, military or commercial/
unlicensed footage were not promoted. Existing FF03/FF04/AP15/ST05 were not
revived; stock ST03 remains tracking-only. Category listings are not an
exhaustive search of all Commons/NASA/Pexels/Pixabay media.

## Next bounded route

Controller first combine S02g's original-side-view result with this audit.
For replacements, prioritize **RP03 only** for a bounded original-edit/camera-
geometry audit; stop if no independent projection calibration is available.
RP01 needs an uncropped suitable shot and actual capture mapping, not another
generic stock search. RP02 should stay rejected absent new creator provenance.
No source contact, posting, new upload or owner filming is implied. Technical
qualification does not replace the existing owner shortlist/metric-use approval.
No new owner question is required merely to restate these shortages.
