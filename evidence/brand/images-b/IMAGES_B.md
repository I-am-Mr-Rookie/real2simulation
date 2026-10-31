# Batch B — in-app scientific illustrations

Generated 2026-10-31 for S15al-orch197. **PARTIAL: B1–B6 chosen white masters, keyed into transparent light/dark candidate exports; optical stroke consistency still needs a follow-up. B7 intentionally skipped.** No web integration in this run. Do not treat every candidate as designer-accepted: B1 is faint at 120px and B5 is heavier than the rest.

## Art direction and recovery

Editorial scientific line drawings, one neutral ink and one rust/ember spot, restrained solid offset shadow, negative space, no lettering, marks, people or likenesses. The Measured Arc logo remains unchanged in #2878E8: the illustrations echo its tracked ball/arc geometry, not its logo. Brief-specified rust #b23a0e / ember #ff8a4c retained, rather than silently recolouring the approved logo. Midnight retains ember: the contact sheet is the deciding evidence; orange remains readable on ink blue. Paper/light/contrast select light-line; dark/midnight/graphite select dark-line.

All 12 original transparent generations were critically inspected. They leaned glossy and dimensional; dark-line outputs additionally suffered severe mottled white/coloured alpha debris. A second generation was requested for EVERY weak variant (12 revisions). The dark debris persisted. These are rejected, not presented as acceptable outputs. On controller's explicit recovery instruction (same chat, Oct31 before 09:15Z), six opaque pure-white masters were generated with simplified pen-diagram prompts. Those are the final picks. Transparent-background arguments: true on all first/second passes, false ONLY on the six recovery masters, as explicitly authorized. Final shipped assets are genuinely transparent.

Post-process in export_assets.py: alpha = 255 - luminance, white-noise floor 24/255, rescaled to full coverage; rust pixels detected by R-G >32 and R-B >45, assigned full alpha. RGB replaced deterministically with the exact light/dark ink and spot colours, so no white RGB matte remains in transparent edges. Lanczos export antialiasing, no generative edits in Python. Bounding-box crop and proportional fit preserve at least 15% margins (B3 cluster half-width). Derived dark variants share EXACT geometry with light, avoiding independent-draw inconsistencies. No hand-written vector artwork or fake SVGs. Neutral shadow is keyed with the ink: dark shadows are a lit ink silhouette, not a separate #71717c material. Minor generated line-weight variation remains between instruments; not calibrated scientific diagrams.

B7 is OPTIONAL under handout: skip all textures. Flat token grounds avoid alpha artefacts, noise and payload. Contrast receives no texture as briefed. No texture files shipped, so <=1.15:1 texture contrast check is not applicable; base colour against itself is 1:1. The brief conflicts (single WebP q70 versus later 1x/2x PNG/WebP instruction) therefore do not affect exports.

## Integration for S15am / S15ai

URL prefix: /images/app/. Each bN has bN-light@1x.webp, bN-light@2x.webp, bN-dark@1x.webp, bN-dark@2x.webp, with same-name .png fallbacks. Use picture/source WebP + img PNG; srcset 1x/2x. Select variant from actual data-theme before paint, not OS preference alone. Reserve width/height or aspect-ratio. Do not load both palette variants; never recolour the blue logo. All are decorative next to visible state copy: recommended alt=""; descriptive alternatives below are only for standalone use. Mandatory evidence labels remain live text and verbatim. No illustration implies a measured/calibrated result.

| Brief | Exact placement | Display size | Descriptive alt if standalone | Loading |
|---|---|---|---|---|
| B1 | Workspace centre viewport above No scene yet | 180px tall, minimum 120px | Empty scene grid with a waiting cube outline and ball | eager only when initial empty viewport; not high-priority sitewide |
| B2 | Workspace upload dropzone centre | 160px, scale 1.03 only on drag-over | A short physics film strip entering an upload tray | eager in initial dropzone; otherwise lazy |
| B3 | Library empty filter result / centred missing-thumbnail fallback on elevated surface | 200px empty state; card width auto, 16:9 | Pendulum cards beside a magnifier | lazy, decoding async |
| B4 | Lab right chart/viewport never-run state | 200px | Ball on a ramp beside experiment controls | lazy, decoding async |
| B5 | Agent panel idle top / question thumbnail only when no clip frame | 120px / 96px; checked at 64px | An instrument lens, ruler and dotted speech bubble | lazy, never replace a real clip frame |
| B6 | Abstained result card / unsupported error empty state | 140px | Incomplete ruler beside a falling ball and off-centre level | lazy; retain scale unverified and Held-out caveat labels |

