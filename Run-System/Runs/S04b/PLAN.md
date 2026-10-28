# S04b plan

- UTC start: 2026-10-27T18:27:27Z; initial main 2045c55; claim ea615b4.
- Objective: runnable Next.js shell with public/private route composition, no viewer/workspace implementation.
- Requested CODEX-2 GPT-6.1 Sol / medium; delegated Codex runtime exact model/effort not exposed.
- Owns: Build/web/src/shell/, Build/web/src/auth/, Build/web/src/app/, Build/web/package.json, Build/api/health/, Build/worker/health/, infra/railway/dev/; own run receipts and serialized canonical controls.
- Dependencies: S04a DONE. Baseline shell contracts 7 passing.
- Checks: production build; deterministic local HTTP smoke for entry/library/private deny/404; contract + viewer regression suites and source isolation.
- Budget: <=30m, no new implementation after 18:52Z; no inference, deployment, credentials or uploads.
- Skills: TDD, verification-before-completion, using-git-worktrees; frontend-design.
- UI plan: cool lab-paper #f5f8fb, ink #172e43, blue #155a92, muted #486579, rule #ccd9e3. Georgia headings with Segoe UI body, no downloaded fonts. Left-aligned bench-like entry with one schematic and a single library link. Header / main two columns / quiet footer; collapses to one column.
- Design review: removed decorative dashboard cards and invented data/curves; use a labelled optical-path schematic only, explicitly illustrative. No physics results, viewer or upload claim.
- Use pinned registry versions verified via npm; official install reference https://nextjs.org/docs/app/getting-started/installation. No root lock/config edits outside Owns; npm install --package-lock=false. Add requested three dependency for S09b without touching viewer.
- Native managed worktree used; platform chooses path outside main. Preserve unrelated main research files.
