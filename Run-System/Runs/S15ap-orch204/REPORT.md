# S15ap-orch204 REPORT: DONE

Lane/model: CLAUDE, anthropic/claude-opus-5-5 high (assigned; runtime identity not independently exposed). Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable); no Meta/GPU/API spend.
UTC: issued 2026-10-31T10:55:26Z; worktree created 10:56Z; controller HOLD then GO received; work stopped 2026-10-31T11:06:31+00:00. Branch run/S15ap-orch204 from main e2b55cf.

## Outcome
New pendulum mark (candidate D): pivot bar, three equal-length strings, solid rust centre bob, hollow rust ghost bobs at left/right extremes; separate 16 u drawing for <=32 px. Light-ink (#1c1a16 + rust #b23a0e) and dark (#f4f4f5 + ember #ff8a4c) variants. Full spec, candidates, grid, clear space, min size, per-mode colours/contrast, do/don't, rights: [LOGO_V2.md](../../../evidence/brand/logo-v2/LOGO_V2.md).

## Files
- Replaced (same names/sizes): Build/web/public/brand/mark-1024.png, mark-512.png, mark-192.png, mark-32.png, icon-maskable-512.png, favicon.ico (16/32/48), wordmark-light.png, wordmark-dark.png (924x192).
- New: Build/web/public/brand/mark.svg, mark-dark.svg, mark-16.svg.
- Evidence: evidence/brand/logo-v2/ LOGO_V2.md, build_logo_v2.py, check_logo_v2.py, concept-a/b/c/d PNG+SVG, contact-sheet-final.png (16/24/32/64/192/512 on all 6 modes), wordmarks-review.png, favicon-frames-6x.png.

## Checks (fresh)
- `python evidence/brand/logo-v2/build_logo_v2.py` exit 0.
- `python evidence/brand/logo-v2/check_logo_v2.py`: "logo-v2 checks OK" (sizes, RGBA, transparent corners on marks/wordmarks, maskable opaque and art inside 80 percent safe circle, ICO frames 16/32/48, SVG root/viewBox and no embedded raster).
- Visual review (viewed): concepts A/B/C at 192/32/16 on paper and dark, then D; contact sheet on six modes; ICO frames at 6x nearest; maskable tile; both wordmarks. 16 px first version merged ghosts into the bob; fixed by spreading/raising ghosts in the small drawing, re-rendered and re-viewed.
- Contrast computed: ink 14.82 to 17.37:1, bob 5.18 to 8.11:1 across modes.
- No em dashes in written files (rg).
- `python Run-System/worker_timebox.py check Run-System/Runs/S15ap-orch204/TIMEBOX.json`: "TIMING PASS", exit 0.

## Ponytail (full) applied
- Reuse: one primitive list per drawing generates both the SVG text and the Pillow raster, so vector and PNG cannot drift; colours taken from COLOR_MODES.md tokens; existing filenames kept so header/favicon/OG wiring needs no code edit; locally installed Instrument Sans used for wordmark.
- Smallest complete: no new dependencies (cairosvg/resvg/Playwright absent in Python; Pillow supersampling used instead), no web code edits, one build script + one assert check script.
- Skipped: OG image regeneration and pwa/ icon copies (outside Owns); per-mode PNG variants beyond light/dark (not requested); dashed details (fail at small size).

## Risks / limits
- PNG marks are the light-ink variant; on dark UI surfaces the header must use mark-dark.svg or wordmark-dark.png (web wiring not changed here; if the header currently shows mark-192.png on dark modes the ink bar will be dark-on-dark). Follow-up for a web run.
- Maskable tile background changed from S15ag dark to paper per contract.
- Rasters are Pillow supersampled, not a browser SVG render; SVGs were not rendered in a browser in this run.
- Instrument Sans SemiBold instance requested via Pillow set_variation_by_name; falls back silently to default instance if unsupported.
- Communication: silent except required HOLD acknowledgement and the single completion message.