## Final prompts (verbatim)

### B1-WHITE — final master for light + dark

Subject: an empty wireframe floor grid in perspective with a single dotted outline of a cube waiting to appear, and a tiny ball resting at the grid origin. Composition: centred, grid occupies lower 60%, 15% margins.  MASTER FOR DETERMINISTIC INK EXTRACTION: pure opaque white background #ffffff everywhere outside the strokes. Extremely minimal editorial scientific technical-pen line drawing. Single consistent crisp black #1c1a16 rounded stroke, just 3px wide at 1000px. No filled areas at all: interiors pure white too. Only the ball / pendulum bob is a solid flat #b23a0e spot. Tiny solid black offset shadow down-right under main subject only. NO shading, gradients, highlights, texture, grain, sheen, 3D rendering, volumetric objects or dimensional stickers. Flat diagram. Reduce ruler ticks, knobs and tripod detail to their essential silhouette. Generous 18% clear margins. Square canvas. Calm precise scientific instrument language, motion arcs echo Measured Arc but no brand mark. No text, numerals, letters, logos, watermarks, real people, faces, UI chrome or third-party likenesses.

Generation: built-in image_gen__imagegen, transparent_background=false. Pick: masters/b1-white.png. Derived light/dark via authorized deterministic ink extraction. No separate midnight regeneration required.

### B2-WHITE — final master for light + dark

Subject: a short strip of video film frames (3 frames, each showing a tiny ball at a different height) sliding down into an open tray-like upward arrow cradle. Composition: centred, frames enter from upper right, 15% margins.  MASTER FOR DETERMINISTIC INK EXTRACTION: pure opaque white background #ffffff everywhere outside the strokes. Extremely minimal editorial scientific technical-pen line drawing. Single consistent crisp black #1c1a16 rounded stroke, just 3px wide at 1000px. No filled areas at all: interiors pure white too. Only the ball / pendulum bob is a solid flat #b23a0e spot. Tiny solid black offset shadow down-right under main subject only. NO shading, gradients, highlights, texture, grain, sheen, 3D rendering, volumetric objects or dimensional stickers. Flat diagram. Reduce ruler ticks, knobs and tripod detail to their essential silhouette. Generous 18% clear margins. Square canvas. Calm precise scientific instrument language, motion arcs echo Measured Arc but no brand mark. No text, numerals, letters, logos, watermarks, real people, faces, UI chrome or third-party likenesses.

Generation: built-in image_gen__imagegen, transparent_background=false. Pick: masters/b2-white.png. Derived light/dark via authorized deterministic ink extraction. No separate midnight regeneration required.

### B3-WHITE — final master for light + dark

Subject: three stacked blank cards fanned slightly like index cards, the top one showing a tiny pendulum line drawing, beside a small magnifier. Composition: centred cluster occupying middle 50% width.  MASTER FOR DETERMINISTIC INK EXTRACTION: pure opaque white background #ffffff everywhere outside the strokes. Extremely minimal editorial scientific technical-pen line drawing. Single consistent crisp black #1c1a16 rounded stroke, just 3px wide at 1000px. No filled areas at all: interiors pure white too. Only the ball / pendulum bob is a solid flat #b23a0e spot. Tiny solid black offset shadow down-right under main subject only. NO shading, gradients, highlights, texture, grain, sheen, 3D rendering, volumetric objects or dimensional stickers. Flat diagram. Reduce ruler ticks, knobs and tripod detail to their essential silhouette. Generous 18% clear margins. 16:9 canvas, centred cluster half the canvas width. Calm precise scientific instrument language, motion arcs echo Measured Arc but no brand mark. No text, numerals, letters, logos, watermarks, real people, faces, UI chrome or third-party likenesses.

Generation: built-in image_gen__imagegen, transparent_background=false. Pick: masters/b3-white.png. Derived light/dark via authorized deterministic ink extraction. No separate midnight regeneration required.

### B4-WHITE — final master for light + dark

Subject: an inclined plane (ramp) on a simple stand with a ball at the top, two small slider-knob shapes floating beside it like physical control knobs, and a faint dotted path down the ramp. Composition: ramp diagonal lower-left to centre-right, knobs upper-right.  MASTER FOR DETERMINISTIC INK EXTRACTION: pure opaque white background #ffffff everywhere outside the strokes. Extremely minimal editorial scientific technical-pen line drawing. Single consistent crisp black #1c1a16 rounded stroke, just 3px wide at 1000px. No filled areas at all: interiors pure white too. Only the ball / pendulum bob is a solid flat #b23a0e spot. Tiny solid black offset shadow down-right under main subject only. NO shading, gradients, highlights, texture, grain, sheen, 3D rendering, volumetric objects or dimensional stickers. Flat diagram. Reduce ruler ticks, knobs and tripod detail to their essential silhouette. Generous 18% clear margins. 4:3 canvas. Calm precise scientific instrument language, motion arcs echo Measured Arc but no brand mark. No text, numerals, letters, logos, watermarks, real people, faces, UI chrome or third-party likenesses.

