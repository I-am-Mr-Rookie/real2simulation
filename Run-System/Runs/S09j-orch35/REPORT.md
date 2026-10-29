# S09j-orch35 REPORT — DONE

- Run S09j, lane CLAUDE, model anthropic/claude-opus-5-5 / medium (as assigned). Coding quota: OpenCodex-managed; not polled.
- UTC issued 2026-10-29T16:00:45Z; worktree start 16:02:03Z; work stopped 2026-10-29T16:04:44Z. Branch run/S09j-orch35 from main be06dda.
- Tokens/cost: unknown (not observable). No Modal/GPU, deploy, install, account or canonical-control change.

## Outcome

Acceptance "Document 375px and performance results; separate fixture from real-scene evidence": met by
[evidence/S09/CHECKPOINT.md](../../../evidence/S09/CHECKPOINT.md) — section A synthetic fixture (S09a–g), section B real RM02/RM04/RM05
MapAnything scenes (scale UNVERIFIED, Fallback 2, RM05 unapproved/display-only), S09i measured fps/heap table with source links, known limits.
Visual fixes: none needed — no viewer defect observed in the fresh in-app-browser check, so no viewer/test code changed.

## Fresh checks (this run)

| Command / check | Result |
|---|---|
| node --test "tests/viewer/*.test.mjs" (media present) | 46/46 pass, 0 skip |
| same, media junction removed (fresh-clone condition) | 43 pass, 3 skipped, 0 fail |
| SMOKE_DEVICE=375x667@3 node tests/viewer/browser-smoke.mjs | ok, layoutOk; scrollW 375; buttons 44×44 in viewport |
| node tests/viewer/browser-smoke.mjs (800 px) | ok; scrollW 800; mode full |
| ChatGPT IAB real-scenes.html RM02/04/05 @1280 and @375×812 (override reset) | all loading,ready; UNVERIFIED banner; scrollWidth = viewport; focus ring visible; no console errors |

## Ponytail (full) applied

- Reuse: existing tests/viewer harnesses (browser-smoke.mjs, real-scenes.html) and S09h/S09i bundles via temporary junctions
  (Build/web/node_modules → canonical install; evidence/S09/local → .worktrees/S09i-orch33 media); no rebuild, no install.
- Smallest complete change: one new doc (CHECKPOINT.md) + run files; zero code edits because no defect was observed (no speculative fixes).
- Skipped: re-measuring fps (S09i numbers reused with source); saving new screenshots (derived scene media, gitignored, would write into another worktree);
  widening browser-smoke.html JSON output (harness-only cosmetic, outside acceptance); tightening desktop camera framing (judgment, not a defect).
- Cleanup: both junctions removed with non-recursive Directory.Delete (targets verified intact); http.server stopped (port 8939 no listener); IAB tab closed, viewport reset.

## Risks / limits

vsync-capped fps, no VRAM, emulated 375 px (no real phone), 20k-point bundles only, real media gitignored so real tests skip on a fresh copy;
scale UNVERIFIED — nothing here is Gate R / physics / calibrated evidence. Communication: silent; one completion message to controller.

Next: controller review/merge; S09 parent remains fixture + scale-unverified real scenes until Gate R/Fallback-2 geometry exists.
