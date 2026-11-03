# N88-orch333
Status: DONE
Branch: run/N88-orch333; managed worktree under C:/Users/HP/.codex/worktrees/n88-orch333/2026-10-26 - Meta Global AI Developer Hackathon.
Changed: one public-pack writer records manifest SHA-256, size and nanosecond mtime in server-owned public.json; all binary copy paths use it.
Changed: quota excludes matching fingerprints, returns storage_bytes_public, always charges scene.json/public.json, and never trusts status.sample.
Changed: existing sample repair hash-backfills missing public.json once; edited/non-public artifacts stay charged.
Changed: workspace storage meter shows muted "Public samples not counted" only for positive excluded bytes; shared quota text agrees.
Python: requested storage/delete/fallback suite 170 passed, 1 host-symlink skip, 5 subtests passed; existing anyio deprecation warning.
Node: workspace and shell-workspace suites 208 passed, 0 failed.
Web: npm --prefix Build/web run build passed. git diff --check passed.
Offline actual-pack smoke: 36,720,689 public bytes excluded; 494,520 metadata bytes counted; edit/new-file/backfill assertions passed.
Evidence: evidence/N88/CHECKS.md and evidence/N88/public-bundle-smoke.json.
Paid calls: none. Delete, upload limits, 413 QUOTA_STORAGE and public pack bytes unchanged.
Skipped: browser QA (explicitly out of scope), deployment and live-user verification.
Risks: stat fingerprints cannot detect same-size mutations preserving mtime; public.json must stay server-owned. Existing per-write reservation gap unchanged.
