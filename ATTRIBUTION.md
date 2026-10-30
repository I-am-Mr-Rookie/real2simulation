# Attribution

Real2Simulation uses only licensed clips. Ledger of every candidate, licence and source: [clips.csv](clips.csv).
Library credit export: [evidence/S18/S18h-credits.json](evidence/S18/S18h-credits.json)
(audit: [S18h-LICENCE-AUDIT.md](evidence/S18/S18h-LICENCE-AUDIT.md)). No endorsement by any creator or agency is implied.

## Footage used

Clips used by the benchmark ([BENCHMARK.md](BENCHMARK.md) → Method → Clips) and the library (S18h credits).

| Clip | Credit | Licence | Source |
|---|---|---|---|
| ST03 | Roman Odintsov — Woman dropping apple on ground | Pexels License | https://www.pexels.com/video/woman-dropping-apple-on-ground-12723966/ |
| BN01 | GolhaMedia — Bouncy ball 240fps (Wikimedia Commons) | CC BY-SA 4.0 | https://commons.wikimedia.org/wiki/File:Bouncy_ball_240fps.webm |
| PD02 | Alexandre Henry Alves — Foucault Pendulum Swing in Grand Hall | Pexels License | https://www.pexels.com/video/foucault-pendulum-swing-in-grand-hall-35640361/ |
| PD03 | Engin Akyurt — A Swinging Pendulum | Pexels License | https://www.pexels.com/video/a-swinging-pendulum-6613341/ |
| PD04 | MikeRun — Blocked-pendulum-slow-motion (Wikimedia Commons) | CC BY-SA 4.0 | https://commons.wikimedia.org/wiki/File:Blocked-pendulum-slow-motion.webm |
| PD06 | Spheroidite — Foucault pendulum utexas motion (Wikimedia Commons) | CC BY-SA 4.0 | https://commons.wikimedia.org/wiki/File:Foucault_pendulum_utexas_motion.webm |
| RM02 | Andy Barbour — Tracking shot of empty classroom (also library, S18h) | Pexels License | https://www.pexels.com/video/tracking-shot-of-empty-classroom-6671552/ |
| RM04 | Pavel Danilyuk — An Empty Classroom (also library, S18h) | Pexels License | https://www.pexels.com/video/an-empty-classroom-8342689/ |
| RM05 | NASA — Step Inside the International Space Station (clean), NASA Image and Video Library | Public domain (US Gov / NASA) | https://images.nasa.gov/details/Step_Inside_the_Station-4K-Clean |

