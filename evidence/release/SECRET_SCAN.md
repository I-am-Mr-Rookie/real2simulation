# S25c secret / private-data scan

Run S25c-orch155. Scan time 2026-10-30T19:51:37.1509172Z (UTC). Base main `21090623` / worktree branch run/S25c-orch155.

## Verdict: PASS — no real secret found. No STOP-publication finding.

## Tool and scope
- No gitleaks / trufflehog / detect-secrets installed -> scripted regex scan: `Run-System/Runs/S25c-orch155/scan.py` (stdlib Python + `git`; no network).
- Scope: all local branches (351 branch refs), 1,158 commits via `git rev-list --all`, 6,166 unique blobs reachable from `git log --all --raw` (includes deleted files and old versions); 3,675 files tracked at main HEAD. 358 blobs skipped (binary or >8 MB: media, PDFs, images).
- Rules: AWS AKIA/ASIA + secret key, HF `hf_`, OpenAI/Anthropic `sk-`, GitHub `ghp_/github_pat_`, Clerk `sk_/pk_ live/test`, Modal `ak-/as-` + MODAL_TOKEN_*, Baseten, Railway token, Slack, private-key PEM headers, JWT, Meta/Llama `*KEY/TOKEN=`, generic `NAME_(KEY|TOKEN|SECRET|PASSWORD)=<20+ chars>`.
- Exact-value check: every .env value (12 names, length >=8) was compared in-process by byte search against every scanned blob. Values never printed.
- Path check: .env*, .playwright-mcp/, .tmp-*, archive/06, storage-state/cookies, *.pem/key/p12/pfx, Updated_Instructions PDF, video media, in tracked files and all history.

## Findings
| Path | Commit | Rule | Key NAME | Severity | Reasoning |
|---|---|---|---|---|---|
| .env.example:8 | 58f1d2ce | modal_tok | MODAL_TOKEN_ID/SECRET | none | FALSE POSITIVE: regex `\s*` spanned the newline; both values are empty in the example. |
| many (QUEUE/STATE/README/REPORTs, 9 + 352 + 371 + 62 hits) | many | env-value match | BASETEN_MODEL, MODEL_API_MODEL, LLM_MODEL, BASETEN_BASE_URL | none | FALSE POSITIVE: values are public model identifiers / endpoint URLs, not credentials. |
| (none) | - | env-value match | all *_API_KEY, MERGE_*, MODAL_TOKEN_*, FIREWORKS_API_KEY | - | No .env credential value appears in any tracked file or history blob. |
| (none) | - | all provider key patterns | - | - | Zero hits for AKIA, hf_, sk-, ghp_, Clerk, PEM, JWT, Slack, Baseten, Railway. |
| .env.example | 58f1d2ce | path | - | none | Only .env* path ever committed; placeholders only. |
| test-data/public/*.mp4/webm (18) | various | media | - | low / owner check | Only media in history; `test-data/public` = licensed public clips per clips.csv (not re-verified here). |

Not in history/tracked: .env, archive/06 Real User data, .playwright-mcp/, .tmp-*, storage-state/cookies, key files. The owner PDF (Updated_Instructions...) was never committed. Other tracked PDFs are generated reports (evidence/S17/compiled/*).

## Working-tree risk (untracked, NOT ignored)
`git status` shows untracked: `.playwright-mcp/`, `.tmp-s19d-ctx/`, and the Updated_Instructions PDF. A careless `git add -A` would stage them. Recommended .gitignore additions (recorded only; .gitignore not owned by this run):
```
.playwright-mcp/
.tmp-*/
Updated_Instructions_*.pdf
*storage-state*.json
*cookies*.json
```
Already ignored: .env, .env.*, archive/, .worktrees/, keys, Build Notes.pdf, Hackathon Credit Terms.pdf.

## Limits
- Regex scan can miss non-pattern or obfuscated secrets; binary/>8 MB blobs (358) not text-scanned; no entropy scan; no remote refs/stash/reflog or worktree-only unstaged files beyond branches; other worktrees' untracked files not scanned.
- Re-run right before publication (new commits land continually): `python Run-System/Runs/S25c-orch155/scan.py` from a checkout that can see the root `.env` path (script path is hard-wired to the canonical root).

