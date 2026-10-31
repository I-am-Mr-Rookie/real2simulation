# Batch A — marketing image handoff

S15ak-orch196, 2026-10-31. All A1–A5 generated with the built-in image tool and reviewed as a set. Backend model/version not exposed; no unsupported model identifier claimed. Assigned worker gpt-6.1-sol/high. Exact prompts and original output paths for **all 24 calls** are also in [generation.json](generation.json). Nine selected originals are preserved in `masters/`; other rejects remain at the recorded Codex-generated paths, not in public assets.

## Controller-approved transparency recovery

A2, A3, A4 changed from transparent cut-outs to **OPAQUE family tiles** after repeatable white/coloured alpha contamination in dark-line outputs. Controller explicitly approved opaque marketing families in this chat, deadline unchanged. Dark A2/A3/A4 were regenerated with `transparent_background:false`; their rejected transparent attempts used `true` as originally briefed. A1/A5 always used `false`. Light A2/A3/A4 were generated with true alpha then composited onto the paper family ground. No transparent final assets are shipped. Filename `light-line` / `dark-line` describes ink style, NOT alpha.

Pillow post-process: composite selected originals, quantize without dithering to the four specified flat palette colours, then Lanczos contain-resize (never crop) and encode. This eliminates model-generated ground noise and locks colours: light ground #f3eee3, ink #1c1a16, rust #b23a0e, secondary #d8cfbe; dark ground #18181b, ink #f4f4f5, ember #ff8a4c, shadow #71717c. It is a documented deterministic export normalization; no drawn geometry was added. 2x files are upsampled generated masters, not native 2x detail.

## Six-mode placement decision

Paper/light/contrast use light-line; dark/midnight/graphite use dark-line. A5 is the required paper OG artwork in ALL modes, not a runtime dark UI component. Controller permits family tiles instead of six duplicate grounds. In midnight and graphite the dark tile edge is intentional: mount inside a framed level-2 illustration slab, do NOT pretend the art is a seamless background. Orange remains readable on midnight; no sky recolour needed. Preserve the Measured Arc logo #2878E8 as a separate identity asset: images echo camera/tracked-ball geometry, never redraw the logo or mix another blue into illustrations.

## Designer review / picks and rejects

- All six exported WebP sheets inspected: contact-paper/light/dark/midnight/graphite/contrast.jpg. Feature art reviewed at 240px, main story at approximately 600px. Readable consistent pen geometry, one motion accent, quiet spacing; A3 error bars survive thumbnail size. A4 ghost deliberately faint; do not shrink below 240px without another visual check.
- The two `alpha-200-*.png` sheets inspect **final opaque PNGs** at actual 200% on #ffffff / #111113; names retained from the original transparency QA. No cut-out halos remain because shipped files are opaque. Minor raster antialiasing is expected, not a white wash.
- A1 initial: rejected heavy black phone/tripod, glossy balls and extra dimensional fills. R2 light + dark: choose cleaner outline story, one hard phone shadow, scale ticks without numbers. Horizon and ball-size stylization are illustrative, not a calibrated diagram.
- A2 initial: rejected gloss, mechanical knobs, chunky stand. R2 light: choose minimal phone/stand, hollow swing positions. Three transparent dark attempts rejected for white wash, coloured fringes and speckles. Opaque retry: choose clean matching silhouette.
- A3 initial: rejected cream lens and chunky pseudo-3D rim. R2 light: choose transparent lens and visible uncertainty bars, then opaque export. Three transparent dark attempts rejected for alpha wash/speckles. First opaque dark: rejected connector loop resembling a lowercase p; final edit removes ALL magnifier connectors. Error-bar caps are scientific marks, not letters.
- A4 initial: rejected glossy sphere and solid ghost. R2 light: choose flat wireframe sphere and outlined ghost. Three transparent dark attempts rejected for alpha wash/fringes. Opaque dark retry: choose sparse synthetic grid and faint ghost, not a game-engine render.
- A5 initial: rejected an unbriefed phone/tripod and clipped right edge. R2: choose ONLY stroboscopic ball motif, fitted trace, tiny grid, blank left 60%. Blank-left check is saved in checks verification. No title/logo baked in.
- Final images: no visible text, numerals, watermark, third-party mark, real people or likeness. Scientific strokes/ruler ticks/error bars are intentional. All imagery is illustrative, NEVER RECORDED evidence or a measured physical result.

