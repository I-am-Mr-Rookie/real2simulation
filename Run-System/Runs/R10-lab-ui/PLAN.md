# R10-lab-ui

- CODEX-2 / assigned Sol medium; parent project `91e441f8-e40c-4ec4-bea2-de7fa1582d97`.
- Isolated branch `run/R10-lab-ui`, base `3fa80eb4985779f8b913ce1d9cdbd932f1b65468`.
- Objective: plot the full finite synthetic observations, label downward vertical displacement correctly, keep table sampling and honestly describe unsupported fits.
- Owns: `Build/web/src/lab/{LabClient.jsx,fit-contract.mjs,lab.css}`, `tests/lab/ui-contract.test.mjs`, `evidence/S10/ui-hardening/`, this run directory only.
- Issued: 2026-10-28T19:55:20.136Z; implementation cutoff: 2026-10-28T20:20:20.136Z; deadline: 2026-10-28T20:25:20.136Z (= **2026-10-29T02:25:20.136+06:00**).
- Handout's Dhaka `06:55` conflicts with its authoritative UTC deadline; use UTC arithmetic (30 minutes), not the erroneous Dhaka string.
- Apply Ponytail full: reuse existing SVG, fit boundary and table sampler; no dependency, service change or new visualization feature.
- Acceptance: full 2,000-point oscillating series reaches SVG (not table rows), finite-only data and table <=9 with final sample; displacement labels and ballistic-only status; reject reproduced contradictory fit envelope; regression checks preserve source/uncertainty/privacy and stale/abort guards.
- Parent owns real IAB/mobile verification; no browser or server here. No merges/rebases/shared-control changes.
