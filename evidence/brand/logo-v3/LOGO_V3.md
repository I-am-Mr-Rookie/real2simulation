# Logo v3: pendulum from Koushik's pencil sketch (S15at-orch207, Oct31 2026)

Source: two owner photos of one pencil sketch, `evidence/owner/logo-sketches-2026-10-31/owner-pendulum-logo-sketch-1.jpeg` and `-2.jpeg` (local-only owner inputs, not committed). Side by side: `evidence/owner/logo-sketches-2026-10-31/sketch-vs-mark-v3.png` (local-only: it contains a crop of the owner photo, so the controller moved it out of Git before merge).

## Sketch to mark

| Sketch element | Mark (64 u grid, [mark.svg](../../../Build/web/public/brand/mark.svg)) |
|---|---|
| Fixed support: horizontal line, wider than the swing | Support line (7,18) to (57,18), 3 u, round caps. Spans 7..57, wider than the ghost extents 8.5..55.5 |
| Short diagonal hatch ticks above the line (ceiling symbol) | 7 parallel ticks, 2 u, from the line up 7 u, leaning +4 u right, x 9 to 51 evenly spaced |
| One pivot at the middle of the line | Pivot (32,18); every string starts there |
| Solid string straight down | (32,18) to (32,42), 2.5 u |
| Solid filled centre bob | Solid circle r 7.5 at (32,49), rust/ember |
| Dashed strings to the two extremes, starting a little below the pivot | 2 u dashes, 3.5 u on, 4.5 u off, starting 7 u from the pivot, ending short of each ring (computed, so a round cap never enters the ring) |
| Hollow ghost bobs left and right, roughly level with the centre bob | Rings r 5.5, 2 u stroke, centres (15,46) and (49,46), 3 u above the bob centre. Pivot distance 32.8 u vs 31 u for the centre bob, so all three sit close to one swing arc while still reading level as in the sketch |

What changed vs v2 (S15ap): T bar became the hatched fixed support; solid ghost strings became dashed; ghost ring stroke 3 to 2 u (lighter, like the sketch); colours, renderer, filenames and sizes unchanged.

## Small drawing (<=32 px)

[mark-16.svg](../../../Build/web/public/brand/mark-16.svg), 16 u grid, used for mark-32.png and favicon 16/32 (favicon 48 uses the full drawing):
- Support 1.25 u, hatch cut from 7 ticks to 3 bolder ticks (1.25 u, 3 u tall).
- Dashes are mush at 16 to 32 px, so ghost strings become faint solid lines (ink at 50 percent light, 60 percent dark), drawn first so the solid support and string paint over the shared pivot.
- Ghost rings r 1.5 at (2.5,10.5)/(13.5,10.5), spread so a 1 px gap separates them from the r 2.5 bob.
- Viewed: [small-real-size.png](small-real-size.png) (true 16 and 32 px on all 6 modes), [small-real-size-6x.png](small-real-size-6x.png), [favicon-frames-6x.png](favicon-frames-6x.png) (ICO 16, 32, 48, then mark-32.png, nearest-neighbour 6x, paper and dark). At 16 px it reads as support plus three bobs; hatch detail is suggestive only. At 48 px the full drawing with dashes still separates.

## Clear space and minimum size

- Clear space: at least one ghost ring radius plus stroke (6.5 u of 64, about 10 percent of the mark size) on every side.
- Minimum: 16 px with the small drawing only. Full drawing from 48 px. Header: 24 to 32 CSS px (the site header uses mark-192.png at 28 px plus HTML text).

## Colour per mode (contrast vs background)

Same palette as v2, so ink and bob ratios are the S15ap computed values (WCAG relative luminance). Faint 16 px ghost strings computed this run as ink composited at the stated opacity.

| Mode | Background | Variant | Ink (support, hatch, strings) | Bob and ghosts | Faint string (<=32 px) |
|---|---|---|---|---|---|
| paper | #f3eee3 | light | #1c1a16, 15.02:1 | #b23a0e, 5.18:1 | 50%, 3.22:1 |
| light | #f7f7f8 | light | #1c1a16, 16.23:1 | #b23a0e, 5.60:1 | 50%, 3.30:1 |
| contrast | #ffffff | light | #1c1a16, 17.37:1 | #b23a0e, 5.99:1 | 50%, 3.35:1 |
| dark | #111113 | dark (mark-dark.svg) | #f4f4f5, 17.16:1 | #ff8a4c, 8.08:1 | 60%, 6.63:1 |
| midnight | #0b1020 | dark | #f4f4f5, 17.22:1 | #ff8a4c, 8.11:1 | 60%, 6.65:1 |
| graphite | #1f2023 | dark | #f4f4f5, 14.82:1 | #ff8a4c, 6.98:1 | 60%, 6.17:1 |

Contact sheet, 16/24/32/64/192/512 px on all six modes plus the lockup per mode: [contact-sheet-final.png](contact-sheet-final.png).

## Lockup (mark plus text)

wordmark-light.png and wordmark-dark.png (924 x 192, transparent): mark at 192 px plus "Real2Simulation" in Instrument Sans SemiBold 92 px, same typography and text position as v2. The v3 art spans hatch top to bob bottom (y 11 to 57.5 of 64), so the mark is lifted 7 px to centre that span on the text. Review: [wordmarks-review.png](wordmarks-review.png); every mode: bottom row of each band in the contact sheet. The site header keeps rendering mark-192.png plus HTML text (filename unchanged).

## Exports (same filenames and sizes, Build/web/public/brand/)

mark.svg, mark-dark.svg, mark-16.svg, mark-1024/512/192.png (full drawing), mark-32.png (small drawing), favicon.ico (16/32 small, 48 full), icon-maskable-512.png (opaque paper tile, art 320 px centred inside the 80 percent safe circle), wordmark-light.png, wordmark-dark.png. PNGs are the light variant; dark surfaces use mark-dark.svg or wordmark-dark.png.

## Do / don't

- Do: keep the hatched support, one pivot, solid centre string and bob, dashed strings and hollow ghosts; use the 16 u drawing at 32 px and below.
- Don't: turn the support back into a T bar; make the ghost strings solid at full size; fill the ghosts; recolour ghosts to ink; use dashes at 16 to 32 px; put light ink on dark surfaces.

## Rights

Geometry drawn in this run from Koushik's own sketch; no third-party artwork, tracing or image model. Instrument Sans (OFL, already used by the site) only rasterizes the wordmark; no font file is redistributed.

## Reproduce

`python evidence/brand/logo-v3/build_logo_v3.py` then `python evidence/brand/logo-v3/check_logo_v3.py` (sizes, RGBA/alpha, maskable opacity and safe circle, ICO frames, no embedded raster, wordmark mark not clipped, structure: 2 hollow ghosts plus 1 solid bob plus support/hatch/string lines). The side-by-side is regenerated only where the local owner photo exists.

