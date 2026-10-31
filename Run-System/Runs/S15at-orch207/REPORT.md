# S15at-orch207 REPORT: Logo v3 from owner pencil sketch

Status: DONE. Lane CLAUDE, anthropic/claude-opus-5-5/high. UTC issued 2026-10-31T11:15:00Z, started 11:16:48Z, stopped 2026-10-31T11:21:45+00:00. Branch run/S15at-orch207 from main 1b9ab540. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No Meta/GPU/API call, no secrets, no Chrome.

## Result
- Viewed both owner photos. Mark redrawn to the sketch: wide support line with 7 hatch ticks above, single pivot at its middle, solid string to solid rust/ember bob, dashed strings (starting below the pivot, as drawn) to hollow ghost rings roughly level with the bob. Mapping table and construction: [LOGO_V3.md](../../../evidence/brand/logo-v3/LOGO_V3.md).
- Small drawing (mark-16.svg, used <=32 px): 3 bolder hatch ticks; dashes replaced by faint solid strings (50/60 percent ink) because 1 px dashes formed an arrowhead blob at 16/32 px in the first render.
- Controller note honoured: wordmark-light/dark.png keep "Real2Simulation" in v2 typography; mark lifted 7 px so the hatch-to-bob span centres on the text; lockups shown in LOGO_V3.md and per mode in the contact sheet. Header (SiteFrame.jsx: mark-192.png + HTML text) and layout icons untouched; filenames/sizes unchanged.

## Files
- Replaced in place: Build/web/public/brand/ mark.svg, mark-dark.svg, mark-16.svg, mark-1024/512/192/32.png, icon-maskable-512.png, favicon.ico, wordmark-light.png, wordmark-dark.png.
- New evidence/brand/logo-v3/: build_logo_v3.py, check_logo_v3.py, LOGO_V3.md, sketch-vs-mark.png, contact-sheet-final.png, small-real-size.png, small-real-size-6x.png, favicon-frames-6x.png, wordmarks-review.png.

## Checks (fresh)
- `python evidence/brand/logo-v3/build_logo_v3.py` OK; `python evidence/brand/logo-v3/check_logo_v3.py` -> `logo-v3 checks OK` (sizes, RGBA, transparent corners, maskable opaque + 80 percent safe circle, ICO 16/32/48, no embedded raster, wordmark mark not clipped, 2 hollow + 1 solid circles, support/hatch/string lines present).
- Visual: sketch-vs-mark, contact sheet (6 modes x 16..512 + lockups), small sizes true 1x and 6x, favicon frames 6x, wordmarks review all inspected. One iteration fixed dashes crowding the pivot (start offset 4 -> 7 u) and the 16 px blob (faint solid strings); one fixed a clipped lockup row in the contact sheet.
- Faint string contrast computed (3.22 to 3.35:1 light, 6.17 to 6.65:1 dark); ink/bob ratios reused from S15ap (same hex values).
- No em dashes in authored files (rg).

## Ponytail (full) applied
- Reuse: copied build/check_logo_v2.py; renderer, svg(), raster(), wordmark(), exports, maskable and ICO code unchanged. Only the primitive lists changed plus three small helpers (hatch, faint_string, edge reused from to_edge) and a stroke-opacity branch in svg() for the faint role.
- Smallest complete: one FINAL + one SMALL drawing; dropped v2's four concept candidates (owner already chose the structure). Check script copy plus a structure assert.
- Skipped: browser render of the SVGs (no SVG rasterizer installed; Pillow renders from the same primitive list as v2 did); header/PWA wiring (S15as owns it); dark PNG variants (not requested, v2 convention kept).

## Risks / limits
- sketch-vs-mark.png contained a grayscale crop of the owner's sketch photo. Controller (acceptance) moved it to local-only evidence/owner/logo-sketches-2026-10-31/sketch-vs-mark-v3.png and amended the run commit so it never enters main history.
- At 16 px the hatch reads as a few ticks, not a crisp ceiling symbol; inherent at that size.
- Header shows mark-192.png at 28 CSS px (full drawing downscaled); hatches are fine at 56 device px but soft at 28 px on 1x screens. S15as may prefer mark-32.png or mark-16.svg there.
- Communication: silent; one completion line to controller.

