# FF01/FF02 original-source calibration forensics

**Research DONE; neither clip is metric-qualified or owner-approved.** A useful
non-circular height lead was recovered, but **no demonstrated joint scale +
capture-time mapping** for a visible fall segment. Do not change S07a/Gate M.

## Primary sources / custody

| ID | Original source checked | Retained evidence |
|---|---|---|
| FF01 | [Commons file](https://commons.wikimedia.org/wiki/File:Freier_Fall_ohne_Anfangsgeschwindigkeit.webm), Rhetos, capture date 2024-10-16; [creator explanation](https://www.rhetos.de/html/lex/freier_fall_ohne_anfangsgeschwindigkeit.htm) | [Commons excerpt](source-0.md), [creator excerpt](source-3.md) |
| FF02 | [Commons file](https://commons.wikimedia.org/wiki/File:Freier_fall_(Staustufe_M%C3%BChlheim_am_Main).webm), same creator/date/location; [detailed original experiment](https://www.rhetos.de/html/lex/freier_fall_(staustufe_muehlheim).htm) | [Commons excerpt](source-1.md), [creator excerpt](source-2.md) |

Four Firecrawl live-request scrapes returned HTTP200. Excerpts omit navigation
and trailing unrelated sections; they are not full-site captures. Creator pages
declare revision 2026-09-20. Independent web search/open also returned the
experiment and Commons sources. Source versions are not laboratory certificates.

Fresh local SHA1 equals each current Commons file's published checksum:
FF01 `51953ee44654b75724dd3f0c8831281e6a2b6e7d`;
FF02 `3c075f4fc34b8cb9a73dfc1ba8f085f92df8df14`.
[SHA256/stream probes](media-probes.json) and [PTS/identity assertions](pts-and-source-identity.json)
tie observations to actual retained media, not similarly titled reuploads.
The creator's embedded FF02 URL is an edited WEBM, not a demonstrated native
Lumix recording. Its [HEAD response](uploader-embed-head.json) has the same byte
length as local FF02 and last-modified 2024-11-01; **length is not a hash match**.
No new remote media body was downloaded.

## Scale: a new lead, not completed calibration

**FF01:** creator explanation measures 1.36s with film-editing software and
calculates approximately 9m using assumed Earth gravity. This remains circular
for recovering gravity. The nearby bridge overview/arrow is explanatory, not
an independently dimensioned same-plane reference.

**FF02:** the English Commons description still describes height inferred from
fall time. However, the linked original German experiment adds **independent
measurement methods** that the previous manifest/audit did not establish:

| Method reported by creator | Independence / usability determination |
|---|---|
| Non-stretch packing rope with metal weight lowered from railing top to ground; rope laid out horizontally and measured with folding rulers; approximately 9.0m | **Non-circular physical measurement claim, highest-value lead.** No retained in-shot plumb-line endpoints/readout, instrument uncertainty, release/impact correspondence or perspective solution. This is not yet a verified pixel-to-metre calibration. |
| 65 stairs; one step measured at approximately 11.5cm; estimated railing contribution about 1m; total approximately 8.5m | Geometric, not gravity-derived, but extrapolates one step and an estimated railing. The visible ruler is on stairs in another shot, not the falling body's plane or a demonstrated reference spanning the fall. |
| Cyclist assumed about 1.7m high, repeated against bridge view | Assumed human size and perspective; not an independently known reference. Reject as calibration. |
| Optical fall estimate approximately 8.7m; acoustic impact estimate approximately 9.2m | Fall-dynamics-dependent; do not use to recover the same gravity. |

All numbers above are **source-reported**, not fitter output or new measurements
by this run. No physical uncertainty percentage is invented. The article mixes
its earlier geometric estimates with the later rope result, and its error
discussion has inconsistent units and timer resolution; do not turn that prose
into a calibrated uncertainty bound.

The camera looks steeply down from the railing; hand, railing, falling bag,
stairs and ground have different depths. The ruler shot cannot supply a global
metres/pixel factor. Even a trusted 9m vertical span does not establish the
projective mapping along this foreshortened motion. Release hand height,
ground endpoint, camera pose/movement, lens model and reference correspondence
remain unverified. The rope claim cannot automatically be transferred to FF01.

## Time: corrected claim versus demonstrated mapping

- FF02 file history: original upload 2024-10-18; replacement 2024-11-01
  explicitly corrects **20 to 25 fps**. FF01's current upload is also Nov1.
- Creator's experiment says Lumix captured 25 images/s and assigns each image
  0.04s. This is explicit first-party testimony, stronger than guessing from
  delivery metadata, but **not independent evidence that a particular edited
  segment preserves every capture frame at that rate**.
- Fresh ffprobe: both retained files deliver 25/1 fps. FF01 has 2,474 video
  frames; FF02 4,189. Every adjacent decoded-frame PTS delta is 40ms.
  These are presentation timestamps only.
- [FF01 overview](FF01-overview.jpg) shows normal-looking motion, a long
  frame-by-frame replay, held frames, dissolves and end cards. Exact-seek
  [13.20s](FF01-13.2.jpg) and [13.52s](FF01-13.52.jpg) show editor clock 0.04
  and 0.36 respectively: **local editor clock consistency**, not a sensor clock.
- [FF02 frame-step sheet](FF02-46.jpg) shows successive labelled fractions
  1/25, 2/25, 3/25, 4/25 held across multiple presentation samples with
  crossfades. Thus global file PTS cannot be capture time. Do not apply a
  guessed constant slow-motion factor to the whole video.
- [FF02 108s sheet](FF02-108.jpg) includes separately labelled fall bursts and
  post-impact holds; [132s sheet](FF02-132.jpg) includes the wood drop and
  another extended hold. A normal-looking burst does not prove unretimed raw
  capture or that editor clocks are independent measurements.
- Exact decoded-crop MD5 probe at FF02 54–64s found **0 adjacent identical hashes
  among 250 frames**, despite visible held/stepped content. Crossfades/encode
  noise make exact equality an inadequate hold detector; this result is **not**
  evidence of 250 independent captured images. [Probe](freeze-probe.json).

No native camera metadata, original sensor timecodes or authenticated
capture-frame/edit-decision correspondence was recovered. Actual capture mapping
remains unverified for both clips. Editor overlay alone does not satisfy it.

## Capture groups / trial independence

Keep `RHETOS_BRIDGE_2024_10_16`. FF02 explicitly presents **three sandbag drops
and one wood drop**; source-reported durations distinguish those events.
FF01 resembles the first sandbag shot, but this run does **not** establish
frame-identical duplication or certify that FF01 is a fourth independent trial.
Compare [FF01 13.52s](FF01-13.52.jpg) and [FF02 113.20s](FF02-113.20.jpg):
bag/hand/railing resemblance, different rendering/positions/labels. A diagnostic
cropped SSIM was 0.876526, **not proof of identity**. FF01's 1.36s versus FF02
first-fall 1.32s labels also prevent treating timer agreement as duplication proof.

Multiple events in one capture group may eventually supply distinct repetitions,
but share the same scale/clock systematic errors. Neither two filenames nor
three edited labels establish independent qualified trials. No extra trial is
credited here.

## Rights and next bounded check

Commons declares both originals **CC BY-SA 4.0**, author Rhetos. Their end cards
instead state CC BY 4.0 and name Mathe-AC Lernwerkstatt Aachen. Preserve both
notices; retain the existing stricter Commons route, not an inferred relicence.
See [local derivative notice](LICENSE-NOTICE.md). FF01/FF02 remain absent from
the scoped owner-approved ten IDs. Forensic inspection is authorized by S02g;
pipeline/metric/final/public use is not thereby approved.

Next technical check, if separately scheduled: establish the rope measurement's
actual endpoints, release/impact locations and uncertainty, then recover
capture-frame provenance for one bounded normal-motion burst. If those records
are absent from public source material, retain abstention; do not derive scale
from time/gravity or derive clock from assumed gravity. No creator contact is
authorized. Replacement discovery remains S02f's separate scope. Controller may
record the **rope-measurement lead** without marking metric scale verified,
changing clip approval, unlocking S07b or counting three qualified clips.
