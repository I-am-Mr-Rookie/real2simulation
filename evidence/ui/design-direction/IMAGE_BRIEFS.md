# IMAGE_BRIEFS — S15aj (for S15ak batch A, S15al batch B; GPT-6.1 Sol high, best available image model)

Rights: every image is generated for this build; no references to or imitation of third-party artwork, brands or people. Record the exact prompt used in IMAGES_A.md / IMAGES_B.md.
One illustration language across all 12 briefs (A1-A5, B1-B6 share the line style; B7 is a ground texture):
- Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces.
- Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).
- Light-line variant for paper, light, contrast modes; dark-line variant for dark, midnight, graphite. Spot colour: #b23a0e (light) / #ff8a4c (dark). Midnight may use #7dd3fc spot only if the orange clashes on #111831 in the contact sheet — decide by looking, record the decision.
- Acceptance per image: contact sheet on all 6 mode surfaces (from COLOR_MODES.md); silhouette readable at the smallest placement size; transparent PNGs have clean alpha (no halo on #111113 and #ffffff); no stray text-like marks (zoom 200%). Iterate once on weak results, then pick.

## Batch A — marketing (S15ak -> Build/web/public/images/marketing/)

### A1 — Home hero: real clip becomes simulation
- **Purpose:** The single image that explains the product in 1 second.
- **Placement:** Home hero right column, inside a level-2 slab, radius 14, tilted -2deg (S15ai).
- **Size/aspect:** 16:10, 1600x1000 (2x 3200x2000)
- **Transparent:** no — opaque, background matches mode surface
- **Variants:** light-line on #f3eee3 (paper/light/contrast), dark-line on #18181b (dark/graphite); midnight reuses dark-line with background #111831 (regenerate background only if seams show).
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `a1-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: a generic smartphone standing upright on a tabletop tripod, filming a small ball falling past a simple metre stick; to the right of the phone the same falling ball is shown as a sequence of evenly timed ghosted positions (stroboscopic dots, increasing spacing) that continue into a clean parabola-free vertical dotted trajectory, which transitions into a minimal wireframe floor plane and grid, suggesting a simulation replay. Composition: left-to-right story, phone at left third, ball sequence centre, simulation wireframe at right third; horizon at 62% height; leave 8% clear margin on all sides. Lighting: none (flat illustration); depth only from the single hard offset shadow under the phone. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background solid #f3eee3. Only the ball and its position dots use the spot colour. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background solid #18181b."

- **Do:** show real-to-simulated transition; keep metre stick ticks abstract (no numerals)
- **Don't:** no rockets, no planets, no lab coats, no glowing neon, no circuit boards

### A2 — Feature 1: Record
- **Purpose:** Feature card art for 'Record' step.
- **Placement:** Home feature card 1 top, 16px inset, above h3.
- **Size/aspect:** 4:3, 800x600 (2x 1600x1200)
- **Transparent:** yes — transparent
- **Variants:** light-line and dark-line.
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `a2-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: a generic phone on a small tripod pointed at a pendulum (a bob on a string hanging from a simple stand), the bob drawn at three faint swing positions. Composition: phone lower-left, pendulum centre-right, object centred optically, 12% margins. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the bob. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent."

- **Do:** keep silhouettes readable at 240px wide
- **Don't:** no recording red dot UI, no camera brand details

### A3 — Feature 2: Fit
- **Purpose:** Feature card art for 'Fit' step.
- **Placement:** Home feature card 2 top.
- **Size/aspect:** 4:3, 800x600 (2x)
- **Transparent:** yes — transparent
- **Variants:** light-line and dark-line.
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `a3-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: a scatter of hand-plotted measurement points with small vertical error bars on a minimal pair of axes (no tick labels), and one smooth fitted curve passing through them; a small magnifier lens hovering over one point. Composition: axes fill 70% of the frame, lens upper-right. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the fitted curve; points in ink. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent."

- **Do:** error bars must be visible — uncertainty is the product's honesty
- **Don't:** no numbers or axis labels, no dashboard chrome

### A4 — Feature 3: Replay
- **Purpose:** Feature card art for 'Replay' step.
- **Placement:** Home feature card 3 top.
- **Size/aspect:** 4:3, 800x600 (2x)
- **Transparent:** yes — transparent
- **Variants:** light-line and dark-line.
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `a4-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: a minimal wireframe 3D scene: a floor grid in perspective, a sphere at the top of a dotted vertical path with motion ticks, and a small translucent ghost copy of the sphere lower down, like a simulation playback; a small play-triangle shape drawn as an abstract cut-out in the floor grid corner. Composition: grid vanishing point slightly above centre; sphere at upper centre. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the sphere. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent."

- **Do:** clearly synthetic/wireframe so it reads SIMULATED
- **Don't:** no realistic rendering, no game engine look

### A5 — OG / social card background
- **Purpose:** Background for the 1200x630 Open Graph image; text and logo are added in code, not in the image.
- **Placement:** Build/web/public/images/marketing/og-bg; composited by code with title + S15ag logo on the left.
- **Size/aspect:** 1200x630 exact (and 2400x1260)
- **Transparent:** no — opaque
- **Variants:** one variant: paper (light-line on #f3eee3). Optional second: dark-line on #111113.
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `a5-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: the falling-ball stroboscopic sequence from A1 (ball positions with increasing spacing) beside a thin fitted curve and a tiny wireframe floor grid, arranged as a single elegant diagonal motif. Composition: ALL artwork confined to the right 40% of the canvas; left 60% completely empty flat background for overlaid text; nothing within 48px of edges. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background solid #f3eee3. Spot colour on ball positions only. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background solid #18181b."

- **Do:** respect the empty left 60% strictly
- **Don't:** no text, no fake title, no logo-like marks

## Batch B — in-app (S15al -> Build/web/public/images/app/)

### B1 — Viewport empty: no scene yet
- **Purpose:** Replaces the dashed box + 'EMPTY · NO SCENE' chip.
- **Placement:** Workspace centre viewport, 180px tall art above 'No scene yet' (S15am).
- **Size/aspect:** 1:1, 512x512 (2x 1024)
- **Transparent:** yes — transparent
- **Variants:** light-line and dark-line; contrast mode uses light-line.
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `b1-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: an empty wireframe floor grid in perspective with a single dotted outline of a cube waiting to appear, and a tiny ball resting at the grid origin. Composition: centred, grid occupies lower 60%, 15% margins. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the tiny ball. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent."

- **Do:** read at 120-180px; calm
- **Don't:** no question marks, no sad faces

### B2 — Upload dropzone art
- **Purpose:** Hero art inside the dropzone.
- **Placement:** Workspace dropzone centre, 160px.
- **Size/aspect:** 1:1, 512x512 (2x)
- **Transparent:** yes — transparent
- **Variants:** light-line and dark-line.
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `b2-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: a short strip of video film frames (3 frames, each showing a tiny ball at a different height) sliding down into an open tray-like upward arrow cradle. Composition: centred, frames enter from upper right, 15% margins. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour on the ball inside each frame. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent."

- **Do:** simple enough to scale on drag-over (1.03)
- **Don't:** no cloud icon cliché, no file-type badges

### B3 — Library empty / clip thumbnail placeholder
- **Purpose:** Empty filter result and missing-thumbnail placeholder.
- **Placement:** Library grid empty state (200px) and card thumbnail fallback (centred on surface-elevated).
- **Size/aspect:** 16:9, 960x540 (2x)
- **Transparent:** yes — transparent
- **Variants:** light-line and dark-line.
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `b3-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: three stacked blank cards fanned slightly like index cards, the top one showing a tiny pendulum line drawing, beside a small magnifier. Composition: centred cluster occupying middle 50% width. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the pendulum bob. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent."

- **Do:** must work cropped to 16:9 card
- **Don't:** no tags or text on cards

### B4 — Lab empty: set parameters and run
- **Purpose:** Never-run state of the local simulation lab.
- **Placement:** Lab right column chart/viewport area, 200px.
- **Size/aspect:** 4:3, 800x600 (2x)
- **Transparent:** yes — transparent
- **Variants:** light-line and dark-line.
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `b4-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: an inclined plane (ramp) on a simple stand with a ball at the top, two small slider-knob shapes floating beside it like physical control knobs, and a faint dotted path down the ramp. Composition: ramp diagonal lower-left to centre-right, knobs upper-right. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the ball. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent."

- **Do:** clearly an experiment setup
- **Don't:** no beakers, no flasks, no chemistry

### B5 — Agent / question-card companion
- **Purpose:** Small companion art at the top of the agent panel idle state and the question card thumbnail fallback.
- **Placement:** Agent tab idle state (120px) and question card when no clip frame is available (96px).
- **Size/aspect:** 1:1, 384x384 (2x)
- **Transparent:** yes — transparent
- **Variants:** light-line and dark-line.
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `b5-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: an abstract agent glyph: a small round lens/eye-like instrument (not a face) on a tripod, next to a ruler laid diagonally and a small floating speech-bubble outline that contains only a dotted line. Composition: centred, compact, 18% margins, legible at 64px. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the lens ring. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent."

- **Do:** read as 'instrument that asks', friendly but not cute
- **Don't:** no robot, no face, no sparkles cliché, no brain

### B6 — Abstain: scale unverified
- **Purpose:** Illustration for abstained/unsupported results (scale unverified, held-out caveat).
- **Placement:** Result card abstain variant and error empty state, 140px.
- **Size/aspect:** 1:1, 512x512 (2x)
- **Transparent:** yes — transparent
- **Variants:** light-line and dark-line.
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `b6-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: a ruler drawn with one end fading into dotted outline (incomplete), a small falling ball beside it, and a small spirit level whose bubble sits off-centre. Composition: centred, ruler diagonal. Lighting: flat. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background fully transparent. Spot colour only on the level bubble. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background fully transparent."

- **Do:** conveys 'we cannot confirm scale' without alarm
- **Don't:** no red X, no warning triangle (UI adds the icon)

### B7 — Per-mode background textures
- **Purpose:** Very subtle page grounds behind the app/public pages; replace flat colour without noise.
- **Placement:** CSS background-image on body per data-theme, background-size: cover, fixed; opacity handled in the image itself.
- **Size/aspect:** 16:9, 2560x1440 (single size, WebP q70 only)
- **Transparent:** no — opaque
- **Variants:** six: paper #f3eee3 (warm mesh: blobs #f6e7d0, #ece6d6), light #f7f7f8 (#eef0f4, #f5f1ec), dark #111113 (#17171c, #1a1512), midnight #0b1020 (#101a36, #0e1530), graphite #1f2023 (#25262a, #29231f), contrast: NONE (flat #ffffff, do not generate).
- **Export (worker):** WebP q82 + PNG fallback at 1x and 2x; filenames `b7-<variant>@<1x|2x>.<webp|png>`.

**Prompt (light-line):**
> Subject: an extremely subtle soft mesh gradient ground made of 2-3 large diffuse blobs in the listed mode tints, with a barely visible thin concentric arc motif (like a pendulum swing trace) in the lower-right at 4% contrast. Composition: blobs at top-left and bottom-right, centre calm; must stay under 1.15:1 contrast against the base colour everywhere so text contrast is unaffected. Lighting: none. Style: editorial scientific line illustration, single consistent ink line weight (like a 2px technical pen at 1000px width), slightly hand-drawn but precise, rounded line caps; flat shapes only, no gradients inside objects, no 3D rendering, no photorealism; exactly ONE spot colour used sparingly for the subject of motion; a hard offset shadow shape (solid, no blur, offset down-right) under the main object only, echoing the UI's hard shadows; generous negative space; calm, intelligent, tactile, not cartoonish, no faces. Palette (light-line variant): line #1c1a16, spot colour #b23a0e, shadow shape #1c1a16 at 100%, secondary tint #d8cfbe, background solid #f3eee3. For this brief ignore the spot colour and line-weight rules: no lines except the faint arc; no offset shadow. Constraints: no text, no letters, no numbers, no logos, no watermarks, no UI chrome, no real people or likenesses, no hands with detailed skin, no third-party products or brand marks, no phone brand features (generic rounded rectangle phone only).

**Prompt (dark-line):** same prompt with this palette sentence instead: "Palette (dark-line variant): line #f4f4f5, spot colour #ff8a4c, shadow shape #71717c, secondary tint #2e2e35, background solid #18181b."

- **Do:** verify with a colour picker that no area deviates >6 RGB levels from base
- **Don't:** no noise/grain, no dot grid, no blueprint grid, no paper texture (owner rejected)

