# S09h — three real scene bundles through the viewer

Evidence class: **real reconstruction (MapAnything nominal output), scale UNVERIFIED**. Not Gate R, not physics,
not calibrated-scale evidence (Gate R FAIL -> S05f Fallback 2). Synthetic-fixture evidence is separate
(tests/viewer/*.test.mjs fixture cases, browser-smoke.mjs). No Modal/GPU in this run.

## Bundles (media gitignored: evidence/S09/local/<RM>/, never committed)

Rebuilt offline, CPU only, with the existing converter: `python Build/gpu/scene_job.py <RM> evidence/S09/local/<RM> --npz <npz>`
(contracts/scene validator PASS for all three).

| Scene | Source npz (gitignored, other worktree) | npz sha256 | scene id | points | scale | points.ply sha256 / bytes |
|---|---|---|---|---|---|---|
| RM02 | .worktrees/S06e-orch24/evidence/S06/S06e/local/RM02/RM02-mapanything.npz | 94c2ff13…b344 | rm02-mapanything-s06d | 20000 | estimated | e4681461…1399 / 753214 |
| RM04 | .worktrees/S06f-orch25/evidence/S06/S06f/local/RM04/RM04-mapanything.npz | 1ff2069d…5d6f | rm04-mapanything-s06d | 20000 | estimated | 9f0c0bd9…2385 / 752219 |
| RM05 | .worktrees/S05c-orch19/evidence/S05/S05b/recovery8/attempt-3853a52b…/local/RM05-mapanything.npz | a3bebfeb…a362 | rm05-mapanything-s06d | 20000 | estimated | 4046fcc2…b3ff / 740065 |

RM02 and RM04 offline rebuilds are byte-identical (main + mobile sha256) to the committed S06e/S06f GPU manifests
(evidence/S06/S06e/scene-RM02-gpu.json, evidence/S06/S06f/scene-RM04-gpu.json). RM05 is new from the S05c npz.
RM05 clip row is `UNAPPROVED_CANDIDATE` / SCENE_ONLY_UNTIL_SCALE_VERIFIED in clips.csv (NASA PD; converter allowlists it as an
APPROVAL.md scene id) — display-only, microgravity ISS interior, not an Earth room.

## Load checks

- Node: `node --test "tests/viewer/*.test.mjs"` -> 46/46 pass, 0 skipped. tests/viewer/real-scenes.test.mjs loads each bundle via
  createArtifactLoader (manifest gate + sha256) -> createViewerAdapter (checkViewerRequest, buildSceneModel/decodePlyXyzRgb):
  states loading,ready; 20000 finite points inside bounds_m; synthetic false; physics/gate false; SCALE_UNVERIFIED_BANNER.
  Tests skip (not fail) when local media is absent (fresh clone).
- In-app browser (ChatGPT IAB, not Chrome), tests/viewer/real-scenes.html on 127.0.0.1 via python http.server (stopped):
  desktop 1280 px and 375 px viewport override (reset after) — all three `loading,ready`, banner
  "RECONSTRUCTION — metric scale UNVERIFIED …", data-viewer-banner=scale-unverified, 375 px layout compact, scrollWidth 375 (no
  horizontal scroll). Screenshots: evidence/S09/local/ui/RM0{2,4,5}-{desktop,375}.png (gitignored: derived scene media).

## Limits

Points only (bundles have no surfaces/colliders; Fallback-2 planes+boxes not present in these bundles, not invented here).
Main asset only (mobile LOD still not loaded, S09e note). Not mounted by an app route. SwiftShader/IAB only; no real phone.
