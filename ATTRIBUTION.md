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

Note: the `owner_approved` column in [clips.csv](clips.csv) still reads NO for these rows; per-clip approval
receipts are referenced from BENCHMARK.md evidence pointers. Reconcile before publication (S25b).

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
