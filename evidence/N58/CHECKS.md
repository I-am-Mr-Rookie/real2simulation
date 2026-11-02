# Final checks

Code commit: `23f449578ef6b8e13bbb88a50eb8b1eb83820ec9` on `run/N58-orch303`.

- Node workspace/shell/editor/lab/private-route/BFF suites: **386 passed, 0 failed, 0 skipped**. `resolve-deps.mjs` points only at the already installed web Rapier package.
- Final targeted actual preview-card render: **1 passed** after adding the aspect-preserving relative-plot assertion. Wrong-source video and saved-snapshot precedence are covered.
- `python -m pytest tests/api-storage evidence/N58/test_stage.py -q`: **21 passed**, one installed-anyio pytest deprecation warning.
- Final shipping `npm run build`: **passed**. The temporary `/lab/n58-check` route is absent from the build and a fresh request returned **404**.
- Headed Chromium browser script: **19 passing receipts**, no page errors, room view response **200**, paid operations blocked. Widths 1366/375, light/dark, real public samples and a generated template. See browser-receipts.json.
- In-app browser recovered and manual phone/desktop checks completed. See IAB-CHECKS.md and local-only PNGs. It is not a Clerk-authenticated DEV test.
- Actual API staging from the committed worktree: **passed**, **201 files**. The copied RM04 archive is **9,330,251 bytes**, SHA-256 `1ff2069d346e751e608e0ea5034e278deed6e84d186a5475e5f56eacbb645d6f`, matching the manifest. No deploy occurred.
- Stage regression also rejects a missing archive and a corrupted archive before creating its destination.
- `git diff --check` and staged text credential-pattern/prohibited-binary scan passed. Scan is heuristic, not a comprehensive security audit. No private data, media binary, secret or temporary route is committed.
- Paid calls: **0**, cost **$0**. No paid remote operation, upload to a provider, model/routing/spend change, DEV deployment or owner-data access.

Not checked: real sign-in/sign-out, real microphone/transcription, paid segmentation/SF3D/shell generation, successful known-size calibration or DEV snapshot physical deletion. Local byte deletion is asserted against a real temporary filesystem and preserves uploads.
