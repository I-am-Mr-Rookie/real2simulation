# N50 browser verification

- Headed Playwright bundled Chromium 157.0.8103.27, local production build at http://localhost:3250/lab?editor=1. No DEV deployment.
- Fixture: `two-sf3d-scene.json`, two synthetic pyramid mesh records in the SF3D schema, no recording or private frames. GLB requests deliberately intercepted as 404; screenshots show the supported collider fallback, not paid SF3D output.
- Exactly one viewport attribution chip with two mesh objects; zero with an empty scene. Selected mesh says `MODEL-GENERATED shape (Stable Fast 3D)`.
- 1280 x 900: wheel over Selected object heading, Room heading and Scene JSON summary each moved page scrollY from 0 to 160.
- Wheel event observation: outside-canvas events had defaultPrevented=false; canvas event had defaultPrevented=true and page scrollY stayed 0.
- Expanded Scene JSON: inspector scrolled before page; textarea scrolled before page. At inspector/textarea bottom, a fresh wheel over inspector gutter moved page from 0 to 140, inspector stayed at its maximum 140.
- Chromium keeps a wheel transaction latched across rapid scripted target changes. Boundary check was verified as a separate fresh gesture; a combined-script attempt did not chain until the subsequent separate gesture.
- Real CDP touchStart/touchMove/touchEnd swipe over inspector: page scrollY 225, inspector scrollTop 0; touch events not prevented, computed touch-action auto.
- 375 x 812: document scrollWidth 375. Template trials stays in the toolbar right group with all four file/view icons on the same row after removing inherited button margins.
- `editor-1280.png` and `editor-375.png` are local, uncommitted screenshots per worker contract (no media binaries committed).
- Global footer credit, About, README, NOTICE, licence and scene metadata validation unchanged.