## Integration for S15ai / S15am

Use `/images/marketing/<filename>`; width/height attributes from inventory; `<picture>` WebP with PNG fallback. 1x/2x srcset; do not fetch both formats. Select a single family using the existing theme tokens/mechanism, no new theme framework. Do not CSS-invert these images (would alter spot colours).

| Brief | Exact placement | Alt text (or empty if adjacent text duplicates meaning) | Loading |
|---|---|---|---|
| A1 | Home hero right 45% column, level-2 slab, radius 14px, only slab tilted -2deg | A phone records a falling ball beside a scale; tracked positions continue into a wireframe replay. | eager / high fetch priority for visible hero only |
| A2 | Home Record feature card top, 4:3, at least 240px wide | A phone records a pendulum at three swing positions. | lazy, async decode |
| A3 | Home Fit feature card top, 4:3, at least 240px | Measurement points with uncertainty bars and a fitted curve under a magnifier. | lazy, async decode |
| A4 | Home Replay feature card top, 4:3, at least 240px | A simulated ball and its ghost position above a wireframe floor. | lazy, async decode |
| A5 | OG/social renderer background at 1200x630; logo/title added in code on LEFT 60%, 48px minimum padding | Decorative falling-ball trajectory on a blank title-card ground. | not a page image; no preload; use PNG for compatibility |

S15am may reuse as onboarding illustrations only with the same illustrative caveat; no app code is changed here. Logo/title/live labels remain code-rendered and accessible. OG composition/publication and integrated UI screenshot QA are downstream, not claimed here.

## Final prompts (verbatim)

### A1

**a1-light-line** — source key `a1-light-line-r2`; preserved `masters/a1-light-line.png`.

```text
Subject: a generic smartphone standing upright on a tabletop tripod, filming a small ball falling past a simple metre stick; to the right of the phone the same falling ball is shown as a sequence of evenly timed ghosted positions (stroboscopic dots, increasing spacing) that continue into a clean parabola-free vertical dotted trajectory, which transitions into a minimal wireframe floor plane and grid, suggesting a simulation replay. Composition: left-to-right story, phone at left third, ball sequence centre, simulation wireframe at right third; horizon at 62% height; leave 8% clear margin on all sides. Lighting: none (flat illustration); depth only from the single hard offset shadow under the phone. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background solid #f3eee3. Only the ball and its position dots use the spot colour. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).
ART DIRECTOR CORRECTION: Preserve the three-part left-to-right real clip / increasing-spaced falling positions / wireframe replay story. Simplify the tripod into ONLY outlines, zero solid-black filled phone or legs; phone screen must show only a simple ball and stick, no control icons. Shift the horizon to 62% height. Keep every object 8% inside edges; make all ball positions equal physical diameter, earlier ones may be hollow.
CRITICAL STYLE: this is a minimal TWO-DIMENSIONAL technical-pen drawing, not shaded clipart. Use only flat solid palette colours, no bevels, gradients, texture, light sources, glints or paper grain. Single consistent rounded 2px-equivalent stroke. Tiny hard offset silhouette only where briefed. Do not copy any shading from reference. Strict 16:10 canvas. No text, no glyphs, no logos, no people.
```

**a1-dark-line** — source key `a1-dark-line`; preserved `masters/a1-dark-line.png`.

