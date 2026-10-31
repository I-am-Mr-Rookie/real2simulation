# S15ar before/after (em dash U+2014 sweep, excluding S15au files)
| File | Before | After |
|---|---|---|
| auth/dev-scenes.mjs | FIXTURE / SYNTHETIC — empty ... | FIXTURE / SYNTHETIC: empty ... |
| workspace/fixtures.mjs | SYNTHETIC fixture — not ... | SYNTHETIC fixture: not ... |
| viewer/trajectory-replay.mjs | SIMULATED trajectory — simulator output | SIMULATED trajectory: simulator output |
| viewer/fixture.mjs (x2) | SYNTHETIC fixture — / RECONSTRUCTION — | SYNTHETIC fixture: / RECONSTRUCTION: |
| shell/examples.json | SYNTHETIC fixture — not ... | SYNTHETIC fixture: not ... |
| workspace/interview.mjs | chip — text (answer join) | chip, text |
| workspace/view.mjs | clip — input — label | clip · input · label |
| workspace/fit-view.mjs | empty-cell marker \u2014 | \u00b7 |
| server text (provenance label/stage labels) | passed raw | dash(): " — " -> " · " at display time, words unchanged |
Test fixture tests/workspace/interview.test.mjs updated to ', '. Range en dashes without spaces (0.2x-5x, time ranges) kept: not em-dash substitutes.
Server-side library banners (Build/library/loader.mjs, 'SIMULATED — ...') are not rendered by any web file found; untouched (outside Owns).
