# Private GitHub repository and restoration

## Current source repository

The private repository now contains a normal, browsable project snapshot on `main`, connected to this local checkout as `origin`. It is not automatically synchronized: commit and push subsequent intended changes normally.

```powershell
git clone https://github.com/I-am-Mr-Rookie/real2simulation.git
# In an existing clone, after reviewing and staging intended nonsecret changes:
git commit -m 'Describe the change'
git push origin main
```

The source snapshot restores the pre-Astra checkpoint `4a6609f70c7f6ff10bbb75dc32c95193850c1f17`, with only repository/backup documentation and video-ignore rules changed for normal GitHub use. No Astra implementation commits were found. The one uncommitted owner reply in RUNS.md was preserved in the local stash before restoring that file.

The original local history is retained on `recovery/pre-live-snapshot-20261028` and in the existing release below. Source `main` starts from the GitHub repository's metadata history; no old commit IDs were rewritten or force-pushed. Other local run branches remain unchanged. Do not merge the old raw-video history back into source `main`; port intended source changes selectively.

All 19 previously tracked input videos remain unchanged on disk, but are excluded from the source snapshot to avoid oversized files and heavy clones. Download the retained exact-history bundle to recover these inputs. Source, manifests, attribution and other tracked evidence remain in normal Git. Secrets/private/ignored files still stay local; no automatic sync or full-computer backup is implied.

## Original exact-history backup (retained)

Repository: https://github.com/I-am-Mr-Rookie/real2simulation

Koushik authorized creation of this **private** repository and chose an exact-history Git bundle on a private GitHub release, without rewriting history (Oct 28, 2026).

## What is backed up

The release asset `real2simulation.bundle` contains the committed repository and all local Git refs included at that checkpoint. Original commit IDs are preserved. Its companion `BACKUP-MANIFEST.md` records the source main commit, bundle SHA-256 and restore instructions.

This historical bundle preserves the original product history and input videos, including the 168 MiB `test-data/public/RM05.mp4` that blocks a normal push of that history. The current GitHub default branch now contains the source project; the bundle remains available separately without history rewriting.

Not included: `.env` and credentials, private teammate/archive material, local caches/dependencies, ignored files, uncommitted worktree changes, or edits made after the checkpoint. Git is not a full computer backup. Preserve any needed private local material separately and securely; do not upload it to this repository.

## Restore

Use an empty directory outside an existing checkout, while authenticated to the private repository:

```powershell
gh release list --repo I-am-Mr-Rookie/real2simulation
# Substitute the exact backup release tag printed above.
$tag = 'BACKUP_RELEASE_TAG'
gh release download $tag --repo I-am-Mr-Rookie/real2simulation --pattern 'real2simulation.bundle' --pattern 'BACKUP-MANIFEST.md'
Get-FileHash -LiteralPath '.\real2simulation.bundle' -Algorithm SHA256
# Compare the hash against BACKUP-MANIFEST.md before restoring.
git clone --branch main '.\real2simulation.bundle' '.\Real2Simulation-restored'
git -C '.\Real2Simulation-restored' log -1 --oneline
```

Cloning restores `main` and makes the other bundled branch tips available as remote-tracking refs. The bundle itself retains the original refs for additional recovery. Restore credentials and dependencies separately. Never paste credentials into Git, RUNS.md or chat.

Git rollback does not undo cloud spending, deployments, uploads, repository visibility, legal acceptance or submissions.
