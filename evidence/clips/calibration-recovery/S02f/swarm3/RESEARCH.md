# S02f-swarm3 source recovery — no approval-ready Earth candidate

Research date: 2026-10-28. Existing S02f RP01/RP02/RP03 and recovery2 NASA families were not reacquired. No footage was downloaded, uploaded, or edited.

## Result

No new candidate satisfies all four gates simultaneously: (1) an Earth 1-g free-fall trajectory in the camera frame, (2) a metric image-plane scale, (3) a physical capture clock mapped to frames, and (4) an allowed, usable, uncut trajectory with independent-trial provenance. The strongest new primary-source lead is the NASA Glenn drop-tower dataset, but it records object motion inside a freely falling rig (near-zero relative gravity), not an Earth-g trajectory; its public page does not expose an uncut asset for reuse.

## Evidence table

| ID / source | Metric scale | Physical clock | Trajectory / independence | Rights | Disposition |
|---|---|---|---|---|---|
| NASA Glenn CELERE / drop-tower challenge: [past challenges](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/education-and-outreach/past-drop-tower-challenges-and-competitions/) | NASA states a 30 m / 100 ft tower; the 2.2 s tower page states 24 m / 79 ft. This is rig travel, not a calibrated image-plane scale for the tracked object. | NASA states test videos at 30 fps for the challenge data. This is a declared delivery/capture rate for that program, unlike a guessed file fps. | Video is of water/object motion during a drop while the experiment and camera fall together; NASA explicitly describes apparent near-weightlessness. It cannot provide Earth-g acceleration in the camera frame. Participant-specific videos are not a public uncut asset in the cited page. | NASA media are generally usable subject to NASA media guidelines; the specific participant video/third-party content needs asset-level confirmation. | HOLD/REJECT for S02f Earth-g input; useful falsification of “30 fps + 24 m drop = calibrated trajectory.” |
| NASA/CWRU ALB paper, [NTRS PDF](https://ntrs.nasa.gov/api/citations/20150019482/downloads/20150019482.pdf?attachment=true) | Primary paper states approximately 24 m tower, 3 mm beads, and a fixed 13±0.5° plate angle. These are apparatus facts, not an image-plane calibration for the liquid front. | Primary paper identifies Sony HDR-CX260V/W and states 30 fps at 1920x1080/60p. It also says the video was edited before analysis, so source cadence is not equivalent to an uncut delivery timeline. | 19 successful trials are reported, but the measured phenomenon is capillary liquid motion in a rig in microgravity; relative free-fall cancels Earth g. No usable uncut trajectory file or frame-to-physical-time receipt is supplied with the paper. | NTRS paper is primary evidence; footage rights are not granted by the paper. NASA generic guidance is not an asset-specific licence for a university/NASA experiment video. | REJECT as Earth-g trajectory; retain only as a source-backed calibration/clock falsification lead. |
| University of Alaska Anchorage, [Physics Demonstrations](https://www.uaa.alaska.edu/academics/college-of-arts-and-sciences/departments/physics-and-astronomy/demo.cshtml) | Page lists a “Free Fall” pair-of-objects demo but gives no measured ruler, known-size witness, or camera geometry. | Page says high-speed camera, but no fps or trigger/frame mapping. | Likely visually relevant, but no uncut/continuous trajectory or independent trial metadata is provided on the source page. | Explicitly CC BY-NC-SA, which is outside the allowed licence set (NC/SA). | REJECT on rights before physics qualification. |
| NASA Apollo 15, [hammer–feather source](https://science.nasa.gov/resource/the-apollo-15-hammer-feather-drop/) | NASA source states approximately 1.6 m release height. | No physical camera clock or frame mapping is stated in the source text. | Lunar, not Earth, free fall; public demonstration footage is not an Earth-g candidate and is not an uncut calibrated trial. | NASA source, but mission footage asset-level terms still need confirmation. | REJECT: wrong body and missing clock. |
| Pexels/Pixabay falling-video collections: [Pexels](https://www.pexels.com/search/videos/falling/), [Pixabay](https://pixabay.com/videos/search/falling%20balls/) | Search results expose generic stock clips, not measured apparatus dimensions or camera geometry. | No physical capture clock/trigger metadata in the collection results. | Promotional/stock clips do not establish uncut release-to-impact continuity or independent trials. | Platform licence is not enough to infer physics metadata; no candidate was selected. | REJECT; no evidence to justify downloading or using a clip. |

## Falsification notes

- A declared 30 fps is a capture-clock lead, not a metric scale. A 24–30 m tower height is a rig-level distance, not pixels-to-metres for an object in a camera attached to the rig.
- In a drop tower, the camera and test object share free fall. The observed internal motion is near-zero-g relative motion, so fitting it as Earth (g) would be physically wrong.
- “3 mm beads,” a plate angle, or a stated release height is not a substitute for a coplanar image-plane witness and uncertainty. Known-size objects outside the tracked plane do not calibrate projective scale.
- A paper saying “30 fps” and “edited” does not prove an uncut source file, exact frame numbering, dropped-frame behavior, or a stable timebase. No such mapping was invented.

## Best safe route

Do not promote any new lead to S07a or Gate M. If the controller wants one next bounded route, request a rights-cleared original NASA participant drop file plus its raw-frame/camera receipt, then verify whether the camera is fixed to the rig (which would still disqualify Earth-g fitting) or independently observes a falling object against a stationary metric background. Otherwise, keep the existing small-sample fallback locked and do not spend compute.

## Source coverage limit

This was a targeted primary-source search, not an exhaustive catalogue. Wikimedia Rhetos/NUSTEM/GetAClass families were intentionally skipped because S02f already audited them. No claim is made that no suitable public footage exists.
