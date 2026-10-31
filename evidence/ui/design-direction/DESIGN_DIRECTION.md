# DESIGN_DIRECTION — Real2Simulation (S15aj, design director)

Audience: S15ah (workspace restyle, in flight), S15ai (public pages), S15ak/S15al (Sol image workers), S15am (colour modes + redlines).
Owner constraints honoured: keep **Instrument Sans + Space Mono**, keep the **hard offset shadow/overlay character** (refined, not removed), modern SaaS, less text, more icons, more colour modes, honesty labels visible + verbatim. Layout from Q21-OWNER-SPEC (left rail, centre project, right agent panel, question card) is fixed.
Evidence used: controller screenshots evidence/S15/s15o/controller/23-32 (esp. 26, 28, 32), Mobbin picks in .tmp-mobbin-onboarding/, fresh Mobbin searches this run (URLs below). Checklists applied: myfront round-3 (character over generic; finish every state; refinement can regress) and make-interfaces-feel-better (concentric radius, optical alignment, shadows vs borders, text-wrap, tabular numbers, hit areas, scoped transitions).

## 1. Blunt critique of current DEV (screens 26, 28, 32)

It looks like a well-meaning internal form, not a product. Specific causes:

1. **Everything shouts at the same volume.** Every block (tool rows, status card, result card, header button) gets the same 1.5px black border + 4px black offset shadow. When 14 things on screen have the signature shadow, it stops being a signature and becomes noise. Rule: shadow-2 on at most 2 elements per view.
2. **No hierarchy in the header.** "Private development fixture" in 2 lines of 18px bold is the biggest text on screen. The page title should be the project/clip name; "fixture" is a badge.
3. **Copy volume.** The centre pane opens with two paragraphs of policy ("Connected to the private workspace API… Only approved licensed clips…", "Instruments are not available in this build…"). Tool rows carry 2-3 lines of sentence (Runs & history shows a raw job hash wrapped over 3 lines). Policy belongs in one info popover; job ids are mono, truncated middle, copy-on-click.
4. **Stage nav is a row of text links with ordinal numbers and parentheses** ("03 Run (not run)"). Status in parentheses is the amateur tell. Use a stepper with state icons.
5. **The empty state is a dashed box with a tiny mono chip "EMPTY · NO SCENE"** occupying the most valuable area, plus a caption below repeating it. Empty states need an illustration, one line, one action.
6. **Result card is a wall of prose.** g = 8.62 ± 1.28 m/s² is the hero number of the whole product and it sits inline in a paragraph at body size. Numbers must be big, mono, tabular, with uncertainty and evidence badges as chips.
7. **Duplicate titles**: "Agent & tools" appears as a header button AND panel title; the question appears 2x (centre banner + panel) with the same full sentence. Centre gets a 1-line pointer chip, panel gets the question.
8. **Colour is unused.** Beige ground + black + one rust underline. No semantic colour; RECORDED vs SIMULATED look identical (plain text). Badges must be colour-coded per COLOR_MODES.md.
9. **Spacing is uneven**: 8px between tool rows, 16-20px elsewhere, panel content hugs the 1px edge, rail icons have no active state, the "Go to" flyout overlaps content with a 3px black bar and no elevation (screen 32).
10. **Kbd hints (Alt+1) on every row** are noise; show on hover/tooltip only.
11. **The page is boxed inside a beige marketing frame** (top nav + 72px side gutters) at 1280px; the workspace should be full-bleed app chrome.
12. **No motion, no focus styling beyond defaults, native-looking textarea**, disabled "Finish" is low contrast grey on grey.

What is GOOD and stays: Instrument Sans (crisp, characterful), Space Mono for numbers/ids, the warm paper ground as one mode, the hard offset shadow as an *accent*, rust accent, the rail/centre/panel structure.

## 2. Personality (3 words)

**Precise · Candid · Tactile.**
Precise = lab instrument, numbers first. Candid = every claim wears its evidence label. Tactile = hard offset shadows on the few things you can press or that are "physical" (the result slab, question card, primary button).