CC BY-SA clips: any adapted footage is identified and shared under the same or a compatible licence, with
source and licence links kept (https://creativecommons.org/licenses/by-sa/4.0/).

Library entries labelled **SIMULATED** in S18h are project-authored and contain no footage.

## Per-asset record (S25b)

Scope: every clips.csv asset used by the benchmark, library or demo script. Licence strings are copied from
clips.csv; the licence pages were not re-fetched in S25b. Raw videos are gitignored (test-data/public/**) and are
never redistributed. Status key: **BLOCKED-for-public** = no public display until the stated condition is met.

| ID | Title | Author | Source URL | Licence | Modifications | Shown publicly? |
|---|---|---|---|---|---|---|
| ST03 | Woman dropping apple on ground | Roman Odintsov | https://www.pexels.com/video/woman-dropping-apple-on-ground-12723966/ | Pexels License | Local frame extraction, SAM 3.1 masks/tracks, reconstruction, derived plots (no re-upload of raw file) | Credit on end card; raw frames BLOCKED-for-public until owner Q19 (default B: plots/overlays only) |
| PD02 | Foucault Pendulum Swing in Grand Hall | Alexandre Henry Alves | https://www.pexels.com/video/foucault-pendulum-swing-in-grand-hall-35640361/ | Pexels License | Local frame extraction, SAM 3.1 masks/tracks, reconstruction, derived plots (no re-upload of raw file) | Credit on end card; raw frames BLOCKED-for-public until owner Q19 (default B: plots/overlays only) |
| RM02 | Tracking shot of empty classroom | Andy Barbour | https://www.pexels.com/video/tracking-shot-of-empty-classroom-6671552/ | Pexels | Local frame extraction, SAM 3.1 masks/tracks, reconstruction, derived plots (no re-upload of raw file) | Credit on end card; raw frames BLOCKED-for-public until owner Q19 (default B: plots/overlays only) |
| BN01 | Bouncy ball 240fps | GolhaMedia | https://commons.wikimedia.org/wiki/File:Bouncy_ball_240fps.webm | CC-BY-SA-4.0 | Local frame extraction, SAM 3.1 masks/tracks, derived plots; if shown, mark as adapted and share under CC BY-SA 4.0 | No. Raw frames BLOCKED-for-public (S02e holds public raw redistribution) |
| PD03 | A Swinging Pendulum | Engin Akyurt | https://www.pexels.com/video/a-swinging-pendulum-6613341/ | Pexels License | Local frame extraction, SAM 3.1 masks/tracks, reconstruction, derived plots (no re-upload of raw file) | No. Raw frames BLOCKED-for-public (S02e holds public raw redistribution) |
| PD04 | Blocked-pendulum-slow-motion | MikeRun | https://commons.wikimedia.org/wiki/File:Blocked-pendulum-slow-motion.webm | CC-BY-SA-4.0 | Local frame extraction, SAM 3.1 masks/tracks, derived plots; if shown, mark as adapted and share under CC BY-SA 4.0 | No. Raw frames BLOCKED-for-public (S02e holds public raw redistribution) |
| PD06 | Foucault pendulum utexas motion | Spheroidite | https://commons.wikimedia.org/wiki/File:Foucault_pendulum_utexas_motion.webm | CC-BY-SA-4.0 | Local frame extraction, SAM 3.1 masks/tracks, derived plots; if shown, mark as adapted and share under CC BY-SA 4.0 | No. Raw frames BLOCKED-for-public (S02e holds public raw redistribution) |
| RM04 | An Empty Classroom | Pavel Danilyuk | https://www.pexels.com/video/an-empty-classroom-8342689/ | Pexels License | Local frame extraction, SAM 3.1 masks/tracks, reconstruction, derived plots (no re-upload of raw file) | Library descriptor metadata only (S18h); no frames. Raw frames BLOCKED-for-public |
| RM05 | Step Inside the Station (4K Clean) | NASA (JSC) | https://images.nasa.gov/details/Step_Inside_the_Station-4K-Clean | PD-USGov-NASA | Local frame extraction, SAM 3.1 masks/tracks, reconstruction, derived plots (no re-upload of raw file) | No. Raw frames BLOCKED-for-public (S02e holds public raw redistribution) |
| PJ03 | Ballistische Kurve | Rhetos; end card Mathe-AC Lernwerkstatt Aachen | https://commons.wikimedia.org/wiki/File:Ballistische_Kurve.webm | CC-BY-SA-4.0 | Local frame extraction, SAM 3.1 masks/tracks, derived plots; if shown, mark as adapted and share under CC BY-SA 4.0 | No. BLOCKED-for-public: embedded third-party end card (Mathe-AC Lernwerkstatt Aachen) licence not verified |

Library (S18h): 2 real-clip descriptors (RM02, RM04; metadata only) and 13 project-authored **SIMULATED** entries (no footage).
Demo script ([media/script/DEMO_SCRIPT_DRAFT.md](media/script/DEMO_SCRIPT_DRAFT.md)) references PD02, RM02 and ST03 only; Pexels
depicted-person limits apply to ST03 (woman) and PD02 (hall visitors).

### Unused clips (in clips.csv, not used or shown)

FF01, FF02, FF03, FF04, AP15, PJ01, PD01, RM01, RM03, BN02, N1, N2, N3. Not used in the benchmark, library or demo; no public display. AP15 is NOT_TRACKABLE, ST05 on HOLD (S02e).

Approval and CSV status: the S02e owner grant ([evidence/owner/S02/APPROVAL.md](evidence/owner/S02/APPROVAL.md)) covers
local pipeline work only. The clips.csv columns status/owner_approved still read UNAPPROVED_CANDIDATE/NO by
design and must not be read as public-use approval. Reconciliation list:
[evidence/release/PUBLIC_PACKAGE_CHECKLIST.md](evidence/release/PUBLIC_PACKAGE_CHECKLIST.md).
## Models

- SAM 3.1 (`facebook/sam3.1`), Meta, SAM License: [evidence/S05/upstream/sam_license.txt](evidence/S05/upstream/sam_license.txt).
  Review: [evidence/S05/LICENSE_REVIEW.md](evidence/S05/LICENSE_REVIEW.md).
- Apache-2.0 upstream reconstruction code licence copy: [evidence/S05/upstream/map_license.txt](evidence/S05/upstream/map_license.txt).
- Muse models via Meta Model API and Baseten: used as hosted APIs; no weights redistributed.

## Third-party libraries (direct dependencies)

| Library | Version | Licence |
|---|---|---|
| Next.js | 16.4.3 | MIT |
| React / React DOM | 19.3.1 | MIT |
| three.js | 0.186.1 | MIT |
| @clerk/nextjs | 7.9.21 | MIT |
| @dimforge/rapier3d-compat | 0.21.0 | Apache-2.0 |
| FastAPI | 0.124.4 | MIT |
| Uvicorn | 0.33.0 | BSD-3-Clause |
| boto3 | 1.43.120 | Apache-2.0 |
| psycopg | 3.3.6 | LGPL-3.0 |
| redis-py | 8.1.0 | MIT |
| jsonschema | 4.23.0 | MIT |

Versions are from [Build/web/package.json](Build/web/package.json), [Build/simulator/package.json](Build/simulator/package.json)
and the Python requirements files under Build/ and contracts/. Licences are the upstream projects' published licences;
transitive dependencies keep their own licences.
