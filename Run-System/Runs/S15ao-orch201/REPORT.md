# S15ao-orch201 REPORT — PARTIAL

Lane/model: CLAUDE, anthropic/claude-opus-5-5 high (as assigned). Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable). No Meta/GPU/paid call, no deploy, no Chrome, no secrets.
UTC start 2026-10-31T10:05:39Z (issue); work stopped/reported at deadline 10:35:39Z (PARTIAL rule). Branch run/S15ao-orch201, rebased on main e2b55cfc; commit list in git log.

## Done (screenshot/test-proven)
- Library L1 (Build/web/src/app/(public)/library/): filter chip row `All · RECORDED · SIMULATED · what-if` + any other manifest label verbatim (UNAVAILABLE), counts computed from manifest (`filterChips`/`matchesFilter` in library-copy.mjs; zero counts shown honestly: RECORDED 0, what-if 0). aria-pressed buttons, 44px. Card = 16:9 thumbnail (B3 art, manifest has no thumbnails) with availability + SCALE_UNVERIFIED chips bottom-left, mono kicker `id · licence` (licence only if manifest has one), credit line + "Display only · not a measurement." verbatim. Empty filter = B3 + "No clips match" + "Clear filters" (evidence/S15ao/library-empty-filter-dark-1280.png). Page CSS moved verbatim from inline <style> to page-level library.css, L1 additions tokens-only.
- Lab LB1 (Build/web/src/lab/): two-column ≥900px (controls card left, sticky; chart/viewport right), single column below; B4 never-run state "Set parameters and run"; `SIMULATED` chip pinned top-left on BOTH charts (trajectory plot + in-browser simulation SVG). lab max-width 960→1120.
- AppArt.jsx: one <picture> per theme family (webp 1x/2x + png), reuses global .art-light/.art-dark html[data-tone] switch (same pattern as MarketingArt).
- Duplicate icon link removed: app/icon.svg file convention deleted; /icon.svg kept serving via app/icon.svg/route.js (same SVG) so shell/smoke.mjs and old links still work. Verified HTML head: only manifest + /brand favicon.ico, mark-32, mark-192, apple mark-192.
- Nav: (public)/public.css — nav links min 44×44 (measured navMin 44 in all 12 shots), Sign in nowrap + nav single row at 375 (measured oneRow true, no horizontal scroll, all 3 modes, both pages). Shortcut: header theme <select> trimmed to 6.75rem ≤700px ("High contrast" label clips to "High con"); drop when S15an's swatch menu replaces the select.

## Not done / blockers
- PWA manifest icons → /brand: BLOCKED by Owns. public/pwa/manifest.webmanifest is generated from Build/web/src/pwa/manifest.mjs and tests/pwa/manifest.test.mjs asserts file == source AND icon pixels == procedural generator. Needs an owner of src/pwa + tests/pwa (change manifest.mjs icons to /brand/mark-192.png, mark-512.png, icon-maskable-512.png; regenerate; relax pixel test for brand files; update sw.js/cache-policy precache lists). No messaging tool was available to send this as a nonterminal blocker; recorded here.
- Lab after-run screenshot (chart chip rendered) not captured: `next start` returns local_lab_disabled (route allows development/test only; NODE_ENV=test at start does not help, inlined at build) and `next dev` failed in this worktree (ENOENT .next/dev build-manifest). Chip presence is proven at source level (test: every <svg> in LabClient/BrowserSimulation is preceded by the chip) + build, not visually.
- "by experiment" chips skipped: manifest has no experiment field; deriving from titles would be authored data.

## Checks (fresh, after rebase)
- node --test tests/workspace, shell-workspace, web-private, web-workspace-api: 163/163 pass (includes new tests/web-private/public-polish.test.mjs, 4 tests).
- node --test tests/pwa: 52/52 pass (unchanged manifest).
- npm run build (Build/web): pass, routes include /icon.svg, /lab, /library.
- Screenshots evidence/S15ao/: library|lab × dark|paper|contrast × 1280|375 (prod build, guest snapshot from Build.library.guest via R2S_GUEST_SNAPSHOT temp file), plus library-empty-filter-dark-1280.png.

## DESIGN_QA self-score (L1/LB1)
- Labels verbatim/visible all modes: pass (SIMULATED · playable/practice setup, SCALE_UNVERIFIED, credit, Display only, UNAVAILABLE, Mystery-g copy unchanged).
- 375 no horizontal scroll: pass (12/12). Targets ≥44px: pass. Tokens only: pass (test greps no hex in library.css). 
- Less text/more visual: improved (art thumbs, chips) but thumbnails are the same B3 art per card — real per-demo thumbnails need manifest images. AA: not measured with contrast.py (token values unchanged from S15ah/S15am).
- Overall: library/lab redlines largely met; PWA icons + run-state visual proof outstanding → PARTIAL.

## Ponytail
Reuse: existing .art-light/.art-dark switch, state-tag/token vars, groupDemos/creditLine, existing lab tokens; filter logic = 2 pure functions + 1 test. Smallest: CSS moved not rewritten; route handler 4 lines instead of editing smoke/test owners. Skipped: experiment chips, slider/stat-tile LB1 extras (no such controls exist), per-card real thumbnails. Risk: public.css overrides header rules owned by S15an (cascade-only, no git conflict) — controller should re-check header at 375 after merging S15an.

## Communication
Silent; no optional chat. Controller message tool unavailable → completion line given as final answer.