Generation: built-in image_gen__imagegen, transparent_background=false. Pick: masters/b4-white.png. Derived light/dark via authorized deterministic ink extraction. No separate midnight regeneration required.

### B5-WHITE — final master for light + dark

Subject: an abstract agent glyph: a small round lens/eye-like instrument (not a face) on a tripod, next to a ruler laid diagonally and a small floating speech-bubble outline that contains only a dotted line. Composition: centred, compact, 18% margins, legible at 64px.  MASTER FOR DETERMINISTIC INK EXTRACTION: pure opaque white background #ffffff everywhere outside the strokes. Extremely minimal editorial scientific technical-pen line drawing. Single consistent crisp black #1c1a16 rounded stroke, just 3px wide at 1000px. No filled areas at all: interiors pure white too. Only the lens ring is a solid flat #b23a0e spot. Tiny solid black offset shadow down-right under main subject only. NO shading, gradients, highlights, texture, grain, sheen, 3D rendering, volumetric objects or dimensional stickers. Flat diagram. Reduce ruler ticks, knobs and tripod detail to their essential silhouette. Generous 18% clear margins. Square canvas. Calm precise scientific instrument language, motion arcs echo Measured Arc but no brand mark. No text, numerals, letters, logos, watermarks, real people, faces, UI chrome or third-party likenesses.

Generation: built-in image_gen__imagegen, transparent_background=false. Pick: masters/b5-white.png. Derived light/dark via authorized deterministic ink extraction. No separate midnight regeneration required.

### B6-WHITE — final master for light + dark

Subject: a ruler drawn with one end fading into dotted outline (incomplete), a small falling ball beside it, and a small spirit level whose bubble sits off-centre. Composition: centred, ruler diagonal.  MASTER FOR DETERMINISTIC INK EXTRACTION: pure opaque white background #ffffff everywhere outside the strokes. Extremely minimal editorial scientific technical-pen line drawing. Single consistent crisp black #1c1a16 rounded stroke, just 3px wide at 1000px. No filled areas at all: interiors pure white too. Only the off-centre level bubble is a solid flat #b23a0e spot. Tiny solid black offset shadow down-right under main subject only. NO shading, gradients, highlights, texture, grain, sheen, 3D rendering, volumetric objects or dimensional stickers. Flat diagram. Reduce ruler ticks, knobs and tripod detail to their essential silhouette. Generous 18% clear margins. Square canvas. Calm precise scientific instrument language, motion arcs echo Measured Arc but no brand mark. No text, numerals, letters, logos, watermarks, real people, faces, UI chrome or third-party likenesses.

Generation: built-in image_gen__imagegen, transparent_background=false. Pick: masters/b6-white.png. Derived light/dark via authorized deterministic ink extraction. No separate midnight regeneration required.

## Rejected prompts and audit

All first-pass and revision prompts are included verbatim below; GENERATED source paths and final-master source paths are in GENERATIONS.json. Original generated files remain under Codex generated_images; only six final masters are copied into this worktree. Rejected images are not served by the application.

### b1-light — rejected

Subject: an empty wireframe floor grid in perspective with a single dotted outline of a cube waiting to appear, and a tiny ball resting at the grid origin. Composition: centred, grid occupies lower 60%, 15% margins. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the tiny ball. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. Square canvas.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b1-dark — rejected

Subject: an empty wireframe floor grid in perspective with a single dotted outline of a cube waiting to appear, and a tiny ball resting at the grid origin. Composition: centred, grid occupies lower 60%, 15% margins. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent. Spot colour only on the tiny ball. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. Square canvas.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b2-light — rejected

Subject: a short strip of video film frames (3 frames, each showing a tiny ball at a different height) sliding down into an open tray-like upward arrow cradle. Composition: centred, frames enter from upper right, 15% margins. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour on the ball inside each frame. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. Square canvas.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b2-dark — rejected

Subject: a short strip of video film frames (3 frames, each showing a tiny ball at a different height) sliding down into an open tray-like upward arrow cradle. Composition: centred, frames enter from upper right, 15% margins. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent. Spot colour on the ball inside each frame. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. Square canvas.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b3-light — rejected