```text
Subject: a generic smartphone standing upright on a tabletop tripod, filming a small ball falling past a simple metre stick; to the right of the phone the same falling ball is shown as a sequence of evenly timed ghosted positions (stroboscopic dots, increasing spacing) that continue into a clean parabola-free vertical dotted trajectory, which transitions into a minimal wireframe floor plane and grid, suggesting a simulation replay. Composition: left-to-right story, phone at left third, ball sequence centre, simulation wireframe at right third; horizon at 62% height; leave 8% clear margin on all sides. Lighting: none (flat illustration); depth only from the single hard offset shadow under the phone. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background solid #18181b. Only the ball and its position dots use the spot colour. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).
ART DIRECTOR CORRECTION: Preserve the three-part left-to-right real clip / increasing-spaced falling positions / wireframe replay story. Simplify the tripod into ONLY outlines, zero solid-black filled phone or legs; phone screen must show only a simple ball and stick, no control icons. Shift the horizon to 62% height. Keep every object 8% inside edges; make all ball positions equal physical diameter, earlier ones may be hollow.
CRITICAL STYLE: this is a minimal TWO-DIMENSIONAL technical-pen drawing, not shaded clipart. Use only flat solid palette colours, no bevels, gradients, texture, light sources, glints or paper grain. Single consistent rounded 2px-equivalent stroke. Tiny hard offset silhouette only where briefed. Do not copy any shading from reference. Strict 16:10 canvas. No text, no glyphs, no logos, no people.
Dark-surface variant: every structural outline is near-white #f4f4f5, NEVER black; warm ember #ff8a4c only on motion subject. Transparent voids stay truly transparent. Match geometry and minimal pen language, no shading.
```

### A2

**a2-light-line** — source key `a2-light-line-r2`; preserved `masters/a2-light-line.png`.

```text
Subject: a generic phone on a small tripod pointed at a pendulum (a bob on a string hanging from a simple stand), the bob drawn at three faint swing positions. Composition: phone lower-left, pendulum centre-right, object centred optically, 12% margins. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the bob. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).
ART DIRECTOR CORRECTION: Preserve the phone left and pendulum right. Remove ALL knob details, thick stand base, gloss, white highlights and 3D-looking thickness. Phone and stand are minimal uniform outlined shapes; one solid hard-edged offset shadow under phone only. Three bobs same diameter, centre bob flat rust disk, side bobs thin hollow rust circles. No extra shading.
CRITICAL STYLE: this is a minimal TWO-DIMENSIONAL technical-pen drawing, not shaded clipart. Use only flat solid palette colours, no bevels, gradients, texture, light sources, glints or paper grain. Single consistent rounded 2px-equivalent stroke. Tiny hard offset silhouette only where briefed. Do not copy any shading from reference. Strict 4:3 canvas. No text, no glyphs, no logos, no people.
```

**a2-dark-line** — source key `a2-dark-opaque`; preserved `masters/a2-dark-line.png`.

```text
Subject: a generic phone on a small tripod pointed at a pendulum (a bob on a string hanging from a simple stand), the bob drawn at three faint swing positions. Composition: phone lower-left, pendulum centre-right, object centred optically, 12% margins. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background solid #18181b. Spot colour only on the bob. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).
ART DIRECTOR CORRECTION: Preserve the phone left and pendulum right. Remove ALL knob details, thick stand base, gloss, white highlights and 3D-looking thickness. Phone and stand are minimal uniform outlined shapes; one solid hard-edged offset shadow under phone only. Three bobs same diameter, centre bob flat rust disk, side bobs thin hollow rust circles. No extra shading.
CRITICAL STYLE: this is a minimal TWO-DIMENSIONAL technical-pen drawing, not shaded clipart. Use only flat solid palette colours, no bevels, gradients, texture, light sources, glints or paper grain. Single consistent rounded 2px-equivalent stroke. Tiny hard offset silhouette only where briefed. Do not copy any shading from reference. Strict 4:3 canvas. No text, no glyphs, no logos, no people.
Dark-surface variant: every structural outline is near-white #f4f4f5, NEVER black; warm ember #ff8a4c only on motion subject. Transparent voids stay truly transparent. Match geometry and minimal pen language, no shading.
CONTROLLER-APPROVED OPAQUE VARIANT: full canvas MUST be opaque exact solid #18181b, never transparent. Every open interior is same solid #18181b. No gradient, texture or noise anywhere; clean pale #f4f4f5 outlines, ember #ff8a4c motion, one hard #71717c shadow; all fills flat. 4:3 composition, keep 12% clear margins.
```

### A3

**a3-light-line** — source key `a3-light-line-r2`; preserved `masters/a3-light-line.png`.