## 3. Principles

1. **One hero per view.** Empty: the dropzone. Interview: the question card. Result: the g value. Everything else is quieter.
2. **Labels are first-class UI, not footnotes.** RECORDED / SIMULATED / what-if / scale unverified / owner clip / Held-out caveat / FIXTURE render as colour chips with icon, verbatim text, never truncated, never only in tooltips.
3. **Say it in 4 words, explain on demand.** Max 1 sentence of helper text per component; longer copy behind an (i) popover or "Details" disclosure.
4. **Shadow = affordance.** Hard shadow only on pressable primaries and the single hero surface. Cards use 1px border + shadow-1 at most.
5. **Numbers are mono, tabular, big.** Units smaller and muted; uncertainty attached (±) never in a different sentence.
6. **Every state is designed**: empty, loading (skeleton), waiting-for-you, error, disabled, focus, hover, 375px.
7. **Refine, don't regress** (myfront): change only what this doc specifies; do not restyle working parts on a whim.

## 4. Mobbin references (what to TAKE from each; never copy assets)

Primary set = M1-M12 (all fetched via the Mobbin tool in this session or already owner-picked in Q21); M13-M15 are supplementary single-component refs.

| # | screen | URL | take | for |
|---|---|---|---|---|
| M1 | hilos — agent chat + right "Edit agent" panel | https://mobbin.com/screens/c8dd2f16-c6a2-4c6b-a9a2-92503f076e3f | 3-column density: narrow icon rail (48px), quiet list column, right panel 360px with sectioned form; centre empty state = small illustration + 1 title + 1 line | workspace shell, empty centre |
| M2 | Framer — canvas + right Agent/Style tabs | https://mobbin.com/screens/4c03063e-692f-4199-a6f4-052c97f7417a | right panel with segmented tabs (Agent / Tools) at top, prompt card with model chip + send icon; floating bottom toolbar pill | right panel tabs, viewport toolbar |
| M3 | Perplexity Computer question card (existing P4) | https://mobbin.com/screens/501351fa-f2ca-490a-93db-3bbda5d591a1 | "1/3" counter, numbered options as rows with keycap numbers, "Other" free text, Continue primary | question card |
| M4 | Replit "agent needs your feedback" (existing P1) | https://mobbin.com/flows/d3355324-0ea5-45af-aeda-ffe4d42a3692 | pulsing "waiting for you" status in panel header; centre shows only a compact pointer | waiting state |
| M5 | Emergent agent questions (existing O2) | https://mobbin.com/screens/2c8a196a-de8f-403c-a06a-5cb746cf7e9a | "Question 2 of 4", Skip / "let the agent answer" secondary actions | question card actions |
| M6 | Perplexity onboarding split preview (existing O1) | https://mobbin.com/screens/6285fdec-d5dc-4a1e-9e16-30d8e00afa6a | question beside a live preview: our clip frame thumbnail beside the question with the measured object highlighted | interview layout |
| M7 | Mintlify analytics (dark) | https://mobbin.com/screens/03b084b9-d5ed-41be-a9ca-43445af854f2 | stat tiles row (label small muted, number 28px), selected tile with raised border; restrained 2-colour chart; dark surface steps (bg/surface/elevated) | result metrics row, dark mode |
| M8 | Churnkey lifetime performance | https://mobbin.com/screens/5f76714e-953a-4edc-a49c-72bfe343c4d9 | big number + coloured sub-delta under it; prose summary with **bold numbers** below the stat row (our "what this means" line) | result card |
| M9 | Tally empty state | https://mobbin.com/screens/0f2523c5-d61e-4384-a934-c169dbb1eaeb | single-line-weight hand-drawn illustration, 1 bold line, 1 muted line, 1 primary button, centred in a calm canvas | all empty states, image language |
| M10 | Steep "Get started" | https://mobbin.com/screens/b026462f-39da-445e-b451-36da6d487c49 | line illustration with ONE spot colour (accent) — exactly our image language; help strip below with icon links | empty states, image briefs |
| M11 | Remote stepper (Upload -> Map -> Review -> Confirm) | https://mobbin.com/screens/29e02c1a-3816-4123-8b25-2b82b50d05bd | compact pill stepper with check icons for done, number for current, muted for future; progress card | stage stepper |
| M12 | Brilliant home hero | https://mobbin.com/screens/fa106126-e261-4f12-8bdd-164e1872d30d | huge 2-line headline with physics-y motion graphics woven around the letters (dots trajectory, sine, slider); 2 CTAs | home hero |
| M13 | Amplitude theme preferences | https://mobbin.com/screens/75fb4ce8-674d-41a2-9877-12c21d704c37 | theme picker as preview thumbnails with check; System option split-preview | theme menu (6 modes) |
| M14 | Craft tags grid | https://mobbin.com/screens/41bdf5f8-0d9a-4c8b-95da-1b3d139a8821 | tag chips row with counts above a card grid; cards with mono date kicker | library filters + cards |
| M15 | Teachable add video | https://mobbin.com/screens/8e7fd793-f41f-4bf4-aae2-2b3475fa8ca4 | dropzone with centred file icon, one line, accepted-types line in muted small, limit notice strip | dropzone |