Subject: three stacked blank cards fanned slightly like index cards, the top one showing a tiny pendulum line drawing, beside a small magnifier. Composition: centred cluster occupying middle 50% width. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the pendulum bob. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. Wide 16:9 canvas.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b3-dark — rejected

Subject: three stacked blank cards fanned slightly like index cards, the top one showing a tiny pendulum line drawing, beside a small magnifier. Composition: centred cluster occupying middle 50% width. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent. Spot colour only on the pendulum bob. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. Wide 16:9 canvas.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b4-light — rejected

Subject: an inclined plane (ramp) on a simple stand with a ball at the top, two small slider-knob shapes floating beside it like physical control knobs, and a faint dotted path down the ramp. Composition: ramp diagonal lower-left to centre-right, knobs upper-right. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the ball. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. 4:3 canvas.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b4-dark — rejected

Subject: an inclined plane (ramp) on a simple stand with a ball at the top, two small slider-knob shapes floating beside it like physical control knobs, and a faint dotted path down the ramp. Composition: ramp diagonal lower-left to centre-right, knobs upper-right. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent. Spot colour only on the ball. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. 4:3 canvas.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b5-light — rejected

Subject: an abstract agent glyph: a small round lens/eye-like instrument (not a face) on a tripod, next to a ruler laid diagonally and a small floating speech-bubble outline that contains only a dotted line. Composition: centred, compact, 18% margins, legible at 64px. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the lens ring. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. Square canvas.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b5-dark — rejected

Subject: an abstract agent glyph: a small round lens/eye-like instrument (not a face) on a tripod, next to a ruler laid diagonally and a small floating speech-bubble outline that contains only a dotted line. Composition: centred, compact, 18% margins, legible at 64px. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent. Spot colour only on the lens ring. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. Square canvas.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b6-light — rejected

Subject: a ruler drawn with one end fading into dotted outline (incomplete), a small falling ball beside it, and a small spirit level whose bubble sits off-centre. Composition: centred, ruler diagonal. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the level bubble. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. Square canvas.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b6-dark — rejected

Subject: a ruler drawn with one end fading into dotted outline (incomplete), a small falling ball beside it, and a small spirit level whose bubble sits off-centre. Composition: centred, ruler diagonal. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent. Spot colour only on the level bubble. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only). Production art direction: clean transparent alpha, no background panel or vignette. Make every ink stroke crisp and consistent. Restrained scientific stationery illustration, not a logo. Keep all subject matter within the stated margins. Flat fills only. Render at least 1024px on the long edge. Square canvas.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b1-light-r2 — rejected

Subject: an empty wireframe floor grid in perspective with a single dotted outline of a cube waiting to appear, and a tiny ball resting at the grid origin. Composition: centred, grid occupies lower 60%, 15% margins.  REVISION: the first attempt was too glossy, shaded and bulky. Draw a MINIMAL FLAT SCIENTIFIC LINE ILLUSTRATION, almost a technical pen diagram, not a rendered object or dimensional sticker. ONE uniform 3px rounded stroke per 1000px canvas. Every large interior is transparent negative space; only a few tiny flat neutral patches. ALL structure outlines and ticks #1c1a16, tiny secondary fill #d8cfbe, hard offset shadow #1c1a16. Exactly one flat spot colour #b23a0e only on the ball or pendulum bob. NO highlights on any ball or lens, no sheen, no gradients, no volume shading, no bevels, no reflections, no stippling, no distressed holes, no texture, no glow. Just ONE small down-right offset solid shadow under the main subject. Keep the whole cluster within 18% clear outer margins. Calm, intelligent, precise, tactile, gently handmade line caps. No text, letters, numbers, logos, watermarks, UI chrome, people, faces, brands or likenesses. Square canvas. Truly transparent background with clean alpha. No white background or backing shape.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b1-dark-r2 — rejected

Subject: an empty wireframe floor grid in perspective with a single dotted outline of a cube waiting to appear, and a tiny ball resting at the grid origin. Composition: centred, grid occupies lower 60%, 15% margins.  REVISION: the first attempt was too glossy, shaded and bulky. Draw a MINIMAL FLAT SCIENTIFIC LINE ILLUSTRATION, almost a technical pen diagram, not a rendered object or dimensional sticker. ONE uniform 3px rounded stroke per 1000px canvas. Every large interior is transparent negative space; only a few tiny flat neutral patches. ALL structure outlines and ticks must be bright #f4f4f5, tiny secondary fill #2e2e35, hard offset shadow #71717c. No dark outlines against transparent canvas. Exactly one flat spot colour #ff8a4c only on the ball or pendulum bob. NO highlights on any ball or lens, no sheen, no gradients, no volume shading, no bevels, no reflections, no stippling, no distressed holes, no texture, no glow. Just ONE small down-right offset solid shadow under the main subject. Keep the whole cluster within 18% clear outer margins. Calm, intelligent, precise, tactile, gently handmade line caps. No text, letters, numbers, logos, watermarks, UI chrome, people, faces, brands or likenesses. Square canvas. Truly transparent background with clean alpha. No white background or backing shape.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b2-light-r2 — rejected

