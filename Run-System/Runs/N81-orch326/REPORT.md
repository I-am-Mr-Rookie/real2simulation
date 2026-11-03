# N81-orch326: DONE
- Changed `Build/web/src/lab-editor/sf3d-shape.mjs`: uniform effective GLB fit inside the proxy, centred X/Z, bottom-aligned, existing yaw preserved. Invalid loaded bounds retain the placeholder.
- Parent non-uniform proxy scaling is cancelled only for visuals. Physics/colliders, saved schema, Python fitting and shared packs are unchanged; old saved scenes render without migration.
- Added six regression tests in `tests/lab-editor/sf3d-fit.test.mjs`; all 46 lab-editor Node tests and 28 targeted reconstruction Python tests passed. Production web build and diff whitespace check passed.
- In-app browser checked N75 and N80 actual local labs before/after, plus 16 same-camera textured views at three angles. Both packs' GLBs were HTTP 200 and fresh hashes match their existing manifests.
- Evidence: `evidence/N81/VERIFY.md`, `asset-audit.json`, `browser-console.json`, seven JPEGs and loopback-only reproduction helpers. Captured console errors: none. Existing shadow-map deprecation warning remains.
- Judgment: N80 is NOT clearly better overall. Objects 1/7 show some fuller tops; object 2 remains fragmented and object 4 incomplete/dark. No pack promotion.
- Paid API/GPU jobs: 0; cost: $0. No new inference, private-room/N06 access, deployment or push. Own browser tabs and all helper listeners stopped.
- Skipped: auth/deployment E2E, new model generation, calibrated physics-contact validation.
- Risk: fixing stretch cannot restore missing geometry. Thin fragments can sit near the proxy bottom while the unchanged box collider top sits higher; MODEL-GENERATED and scale-unverified caveats remain.