```text
Subject: a scatter of hand-plotted measurement points with small vertical error bars on a minimal pair of axes (no tick labels), and one smooth fitted curve passing through them; a small magnifier lens hovering over one point. Composition: axes fill 70% of the frame, lens upper-right. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the fitted curve; points in ink. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).
ART DIRECTOR CORRECTION: Preserve axes, visible error bars, smooth curve and magnifier upper right. Simplify magnifier to one clean outlined circle and line handle with ONE solid offset shadow. Lens interior is fully transparent, NOT cream-filled. No pseudo-lettering: error bars are connected vertical lines with short caps and a point, no separate glyphs. Curve is the only rust element. All linework same weight.
CRITICAL STYLE: this is a minimal TWO-DIMENSIONAL technical-pen drawing, not shaded clipart. Use only flat solid palette colours, no bevels, gradients, texture, light sources, glints or paper grain. Single consistent rounded 2px-equivalent stroke. Tiny hard offset silhouette only where briefed. Do not copy any shading from reference. Strict 4:3 canvas. No text, no glyphs, no logos, no people.
```

**a3-dark-line** — source key `a3-dark-opaque-r2`; preserved `masters/a3-dark-line.png`.

```text
Subject: a scatter of hand-plotted measurement points with small vertical error bars on a minimal pair of axes (no tick labels), and one smooth fitted curve passing through them; a small magnifier lens hovering over one point. Composition: axes fill 70% of the frame, lens upper-right. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background solid #18181b. Spot colour only on the fitted curve; points in ink. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).
ART DIRECTOR CORRECTION: Preserve axes, visible error bars, smooth curve and magnifier upper right. Simplify magnifier to one clean outlined circle and line handle with ONE solid offset shadow. Lens interior is fully transparent, NOT cream-filled. No pseudo-lettering: error bars are connected vertical lines with short caps and a point, no separate glyphs. Curve is the only rust element. All linework same weight.
CRITICAL STYLE: this is a minimal TWO-DIMENSIONAL technical-pen drawing, not shaded clipart. Use only flat solid palette colours, no bevels, gradients, texture, light sources, glints or paper grain. Single consistent rounded 2px-equivalent stroke. Tiny hard offset silhouette only where briefed. Do not copy any shading from reference. Strict 4:3 canvas. No text, no glyphs, no logos, no people.
Dark-surface variant: every structural outline is near-white #f4f4f5, NEVER black; warm ember #ff8a4c only on motion subject. Transparent voids stay truly transparent. Match geometry and minimal pen language, no shading.
CONTROLLER-APPROVED OPAQUE VARIANT: full canvas MUST be opaque exact solid #18181b, never transparent. Every open interior is same solid #18181b. No gradient, texture or noise anywhere; clean pale #f4f4f5 outlines, ember #ff8a4c motion, one hard #71717c shadow; all fills flat. 4:3 composition, keep 12% clear margins.
FINAL SINGLE FIX: The last drawing added a small loop resembling a lowercase p where the magnifier leader meets the curve. REMOVE all magnifier leader/connector lines entirely. The magnifier floats unattached in upper-right. Preserve error bars, data points, smooth orange curve, axes, clean pale monoline, small hard offset magnifier shadow and flat opaque #18181b background. NO glyph-like loops anywhere.
```

### A4

**a4-light-line** — source key `a4-light-line-r2`; preserved `masters/a4-light-line.png`.

```text
Subject: a minimal wireframe 3D scene: a floor grid in perspective, a sphere at the top of a dotted vertical path with motion ticks, and a small translucent ghost copy of the sphere lower down, like a simulation playback; a small play-triangle shape drawn as an abstract cut-out in the floor grid corner. Composition: grid vanishing point slightly above centre; sphere at upper centre. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the sphere. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).
ART DIRECTOR CORRECTION: Preserve sparse wireframe grid and vertical path. Main sphere MUST be a flat rust circular disk with only two fine internal wireframe arcs, NO shine or ball texture; lower ghost is an outlined circle with transparent centre and subtle line opacity. No shadow under ghost; one small flat down-right shadow under main sphere only. Grid lines uniform and crisp; triangle no fill.
CRITICAL STYLE: this is a minimal TWO-DIMENSIONAL technical-pen drawing, not shaded clipart. Use only flat solid palette colours, no bevels, gradients, texture, light sources, glints or paper grain. Single consistent rounded 2px-equivalent stroke. Tiny hard offset silhouette only where briefed. Do not copy any shading from reference. Strict 4:3 canvas. No text, no glyphs, no logos, no people.
```