Subject: a short strip of video film frames (3 frames, each showing a tiny ball at a different height) sliding down into an open tray-like upward arrow cradle. Composition: centred, frames enter from upper right, 15% margins.  REVISION: the first attempt was too glossy, shaded and bulky. Draw a MINIMAL FLAT SCIENTIFIC LINE ILLUSTRATION, almost a technical pen diagram, not a rendered object or dimensional sticker. ONE uniform 3px rounded stroke per 1000px canvas. Every large interior is transparent negative space; only a few tiny flat neutral patches. ALL structure outlines and ticks #1c1a16, tiny secondary fill #d8cfbe, hard offset shadow #1c1a16. Exactly one flat spot colour #b23a0e only on the ball or pendulum bob. NO highlights on any ball or lens, no sheen, no gradients, no volume shading, no bevels, no reflections, no stippling, no distressed holes, no texture, no glow. Just ONE small down-right offset solid shadow under the main subject. Keep the whole cluster within 18% clear outer margins. Calm, intelligent, precise, tactile, gently handmade line caps. No text, letters, numbers, logos, watermarks, UI chrome, people, faces, brands or likenesses. Square canvas. Truly transparent background with clean alpha. No white background or backing shape.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b2-dark-r2 — rejected

Subject: a short strip of video film frames (3 frames, each showing a tiny ball at a different height) sliding down into an open tray-like upward arrow cradle. Composition: centred, frames enter from upper right, 15% margins.  REVISION: the first attempt was too glossy, shaded and bulky. Draw a MINIMAL FLAT SCIENTIFIC LINE ILLUSTRATION, almost a technical pen diagram, not a rendered object or dimensional sticker. ONE uniform 3px rounded stroke per 1000px canvas. Every large interior is transparent negative space; only a few tiny flat neutral patches. ALL structure outlines and ticks must be bright #f4f4f5, tiny secondary fill #2e2e35, hard offset shadow #71717c. No dark outlines against transparent canvas. Exactly one flat spot colour #ff8a4c only on the ball or pendulum bob. NO highlights on any ball or lens, no sheen, no gradients, no volume shading, no bevels, no reflections, no stippling, no distressed holes, no texture, no glow. Just ONE small down-right offset solid shadow under the main subject. Keep the whole cluster within 18% clear outer margins. Calm, intelligent, precise, tactile, gently handmade line caps. No text, letters, numbers, logos, watermarks, UI chrome, people, faces, brands or likenesses. Square canvas. Truly transparent background with clean alpha. No white background or backing shape.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b3-light-r2 — rejected

Subject: three stacked blank cards fanned slightly like index cards, the top one showing a tiny pendulum line drawing, beside a small magnifier. Composition: centred cluster occupying middle 50% width.  REVISION: the first attempt was too glossy, shaded and bulky. Draw a MINIMAL FLAT SCIENTIFIC LINE ILLUSTRATION, almost a technical pen diagram, not a rendered object or dimensional sticker. ONE uniform 3px rounded stroke per 1000px canvas. Every large interior is transparent negative space; only a few tiny flat neutral patches. ALL structure outlines and ticks #1c1a16, tiny secondary fill #d8cfbe, hard offset shadow #1c1a16. Exactly one flat spot colour #b23a0e only on the ball or pendulum bob. NO highlights on any ball or lens, no sheen, no gradients, no volume shading, no bevels, no reflections, no stippling, no distressed holes, no texture, no glow. Just ONE small down-right offset solid shadow under the main subject. Keep the whole cluster within 18% clear outer margins. Calm, intelligent, precise, tactile, gently handmade line caps. No text, letters, numbers, logos, watermarks, UI chrome, people, faces, brands or likenesses. 16:9 canvas, cluster middle 50% width. Truly transparent background with clean alpha. No white background or backing shape.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b3-dark-r2 — rejected