Do NOT take: Snowflake CoCo's plain styling (owner), neon dashboards, acid-lime-on-black, blueprint dot grids (myfront "slop" list), SchoolAI-style photo collage (we have no rights to photos; illustrations only).

## 5. Type scale (Instrument Sans = UI/display, Space Mono = numbers, ids, kickers, kbd)

| token | font | size/line | weight | tracking | use |
|---|---|---|---|---|---|
| display | Sans | 56/60 (clamp 36-56) | 600 | -0.025em | home hero only |
| h1 | Sans | 32/38 | 600 | -0.02em | public page titles |
| h2 | Sans | 22/28 | 600 | -0.01em | section, result card title |
| h3 | Sans | 16/22 | 600 | -0.005em | pane/card titles, workspace header title |
| body | Sans | 14/21 | 400 | 0 | default app text |
| body-lg | Sans | 16/25 | 400 | 0 | public pages body, hero sub (max 60ch) |
| small | Sans | 13/18 | 400/500 | 0 | secondary lines, tool row sub |
| micro | Sans | 12/16 | 500 | 0.01em | tooltips, captions |
| kicker | Mono | 11/14 | 700 | 0.08em UPPER | section labels ("AGENT", "TOOLS") |
| metric-xl | Mono | 40/44 | 700 | -0.02em tabular | hero g value |
| metric | Mono | 22/26 | 700 | tabular | stat tiles |
| mono | Mono | 12.5/18 | 400 | 0 | job ids, paths, kbd |
| badge | Mono | 11/14 | 700 | 0.04em UPPER (labels keep their own case: "what-if", "owner clip" are NOT uppercased) | evidence chips |

Rules: `font-variant-numeric: tabular-nums` on all metrics; `text-wrap: balance` on h1-h3, `pretty` on body; `-webkit-font-smoothing: antialiased` on dark modes; never more than 3 sizes in one component.

## 6. Spacing, radius, layout

Spacing (4px base): 2, 4, 8, 12, 16, 20, 24, 32, 48, 64, 96 -> `--r2s-space-0_5 … --r2s-space-11` (keep existing 1-6 names mapped: 1=4, 2=8, 3=12, 4=16, 5=24, 6=40 -> change 6 to 32 and add 7=48, 8=64, 9=96).
Radius: xs 4 (chips, kbd), sm 6 (inputs, tool rows), md 10 (cards, panels, buttons), lg 14 (question card, result slab, modals), pill 999 (stepper pills, toggles). **Concentric**: inner radius = outer radius - padding (card 14 with 8 padding -> inner 6).
Layout (desktop >=1280): full-bleed app; rail 56px; centre fluid (min 560); right panel 360px (resizable 320-440). Header 52px. Content padding 24px. 1024-1279: panel overlays as drawer (shadow-3 + overlay). <=767: rail becomes bottom tab bar 56px + safe-area; panel = bottom sheet 85vh.
Hit areas >= 40px desktop, >= 44px touch, even when the icon is 16-18px.

