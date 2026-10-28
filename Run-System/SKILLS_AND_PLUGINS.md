# Run skill and plugin checklist

Koushik's Oct 27 instruction: use the relevant installed skills and plugins properly.
This is a preflight/report requirement, not permission to expand a task or bypass approvals.

## Every fresh run

1. Read the task, Owns paths, acceptance checks and relevant project instructions.
2. Review the available skill and MCP/plugin inventory; Koushik's examples are not
   exhaustive. Filter tool metadata to the task instead of dumping full catalogs or
   calling every server. Select relevant installed skills from the session catalog. If omitted, search known
   skill roots for the exact `SKILL.md`; read it and its required references before use.
   Never load every skill or tool catalog. Do not install/enable a missing plugin without approval.
3. Follow selected skills' workflows, not just their names. Every session records
   selection/application in REPORT.md rather than optional chat narration; root
   AGENTS.md's silent default applies even without a prompt reminder. Mandatory
   higher-priority runtime/skill announcements remain minimal and intact.
   Discover purpose-built plugin tools when they fit the task; prefer them over generic
   browser/shell work unless the skill specifies a CLI or the tool lacks the needed capability.
4. Keep the task's lane, model, timebox, Owns set and approval boundaries unchanged.
5. In REPORT.md add **Skills/plugins**: names/paths, concrete application (e.g. a failing
   test followed by a passing check, or the relevant plugin operation), and relevant
   unavailable/skipped tools with reasons. Never count discovery alone as actual use.

## Task-to-tool starting points (not an exhaustive or mandatory call list)

**Explicit S02c requirement (Koushik, Oct28):** every primary, Opus shard,
continuation and integrator reads/applies installed Ponytail full/default.
Follow `S02C_PARALLEL.md` and record concrete reuse/minimal complete changes,
fresh checks and limitations in REPORT. Mention/discovery alone is not use.

| Work | Relevant installed skills/plugins |
|---|---|
| Workflow | Superpowers `using-superpowers`; then applicable `executing-plans`, `using-git-worktrees`, `finishing-a-development-branch` |
| Coding and review | Ponytail: smallest complete change, preserve trust-boundary validation and tests; Superpowers `test-driven-development` for nontrivial new behavior, `verification-before-completion` before success claims |
| Failure/retry | Superpowers `systematic-debugging`; investigate root cause before patching; retain orchestrator retry limits |
| Frontend | `frontend-design`; Mobbin for examined UI/flow references; Magic Patterns for applicable prototype/design/integration work (read its surface-specific instructions). Do not replace the approved product plan with a new design exercise |
| Clerk | `clerk-cli` for management; `clerk-setup`, `clerk-react-patterns`, `clerk-testing` as applicable; follow documented CLI diagnostics and scoped auth tests, never print keys |
| Railway | Existing Railway plugin/MCP for relevant project/config/deployment checks; dev only is approved; distinguish configuration, health and end-to-end behavior |
| GitHub | Existing GitHub plugin for relevant repository/PR checks; local Git remains appropriate for local branches/tests. No remote/publication/PR creation solely to demonstrate plugin use |
| Browser/native UI | Installed `computer-use` skill before requested native control; follow its supported runtime and verify the target surface. Use purpose-built service tools when available |
| Cross-vendor review | Applicable Superpowers review skills and owning task's evidence; keep required reviewer vendor separate from implementation vendor |

Installed roots on this PC (discover exact versions if these change):
- Superpowers: `C:/Users/HP/.codex/plugins/cache/openai-curated-remote/superpowers/7.0.1/skills/`
- Ponytail: `C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.2/skills/`
- Clerk and frontend skills: `C:/Users/HP/.codex/skills/`
- Other advertised skill roots: use the fresh session's catalog.

Skills are subordinate to Koushik's scope and higher-priority safety/tool rules.
No synthetic fixture is real gate evidence. No secrets/private files, purchases,
accounts, legal terms, public uploads or unapproved deployments become authorized here.