Subject: three stacked blank cards fanned slightly like index cards, the top one showing a tiny pendulum line drawing, beside a small magnifier. Composition: centred cluster occupying middle 50% width.  REVISION: the first attempt was too glossy, shaded and bulky. Draw a MINIMAL FLAT SCIENTIFIC LINE ILLUSTRATION, almost a technical pen diagram, not a rendered object or dimensional sticker. ONE uniform 3px rounded stroke per 1000px canvas. Every large interior is transparent negative space; only a few tiny flat neutral patches. ALL structure outlines and ticks must be bright #f4f4f5, tiny secondary fill #2e2e35, hard offset shadow #71717c. No dark outlines against transparent canvas. Exactly one flat spot colour #ff8a4c only on the ball or pendulum bob. NO highlights on any ball or lens, no sheen, no gradients, no volume shading, no bevels, no reflections, no stippling, no distressed holes, no texture, no glow. Just ONE small down-right offset solid shadow under the main subject. Keep the whole cluster within 18% clear outer margins. Calm, intelligent, precise, tactile, gently handmade line caps. No text, letters, numbers, logos, watermarks, UI chrome, people, faces, brands or likenesses. 16:9 canvas, cluster middle 50% width. Truly transparent background with clean alpha. No white background or backing shape.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b4-light-r2 — rejected

Subject: an inclined plane (ramp) on a simple stand with a ball at the top, two small slider-knob shapes floating beside it like physical control knobs, and a faint dotted path down the ramp. Composition: ramp diagonal lower-left to centre-right, knobs upper-right.  REVISION: the first attempt was too glossy, shaded and bulky. Draw a MINIMAL FLAT SCIENTIFIC LINE ILLUSTRATION, almost a technical pen diagram, not a rendered object or dimensional sticker. ONE uniform 3px rounded stroke per 1000px canvas. Every large interior is transparent negative space; only a few tiny flat neutral patches. ALL structure outlines and ticks #1c1a16, tiny secondary fill #d8cfbe, hard offset shadow #1c1a16. Exactly one flat spot colour #b23a0e only on the ball or pendulum bob. NO highlights on any ball or lens, no sheen, no gradients, no volume shading, no bevels, no reflections, no stippling, no distressed holes, no texture, no glow. Just ONE small down-right offset solid shadow under the main subject. Keep the whole cluster within 18% clear outer margins. Calm, intelligent, precise, tactile, gently handmade line caps. No text, letters, numbers, logos, watermarks, UI chrome, people, faces, brands or likenesses. 4:3 canvas. Truly transparent background with clean alpha. No white background or backing shape.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b4-dark-r2 — rejected

Subject: an inclined plane (ramp) on a simple stand with a ball at the top, two small slider-knob shapes floating beside it like physical control knobs, and a faint dotted path down the ramp. Composition: ramp diagonal lower-left to centre-right, knobs upper-right.  REVISION: the first attempt was too glossy, shaded and bulky. Draw a MINIMAL FLAT SCIENTIFIC LINE ILLUSTRATION, almost a technical pen diagram, not a rendered object or dimensional sticker. ONE uniform 3px rounded stroke per 1000px canvas. Every large interior is transparent negative space; only a few tiny flat neutral patches. ALL structure outlines and ticks must be bright #f4f4f5, tiny secondary fill #2e2e35, hard offset shadow #71717c. No dark outlines against transparent canvas. Exactly one flat spot colour #ff8a4c only on the ball or pendulum bob. NO highlights on any ball or lens, no sheen, no gradients, no volume shading, no bevels, no reflections, no stippling, no distressed holes, no texture, no glow. Just ONE small down-right offset solid shadow under the main subject. Keep the whole cluster within 18% clear outer margins. Calm, intelligent, precise, tactile, gently handmade line caps. No text, letters, numbers, logos, watermarks, UI chrome, people, faces, brands or likenesses. 4:3 canvas. Truly transparent background with clean alpha. No white background or backing shape.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b5-dark-r2 — rejected

Subject: an abstract agent glyph: a small round lens/eye-like instrument (not a face) on a tripod, next to a ruler laid diagonally and a small floating speech-bubble outline that contains only a dotted line. Composition: centred, compact, 18% margins, legible at 64px.  REVISION: the first attempt was too glossy, shaded and bulky. Draw a MINIMAL FLAT SCIENTIFIC LINE ILLUSTRATION, almost a technical pen diagram, not a rendered object or dimensional sticker. ONE uniform 3px rounded stroke per 1000px canvas. Every large interior is transparent negative space; only a few tiny flat neutral patches. ALL structure outlines and ticks must be bright #f4f4f5, tiny secondary fill #2e2e35, hard offset shadow #71717c. No dark outlines against transparent canvas. Exactly one flat spot colour #ff8a4c only on the lens ring. NO highlights on any ball or lens, no sheen, no gradients, no volume shading, no bevels, no reflections, no stippling, no distressed holes, no texture, no glow. Just ONE small down-right offset solid shadow under the main subject. Keep the whole cluster within 18% clear outer margins. Calm, intelligent, precise, tactile, gently handmade line caps. No text, letters, numbers, logos, watermarks, UI chrome, people, faces, brands or likenesses. Square canvas. Truly transparent background with clean alpha. No white background or backing shape.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### b6-light-r2 — rejected

