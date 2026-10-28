# S02a — licensed fall candidates

Checked 2026-10-27 UTC. **Sourcing DONE, clip-set acquisition/qualification NOT DONE.**
Four terrestrial video candidates (three provisional capture groups) plus Apollo 15 are in `clips.csv`. No media downloaded, file metadata measured, owner approval inferred, or product gate run. These are candidates, not five usable benchmark clips.

## Sources and evidence

`S02a-provenance.json` records live HTTP checks, page hashes, revision IDs, media links and file-specific licence markers. Reproduce with `python evidence/clips/capture_s02a_provenance.py`; offline manifest checks: `python evidence/clips/check_s02a_manifest.py`.

Source-page durations/resolutions are separate from empty `file_fps` / `file_duration_s`. `original_source_url` is the creator declaration for self-published Commons work, and NASA's official record for AP15. Original Commons media links are retained; prefer the linked NASA M4V for AP15, with Commons as the rights/provenance mirror. They are different encodes, not interchangeable metadata.

## FF01

[Rhetos's self-published sandbag drop](https://commons.wikimedia.org/wiki/File:Freier_Fall_ohne_Anfangsgeschwindigkeit.webm), dated Oct 16, 2024; CC BY-SA 4.0. No independent scale/capture cadence established. Same creator/date/location as FF02: possible shared footage, **not two independent experiments** until frame comparison. Listing: 1:39, 1920×1080. After Koushik reported access restored, browser playback showed a bridge-height question and a downward railing/ground view with an editor-timer annotation; this is edited explanatory material, not verified raw frames. Full drop/cadence review remains undone.

## FF02

[Rhetos's bridge drop](https://commons.wikimedia.org/wiki/File:Freier_fall_(Staustufe_M%C3%BChlheim_am_Main).webm), CC BY-SA 4.0. The source estimates height from fall duration: using that height to recover gravity would be circular. Current revision's upload comment corrects capture rate from 20 to 25 fps; this is an uploader claim, **not inspected file metadata or proof of real-time playback**. Check cuts and duplicated frames. Listing: 2:48, 1920×1080; shared capture-group warning applies.

## FF03

[Rhetos's time-symmetry ball demonstration](https://commons.wikimedia.org/wiki/File:Zeitsymmetrie_(freier_Fall).webm), CC BY-SA 4.0, dated Dec 6, 2024. Ball size unspecified; rising/falling ambiguity is intentional. Keep as a time-direction/reversal challenge; isolate authentic forward footage before any physical fit. Listing: 44 s, 1920×1080. No independent metric scale, original capture rate or playback verification established.

## FF04

[Pittigrilli's cup drop](https://commons.wikimedia.org/wiki/File:Slow_motion_video_of_cup_falling_on_floor.webm), CC BY-SA 4.0, dated Apr 6, 2022. Independent source, explicit slow motion, unspecified cup dimensions. Only pre-impact motion is relevant; breaking glass is not a bounce model. Listing: 8 s, 480×308. Candidate for tracking/timebase abstention, **not metric gravity** without independent scale and speed factor. Browser playback showed impact/broken glass against a dark background; full pre-impact frame review remains undone.

## AP15

[NASA original](https://science.nasa.gov/resource/the-apollo-15-hammer-feather-drop-2/) and [Commons file-specific PD-USGov-NASA declaration](https://commons.wikimedia.org/wiki/File:Apollo_15_feather_and_hammer_drop.ogv) identify NASA footage. NASA reports an approximately 1.6 m release height, useful only as an uncertain prior, not precise calibration. Browser playback started and showed the lunar scene; full drop/frame-by-frame analysis not performed. Review historical video cadence, deinterlacing, repeats, release/contact frames, perspective and feather visibility. Commons lists a 47 s 654×480 encode; do not apply that metadata to NASA's M4V.

## Rights handling (not a legal clearance)

- All four terrestrial file pages explicitly declare **CC BY-SA 4.0**, not NC/ND. Credit title/creator, source and [licence](https://creativecommons.org/licenses/by-sa/4.0/); identify modifications and preserve notices. Distribute adapted footage under the same/compatible licence. Keep media/adaptation notices separate; do not assume either that ShareAlike automatically relicenses all app code or that a mixed demo is exempt. Review the actual edit before publication.
- NASA's [media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/) supports factual/informational use with acknowledgement, but is not blanket clearance for trademarks, identifiable people, endorsement or promotional use. Keep Apollo factual; revisit those restrictions before a public pitch/video. No terms accepted or permissions sought in this run.
- None is owner-approved; no acquisition, upload, accounts or public distribution occurred. No YouTube, sports, NC/ND, private exports or archive content used.

## Handoff

S02b: source remaining types/rooms, preferably independently calibrated falls if available. S02c: acquire permitted originals, preserve attribution and hashes; do not count variants/replays as independent trials. S02d: inspect local fps/duration, unique-frame cadence, edit boundaries and reference sizes; unknown physical scale means scene-only/stress-only, never invented dimensions. S02e: Koushik's explicit list approval. S07: unknown/reversed/slow-motion timebases must abstain or carry justified uncertainty, not assume playback fps equals capture fps.

**Current evidence supports zero calibrated terrestrial gravity trials.** S02a's source-candidate acceptance is met; S02 as a whole and Gate M remain incomplete. Known Earth/Moon gravity is an evaluation reference, never a source of calibration height or model-authored output.

## Exclusions and access limits

- [Falling ball original plus text.jpg](https://commons.wikimedia.org/wiki/File:Falling_ball_original_plus_text.jpg): useful strobe-image lead, not a video; excluded from candidate count.
- [Pexels geometric-object drop](https://www.pexels.com/video/dropping-a-ball-shape-object-7829008/): not selected; physical authenticity/calibration not established from listing.
- Initial browser Commons preview returned HTTP 429; after Koushik reported recovery, FF01 opened and played successfully. Rhetos explanatory pages still returned 429 through web fetch. Commons file pages were independently retrieved successfully via HTTP and web text. No bypass of authentication or paywalls; creator-site claims are not treated as inspected evidence.
