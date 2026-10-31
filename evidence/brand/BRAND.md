# Real2Simulation — generated brand mark

**Recommendation:** refined candidate A, **Measured Arc**. A camera-frame pair brackets a tracked ball and its motion curve: real video becomes a measured simulation. Clean single-accent geometry fits the Oct31 modern-SaaS direction without implying a successful physical measurement.

## Generation provenance / prompts

- Created 2026-10-31 for this hackathon build, run `S15ag-orch193`.
- Worker assignment: `gpt-6.1-sol`, high effort (owner-pinned). Actual underlying runtime model identity is not exposed independently in this session.
- Image tool used: built-in `image_gen.imagegen` (`image_gen__imagegen` in orchestration), default available image-generation backend; **backend model/version not exposed in its returned metadata**. There is no model selector in the available tool schema, so no unsupported “best model” identifier is claimed. No CLI/API fallback or API key was used.
- Four successful image calls: three distinct original concepts, then one targeted refinement of A. All calls requested `transparent_background: true`. Each original output is 1254 × 1254 RGBA with genuine alpha. Only candidate A was supplied as the refinement's edit target.
- Full exact prompts: [PROMPTS.md](PROMPTS.md). Prompts specify concept, camera/physics geometry, 16–32px readability, flat blue, transparent background, no text inside the mark, no gradients/shadows, no Meta/infinity-loop/third-party marks. No external brand references or imported logo artwork.
- Generated originals copied from `C:/Users/HP/.codex/generated_images/01a19108-c5b7-7cb0-a305-41e20181ac0f/`; originals there remain untouched.

## Candidates / visual review

| Candidate | Original mark | Transparent wordmark variant | Assessment |
|---|---|---|---|
| A — measured arc | [candidate-a-measured-arc.png](candidate-a-measured-arc.png) | [candidate-a-measured-arc-wordmark.png](candidate-a-measured-arc-wordmark.png) | Clearest relationship between phone-video framing and tracked motion. Strong choice to refine. |
| B — real to sim | [candidate-b-real-to-sim.png](candidate-b-real-to-sim.png) | [candidate-b-real-to-sim-wordmark.png](candidate-b-real-to-sim-wordmark.png) | Compact, but solid/open split is more abstract; the sample square reads like an unrelated badge. |
| C — falling samples | [candidate-c-falling-samples.png](candidate-c-falling-samples.png) | [candidate-c-falling-samples-wordmark.png](candidate-c-falling-samples-wordmark.png) | Communicates falling motion, but has more disconnected parts and the baseline adds clutter at favicon size. |
| **A refined — PICK** | [candidate-a-refined.png](candidate-a-refined.png) | [candidate-a-refined-wordmark.png](candidate-a-refined-wordmark.png) | Requested bolder flat geometry while preserving A's identity. Chosen for distinctive frame/arc silhouette, larger ball, clean negative space and one colour across both themes. |

Each original was viewed; all four were then compared on both backgrounds in [candidates-light-dark.png](candidates-light-dark.png). The selected exports were inspected at actual 16/24/32/48/64/192px in [legibility-light.png](legibility-light.png) and [legibility-dark.png](legibility-dark.png). At 16px the frame/curve silhouette is recognizable; 24–32px is preferred in the app. 16px is favicon-only, not a detailed scientific diagram.

The generated source had slight colour mottling and almost invisible stray alpha speckles. Explicitly requested Pillow export processing fixes the fill to one exact blue, removes alpha below 16/255, median-filters alpha at 3px, crops/centres the generated silhouette, and resizes only its alpha for the final flat-fill PNGs. This is raster cleanup, **not** a claimed vector trace or a replacement hand-drawn logo. Raw originals are retained separately.

## Palette / type

| Role | Hex | Notes |
|---|---|---|
| Single accent / mark | `#2878E8` | Same mark for both themes; do not invert or recolour automatically. |
| Light surface | `#FFFFFF` | Tested mark contrast 4.249:1. |
| Dark surface | `#0B0B0F` | Tested mark contrast 4.623:1. |
| Light-theme wordmark ink | `#17181C` | Contrast 17.739:1 on white. |
| Dark-theme wordmark ink | `#F4F4F5` | Contrast 17.872:1 on dark. |

Mark contrast exceeds 3:1 against both tested surfaces (nontext graphic); it is **not** a 4.5:1 small-body-text colour on white. Wordmark uses locally installed Windows **Segoe UI Regular**, rasterized by Pillow, with exact text `Real2Simulation`; no generated lettering artefacts and no font file redistributed. For the live header, accessible HTML text with the app's existing sans font is preferable to a raster wordmark where practical.