## 7. Shadow / overlay spec (the signature, rationed)

Defined per mode in COLOR_MODES.md (--r2s-shadow-1/2/3, --r2s-overlay). Light modes: ink-coloured hard slab. Dark modes: **lit slab** using border-strong tone (black slab is invisible on dark) + soft ambient blur only on level 3.

| level | recipe | allowed on | max per view |
|---|---|---|---|
| 0 | 1px border-strong/ border, no shadow | tool rows, inputs, list items, chips | unlimited |
| 1 | shadow-1 (2px hard) + 1px border | cards, stat tiles, library cards | as needed |
| 2 | shadow-2 (4px/3px hard) + 1.5px border | primary button, question card, result slab, active rail item | 2 |
| 3 | shadow-3 (hard + ambient) | popovers, menus, drawers, toasts, modals | 1 open at a time |

Press: primary/level-2 surfaces translate(2px,2px) and drop to shadow-1 on :active (tactile "press into the paper"), 90ms. Hover: shadow grows by 1px, 120ms. Overlay scrim fades 160ms; drawer slides 220ms. Contrast mode: no blur ever.

## 8. Iconography

One set: **S15ah's inline lucide-style SVG set** `Build/web/src/shell/icons.mjs` (24px viewBox stroke paths, no dependency). Reuse it; add missing glyphs as new PATHS entries drawn in the same style — do NOT add an icon package or mix sets. 1.75px stroke, 16px in rows/buttons, 18px rail, 20px empty-state header, 14px in chips. Colour = currentColor; muted by default, text on hover, accent when active. Icon + label always for primary actions; icon-only only in rail/toolbars with tooltip + aria-label.
Mapping (existing PATHS names in plain, NEW names to add in bold): Upload=upload, Interview=chat, Run=play, Fit=chart, Report=doc, Agent=**sparkle**, Clips=film, Runs & history=history, Library=book, Lab=flask, Theme=sun/moon/monitor + **palette**, RECORDED=**record** (dot in circle), SIMULATED=cube, what-if=**branch**, scale unverified=**ruler**, Held-out caveat=alert, owner clip=**user**, FIXTURE=**testtube**, done=check, info=info, copy=**copy**, chevron=**chevron**.

## 9. Motion

Durations: 90 press, 120 hover, 160 fade, 220 panel/drawer, 320 stepper progress. Easing `cubic-bezier(.2,.8,.2,1)` (out), drawers `cubic-bezier(.32,.72,0,1)`. Transition only transform/opacity/box-shadow/background-color — never `all`. Waiting-for-you: 1.6s soft pulse on the panel status dot only. Number reveal: g value counts in 400ms only on first result render. `prefers-reduced-motion: reduce` -> all to 0ms except opacity fades <=120ms. No parallax, no confetti.

## 10. Component specs

