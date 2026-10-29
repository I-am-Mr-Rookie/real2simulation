# S09h-orch30 REPORT — DONE

- Lane/model: CLAUDE, anthropic/claude-opus-5-5 high. Coding quota: OpenCodex-managed; not polled. Tokens/cost: unknown (not observable); Modal/GPU $0 (none used).
- UTC start 2026-10-29T15:43:29Z (issued 15:42:54Z); work stopped 2026-10-29T15:51:31+00:00. Base main 90d6f45; branch run/S09h-orch30; worktree .worktrees/S09h-orch30.

## Result
Three real MapAnything bundles (RM02, RM04, RM05) load through the existing viewer (artifact loader manifest+sha gate ->
adapter/checkViewerRequest -> buildSceneModel/decodePlyXyzRgb -> three renderer) and display a "metric scale UNVERIFIED" banner.
Details/sha table: evidence/S09/S09h-real-scenes.md.

## Files
- Build/web/src/viewer/fixture.mjs: SCALE_UNVERIFIED_BANNER constant.
- Build/web/src/viewer/scene-model.mjs: non-synthetic scenes without scale.status 'measured' get that banner (was null).
- Build/web/src/viewer/three-renderer.mjs: data-viewer-banner = 'synthetic' | 'scale-unverified' (was always 'synthetic').
- Build/web/src/viewer/README.md: S09h section.
- tests/viewer/real-scenes.test.mjs (3 real-load tests, skip without local media; 1 always-run banner test); tests/viewer/real-scenes.html (visual page).
- evidence/S09/.gitignore (local/), evidence/S09/S09h-real-scenes.md.
- Gitignored, not committed: evidence/S09/local/RM0{2,4,5}/ bundles, evidence/S09/local/ui/*.png screenshots; Build/web/node_modules junction -> canonical node_modules (needed for three in worktree).

## Commands / fresh results
- python Build/gpu/scene_job.py RM02|RM04|RM05 evidence/S09/local/<RM> --npz <npz> -> PASS x3 (contracts/scene validator), 20000 points each, CPU only.
- RM02/RM04 rebuilt main+mobile sha256 == committed S06e/S06f GPU manifests (byte-identical).
- node --test "tests/viewer/*.test.mjs" -> 46/46 pass, 0 skipped (includes RM02/RM04/RM05).
- node tests/viewer/browser-smoke.mjs -> ok:true (synthetic regression; banner path unchanged for synthetic).
- In-app browser (IAB, not Chrome): desktop 1280 px and 375 px viewport (reset after): all three loading,ready; banner visible;
  375 px compact layout, scrollWidth 375. First 375 pass found scrollWidth 431 caused by the test page's <pre> status line (not
  the viewer); fixed with pre-wrap and rechecked. Server (python http.server :8793) stopped; tab closed.

## Ponytail (applied, full)
- Reuse: existing converter scene_job.py --npz for all three (no new conversion code); existing loader/adapter/renderer unchanged except banner.
- Smallest change: one constant + one ternary + one attribute value; test serves files through a fake fetch like artifact-loader.test.mjs.
- Skipped: mobile LOD loading, app-route mounting, planes/boxes overlays (bundles have no surfaces/colliders; not invented), real-phone check.

## Limits / risks
- Scale is nominal ('estimated'); not calibrated, not Gate R, not physics evidence. Fallback-2 planes+boxes are not in these bundles.
- RM05 clips.csv row is UNAPPROVED_CANDIDATE / SCENE_ONLY_UNTIL_SCALE_VERIFIED (NASA PD); used display-only per controller contract; owner/controller should confirm RM05 for any public demo.
- Real-load tests skip on a fresh clone (media gitignored); source npz live in other worktrees (.worktrees/S06e-orch24, S06f-orch25, S05c-orch19) — archiving those loses the rebuild inputs.
- Communication: silent; one completion message to controller only.

Next: controller review/merge; S09 mobile LOD + route mount are later runs.
