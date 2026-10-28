# S09d REPORT — Add colliders, camera path and scene labels

- Status: **DONE** (acceptance: fixture interaction shows aligned geometry and labels)
- Lane/model: CLAUDE; requested Opus 5.5 medium; actual = orchestrator-delegated Claude-agent session in Codex desktop, exact model/effort not exposed.
- UTC: start 2026-10-27T19:04:34Z, verification end 2026-10-27T19:12:57Z (host clock). Merged SHA 474cb03 (ff after rebase on 03092d4).

## Objective
Draw scene-v1 colliders, labels and camera_path in the three renderer with deterministic, testable overlay maths; prove alignment on the synthetic fixture.

## Changes (Owns: Build/web/src/viewer/, tests/viewer/, evidence/S09/)
- Build/web/src/viewer/scene-overlays.mjs (new, pure): unitQuat/rotate, boxCorners, colliderEdgePositions (12 edges/box),
  overlayAlignment (face-to-surface gap via support along normal, origin in footprint, bounds, points on face, labels in bounds),
  prepareCameraPath (strict validation) + sampleCameraPath (lerp + shortest-arc slerp, clamped), ndcToScreen.
- three-renderer.mjs: collider LineSegments (disposed), textContent label layer projected each draw (host position restored),
  setCameraTime / playCameraPath / 'p' key; frames only while playing; orbit input returns to orbit; handle.alignment, labelScreen().
- tests/viewer/scene-overlays.test.mjs (5 tests); three-renderer.test.mjs (+1 interaction test; GPU tracker now also counts line
  materials, so expected live GPU objects 2→4 for the new collider resources); browser-smoke.html overlay checks; README; evidence/S09/S09d.md.

## Commands and results
- node --test tests/viewer/viewer.test.mjs tests/viewer/three-renderer.test.mjs tests/viewer/artifact-loader.test.mjs tests/viewer/scene-overlays.test.mjs
  → 30/30 pass, fail 0 (worktree, after rebase, on main).
- node tests/viewer/browser-smoke.mjs → exit 0, ok=true, overlaysOk=true (before and after rebase): collider px 928, pointsOnFace [4,4],
  label DOM within 1.5 px of projected anchor (160,141.4), moves to 138.6 along camera path; dispose leaves 0 geometries, context lost.
- 6 mutations (support term, slerp flip, footprint, textContent→innerHTML, playback reschedule, orbit-mode reset) → each fail 1; restored.
- python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json → PASS.

## Limits
- Synthetic authored fixture: alignment shows overlay/manifest consistency, not reconstruction quality; not measured/simulated or Gate R evidence.
- Alignment report is exposed on the handle only (not shown in UI, scenes not rejected). No label occlusion/declutter; surfaces not drawn;
  path playback has no UI control beyond 'p'/API. No real-GPU/mobile measurement. Tests written alongside code (not strict TDD red); mutation checks compensate.
- Worktree used a node_modules junction to main's install (ignored; link removed non-recursively before worktree removal; target intact).
  One combined shell command was blocked by policy; split into separate safe steps, no bypass.

## Skills/plugins
- Original run (as first reported): no skill bodies were loaded; a verification gate (fresh full commands, counts/exit codes read
  before claims) and mutation checks were applied without reading the skill. This violated AGENTS.md / Run-System/SKILLS_AND_PLUGINS.md;
  acceptance was held (72dd462).
- Correction (2026-10-27T19:15–19:16Z UTC, no product changes): read Superpowers verification-before-completion
  (C:/Users/HP/.codex/plugins/cache/openai-curated-remote/superpowers/7.0.1/skills/verification-before-completion/SKILL.md;
  no required references; agents/openai.yaml is metadata only) and applied its Gate Function on main 72dd462:
  - Tests: node --test tests/viewer/viewer.test.mjs tests/viewer/three-renderer.test.mjs tests/viewer/artifact-loader.test.mjs tests/viewer/scene-overlays.test.mjs → tests 30, pass 30, fail 0, exit 0.
  - Browser smoke: node tests/viewer/browser-smoke.mjs → exit 0, ok=true, overlaysOk=true (same pixel/label figures as above).
  - Validator: python contracts/scene/validate_scene.py test-data/synthetic/scene/room-v1/scene.json → PASS, exit 0.
  - Agent/VCS check: git show --stat 474cb03 → 8 files, +447/−20, all within Owns + run PLAN; 474cb03 is an ancestor of HEAD.
  - Regression red-green: replaced the support-along-normal term in scene-overlays.mjs → scene-overlays suite pass 4 / fail 1
    ("misalignment is reported…"); restored (git diff clean) → tests 5, pass 5, fail 0.
  - Requirements checklist vs PLAN acceptance: (1) node suite incl. alignment + path sampling — met; (2) browser collider px, in-canvas
    label text, path moves label, clean dispose — met; (3) mutation checks — met (6/6 original, 1 fresh red-green).
- Limitation preserved: tests were written alongside code, not strict TDD red-first; test-driven-development was not applied.
- Not used: Playwright MCP (existing CDP smoke sufficed); web tools (offline task).

## Communication compliance
- Silent-workflow AGENTS.md section (ca3b62b) arrived mid-run and was read before control updates. Earlier in this run, brief
  progress narration was sent before that section was read; from then on no optional narration. Questions: none (fallback unused). Final reply: one line.
- Skill-correction session: silent workflow followed; no narration; one final status/report-pointer line.

## Cost / quota
Tokens unavailable; Claude quota unavailable; Meta/service/GPU $0. Owner questions: 0. No D1/D2 decisions.

## Next
S09e CLAUDE Opus 5.5 medium (pixel-ratio and detail budgets).
