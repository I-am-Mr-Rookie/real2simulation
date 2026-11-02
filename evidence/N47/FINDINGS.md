# N47 DEV QA recheck

**QA DONE. F1 to F4 FIXED; F5 STILL OPEN. Both live workflows completed. No P1 found in this pass.**

## Findings first

### N47-1 [P2, visual quality] Furniture is still severely distorted

1. Sign in to the primary DEV domain with the N47 test account below.
2. Open room `6979686e91dd4e47975bcbaa5afb4e14` in the lab at 1280 x 900, default view.
3. Compare the rendered furniture with the room-view photo in the right panel. The textured chair/table shapes are flattened, warped blobs; large box fallbacks dominate the foreground. The shapes do not look like the source classroom furniture.

This is a remaining reconstruction-quality problem, not a repeat of the fixed tabletop collision bug. Geometry is correctly labelled MODEL-ESTIMATED and shape captions credit Stability AI. No physical dimensions or unseen surfaces are validated here. N44 explicitly left SF3D mesh distortion outside its fix.

Receipt: [desktop room and source photo](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N47-orch292/evidence/N47/r3-22-mode-a-agent-experiment.png>), `new-room-result.json`.

### N47-2 [P2, latency/degradation] One SF3D job times out; a short room upload takes over eleven minutes

1. New project > Room video > Continue.
2. Upload the approved `RM02-trim.mp4` and click Build my lab once.
3. The job runs from `04:30:54Z` to `04:42:01Z`. L4 spends about four minutes waiting for capacity before the automatic A10G retry succeeds.
4. During the automatic shell pass, `room-object-1` SF3D hits its 300-second function timeout. That object remains a box; two other SF3D objects succeed. The failed attempt still costs an estimated `$0.13431147` in the runtime ledger.

The workflow recovers and finishes, so this is a degraded experience rather than a failed upload or missing lab. The box fallback reason is retained in the scene. No second reconstruction or manual retry was started.

Receipts: `new-room-status.json`, `new-room-result.json` (`room.shell.kept`), `runtime-ledger-window.json`, [finished room](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N47-orch292/evidence/N47/r3-18-mode-a-new-room-shell.png>).

### N47-3 / F5 [P3, STILL OPEN] Larger mobile captions overlap and hide each other

1. Open the new room above at 375 x 812, fresh load, default camera. Scroll the canvas into view without zooming or orbiting.
2. The two MODEL-GENERATED shape / Powered by Stability AI captions now have readable-sized text, but overlap horizontally. The left caption masks the beginning of the right caption.
3. Repeat on the refreshed original RM02 room `82f05b85de1748b3bd91003122b8e70d`: its captions also overlap. The custom domain reproduces it.

N44 fixed the tiny distance-scaled text, but not simultaneous legibility of the required adjacent labels. Footer credit remains readable. No document-wide horizontal overflow was observed on these room views.

Receipts: [new room, 375 px](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N47-orch292/evidence/N47/r3-23-F5-mobile-room-captions.png>), [refreshed original room](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N47-orch292/evidence/N47/old-final-26-old-room-mobile-captions.png>), [custom domain](<C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/.worktrees/N47-orch292/evidence/N47/33-custom-domain-lab-375.png>).

## N43 recheck matrix

| Finding | DEV result | Fresh evidence |
|---|---|---|
| F1: centred balls roll off SF3D tables | **FIXED** | Exact original N43 table-1 scene rests at y `0.4422813654`, expected `0.44235`. Original table-3 centre rests at `0.4597813785`, expected `0.45985`. After rebuilding the saved shell, both regenerated SF3D tables also retain centred balls through at least four simulated seconds: y `0.6472817063` and `0.6735317111`. All four traces pass the offline rest check. `f1-*-traces.json`, `f1-refreshed-rest-targets.json`. |
| F2: bogus walls/opening counts | **FIXED for requested wall/opening honesty** | Clicked Build lab shell on the original RM02 room first. Its new shell was saved at `04:34:56Z`: UI says `0 walls (4 not observed), 0 openings`. The independently uploaded room has the same honest wall/opening result. Original refreshed shell kept nine furniture objects; fresh room kept seven. No claim that the classroom boundaries were successfully reconstructed. `old-room-after-shell.json`, `new-room-result.json`, `old-final-24-F2-refreshed-old-room.png`. |
| F3: lab ignores saved tier; no answering model | **FIXED** | Workspace saved `Standard: Muse Open`. Both lab turns actually use `meta-models/muse-spark-open-1026`; the lab visibly says `Answered by meta-models/muse-spark-open-1026`. `16-saved-muse-open.txt`, `r3-17-F3-open-answer-model.txt`, `r3-results.json`, `mode-a-agent-turn.json`. |
| F4: Room upload/job lose project id | **FIXED** | New Room project `23f65c8fe2a04434913f2311de7014ef` is shared by uploaded file `c6db535cbf9d4baa822dc61453acee56` and room job `6979686e91dd4e47975bcbaa5afb4e14`, including final list reads after completion. The previous N43 null-project rows are unchanged. `new-results.json`, `new-files-final.json`, `new-rooms-final.json`, `new-projects-final.json`. |
| F5: mobile captions unreadable | **STILL OPEN** | Text size improved, but adjacent captions obscure each other at 375 px. N47-3 above. |

## Execution receipts

