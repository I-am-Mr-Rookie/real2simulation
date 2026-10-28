# S09d PLAN — colliders, camera path and scene labels

- Lane CLAUDE; requested Opus 5.5 / medium; orchestrator-delegated Claude-agent session (exact model/effort not exposed).
- UTC start 2026-10-27T19:04:34Z. Base main eb245ef. Timebox 30 min.
- Objective: draw scene-v1 colliders (box edges), labels (textContent DOM overlay projected from 3D) and camera_path
  playback in the three renderer; pure, testable overlay maths; prove alignment on the synthetic fixture.
- Owns: Build/web/src/viewer/; tests/viewer/; evidence/S09/ (+ this run folder, serialized control updates on main).
- Acceptance: "Fixture interaction shows aligned geometry and labels."
  1. node --test tests/viewer/*.test.mjs green, incl. alignment (points / collider faces / surfaces / labels) and path sampling.
  2. Browser smoke: collider pixels drawn, label text shown inside canvas, camera path t=0->1 moves label, dispose frees all.
  3. Mutation checks on alignment / slerp / label textContent.
