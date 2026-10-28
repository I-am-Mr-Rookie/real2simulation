# S02c alternate-source assessment — 2026-10-27 UTC

Q2 authorizes provisional local acquisition, not final use; all three are
unapproved candidates. Source pages and the [Pexels licence](https://www.pexels.com/license/)
were read. The licence permits use and modification, restricts endorsement and
redistribution via stock platforms, and does not itself clear depicted third-party
rights. Raw-file inclusion in a future public repository remains unresolved.

| ID | Source and creator | Local inspection, not a gate pass |
|---|---|---|
| RM04 | [An Empty Classroom](https://www.pexels.com/video/an-empty-classroom-8342689/), Pavel Danilyuk | 3840x2160, 25 fps, 9.24 s. Contact sheet: empty classroom, zoom-dominant with little apparent parallax; wall art/rights and suitability for reconstruction require further review. Scene-only, no calibrated size. |
| PD02 | [Foucault Pendulum Swing in Grand Hall](https://www.pexels.com/video/foucault-pendulum-swing-in-grand-hall-35640361/), Alexandre Henry Alves | 1920x1080, 30 fps, 14.633 s. Contact sheet: moving pendulum bob in public interior; pivot not visible, people present; no scale or capture timebase verified. |
| PD03 | [A Swinging Pendulum](https://www.pexels.com/video/a-swinging-pendulum-6613341/), Engin Akyurt | 2732x1440, 30000/1001 fps, 59.826 s. Contact sheet: Newton cradle, moving balls; source identifies slow motion; factor and scale unverified. The sheet samples only first 16 s, not full playback. |

Source-page dates: RM04 2021 and PD02 January 2026. Pexels download links
returned HTTP 200 video/mp4; metadata and SHA-256 receipts are recorded in
`S02c-acquisition.json`, thumbnails in `RM04-contact.jpg`, `PD02-contact.jpg`,
`PD03-contact.jpg`. No individual clip is asserted fully usable from these coarse
images. Physical continuity, scale/timebase, rights of depicted objects and
final use require further checks; S02e remains the owner approval gate.

Other avenues: [Blocked pendulum](https://commons.wikimedia.org/wiki/File:Blocked-pendulum-slow-motion.webm)
is MikeRun own work, CC BY-SA 4.0, 20 s; one normal GET of its original returned
403, so no local footage or suitability claim. The separate Commons
[pendulum](https://commons.wikimedia.org/wiki/File:Pendulum20191031_1080p_60FPS.webm)
is a simulation and was rejected. No FF03 request, retry loop or access bypass.
The alternate Pexels route works: the blocker is not general network availability.
Further work: identify actual moving-camera room footage and independent real
fall/bounce/projectile footage; assess full continuous segments, acquisition
timebase and scale, resolve Pexels redistribution before any public repo, then
record each individually verified clip. Do not count candidate file totals as
usable clips.
