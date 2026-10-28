# S10g-ui plan

- Objective: Build the public `/lab` synthetic Mystery-g UI with accessible template selection, run/fit/reveal states, sampled trajectory output, and uncertainty/limitation labels.
- Owns: `Build/web/src/app/(public)/lab/page.jsx`, `Build/web/src/lab/LabClient.jsx`, `Build/web/src/lab/lab.css`, `tests/lab/ui-contract.test.mjs`, `evidence/S10/ui/`, `Run-System/Runs/S10g-ui/`.
- Base: clean branch `run/S10g-ui` created from `main` at `bd5df5fcfa502433fd5df4d0ec24010efb604d2b`.
- Reuse: existing public shell, global design tokens, native React/Next fetch, and no new dependency. Shared layout/header/styles/auth/API files were not changed.
