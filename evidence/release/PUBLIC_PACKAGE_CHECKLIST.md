# Public package checklist (S25b-orch154)

Draft, 2026-10-30. Nothing here publishes, changes repo visibility or uploads. Owner go-ahead is required for each public action.

## 1. Rights per asset
Full per-asset record: [ATTRIBUTION.md](../../ATTRIBUTION.md) → Per-asset record. Summary:

| Asset | Licence (per clips.csv) | Public status |
|---|---|---|
| PD02, RM02, ST03 (demo script) | Pexels License | public: short demo-video snippets with on-screen credit (owner Q19 A, Oct31); credits on screen and in ATTRIBUTION.md. ST03 shows a person. Repo visibility still PENDING S25d. |
| RM04 | Pexels License | Descriptor metadata only (library). Frames BLOCKED-for-public. |
| PD03 | Pexels License | Local only; BLOCKED-for-public. |
| BN01, PD04, PD06 | CC BY-SA 4.0 | Local only; if shown, mark adapted + share-alike. |
| PJ03 | CC BY-SA 4.0 + third-party end card | BLOCKED-for-public: end-card licence unverified. |
| RM05 | NASA public domain | Local only; no frames shown; no endorsement implied. |
| Library SIMULATED (13) | project-authored | OK, no footage. |
| Unused: FF01-04, AP15, PJ01, PD01, RM01, RM03, BN02, N1-N3 | n/a | Not used; exclude from public claims. |
| Models/libraries | see ATTRIBUTION.md | SAM 3.1 licence copy in evidence/S05/upstream; Muse hosted APIs only. |

Raw video files stay out of Git (.gitignore test-data/public/**; originals in private backup release). Licence pages were not re-fetched in S25b.

## 2. README links
| Item | State |
|---|---|
| Judging URL / frozen revision | PENDING S23 (README marks it PENDING) |
| Demo video | PENDING S24/S23 (README marks it PENDING) |
| Railway dev URLs | Dev only, not the judging build |
| Local links (BENCHMARK.md, Build/*, API_BUDGET.md, .env.example) | Checked to resolve; see REPORT.md |
| LICENSE | DONE: MIT, owner Q18 (S25f); [LICENSE](../../LICENSE) covers own code/docs only; repo visibility stays PENDING S25d owner go-ahead |

## 3. Private data exclusions (must not enter the public repo)
archive/ (incl. teammate data), .env and .env.* (only .env.example), owner PDF `Updated_Instructions_10_28_2026_...pdf`, Build Notes.pdf, Hackathon Credit Terms.pdf, modal.fillout.com*.png, .playwright-mcp/, .tmp-* (e.g. .tmp-s19d-ctx/), test-data/private/, uploads/, .worktrees/, credentials/key files. Note: .playwright-mcp/, .tmp-* and the owner PDF are untracked but NOT in .gitignore: add ignores or delete before publication (controller/owner decision).
Also review Run-System/ and evidence/owner/ contents for personal or account data before the repo goes public.

## 4. Contest note
Per official rules: new work only, built Oct 27 – Nov 4; the demo shows only event work; public repo at submission; no assets without rights. archive/ (AttemptLens phase) is not part of the submission.

## 5. S25c secret-scan handoff
Scan the full tracked tree AND git history of the public candidate for key-name values (Meta/Muse, Modal, Clerk, Railway, AWS, Hugging Face, DB/Redis URLs, S3 keys), tokens in evidence logs and screenshots. Report names/paths only, never values. Confirm .env absent from history, then re-check section 3 exclusions.

## 6. clips.csv inconsistencies (recorded, clips.csv NOT edited)
| # | Finding | Recommended fix (controller) |
|---|---|---|
| 1 | RM02 licence = "Pexels"; RM04, PD02, PD03, ST03 use "Pexels License"; RM01, RM03 also "Pexels". S18h credits also say "Pexels" for RM02. | Normalize to "Pexels License" in clips.csv and S18h credit export. |
| 2 | PD02, RM02, ST03 (and all other rows) show status UNAPPROVED_CANDIDATE / owner_approved NO, while evidence/owner/S02/APPROVAL.md (Oct 28, Q7 "A") approves RM02, RM04, RM05, PD02, PD03, PD04, PD06, PJ03, ST03, BN01 for scoped local processing; APPROVAL.md says not to change flags broadly. | Add a non-boolean column or note (e.g. status=APPROVED_LOCAL_S02E, owner_approved=LOCAL_ONLY) for those 10 IDs only; keep public-use = NO until Q19. |
| 3 | ATTRIBUTION.md old table listed 9 clips; PJ03 (approved) was missing. | Fixed here (per-asset table). |
| 4 | PJ03 end card by Mathe-AC Lernwerkstatt Aachen has no recorded licence. | Keep BLOCKED-for-public; do not show PJ03 frames. |
| 5 | Several rows lack local_path (FF03, FF04, RM01, RM03): unused, no action. | None. |

