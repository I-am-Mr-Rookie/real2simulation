# S02a — DONE (source-candidate scope only)

## Objective / authorization / routing

Koushik authorized `complete run S02a`: source at least three terrestrial fall
candidates and Apollo 15 with original sources, rights, scale/timebase suitability.
Lane CODEX-2; planned GPT-6.1 Terra / high. Actual manual Codex chat model/effort
and task token counts are not exposed; no model/provider/settings changes made.

- UTC start: 2026-10-27T17:22:11Z.
- Task integration and fresh-main verification: 2026-10-27T17:34:17Z.
- UTC end / control receipt checkpoint: 2026-10-27T17:37:20Z; final validation/commit followed.
- Duration to task integration: 12m06s; control receipt/cleanup followed within 30m.
- Initial main: ff0eb57f88115e607de3c796dcdd8d33fbdcce33; claim: 1c0c749.
- Merged task tip: b853382ade0b1d0c2e272db6b0d5e23c00dc9f35; fast-forward only.
- Worktree: `.worktrees/S02a`, branch `run/S02a`. Managed creation failed because
  main was unavailable to app integration; documented local Git fallback used.
- No prior REPORT.md existed at preflight. Read S03 receipt; read new S05a report
  on canonical main during integration. Concurrent S05a/S08a changes preserved.

## Deliverables / acceptance

- `clips.csv`: four terrestrial candidates plus AP15. Four Commons CC BY-SA 4.0
  declarations and one file-specific PD-USGov-NASA declaration checked live.
- `evidence/clips/S02a-sourcing.md`: suitability, caveats, attribution/adaptation
  requirements, exclusions, future acquisition/metadata/approval handoff.
- `evidence/clips/S02a-provenance.json`: five file-page HTTP200 receipts, revision
  IDs, page SHA256 values, short file-specific licence excerpts, original media
  links; official NASA page HTTP200 and linked M4V verified. These are source
  retrieval receipts, not saved full-page snapshots or downloaded-media hashes.
- `capture_s02a_provenance.py` and `check_s02a_manifest.py`: repeatable source
  reads and offline candidate-manifest acceptance; no third-party packages.

Acceptance met: >=3 fall candidates plus Apollo; original source/creator and rights
recorded; scale/timebase suitability explicitly assessed. **No usable/calibrated
gravity-trial count is claimed.** Four falls represent only three provisional
capture groups: FF01/FF02 may share footage. FF03 is a time-direction challenge;
FF04 is slow motion with unknown factor. FF02's inferred height is circular for
recovering gravity. AP15's approximately 1.6 m source height is an uncertain prior,
not independently calibrated ground truth.

## Commands / results

| Check | Result |
|---|---|
| `python evidence/clips/capture_s02a_provenance.py` | Exit0; 5 file-specific rights declarations + NASA original link; source pages only |
| `python evidence/clips/check_s02a_manifest.py` | Exit0; 4 fall candidates / 3 provisional groups + Apollo; explicit unknowns and no acquisition; rerun after rebase and on main |
| `git diff main...run/S02a --check` | Exit0 after rebase |
| `git rebase main`; `git merge --ff-only run/S02a` | Both successful; no conflicts; concurrent CODEX-1 work retained |
| `python Run-System/runs_view.py` | Exit0; 10/193 DONE; S02b now ready; no owner questions |
| Worktree cleanup | Resolved exact local path checked; clean status verified; `git worktree remove` succeeded without force; run branch retained |
| Browser review | NASA playback/lunar scene; FF01 bridge/railing and editor-timer annotation; FF04 glass-impact scene observed; not full frame/cadence analysis |

Initial Commons browser access and Rhetos explanatory-page fetches returned429.
Koushik reported Wikimedia working; fresh browser state confirmed recovery and
FF01/FF04 played. Source HTML reads succeeded independently. Initial unsupported
NASA AX seek failed harmlessly; no exact seek timestamp or frame measurement is
claimed. No credentials, authentication or access restrictions bypassed.

## Limits / next

No media downloaded to test-data/public, no measured file fps/duration, no owner
approval, no Meta/service inference/GPU, no uploads/accounts/terms/deployments,
publication or submission. Historical Meta balance/spend remains unknown; $0 new
Meta/compute/API inference spend. Subscription dollars/tokens unavailable. Shared
Codex quota before/after: used67% 5h /49% weekly (not task cost attribution); no reset.

S02b is now ready: Codex CODEX-2, planned GPT-6.1 Terra / high. Source remaining
experiment types and three rooms. S02c acquisition, S02d local metadata/scale checks
and S02e Koushik approval remain undone. All product gates remain NOT RUN.
No owner question is needed for this source-only run.
