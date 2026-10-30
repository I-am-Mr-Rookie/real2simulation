# S04k-orch133 PLAN

Objective: serve /api/library/* from a staging-time guest snapshot (no runtime Python), fail closed, no deploy.
Lane CLAUDE / anthropic/claude-opus-5-5 high. Issued 2026-10-30T11:12:53Z; deadline 11:42:53Z; cutoff 11:37:53Z.
Owns: Build/web/src/app/api/library/; infra/railway/dev/stage.py; infra/railway/dev/web.Dockerfile;
infra/railway/dev/test_stage.py; tests/web-library/; evidence/S04k/; Run-System/Runs/S04k-orch133/.

Steps: stage.py runs existing load_guest() once (web only) -> Build/web/library-snapshot/guest.json in context;
guest.mjs reads+verifies it once per process (sha/size/refs), serves from memory; python spawn only for local dev
when the snapshot is absent and NODE_ENV != production. Dockerfile mirrors Build/ layout (also fixes unstaged
Build/library/loader.mjs import). Checks: infra unittest, node --test tests/web-library, npm run build, staged-context
build + production-mode HTTP probe.
