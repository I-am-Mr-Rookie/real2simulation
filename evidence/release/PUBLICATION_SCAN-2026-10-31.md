# S25e pre-publication scan, 2026-10-31

Run S25e-orch208 (CLAUDE lane, Opus 5.5 high). Scan start 2026-10-31T11:18Z, finished 11:21Z (UTC).

## Verdict

- **Main history: PASS.** No real secret, credential, private dataset, owner-clip footage or file over 50 MB in any object reachable from main `1b9ab540169b4c9f251f20d91dfc528dd07013df`.
- **Repository as a whole: was NOT CLEAR at scan time (resolved, see Q23 A receipt below; repo PUBLIC since 11:30Z).** The GitHub remote also holds release `backup-20261028T094623Z` ("Exact-history backup, 2026-10-28") with asset `real2simulation.bundle` (684,193,967 bytes, full history of all local refs) plus `BACKUP-MANIFEST.md`. Making the repo public publishes that release. The bundle very likely carries the 18 raw clip videos (`test-data/public/*.mp4|webm`, committed 2026-10-27/28 before the backup, only on non-main branches; bundle contents not opened in this run) and refs this scan did not cover. The public package checklist keeps raw video out of the public repo ("originals in private backup release"). Deleting a release or tag was outside the S25d authorization, so visibility was held until Koushik approved option A.
- Actions: fast-forward push `origin/main 58f1d2ce -> 1b9ab540` (11:22Z, no force); after Q23 A: release+tag deleted, repo made PUBLIC (11:30Z).

## Scope and commands

- Tools: git 2.x, python stdlib, PIL (installed). gitleaks / trufflehog: not installed (`where.exe` found neither); nothing installed.
- Scanner: [scan.py](../../Run-System/Runs/S25e-orch208/scan.py), reusing the S25c-orch155 rules, run as `python Run-System/Runs/S25e-orch208/scan.py 1b9ab540...`. Output JSON: [scan.json](../../Run-System/Runs/S25e-orch208/scan.json).
- Object set: `git rev-list --objects 1b9ab540` (exactly what a push of main publishes, including deleted files and old versions). First commit per blob from `git log --raw --no-renames`.
- Counts: 888 commits, 12,631 objects, 6,239 blobs, 5,159 distinct paths. 614 blobs binary or over 8 MB were not text-scanned (images, PDFs, fonts); images reviewed visually instead (below).
- Text rules: AWS AKIA/ASIA + secret key, Hugging Face `hf_`, OpenAI/Anthropic `sk-`, GitHub `ghp_/gho_/ghs_/ghu_/github_pat_`, Clerk `sk_/pk_ live/test`, Modal `ak-/as-` and MODAL_TOKEN_*, Baseten, Railway token, Slack, Google API key, Stripe live key, private-key PEM headers, JWT, Meta/Llama `*KEY|TOKEN=`, generic `NAME_(KEY|TOKEN|SECRET|PASSWORD)=<20+ chars>`, connection strings with inline password (postgres/mysql/mongodb/redis/amqp).
- Exact-value check: every root `.env` value of 8+ chars (12 names) byte-searched in every blob in-process; values never printed.
- PII: email regex over all blobs; Bangladesh mobile patterns (+880 1x, 01[3-9]xxxxxxxx); commit author/committer emails (`git log --format=%ae|%ce`).
- Paths: `.env*`, `archive/`, `Videos for Meta AI Hackathon`, `logo-sketches`, `.playwright-mcp/`, `.tmp-*`, storage-state/cookies, `*.pem|key|p12|pfx`, owner PDFs, `test-data/private/`, `uploads/`; media extensions; images listed for review.
- Remote refs: `git ls-remote origin` and `gh release list`.

## Findings (path + first commit)

