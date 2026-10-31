# Real2Simulation logo v2: Pendulum (S15ap-orch204)

Replaces the S15ag "Measured Arc" mark (evidence/brand/BRAND.md). Owner idea (Oct31): a simple pendulum in simple harmonic motion, shown in three phases (left, middle, right). Hand-authored vector, no image model.

## Candidates (rendered by build_logo_v2.py; each concept PNG shows 192/32/16 px on paper and dark)

| Candidate | Files | Verdict |
|---|---|---|
| A, dashed paths | [PNG](concept-a-dashed-paths.png), [SVG](concept-a-dashed-paths.svg) | Closest to the site A2 illustration, but dashes turn to grey noise at 32 px and vanish at 16 px. Rejected. |
| B, bar + three phases, no ghost strings | [PNG](concept-b-bar-three-phase.png), [SVG](concept-b-bar-three-phase.svg) | Bold and clean, but without ghost strings it reads as the letters "oTo", not a swing. Rejected. |
| C, pivot dot + dashed arc, ink ghosts | [PNG](concept-c-pivot-dot-arc.png), [SVG](concept-c-pivot-dot-arc.svg) | Arc dashes collide with rings and read as a molecule; ink ghosts lose the single rust accent family. Rejected. |
| **D, bar + solid ghost strings (CHOSEN)** | [PNG](concept-d-final-solid-strings.png), [SVG](concept-d-final-solid-strings.svg) | B's bold silhouette plus thin solid strings from one pivot to each ghost: one pendulum, three phases, instantly. Solid strings survive downscaling where dashes do not. |

Why D: one pivot, three equal-length strings, one solid bob and two hollow ghosts is the exact A2 illustration grammar (pivot bar, string, solid centre bob, hollow ghosts at the extremes) compressed to icon weight. Hollow vs solid encodes "past/extreme positions vs now" without text.

## Construction (64 u grid, [mark.svg](../../../Build/web/public/brand/mark.svg))

- Pivot bar: (20,12) to (44,12), 4 u stroke, round caps. Pivot point (32,12).
- Centre string: (32,12) to (32,46), 3.5 u. Centre bob: solid circle r 9 at (32,49); string length about 37 u.
- Ghost bobs: rings r 6, 3 u stroke at (14,44) and (50,44), about 36.7 u from the pivot, so all three phases sit on the same swing arc (about +/-29 degrees).
- Ghost strings: 2 u, pivot to the ring's outer edge (computed, so the round cap never enters the ring).
- Art box about x 6 to 58, y 10 to 58 of 64 (built-in padding about 9 percent). All primitives are lines and circles; integer centres.

Small drawing ([mark-16.svg](../../../Build/web/public/brand/mark-16.svg), 16 u grid), used for every export at 32 px and below (mark-32.png, favicon 16/32): bar 1.5 u, strings 1 u, ghosts r 1.5 at (2.5,9.5)/(13.5,9.5) raised and spread so a 1 px gap separates them from the r 2.5 bob. favicon 48 uses the full drawing. See [favicon-frames-6x.png](favicon-frames-6x.png) (16, 32, 48 ICO frames, then mark-32.png, nearest-neighbour 6x).

## Clear space and minimum size

- Clear space: at least one ghost ring radius plus stroke (7.5 u of 64, about 12 percent of the mark size) on every side, beyond the built-in padding.
- Minimum size: 16 px using the small drawing only. Full drawing from 48 px. In the header use 24 to 32 CSS px.

## Colour per mode (contrast vs mode background, computed in this run)

| Mode | Background | Variant | Ink (bar, strings) | Bob (rust/ember) |
|---|---|---|---|---|
| paper | #f3eee3 | light-ink | #1c1a16, 15.02:1 | #b23a0e, 5.18:1 |
| light | #f7f7f8 | light-ink | #1c1a16, 16.23:1 | #b23a0e, 5.60:1 |
| contrast | #ffffff | light-ink | #1c1a16, 17.37:1 | #b23a0e, 5.99:1 |
| dark | #111113 | dark (mark-dark.svg) | #f4f4f5, 17.16:1 | #ff8a4c ember, 8.08:1 |
| midnight | #0b1020 | dark | #f4f4f5, 17.22:1 | #ff8a4c, 8.11:1 |
| graphite | #1f2023 | dark | #f4f4f5, 14.82:1 | #ff8a4c, 6.98:1 |

The brand bob stays rust/ember in every mode (it is the brand colour, not the per-mode UI accent, so midnight's sky accent is not applied). Ghost rings use the bob colour, matching the A2 illustration. Contact sheet of the final mark at 16/24/32/64/192/512 px on all six backgrounds: [contact-sheet-final.png](contact-sheet-final.png). Wordmarks: [wordmarks-review.png](wordmarks-review.png).

## Exports (same filenames and pixel sizes as S15ag, Build/web/public/brand/)

mark-1024/512/192.png (full drawing, transparent), mark-32.png (small drawing, transparent), favicon.ico (16/32 small, 48 full), icon-maskable-512.png (opaque paper #f3eee3 tile, art 320 px centred, inside the 80 percent safe circle), wordmark-light/dark.png (924 x 192, mark at 192 + "Real2Simulation" in locally installed Instrument Sans variable font, SemiBold instance requested via Pillow), plus new mark.svg, mark-dark.svg, mark-16.svg. PNG files are the light-ink variant (as before, one file per name); dark surfaces should use mark-dark.svg or wordmark-dark.png.

Note: the maskable tile changed from S15ag's dark #0B0B0F to paper, per the S15ap contract.

## Do / don't

- Do: keep the three phases and the single pivot; keep the bob family rust (light) or ember (dark); use the 16 u drawing at 32 px and below.
- Don't: add dashes, arcs or motion lines; recolour ghosts to ink; rotate, skew or animate the mark into a different silhouette; place light-ink on dark surfaces; put the mark on busy imagery without a solid tile.

## Rights

Original geometry authored in this run (S15ap-orch204, Oct31 2026) from the project's own A2 illustration idea. No third-party artwork, tracing or image model. Instrument Sans is used only to rasterize the wordmark PNG; no font file is redistributed (it is the OFL font already used by the site via next/font).

## Reproduce

`python evidence/brand/logo-v2/build_logo_v2.py` then `python evidence/brand/logo-v2/check_logo_v2.py` (sizes, RGBA/alpha, maskable opacity and safe circle, ICO frames, SVG has no embedded raster). Renderer: Pillow supersampled from the same primitive list that writes the SVGs (no cairosvg/resvg/Playwright installed in Python; no new installs).