**a4-dark-line** — source key `a4-dark-opaque`; preserved `masters/a4-dark-line.png`.

```text
Subject: a minimal wireframe 3D scene: a floor grid in perspective, a sphere at the top of a dotted vertical path with motion ticks, and a small translucent ghost copy of the sphere lower down, like a simulation playback; a small play-triangle shape drawn as an abstract cut-out in the floor grid corner. Composition: grid vanishing point slightly above centre; sphere at upper centre. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background solid #18181b. Spot colour only on the sphere. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).
ART DIRECTOR CORRECTION: Preserve sparse wireframe grid and vertical path. Main sphere MUST be a flat rust circular disk with only two fine internal wireframe arcs, NO shine or ball texture; lower ghost is an outlined circle with transparent centre and subtle line opacity. No shadow under ghost; one small flat down-right shadow under main sphere only. Grid lines uniform and crisp; triangle no fill.
CRITICAL STYLE: this is a minimal TWO-DIMENSIONAL technical-pen drawing, not shaded clipart. Use only flat solid palette colours, no bevels, gradients, texture, light sources, glints or paper grain. Single consistent rounded 2px-equivalent stroke. Tiny hard offset silhouette only where briefed. Do not copy any shading from reference. Strict 4:3 canvas. No text, no glyphs, no logos, no people.
Dark-surface variant: every structural outline is near-white #f4f4f5, NEVER black; warm ember #ff8a4c only on motion subject. Transparent voids stay truly transparent. Match geometry and minimal pen language, no shading.
CONTROLLER-APPROVED OPAQUE VARIANT: full canvas MUST be opaque exact solid #18181b, never transparent. Every open interior is same solid #18181b. No gradient, texture or noise anywhere; clean pale #f4f4f5 outlines, ember #ff8a4c motion, one hard #71717c shadow; all fills flat. 4:3 composition, keep 12% clear margins.
```

### A5

**a5-light-line** — source key `a5-light-line-r2`; preserved `masters/a5-light-line.png`.

```text
Subject: the falling-ball stroboscopic sequence from A1 (ball positions with increasing spacing) beside a thin fitted curve and a tiny wireframe floor grid, arranged as a single elegant diagonal motif. Composition: ALL artwork confined to the right 40% of the canvas; left 60% completely empty flat background for overlaid text; nothing within 48px of edges. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background solid #f3eee3. Spot colour on ball positions only. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).
ART DIRECTOR CORRECTION: REMOVE THE PHONE AND TRIPOD COMPLETELY: they were not in this brief. Keep ONLY equal-diameter stroboscopic ball positions with increasing spacing, a thin fitted curve and tiny wireframe floor grid, all confined to right 35% (x=65% to 92%); left 60% is absolutely blank flat #f3eee3. Leave 8% clear on right too. No perspective/gloss on balls: flat rust circles, no white shine, no extra shadow per ball. The motif is an editorial scientific diagram, not a product shot.
CRITICAL STYLE: this is a minimal TWO-DIMENSIONAL technical-pen drawing, not shaded clipart. Use only flat solid palette colours, no bevels, gradients, texture, light sources, glints or paper grain. Single consistent rounded 2px-equivalent stroke. Tiny hard offset silhouette only where briefed. Do not copy any shading from reference. Strict 40:21 canvas. No text, no glyphs, no logos, no people.
```

## Export inventory

36 exports (9 selected art/colour variants × 2 densities × 2 formats), WebP quality 82 / method 6. Total public export weight **3,546,328 bytes** (3.38 MiB), all WebPs **539,532 bytes**. Only one responsive source per image should be transferred. Full SHA-256/decoding/dimension results: [checks.json](checks.json).