**Rail (56px)**: logo mark 28px top (S15ag); icon buttons 40x40, radius md; active = surface-elevated fill + 2px accent left indicator bar (inset, radius pill) + text colour; hover = elevated fill; tooltip right with kbd. Bottom: theme (palette) + avatar 28px. No text labels on desktop; flyout "Go to" becomes a level-3 popover with 8px offset, never overlapping with a bare bar.
**Pane / centre**: bg = surface; 24px padding; max content width 960 centred when panel closed.
**Header (52px)**: left: collapse icon button (ghost) · clip/project title h3 (1 line, ellipsis) · FIXTURE / owner clip chip. Right: stage stepper (desktop >=1280 sits here, otherwise below) · "Agent" toggle ghost button with sparkles icon + unread dot. One bottom 1px border, no shadow.
**Agent panel (360)**: header 52px: sparkles + "Agent" h3 + status pill (Idle / Working… / **Waiting for you** with pulsing dot, warning tones) + close. Segmented tabs: Agent | Clips | Runs | Report (icons + 1 word; replaces the 4 tall tool cards). Body scrolls; footer composer sticky.
**Tool row**: 40px height, icon 16 + label (body, 500) + right meta (small muted, e.g. "2 runs") + chevron; second line only for state that matters (error/waiting), one line max. No kbd visible (tooltip). Hover elevated fill; selected = accent-tinted 8% bg + accent text icon.
**Question card** (hero in interview, level 2, radius lg, 16 padding): kicker "AGENT QUESTION" + counter mono "1/3" right; question h3 (max 3 lines); optional clip-frame thumbnail 16:9 radius sm with the reference object outlined in accent (M6); options as rows 44px with keycap number (kbd 20px mono) + label, selected = accent border + check; "Other…" row opens textarea (min 3 rows, styled input: surface-elevated, border-strong, focus glow); actions: primary "Continue" (Ctrl+Enter kbd inside button, muted) + ghost "Skip". Disabled primary = border-strong outline + muted text (>=4.5) — never grey-on-grey.
**Centre pointer when question waiting**: one 36px chip row: dot + "Agent needs your answer" + "Open" link. No duplicate question text.
**Stage stepper**: 5 pills Upload · Interview · Run · Fit · Report, 28px tall, radius pill, gap 4 with 12px connector line. Done = success icon check + text; current = accent fill, accent-contrast text, shadow-1; future = muted text, border; not-run = muted + dash icon, tooltip "not run" (the "(not run)" parentheses removed from the label; state also exposed as aria-label "Run, not run"). 375px: collapses to "Step 2/5 · Interview" + progress bar.
**Dropzone**: min-height 280, radius lg, 1.5px dashed border-strong, surface-elevated; centre illustration (IMAGE_BRIEFS B2) 160px, h3 "Drop a phone video", small muted "MP4/MOV · approved licensed clips only" , primary "Choose file", ghost "Use a demo clip". Drag-over: accent dashed border, accent 6% fill, illustration scales 1.03. Rejected file: danger callout inline, keeps reason verbatim.
**Result card (slab, level 2, radius lg, 20 padding)**: row 1 badges: RECORDED/SIMULATED + owner clip + scale unverified (chips). Row 2: kicker "GRAVITY" · metric-xl "8.62" + "± 1.28" (metric, muted) + "m/s²" (body, muted). Row 3: stat tiles (level 1, 3-up): Held-out χ²/dof 0.77 · p 0.51 · scale 0.2028 m (user-declared). Row 4: **Held-out caveat** callout (whatif tokens, alert icon, verbatim caveat, 2 lines then "Details"). Row 5: source path mono small with copy icon. Buttons: primary "Replay simulation", ghost "Open report".
**Evidence badge (chip)**: 22px, radius xs, 6/8 padding, icon 14 + badge text; tokens from COLOR_MODES badge mapping; contrast mode = white with 2px coloured border. Never truncated; wraps as whole chips.
**Buttons**: heights 32 (sm) / 36 (md) / 44 (lg, public CTA). Primary: accent bg, accent-contrast text, 1.5px border shadow-colour, shadow-2, press translate. Secondary: surface bg, border-strong, shadow-1. Ghost: no border, elevated on hover. Danger: danger text on surface + danger border. Icon button: square, ghost. All: radius md, 500 weight, icon 16 + 6 gap.
**Chips/filters**: 28px, radius pill, border, count in mono muted; selected = text bg, surface text (inverted).
**Toasts**: bottom-right (bottom-centre on mobile), 360 max, level 3, icon + 1 line + optional action, auto 5s, pause on hover; errors persist until dismissed; role=status / alert.
**Empty states**: illustration (batch B, 160-200px), h3, 1 muted line (<=80 chars), 1 primary + optional ghost. Centered optically (4% above geometric centre).
**Inputs**: 36px, radius sm, surface-elevated, border-strong, focus = --r2s-glow; labels small 500 above; helper micro muted below; error = danger border + message.

## 11. Screen redlines

