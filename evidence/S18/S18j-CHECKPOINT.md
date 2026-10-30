# S18j — minimum-library fallback checkpoint

Run S18j-orch139, anthropic/claude-opus-5-5 medium, base main `b82b1a6`. Measured/local only; nothing deployed.

## Decision: fallback NOT met — honest minimum library = 2 SIMULATED traces + Mystery-g practice

Spec (QUEUE S18j, final plan S18): *minimum 4 public clips plus Mystery-g; drop any clip whose licence is not verified.*
- Public-clip demos that open today: **0 / 4**. Openable entries: **3 / 18**, all project-authored SIMULATED.
- Six-demo target (<3 s): **not met** (3 openable). Load speed is no longer the blocker — content is.
- No clip is cleared for public library display: evidence/owner/S02/APPROVAL.md approves 10 IDs for **local pipeline work only** (public raw media redistribution held); clips.csv shows owner_approved=NO for all 23. Even with licences verified, a public clip demo needs an accepted clip-derived artifact AND owner go-ahead for public display.

## Web route re-measure (fixes S18i finding)
`python -B -m Build.library.load_times --web-dir <temp copy of Build/ with next build> --snapshot <load_guest dump>`
(production `next start` on 127.0.0.1, R2S_GUEST_SNAPSHOT; Build/web untouched; temp build of current main, 66 s).
Evidence: [S18j-web-load-times.json](S18j-web-load-times.json). 5 warm reps, 3 cold server starts.

| entry | availability | warm open median / p95 | cold open median / max |
|---|---|---|---|
| simulated-projectile-baseline-short | playable | 31 / 56 ms | 734 / 1049 ms |
| simulated-pendulum-short-small-angle | playable | 31 / 43 ms | 729 / 1031 ms |
| simulated-mystery-g | metadata-only | 30 / 38 ms | 717 / 1022 ms |

Server startup (TCP) 524–1339 ms; cold manifest 504–1007 ms. vs S18i Python path: 4–6 s median. Snapshot dump (one load_guest) ≈10 s at staging time, not per request.
Limits: localhost, Node fetch + loader.mjs (no browser render, no network, no Railway); OS file cache not flushed; n small (p95≈max).

## Inventory: kept / cut / restore path

| entry | decision | why | what restores it |
|---|---|---|---|
| simulated-projectile-baseline-short | KEEP (playable) | SIMULATED synthetic trace; opens <3s (warm p95 56 ms, cold max 1049 ms) | — |
| simulated-pendulum-short-small-angle | KEEP (playable) | SIMULATED synthetic trace; opens <3s (warm p95 43 ms, cold max 1031 ms) | — |
| simulated-mystery-g | KEEP (metadata-only) | Earth-g practice shape (S18l); blind challenge is /lab per-session hidden g; opens <3s (warm p95 38 ms, cold max 1022 ms) | — |
| simulated-free-fall-baseline-short | CUT (unavailable) | Trace withheld: same accepted record supplies the Mystery-g setup. | Controller/reviewer decision: S18l already labels library Mystery-g as non-blind Earth-g practice, so withholding may no longer protect anything; re-enable only via Build/library change + test after review. |
| simulated-free-fall-upward-launch / tiny-height / low-gravity-long-horizon | CUT (unavailable) | No complete preserved accepted setup with parameter JSON pointers. | Preserve accepted S10/S11 lab setup with parameter pointers, then regenerate via existing free_fall.py. |
| simulated-projectile-zero-horizontal / tiny-height / low-gravity-long-horizon | CUT (unavailable) | Same: no preserved accepted setup. | Same path via projectile.py. |
| simulated-pendulum-two-period-horizon / initial-angular-velocity / zero-answer-equilibrium | CUT (unavailable) | Same: no preserved accepted setup. | Same path via pendulum.py. |
| rm02-s06d-descriptor | CUT (unavailable) | Declared PLY bytes absent from accepted local evidence; no verified render bundle. Display-only, SCALE_UNVERIFIED. | Retrieve/commit accepted PLY bytes (S06d) within size limits + verified render bundle; still display-only, no physics claim. |
| rm04-s06f-descriptor | CUT (unavailable) | Same as RM02 (S06f). | Same as RM02. |
| rm05-scene | CUT (unavailable) | No accepted scene-v1 viewer descriptor; RM05 is ISS, not an Earth room. | Accepted S06 scene-v1 descriptor for RM05. |
| apollo | CUT (unavailable) | AP15 NOT_TRACKABLE (S02e); Moon result not measured. | A licensed trackable lunar drop clip with measured result; none known. |
| bounce | CUT (unavailable) | No accepted complete bounce record (S18c PARTIAL). | Accepted bounce fit/record (BN01 local-only approved). |

## Cut statement for demo/README (copy-paste)
> The guest library currently opens three project-authored SIMULATED demos (projectile, pendulum, Mystery-g practice). No real-footage demo is included: the candidate public clips are approved for local processing only and have no accepted clip-derived artifacts; scene descriptors are display-only and their point-cloud bytes are not in accepted evidence. Apollo is excluded (not trackable). Nothing here is a measured physical result.

## Owner/controller inputs (not decided here)
1. Public display of any clip-derived demo needs separate owner go-ahead (beyond S02e local-only approval).
2. Whether to re-enable `simulated-free-fall-baseline-short` now that library Mystery-g is labelled non-blind practice (S18l) — reviewer call; not changed here.