| # | Path | Commit | Rule | Verdict | Why |
|---|---|---|---|---|---|
| 1 | Build/api/health/test_dependencies.py:13 | 58f1d2ce | conn_str | false positive | Test canary `postgresql://canary:canary@127.0.0.1:1/dev`, unreachable port, not a credential. |
| 2 | many REPORT/QUEUE/STATE files (356 + 251 + 22 + 9 hits) | many | .env value match: BASETEN_MODEL, MODEL_API_MODEL, LLM_MODEL, BASETEN_BASE_URL | false positive | Public model IDs and endpoint URL, same as S25c. No *_API_KEY, MODAL_TOKEN_*, MERGE_* or FIREWORKS_API_KEY value appears anywhere. |
| 3 | .env.example | 58f1d2ce | path | false positive | Only .env-family path ever committed; empty placeholders. |
| 4 | tests/sidebar-tools/test_library_search.py, test_fireworks.py | various | email regex (`pas...@inference.baseten.co`, `pas...@api.fireworks.ai`, `...@private.invalid`) | false positive | Redaction-test fixtures (fake userinfo in URLs). |
| 5 | 90 asset filenames like `a1-...@2x.webp` | various | email regex | false positive | Image density suffixes, not addresses. |
| 6 | evidence/clips/calibration-recovery/S02f/recovery2/sources/*.json | various | email (two nasa.gov addresses) | accept | Public NASA media-record contact fields copied from images.nasa.gov metadata. |
| 7 | evidence/S05/S05b/upstream-pyproject.toml | various | email (one gmail.com) | accept | Upstream open-source package author field, already public on the package index. |
| 8 | commit metadata | all | author/committer emails | accept | Only GitHub noreply addresses (`mr.rookie@users.noreply...`, `234005366+I-am-Mr-Rookie@users.noreply...`), `codex@local`, `w@x`, `noreply@github.com`. |
| 9 | evidence/S07/S07i/track-own02.json, track-own08.json, S07j/track-own08.json, S10/browser-simulation/pendulum.server-trace.json, clips/S02c-nasa-FF05-metadata.json | various | phone pattern | false positive | Digit runs inside numeric track/trace/metadata values. |
| 10 | evidence/S07/S07g/modal-usage-preadmission.png | (S07g) | image review | low, owner awareness | Modal billing page screenshot: shows the Modal workspace name (owner's public name), credit balance and usage. No key, email or payment details. Not a secret. |
| 11 | evidence/S07/auth-provision2/modal-saved-metadata.jpg | (S07b) | image review | false positive | Secret NAME and type only (`real2simulation-hf-read`, Hugging Face); value not visible. |
| 12 | evidence/owner/S06/SAM3D-ACCESS-granted-20261029.png | (S06) | image review | false positive | Public model page with "granted access" badge; no account name or email visible. |
| 13 | evidence/clips/** frame sheets (RM04, PD03, PD04, PD06, BN01, PJ03, N1-N3, AP15, ST01-ST05, RP01-RP03, FF01-FF02) | various | media licence | accept with note | All trace to allowed licences: Pexels License (ST01/02/04/05 recorded in evidence/clips/shards/STOCK/candidates*.json), Commons CC BY 3.0 / CC BY-SA 4.0 (RP01-RP03 in calibration-recovery S02f/S02i ATTRIBUTION.md, FF01/02 in S02g LICENSE-NOTICE.md), NASA PD. PJ03 end card visible in PJ03-keyframes-48plus.jpg itself states CC BY 4.0 (Mathe-AC Lernwerkstatt Aachen; retaining the end card suffices). Gap: ST01, ST02, ST04, ST05, RP01-RP03 are not rows in clips.csv; RM04/PD03 frames contradict the checklist "BLOCKED-for-public" policy marks (not a licence breach under Pexels). Recommend registering them in clips.csv. |
| 14 | 544 images total | various | owner-clip footage review | PASS | 95 Build/web/public and 54 evidence/brand images are generated/owner-owned art; 180 evidence/clips images are licensed sources (row 13); the other 215 (UI screenshots incl. all OWN01/OWN05 workspace shots) were contact-sheeted (Run-System/Runs/S25e-orch208/ui-sheet-*.jpg, local only) and reviewed: UI, text and numbers only, no owner-clip frames, crops or masks. |
| 15 | archive/, Videos for Meta AI Hackathon/, evidence/owner/logo-sketches-2026-10-31/, .playwright-mcp/, .tmp-*, owner PDFs, key files, test-data/private/, uploads/ | - | path | PASS | Zero objects reachable from main. |
| 16 | any blob | - | size > 50 MB | PASS | None (main has no video files at all). |
| 17 | GitHub release backup-20261028T094623Z: real2simulation.bundle (684 MB) | tag 1fb9df46 | remote content outside main | **BLOCKS visibility** | See verdict. Public visibility would expose the full-ref bundle, including 18 raw videos and unscanned refs. |

## Remediation options for row 17 (need Koushik)

- A: delete the GitHub release and tag `backup-20261028T094623Z` (bundle stays in the local backup or moves to private storage), then make the repo public and verify logged-out.
- B: keep the backup there and keep the repo private (for example publish a fresh public repo containing main only).
- C: owner accepts publishing the bundle after a separate scan of every ref in it and a raw-video redistribution decision.

No credential rotation or history rewrite is needed for main.

## Logged-out check before the flip (repo still private)

`python urllib`, no cookies, 2026-10-31T11:23Z: github.com/I-am-Mr-Rookie/real2simulation 404; raw README.md 404; raw LICENSE 404 (expected while private). `python evidence/release/check_links.py`: all relative links resolve (exit 0).


## Q23 A receipt and publication (2026-10-31)

- Koushik approved Q23 A ("y", about 17:30 Dhaka) via the controller: delete release "Exact-history backup 2026-10-28" and tag backup-20261028T094623Z, then make the repo public. Controller first copied the bundle, logs and BACKUP-MANIFEST.md to C:/Users/HP/Documents/Hackathon/Backups/real2simulation-backup-20261028T094623Z/ (outside the repo; controller-reported SHA-256 matches the manifest). S25e confirmed the copy is present (real2simulation.bundle 684,193,967 bytes) before deleting.
- 11:29:42Z `gh release delete backup-20261028T094623Z -R I-am-Mr-Rookie/real2simulation --cleanup-tag --yes`: exit 0. `git ls-remote origin`: only HEAD and refs/heads/main at 1b9ab540.
- 11:30Z `gh repo edit I-am-Mr-Rookie/real2simulation --visibility public --accept-visibility-change-consequences`: exit 0; `gh repo view --json visibility`: PUBLIC.
- Logged-out verification 11:30:12Z (python urllib, no auth, no cookies): repo page 200; raw README.md 200 (starts "# Real2Simulation"); raw LICENSE 200 ("MIT License"); API releases 200 []; tags 200 []; branches 200 ["main"].
- Row 17 is resolved: nothing besides main 1b9ab540 (scanned above) is public. No further push by S25e; later main commits are pushed by the controller after its own delta scan.