## Final assets (all under `Build/web/public/brand/`)

| File | Export / purpose |
|---|---|
| `mark-1024.png` | 1024² transparent RGBA raster master. |
| `mark-512.png` | 512² transparent RGBA PWA “any” / high-density use. |
| `mark-192.png` | 192² transparent RGBA PWA “any” / header source. |
| `mark-32.png` | 32² transparent RGBA small header/icon use. |
| `favicon.ico` | Real embedded 16², 32² and 48² RGBA frames, not a renamed PNG. |
| `wordmark-light.png` | 924 × 192 transparent lockup, dark text for light surfaces. |
| `wordmark-dark.png` | 924 × 192 transparent lockup, light text for dark surfaces. |
| `icon-maskable-512.png` | 512² **opaque** dark-surface PWA icon; foreground entirely within the central 80%-diameter safe circle. Do not substitute the ordinary transparent mark for a maskable icon. |

**SVG: none.** No faithful vector trace was made. Do not wrap the PNG in SVG and label it vector.

## S15ah integration handoff (not implemented here)

1. Header: display `/brand/mark-192.png` at **32 × 32 CSS px** (24px for a compact rail). Its artwork occupies about 84% of the canvas; the built-in padding is intentional. Keep aspect ratio 1:1 and at least 4px clear space. Use adjacent live text `Real2Simulation`; if the text is visible, mark `alt=""` to avoid duplicate naming. A mark-only home link needs accessible name `Real2Simulation home`.
2. Optional raster lockup: select `/brand/wordmark-light.png` or `wordmark-dark.png` according to the actual theme; height **32–40 CSS px**, width auto (approximately 154–193px). Do not squeeze it into a square or retain the light ink in light mode.
3. Favicon: wire `/brand/favicon.ico` into Next metadata (or copy it to the appropriate favicon path during S15ah). Current `Build/web/src/app/layout.jsx` still points to the old `/pwa/icon.svg` and `/pwa/icon-192.png`; leaving the old SVG reference would keep serving the old brand.
4. PWA “any”: copy `brand/mark-192.png` -> `Build/web/public/pwa/icon-192.png`; copy `brand/mark-512.png` -> `Build/web/public/pwa/icon-512.png`.
5. PWA “maskable”: copy `brand/icon-maskable-512.png` -> `Build/web/public/pwa/icon-maskable-512.png`. This intentionally uses an opaque `#0B0B0F` tile and conservative safe-zone sizing.
6. Update the old SVG entry in `Build/web/public/pwa/manifest.webmanifest` and Next metadata when integrating; there is no new SVG to map. Preserve `purpose: any` vs `maskable`. Consider theme/background token and service-worker cache revision in `Build/web/public/pwa/sw.js` as part of the integration, so cached icons do not remain stale. These existing files are **unchanged** by this run.
7. Verify header contrast/size, browser tab favicon and installed-PWA cropping in the integrated light/dark UI. This asset-only run is not a deployment, runtime theme test or installed-PWA test.

## Rights / limits

Generated for this event/build for **Koushik Sadhak Jeet**, intended as **owner-owned project brand assets**. No third-party logos, footage or stock assets were used; prompts explicitly exclude third-party marks and Meta/infinity-loop lookalikes. This records creation provenance and intended ownership, not a legal guarantee of exclusive copyright or trademark availability. Trademark/near-match clearance has **not** been performed. No publication, submission or third-party upload by this run.

## Reproduce / checks

From the run worktree: `python evidence/brand/export_assets.py` (Python + already installed Pillow 12.2.0; local `C:/Windows/Fonts/segoeui.ttf` for lockups). No dependency installation.

[checks.json](checks.json) records final asset dimensions, modes, byte counts, SHA-256 and contrast calculations. Assertions pass for exact flat opaque-interior fill, PNG sizes/alpha, all three ICO frame sizes/alpha, opaque maskable safe circle, and both theme contrast pairs. Sheets render exported 16/48px ICO frames and exported 32/192px PNGs, not substitutes; 24/64px are additional scaled previews.

Skipped: web code/manifest/PWA replacement, deployment and SVG tracing, as assigned. Risks: backend image-model ID is unobservable; legal trademark clearance and integrated/installed-PWA behaviour remain unverified.