| File | Pixels | Bytes |
|---|---|---:|
| `Build/web/public/images/marketing/a1-light-line@1x.png` | 1600 × 1000 | 183649 |
| `Build/web/public/images/marketing/a1-light-line@1x.webp` | 1600 × 1000 | 41666 |
| `Build/web/public/images/marketing/a1-light-line@2x.png` | 3200 × 2000 | 598988 |
| `Build/web/public/images/marketing/a1-light-line@2x.webp` | 3200 × 2000 | 92072 |
| `Build/web/public/images/marketing/a2-light-line@1x.png` | 800 × 600 | 64397 |
| `Build/web/public/images/marketing/a2-light-line@1x.webp` | 800 × 600 | 12884 |
| `Build/web/public/images/marketing/a2-light-line@2x.png` | 1600 × 1200 | 149141 |
| `Build/web/public/images/marketing/a2-light-line@2x.webp` | 1600 × 1200 | 31558 |
| `Build/web/public/images/marketing/a3-light-line@1x.png` | 800 × 600 | 63761 |
| `Build/web/public/images/marketing/a3-light-line@1x.webp` | 800 × 600 | 12908 |
| `Build/web/public/images/marketing/a3-light-line@2x.png` | 1600 × 1200 | 148608 |
| `Build/web/public/images/marketing/a3-light-line@2x.webp` | 1600 × 1200 | 31290 |
| `Build/web/public/images/marketing/a4-light-line@1x.png` | 800 × 600 | 86117 |
| `Build/web/public/images/marketing/a4-light-line@1x.webp` | 800 × 600 | 15702 |
| `Build/web/public/images/marketing/a4-light-line@2x.png` | 1600 × 1200 | 216483 |
| `Build/web/public/images/marketing/a4-light-line@2x.webp` | 1600 × 1200 | 42862 |
| `Build/web/public/images/marketing/a5-light-line@1x.png` | 1200 × 630 | 38413 |
| `Build/web/public/images/marketing/a5-light-line@1x.webp` | 1200 × 630 | 8694 |
| `Build/web/public/images/marketing/a5-light-line@2x.png` | 2400 × 1260 | 106959 |
| `Build/web/public/images/marketing/a5-light-line@2x.webp` | 2400 × 1260 | 21986 |
| `Build/web/public/images/marketing/a1-dark-line@1x.png` | 1600 × 1000 | 191215 |
| `Build/web/public/images/marketing/a1-dark-line@1x.webp` | 1600 × 1000 | 38378 |
| `Build/web/public/images/marketing/a1-dark-line@2x.png` | 3200 × 2000 | 605779 |
| `Build/web/public/images/marketing/a1-dark-line@2x.webp` | 3200 × 2000 | 80294 |
| `Build/web/public/images/marketing/a2-dark-line@1x.png` | 800 × 600 | 38076 |
| `Build/web/public/images/marketing/a2-dark-line@1x.webp` | 800 × 600 | 7830 |
| `Build/web/public/images/marketing/a2-dark-line@2x.png` | 1600 × 1200 | 93273 |
| `Build/web/public/images/marketing/a2-dark-line@2x.webp` | 1600 × 1200 | 18726 |
| `Build/web/public/images/marketing/a3-dark-line@1x.png` | 800 × 600 | 42408 |
| `Build/web/public/images/marketing/a3-dark-line@1x.webp` | 800 × 600 | 9048 |
| `Build/web/public/images/marketing/a3-dark-line@2x.png` | 1600 × 1200 | 109539 |
| `Build/web/public/images/marketing/a3-dark-line@2x.webp` | 1600 × 1200 | 21436 |
| `Build/web/public/images/marketing/a4-dark-line@1x.png` | 800 × 600 | 75878 |
| `Build/web/public/images/marketing/a4-dark-line@1x.webp` | 800 × 600 | 15560 |
| `Build/web/public/images/marketing/a4-dark-line@2x.png` | 1600 × 1200 | 194112 |
| `Build/web/public/images/marketing/a4-dark-line@2x.webp` | 1600 × 1200 | 36638 |

## Rights / reproducibility / limits

Generated for this hackathon build using the built-in image tool for Koushik Sadhak Jeet; intended owner-owned project assets. No external artwork, third-party marks, stock imagery, real-person likenesses or footage used. This is creation provenance/intended ownership, not trademark clearance or a legal guarantee of exclusive copyright.

Reproduce: `python evidence/brand/images-a/export_images.py` from the worktree, using preserved masters and installed Pillow; no install, API key or external call. Original masters retain tool provenance metadata; optimized public images omit copied metadata. No Meta/GPU API, secrets, Chrome, deployment, public upload or publication. Skipped: optional dark OG variant, web code/styles/manifest, production integration. Risk: use opaque framed slabs, not seamless cut-outs; 2x is resampled and tiny ghost features need integrated-size QA.
