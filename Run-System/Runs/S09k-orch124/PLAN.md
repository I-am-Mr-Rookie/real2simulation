# S09k-orch124 PLAN

- Objective: smallest simulated-trajectory replay path in the viewer for the S18k trace DTO.
- Owns: Build/web/src/viewer/; tests/viewer/; evidence/S09/; Run-System/Runs/S09k-orch124/.
- Model: anthropic/claude-opus-5-5 / medium (OpenCodex-managed; not polled). Issued 2026-10-30T09:53:01Z; deadline 10:23:01Z.
- Checks: node --test tests/viewer/*.test.mjs (3 real-media skips expected); headless 375px + 1280px screenshot, no horizontal overflow.