- Primary: [DEV](https://real2simulation.up.railway.app). Spot-check: [custom domain](https://real2simulation.rookiecoders.tech).
- Headed Playwright **Chromium**, version `156.0.8078.4`, installed `ms-playwright/chromium-1248` binary. Never automated Chrome. Desktop 1280 x 900 and fresh-load mobile 375 x 812.
- Existing account ID: `user_3LWziQJxcsdCLbV2bCKATtu7KMg`. New isolated N47 account ID: `user_3LXIA6TC4IXO6sga3yOs7q2ET2I`. Only account IDs are recorded; no real-email screenshots.
- Inputs: existing N13 approved Pexels derivatives in `C:/Users/HP/AppData/Local/Temp/n13clips/`. RM02 is the classroom; ST03 is the falling apple. Source URLs and expected SHA256 hashes are in `provenance.json`. No private owner clip was opened or uploaded.
- Machine-readable results: `results.json`. Offline checker: `node evidence/N47/verify.mjs`, **10 checks passed**. This checks captured output, not independent hardware accuracy.

### Mode A: room upload to editable lab and agent experiment

New project interview > Room video > approved RM02 upload > Build my lab > automatic reconstruction/shell > open new room > Add > Ball. Deleted only that created `ball-1`, then Undo restored the identical object set. Asked the agent to run an experiment with that ball; actual `lab_run` succeeded and returned SIMULATED `g = 9.809993 +/- 0.014 m/s^2` with declared position sigma `0.001 m`. The run stopped at floor contact rather than continuing for the requested full second, and the answer explicitly said so. The agent did not invent the unavailable final-y value. This is simulated tool output, not measured room gravity.

Receipts: `mode-a-delete-undo.json`, `mode-a-kit-scene.json`, `mode-a-agent-turn.json`, `r3-19` through `r3-22` screenshots/text. The delete/undo check happened before the agent turn; all required actions completed without deleting existing room furniture.

### Mode B: track, uncertainty, replay, redo

New project interview > My experiment > approved ST03 upload > Measure this experiment > target name `apple` > Start measuring. No known size was supplied. Hosted SAM processed the video and the fitter returned `2338.683196518687 +/- 120.61493400739636 px/s^2`, displayed as `2340 +/- 120 px/s^2 1 sigma`, with scale-unverified and playback-clock caveats. The chart has measured points, fitted curve and a one-sigma band; mobile inspection observed those parts too.

Opened 3D replay, ran Play, exported SIMULATED sensor traces. Through the supported Scene JSON editor, changed only gravity from `[0,-9.81,0]` to `[0,-4.905,0]`, applied it and ran again. Both trace exports exist; the redo changes the simulated trajectory while the measured source and object specification remain unchanged. Replay labels distinguish Track MEASURED from ball what-if and explain the display mapping for unscaled pixels.

Receipts: `mode-b-result.json`, `mode-b-replay-scene-before.json`, `mode-b-redo-scene.json`, both `mode-b-*-traces.json`, `r3-13` through `r3-15`, `29-mobile-mode-b-fit.png`, `30-mobile-mode-b-replay.png`. This is a licensed stock-video surrogate through the phone-experiment workflow, not a claim to have recorded a new phone experiment.

### Domain spot-check

Signed the same N47 test account into the custom domain; its workspace showed the same projects. The private room-result API returned 200 and JSON identical to the primary domain. Opened that lab at desktop and fresh-load mobile sizes. Default TLS validation was retained. `custom-domain.json`, `31` through `33` screenshots. No duplicate inference was run on the custom domain.

### Spend

**Settled runtime-ledger estimates: `$1.38060220`, below the `$1.50` task cap.** Not a provider invoice.

| Provider / work | Calls | Settled estimated USD |
|---|---:|---:|
| Meta: two shell passes, SAM image prompts | 144 | 0.36000000 |
| Meta: hosted video tracking | 1 | 0.02400000 |
| Modal: L4 capacity failure + A10G room retry | 2 | 0.66509617 |
| Modal: SF3D, including the timeout | 6 | 0.31819427 |
| Baseten: two Muse Open turns, three model calls | 3 | 0.01331176 |

`runtime-ledger-window.json` contains every reservation id, provider/model label, units in 1e-8 USD, reservation/settlement timestamps and settled estimate for this run's paid interval. All 156 rows are settled. The six SF3D rows are three for the explicit old-room shell refresh and three for the new room. The failed SF3D charge is included, not silently omitted. `paid-ledger-summary.json` and `results.json` reconcile the total. Do not add these receipts as new charges to the application ledger.

A read-only Railway SSH query succeeded with an explicit existing SSH key. Earlier attempts had a command-quoting syntax error and a default-key connection stall; neither was an inference call. No purchase, deploy or production change occurred.

### Evidence handling and limits

Screenshots are retained locally in this worktree and omitted from the commit under WORKER_CONTRACT's no-media-binaries rule. `screenshots.json` records their names and SHA256 hashes. Text/JSON receipts are committed; trailing whitespace in captured text was normalized. Temporary authentication state and the browser endpoint are excluded from Git and cleaned up after capture. The recorder experienced control timeouts; sessions were recovered without starting another room or tracking job. An in-flight old-shell HTTP response was lost, so its successful completion is evidenced by a fresh saved-room GET instead.

Skipped: application tests/build/deploy because application code was untouched; physical calibration, new real-phone filming, provider invoices, forced fallback, storage/quota exhaustion, cross-account isolation and every-kit-item physics accuracy. The health-request recorder timeout was not isolated and is not labelled a product failure. Remaining risks: mobile caption overlap, distorted SF3D geometry, and capacity/timeout-driven latency.
