# Real2Simulation — private exact-history backup

The full project is stored in the **Git bundle attached to each backup release**, not in this metadata branch. Original commit IDs are preserved. Source history includes a 168 MiB video that exceeds GitHub's normal Git file limit; Koushik chose this backup method instead of rewriting history.

- [Download backup releases](https://github.com/I-am-Mr-Rookie/real2simulation/releases)
- [Current backup manifest and restore instructions](BACKUP-MANIFEST.md)
- [Master prompt for GPT-6 Astra Pro](prompt%20for%20GPT-6%20Astra%20Pro.md)

The latest checkpoint includes source main commit `4a6609f70c7f6ff10bbb75dc32c95193850c1f17` and all 108 local refs selected by `git bundle create --all`. A local bare-clone restoration was verified against that exact main SHA before upload.

This is a private backup, not a public hackathon submission. Secrets, private/archive material, ignored local files and uncommitted worktree edits are not included. Git cannot undo external spending, uploads or submissions.