Subject: a ruler drawn with one end fading into dotted outline (incomplete), a small falling ball beside it, and a small spirit level whose bubble sits off-centre. Composition: centred, ruler diagonal.  REVISION: the first attempt was too glossy, shaded and bulky. Draw a MINIMAL FLAT SCIENTIFIC LINE ILLUSTRATION, almost a technical pen diagram, not a rendered object or dimensional sticker. ONE uniform 3px rounded stroke per 1000px canvas. Every large interior is transparent negative space; only a few tiny flat neutral patches. ALL structure outlines and ticks #1c1a16, tiny secondary fill #d8cfbe, hard offset shadow #1c1a16. Exactly one flat spot colour #b23a0e only on the off-centre bubble in the level. NO highlights on any ball or lens, no sheen, no gradients, no volume shading, no bevels, no reflections, no stippling, no distressed holes, no texture, no glow. Just ONE small down-right offset solid shadow under the main subject. Keep the whole cluster within 18% clear outer margins. Calm, intelligent, precise, tactile, gently handmade line caps. No text, letters, numbers, logos, watermarks, UI chrome, people, faces, brands or likenesses. Square canvas. Truly transparent background with clean alpha. No white background or backing shape.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b5-light-r2 — rejected

Subject: an abstract agent glyph: a small round lens/eye-like instrument (not a face) on a tripod, next to a ruler laid diagonally and a small floating speech-bubble outline that contains only a dotted line. Composition: centred, compact, 18% margins, legible at 64px.  REVISION: first attempt was glossy, shaded, too detailed and dimensional. MINIMAL FLAT SCIENTIFIC PEN DIAGRAM with uniform 3px rounded strokes per 1000px. Large interiors transparent, not white filled. Structure lines #1c1a16, tiny secondary fill #d8cfbe, hard offset shadow #1c1a16, spot #b23a0e. Only the lens ring gets the spot colour. Ball neutral. No highlights, reflections, gradients, gloss, volumetric shading, 3D, bevels, stippling or distressed alpha. ONE small down-right hard offset solid shadow under main object. 18% margins on square canvas. Calm, intelligent, precise line art. No text, letters, numbers, logos, watermarks, faces, UI chrome, people, brands or likenesses. Truly transparent background, clean alpha. No white backing shape.

Reason: glossy/dimensional fills, over-detailed instrument styling or inconsistent line weight; superseded by the clean white-master pass.

### b6-dark-r2 — rejected

Subject: a ruler drawn with one end fading into dotted outline (incomplete), a small falling ball beside it, and a small spirit level whose bubble sits off-centre. Composition: centred, ruler diagonal.  REVISION: first attempt was glossy, shaded, too detailed and dimensional. MINIMAL FLAT SCIENTIFIC PEN DIAGRAM with uniform 3px rounded strokes per 1000px. Large interiors transparent, not white filled. Structure lines #f4f4f5, tiny secondary fill #2e2e35, hard offset shadow #71717c, spot #ff8a4c. Only the off-centre bubble in the level gets the spot colour. Ball neutral. No highlights, reflections, gradients, gloss, volumetric shading, 3D, bevels, stippling or distressed alpha. ONE small down-right hard offset solid shadow under main object. 18% margins on square canvas. Calm, intelligent, precise line art. No text, letters, numbers, logos, watermarks, faces, UI chrome, people, brands or likenesses. Truly transparent background, clean alpha. No white backing shape.

Reason: dark-mode structure/palette and severe mottled alpha debris; revision did not reliably repair it.

### File inventory

