# S04l-orch138 PLAN
Objective: fix stale Mystery-g copy on /library (align with S18l) and polish the guest library page within the existing paper/offset-shadow brand.
Owns: Build/web/src/app/(public)/library/; tests/web-library/; evidence/S04l/; Run-System/Runs/S04l-orch138/.
Checks: node --test tests/web-library/library.test.mjs; npm run build --prefix Build/web; desktop + 375px screenshots over http://localhost.
Base: main b82b1a6. Model anthropic/claude-opus-5-5 medium; OpenCodex-managed, not polled.
