# Local recovery — retain this checkout

Never archive/delete the prepared s02g-forensics checkout until the owner/controller explicitly resolves scratch custody. `local-preservation/` is ignored, NEVER stage/upload it. It contains 8 licensed-project scratch JPEGs and 1 generated project Python cache, totaling542,671 bytes. `restoration-map.json` records every full SHA256 and absolute original/preservation path. Receipts may be integrated; scratch bytes must stay locally ignored.

Tracked files/old receipt paths: each candidate's exact retained branch and restoration command are in `pre-removal-ledger.json`. No branch/ref deletion or GC authorized. To restore later, ensure the old destination does not exist and the branch still has its recorded HEAD, then run its exact `git worktree add` command. All reachable tracked objects were checked locally; no network/download needed. Do NOT run restoration during cleanup merely as a test (would recreate >600MB per checkout).

After restoring the relevant branch checkout, for EACH ignored file in `restoration-map.json`, confirm preserved full SHA256, create only the original parent directory, copy only to an ABSENT original file (never overwrite), then verify original SHA256. This restores scratch/cache missing from Git. Do not copy arbitrary files or use recursive overwrite.

All44 historical test-data paths redirect to existing canonical paths in `tracked_redirects`; use these canonical originals directly without restoration. Full SHA256 matches CLEAN2 acquisition evidence; synthetic fixture files have no acquisition record and were verified against canonical bytes instead. No licensing/final-use/physical approval is created by deduplication.
