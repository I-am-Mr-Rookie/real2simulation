# Backup manifest — 2026-10-28

- Private repository: `I-am-Mr-Rookie/real2simulation`
- Release tag: `backup-20261028T094623Z`
- Source main commit: `4a6609f70c7f6ff10bbb75dc32c95193850c1f17`
- Asset: `real2simulation.bundle`
- Asset bytes: `684193967`
- SHA-256: `6DD380499124CE82940190BA65C6CD33A75B0581391E1E4ED926AFFB8224A1DC`
- Coverage: committed Git history and all 108 local refs selected by `git bundle create --all`; original commit IDs preserved.
- Verification before upload: `git bundle verify` passed; a bare clone from the bundle restored the exact source main commit.
- Secret scan: Gitleaks v8.30.1 passed across all refs, with one narrowly scoped exact-fingerprint exclusion for a verified nonsecret policy sentence about API spend and AWS permissions. No global scanner rule was weakened.

## Restore

Run in an empty recovery directory while authenticated to the private repository:

```powershell
gh release download backup-20261028T094623Z --repo I-am-Mr-Rookie/real2simulation --pattern 'real2simulation.bundle' --pattern 'BACKUP-MANIFEST.md'
Get-FileHash -LiteralPath '.\real2simulation.bundle' -Algorithm SHA256
# Confirm the SHA-256 matches this manifest, then restore:
git clone --branch main '.\real2simulation.bundle' '.\Real2Simulation-restored'
git -C '.\Real2Simulation-restored' rev-parse HEAD
# Expected: 4a6609f70c7f6ff10bbb75dc32c95193850c1f17
```

Other bundled branch tips are available as remote-tracking refs after a normal clone. The original bundle retains its refs for additional recovery. This metadata branch is not the original project branch; cloning the GitHub URL alone does not restore the product.

Excluded: credentials and `.env`, private teammate/archive material, caches/dependencies and other ignored local files, uncommitted edits in separate worktrees, and changes made after the checkpoint. Restore required private local configuration separately and securely. This is not a full computer backup.
