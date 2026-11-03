# N88 public storage accounting

- `python -m pytest tests/api-storage tests/reconstruction/test_room_delete.py tests/agent/test_fallback.py -q -rs`: 170 passed, 1 skipped, 5 subtests passed. The skip is the host's unavailable symlink creation privilege. Existing anyio pytest deprecation warning only.
- `node --test tests/workspace/*.test.mjs tests/shell-workspace/*.test.mjs`: 208 passed, 0 failed.
- `npm --prefix Build/web run build`: passed, compiled and generated all three static pages.
- `git diff --check`: passed.
- Regression coverage: all copied pack binaries free, legacy points-mobile alias, whole-file charge for edits/replacements/new files, scene and provenance JSON charged, returning-user hash backfill once, bad fingerprints and malformed indexes fail closed, owner isolation, no status.sample exemption, no hashing during quota calls, muted UI note conditional on excluded bytes.
- Offline smoke used the actual local hash-checked public bundle, a disposable synthetic owner, and the current code. See `public-bundle-smoke.json`: six binaries totaling 36,720,689 bytes excluded; 494,520 bytes of metadata still counted. Edited mesh and new file both charged; old-room backfill did not renew the edited mesh exemption. The smaller backfilled metadata total reflects a shorter public.json.
- Public pack contents, delete behavior, upload limits and 413 QUOTA_STORAGE were not changed.
- No browser QA, deployment, paid calls, uploads to providers or private-owner data access.
- Known limit required by the design: size and mtime are fingerprints, not integrity proofs. A local/out-of-band writer that changes bytes while preserving both can evade detection. public.json must remain server-only. Existing no-per-write-reservation quota limitation is unchanged.