### W1 Workspace — empty (no upload) @1440
- Remove the beige marketing frame + public top nav inside the app; full-bleed. Rail 56 | centre | panel 360 (open by default, Agent tab, shows "Idle" + 3 suggestion rows: "Upload a clip", "Try a demo clip", "What can you measure?").
- Header: title "New project" + chip FIXTURE (if dev). Stepper with Upload current.
- Centre: Dropzone hero (spec above) occupying top; below it a single muted line with (i): "Server labels every result RECORDED or SIMULATED." — the two policy paragraphs move into the (i) popover. "Instruments are not available in this build; no reading is shown." becomes a small muted chip "Instruments: off" with the full sentence in its tooltip AND visible in the popover (still verbatim).
- Viewport empty = IMAGE B1 illustration + "No scene yet" + "The viewport appears when an upload produces a scene." (one line, keep text).
### W2 Workspace — interview (question waiting)
- Panel status pill "Waiting for you" (pulse). Question card is the top item of the Agent tab, level 2.
- Centre: pointer chip (spec), stepper Interview current, viewport left 60% / clip frame + status right 40% card level 1 with chips "owner clip" "not a measurement" instead of the 4-line bold paragraph.
- Job id: mono "job_beb2…379f" with copy icon; full id in title attribute.
### W3 Workspace — result
- Stepper: Upload/Interview done, Run/Fit as "not run" state when owner clip, Report current.
- Result slab is the hero at top of centre (spec). Viewport below at 16:9 with floating bottom toolbar pill (M2): play/pause, scrub, speed, "SIMULATED replay" chip always visible in the viewport corner when replay is synthetic.
- Long held-out explanation -> callout 2 lines + Details disclosure (full verbatim text inside).
### W4 375px
- Bottom tab bar: Project · Agent · Clips · Runs · Report (icons + 10px labels). Agent = bottom sheet with question card; stepper collapses (spec). Result: g metric 32px, tiles stack 1-col, chips wrap. No horizontal scroll; tap targets 44.
### H1 Home hero (public, paper default)
- Left 55%: kicker mono "REAL → SIMULATION"; display headline (2 lines max): "Film physics. Get a measured g." — sub (body-lg, 1 line): "Track the object, fit the motion, replay it — every number labelled." CTAs: primary lg "Try the demo library", secondary lg "Open the lab". Under CTAs a row of 3 evidence chips as a legend: RECORDED · SIMULATED · what-if.
- Right 45%: IMAGE A1 hero art on a level-2 slab, radius lg, slight -2° tilt (myfront sticker energy, only element tilted).
- Below fold: 3 feature cards (A2/A3/A4 art top, h3, 1 line) "Record → Fit → Replay". Then honesty strip: "We abstain when scale is unverified." with ruler icon.
### L1 Library
- Header h1 "Demo library" + 1 line. Filter chip row (M14): All · RECORDED · SIMULATED · what-if · by experiment (pendulum, free fall, incline) with counts.
- Grid 3-up (2 at 768, 1 at 375) cards level 1: thumbnail 16:9 (or B3 placeholder), evidence chips row on the thumbnail bottom-left, title h3, mono kicker (clip id · licence short e.g. "CC BY-SA"), attribution small muted 1 line (verbatim, full in card detail). Empty filter result = B3 illustration + "No clips match" + "Clear filters".
### LB1 Lab
- Two-column: left controls card (level 1; inputs 36px; sliders with mono value right), right chart + viewport. "SIMULATED" chip pinned top-left of every chart/viewport. Run button primary. Empty/never-run = B4 art + "Set parameters and run". Lab results stat tiles reuse result-card tiles.

## 12. Hand-off notes
- S15ah in flight (seen in its worktree at 08:31Z, uncommitted): light/dark blocks in app/styles.css, theme.mjs PALETTES, icons.mjs. Keep that mechanism + icon set; S15am replaces only colour VALUES with COLOR_MODES.md (incl. accent decision: rust/ember, not indigo) and adds paper/midnight/graphite/contrast PALETTES entries.
- S15ak/S15al: generate from IMAGE_BRIEFS.md only; transparency + per-mode rules there.
- Controller: accept UI rows with DESIGN_QA.md.

