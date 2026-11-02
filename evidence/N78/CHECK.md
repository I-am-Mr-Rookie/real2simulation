# N78: local verification of the three N76 findings

Base `4411b0a4`, branch `run/N78-orch323`. All browser checks used the attached in-app ChatGPT browser against loopback only. No deployment, private owner account/project, remote API or paid job was used.

## Changes
- Files: the existing phone media query now wraps `.lv-frow`, gives `.lv-fname` its own full-width first row, and lets long names wrap. Name and metadata retain their separate existing lines; preview/action controls wrap below. Desktop markup and layout are unchanged. No `live-view.mjs` change was needed.
- Lab: provenance gets a separate row below the centered transform toolbar at every width. The badge can use the canvas width minus its two insets, instead of the old 40% desktop / 60% phone limits. No label, credit, warning or control is hidden to solve the collision.
- Guide: room intro and classroom alt now explicitly describe the recorded sample shell, walls, furniture and 3D meshes, preserving MODEL-ESTIMATED and unverified scale. New uploads are not claimed to open prebuilt shells. No em dashes or image changes.

## Files browser check
`render-files.mjs` renders the real `createLive().Centre` Files component and real `renderShell`, with the global/workspace CSS emitted by this production build. Data is explicitly synthetic: a short video name and a long unbroken video name, including the exact reported `34 KB, 1.0 s, no project` metadata and both Measure / Build my lab actions. It is read-only SSR, with placeholder media, not a signed-in/authentication or action-handler test.

| Viewport | Result |
| --- | --- |
| 320 px | PASS: text block equals the 214.8125 px row width; metadata is one readable line; actions wrap below. Long filename wraps without overflow. |
| 375 px | PASS: text block equals the 269.8125 px row width; metadata is one readable line; actions are below. |
| 1366 px | PASS: original horizontal desktop arrangement remains, with readable metadata and actions alongside. |

No horizontal page overflow at any of those widths. Fresh DOM rectangles are in `files-layout.json`; screenshots were visually inspected, including 320 px. At 320 px the long-name room row wraps its menu onto another action line, as intended.

## Lab browser check
`serve_local.py` reuses the real sample seeder, room/storage/object GET routes and isolated synthetic owner store, backed by the existing approved public bundle. The UI is `next start` from the local production build, not a recreated editor. The adapter accepts GET only; uploads, shell/GPU builds, agent turns and other writes are unavailable. No production authentication setting or route was weakened.

- PASS at 375, 1024, 1100, 1200, 1280, 1366, 1440, 1600 and 1920 px: toolbar and collapsed badge do not intersect; the measured vertical gap is 6 px at every sampled width, and summary scroll width never exceeds client width. The separate-row rule is independent of canvas width. See `lab-layout.json`.
- PASS visually at 1280 px with the left panel open, plus 1024 px and phone screenshots with it closed. The full `SIMULATED · scale unverified · +1` is readable.
- PASS at 375 px: Rotate is reachable and becomes pressed; expanding the badge shows SIMULATED, one Stability attribution, MODEL-ESTIMATED caveats and the room-scale warning, all readable below the toolbar.
- PASS: `/guide#room` in the local build displays the revised sample-shell introduction. Node test checks both intro and alt text retain the caveats.

## Checks and reproduction
- `node --test tests/workspace/*.test.mjs tests/lab-editor/*.test.mjs tests/web-guide/*.test.mjs`: 210 passed, 0 failed, 0 skipped.
- `npm run build` in `Build/web`: exit 0, compiled successfully; canonical environment loaded in-process without printing/copying secret values.
- `git diff --check`: PASS. No new dependency. App changes are two CSS files and guide copy only.
- Local reproduction: build; run `next start --hostname 127.0.0.1 --port 3078` in `Build/web`; run `node evidence/N78/render-files.mjs`; run `python evidence/N78/serve_local.py <approved-public-bundle-directory>`. The adapter prints the local Files and sample lab URLs and writes `local-fixture.json`.
- Screenshots remain local-only under `C:/Users/HP/.codex/visualizations/2026/11/02/01a19dda-5200-73a2-8e88-b2ec3eaae909/N78/` (worker no-media-binaries rule). Receipt JSON and reproducible fixture helpers are committed; raw stores/build logs/generated HTML are ignored.
- Skipped: live DEV recheck, signed-in Files/action handlers, uploading, microphone, new measurements/fits, deployment and push. Existing mesh quality is outside this row and unchanged.
