# S15x — 6 Mobbin references for the Real2Sim UI pass

Source: Mobbin connector (web platform), screens viewed directly 2026-10-30/31 UTC. Borrow layout/hierarchy/interaction only; no assets copied. Context: evidence/ui/audit-orch82/DEFECTS.md (over-precise fit values, detached right column, empty black viewer slab, repeated SOURCE column, narrow cards). Flow: upload drop clip -> interview (known size) -> run/track -> fit g ± u -> report. Truth labels (SYNTHETIC/SIMULATED, not-calibrated) must stay intact in any borrow.

| # | App / screen | Link | Step |
|---|---|---|---|
| R1 | Higgsfield — Virality Predictor (drop clip, "Analyzing") | https://mobbin.com/screens/77ce4ea4-ca3e-478e-b106-41a7b3e5283e | upload + run/track |
| R2 | Delphi — onboarding "What do people ask you?" | https://mobbin.com/screens/4eb86098-ba6d-49a0-af5d-1403cdd8e69f | interview |
| R3 | PlanetScale — Insights query table with sparklines + column picker | https://mobbin.com/screens/ef455d28-04ea-46f4-a289-cb6c283ea929 | fit / data table |
| R4 | Dovetail — Results summary block | https://mobbin.com/screens/50f32565-520b-451e-9957-085b5d0dbdb7 | report |
| R5 | Dropbox — "Adding file to track" modal + Uploads tray | https://mobbin.com/screens/dfe639b5-dfce-4e47-bf79-29e9bf2daec6 | upload progress |
| R6 | Sprig — result card with chart, tooltip, response count | https://mobbin.com/screens/a43bf0eb-4985-48d1-a06a-a66c2f124d0e | fit / uncertainty chart |

## R1 Higgsfield — Virality Predictor
- Borrow: two-column card: left = headline + one-line instruction + clip preview + single action bar + constraint note ("Max video duration is 15 seconds"); right = framed result stage with "Analyzing" tag and labelled metric bars below; "Previous analyses" strip underneath.
- Fit: same drop-a-clip -> analyze shape; gives a paper-toned (not black slab) framed stage with a status tag; constraint note suits our clip limits.
- Risk: dark neon theme clashes with warm-paper tokens (take layout only); metric bars imply measured values, so ours must show only real fit/tracking status; sports footage in the sample is irrelevant/forbidden for us.

## R2 Delphi — onboarding question step
- Borrow: one question per screen, thin top progress bar, back arrow, centred narrow form (~560px), label above field, single disabled-until-valid Continue.
- Fit: the interview asking a known size (value + unit + which object) as one focused step; fixes DEFECTS #8 (half-width cards).
- Risk: decorative gradient not needed; disabled-button low contrast (keep AA, DEFECTS #4); free-text boxes need unit validation.

## R3 PlanetScale — Insights table
- Borrow: dense table with numeric right-aligned columns, inline sparklines, sticky sorted header, "View options" column toggles, filter box.
- Fit: fit/residual table: columns value ± u, residual, with sparkline of residuals; toggle to reveal raw/full-precision columns (answers DEFECTS #1, #7).
- Risk: density can overwhelm judges; sparklines must be derived from real residuals only, never decorative; monospace SQL styling not relevant.

## R4 Dovetail — results summary
- Borrow: block-based summary page: breadcrumb + Saved/Share/Publish header, card with title + "Summary of N responses", donut with direct labels and counts, "Add a block" and a docked "Chat with…" bar.
- Fit: report page as stacked cards (clip, method, fit, caveats) with a share/export header and N-frames caption.
- Risk: donut is the wrong chart for g ± u (use only for e.g. frame-quality breakdown); rainbow palette off-brand; skip the AI chat bar (scope).

## R5 Dropbox — upload progress modal + Uploads tray
- Borrow: modal with title, "ready in a moment" reassurance, dashed drop zone containing a progress bar and verb ("Copying…"); persistent bottom-right Uploads panel with All/Completed/Skipped/Failed filters, per-file row, success toast.
- Fit: upload and run/track progress with explicit states incl. Failed (fixes wavy-red step list, DEFECTS #9), non-blocking so the user can continue.
- Risk: indeterminate bar can mislead on long GPU jobs — show real step names/elapsed; tray adds state complexity for a single-clip flow (modal only is enough).

## R6 Sprig — chart result card
- Borrow: result card header (question, type chip, "N responses"), chart-type toggle icons, dark compact tooltip with per-series values, 0–100% axes, Pin/Share actions on the card.
- Fit: g-estimate chart with hover tooltip (value ± u at frame/time), chart/table toggle, "N samples" chip.
- Risk: stacked-area style hides uncertainty — use line + band instead; axes must be true to data; card actions beyond Share are scope creep.

## Suggested combination
Default R1, R2, R3 (upload/track stage, interview step, fit table). Alternates: R5 for progress states, R6 for uncertainty chart, R4 for report layout.