| File (under Build/web/public/images/app/) | Pixels | Bytes |
|---|---|---:|
| b1-light@1x.png | 512 × 512 | 29099 |
| b1-light@1x.webp | 512 × 512 | 14326 |
| b1-light@2x.png | 1024 × 1024 | 67228 |
| b1-light@2x.webp | 1024 × 1024 | 32458 |
| b1-dark@1x.png | 512 × 512 | 29333 |
| b1-dark@1x.webp | 512 × 512 | 22076 |
| b1-dark@2x.png | 1024 × 1024 | 67841 |
| b1-dark@2x.webp | 1024 × 1024 | 51048 |
| b2-light@1x.png | 512 × 512 | 54770 |
| b2-light@1x.webp | 512 × 512 | 23028 |
| b2-light@2x.png | 1024 × 1024 | 153815 |
| b2-light@2x.webp | 1024 × 1024 | 63828 |
| b2-dark@1x.png | 512 × 512 | 51094 |
| b2-dark@1x.webp | 512 × 512 | 35600 |
| b2-dark@2x.png | 1024 × 1024 | 170088 |
| b2-dark@2x.webp | 1024 × 1024 | 94470 |
| b3-light@1x.png | 960 × 540 | 48071 |
| b3-light@1x.webp | 960 × 540 | 20894 |
| b3-light@2x.png | 1920 × 1080 | 139844 |
| b3-light@2x.webp | 1920 × 1080 | 58816 |
| b3-dark@1x.png | 960 × 540 | 51379 |
| b3-dark@1x.webp | 960 × 540 | 33732 |
| b3-dark@2x.png | 1920 × 1080 | 153556 |
| b3-dark@2x.webp | 1920 × 1080 | 82260 |
| b4-light@1x.png | 800 × 600 | 65482 |
| b4-light@1x.webp | 800 × 600 | 23724 |
| b4-light@2x.png | 1600 × 1200 | 173760 |
| b4-light@2x.webp | 1600 × 1200 | 66112 |
| b4-dark@1x.png | 800 × 600 | 56079 |
| b4-dark@1x.webp | 800 × 600 | 41596 |
| b4-dark@2x.png | 1600 × 1200 | 176648 |
| b4-dark@2x.webp | 1600 × 1200 | 96298 |
| b5-light@1x.png | 384 × 384 | 35397 |
| b5-light@1x.webp | 384 × 384 | 15600 |
| b5-light@2x.png | 768 × 768 | 85213 |
| b5-light@2x.webp | 768 × 768 | 37064 |
| b5-dark@1x.png | 384 × 384 | 40592 |
| b5-dark@1x.webp | 384 × 384 | 25252 |
| b5-dark@2x.png | 768 × 768 | 99807 |
| b5-dark@2x.webp | 768 × 768 | 54238 |
| b6-light@1x.png | 512 × 512 | 29240 |
| b6-light@1x.webp | 512 × 512 | 12292 |
| b6-light@2x.png | 1024 × 1024 | 79835 |
| b6-light@2x.webp | 1024 × 1024 | 30936 |
| b6-dark@1x.png | 512 × 512 | 27824 |
| b6-dark@1x.webp | 512 × 512 | 19962 |
| b6-dark@2x.png | 1024 × 1024 | 81443 |
| b6-dark@2x.webp | 1024 × 1024 | 46852 |

Palette note: the extraction uses exact ink/spot inputs; Lanczos resampling introduces mixed/overshoot RGB at edges, even some full-alpha pixels. A strict two-RGB-colours assertion failed and is NOT a passing check. Transparency and geometry assertions pass. No claim of pixel-perfect post-resample palette.

## Rights and limitations

Generated for this hackathon build with the built-in image tool for Koushik Sadhak Jeet; intended owner-owned assets. No third-party marks, stock assets, real-person likenesses or artwork references used. This is creation provenance, not a legal guarantee of exclusive copyright or trademark clearance. Built-in backend/model version and exact generation charges are not exposed; no claimed model identifier or invented cost. No API key, Meta/GPU call, publication, deployment, secrets or account changes.

## Exports and fresh review

Exact files, pixel dimensions and byte counts: EXPORTS.json (all 48 exports; PNG fallback and WebP q82 at 1x/2x). Total served export family: **2,969,900 bytes**, comprising **1,002,462 WebP** and **1,967,438 PNG** bytes; clients should load one matching format/density/palette, not the family. PNG files preserve exact palette; lossy WebP can vary edge RGB slightly. All outputs pass size/alpha assertions in export_assets.py. Six contact-<mode>.png sheets show every brief on its intended theme variant at enlarged and smallest-placement scales. alpha-200pct.png is a 200% nearest-neighbour edge proof on #ffffff and #111113. Fresh visual review: no white/coloured alpha debris in keyed exports, no garbled text or third-party marks, all six grounds workable, ember retained for midnight. However B1's grid/cube are too faint at 120px and B5 has a visibly heavier stroke and filled lens rather than thin accent ring. This prevents full consistency acceptance despite successful recovery. No runtime integration claimed.
