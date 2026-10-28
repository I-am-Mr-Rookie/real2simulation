# S02c1 round2 REPORT — Apollo 15 hammer-feather drop (NASA-only)

Status: **DONE** for the explicitly scoped bounded NASA/AP15 investigation (controller-accepted). AP15 verdict: **LOCATED_NOT_TRACKABLE / UNRESOLVED for measurement** — not lunar-g success, not a usable calibrated clip, not S02c success, no owner approval.

Status history: first written PARTIAL at commit 1e3fe80 (pre-rebase SHA); clarified to DONE (scope only) after controller acceptance checks (full-rate crop viewed, CSV 4 data rows / N1–N3 unchanged, owned diff/whitespace clean). All technical limits below unchanged.

- Lane CODEX-2; orchestrator-assigned Opus 5.5/high (runtime not independently observable). UTC 2026-10-27T23:27:53Z – ~23:34:36Z.
- Worktree .worktrees/S02c1, branch run/S02c1 from 449d36e (scaffold commit c802d6a first). Not merged; no clips.csv/controls/parent edits.
- Tokens/cost unknown; coding quota OpenCodex-managed, not polled. Meta/GPU/AWS $0. No uploads, YouTube, subagents, secrets.
- Round1 preserved byte-for-byte: REPORT-round1.md, PLAN-round1.md, candidates-round1.csv.

## Result (AP15 only)

| Item | Finding |
|---|---|
| Source | [NASA Science page](https://science.nasa.gov/resource/the-apollo-15-hammer-feather-drop-2/) HTTP 200: "At the end of the last Apollo 15 moon walk, Commander David Scott ... performed a live demonstration for the television cameras." Rights: NASA work, PD-USGov-NASA per NASA media guidelines (round1/S02a); factual use, no endorsement; identifiable astronaut. |
| Authenticity | Live EVA-3 LRV TV with original air-to-ground audio; machine ASR (AP15r2-asr.txt) matches Scott's narration ("left hand ... feather ... right hand, a hammer ... Galileo ... falcon feather ... I'll drop the two of them here ... How about that?"). Not reenactment, CG or other mission. |
| Better source? | Same page also hosts AS15_Ham_feath_drop3.mov (81,803,913 B; HEAD 200). ffprobe over HTTP: SVQ3 720x480, 2997/100, 2482 frames, 82.815 s + PCM → same master/resolution as retained m4v; not downloaded. The -1.m4v and plain .m4v have identical length (21,279,042) = retained file. Round1 Images API: no other NASA original. **No genuinely better NASA source.** |
| Segment | Retained test-data/public/AP15.m4v (SHA-256 687CEB04…22CC5, read-only). Narration "...same time" ends 59.00 s; "How about that?" 61.16 s. Every frame 58.40–61.70 reviewed: hands raised holding objects to ~59.83; hands open ~59.83–59.90 (approx release); faint descending streak/light object near legs ~60.0–60.9; hands empty, nothing in flight by 60.93. **Drop window ≈ file 59.8–61.0 s (~30–35 frames).** |
| Prior misses | Round1/primary sampled 48–83 at 2 fps and 60–67 at 10 fps, starting after release; 48–50 is a camera zoom-out; 51.0–51.8 motion peak is TV noise lines (AP15r2-50.5-52.6s-allframes.jpg), not the drop. |
| Visibility | Hammer/feather only intermittently distinguishable: they fall in front of the white LRV/suit, ~few px at 720x480, low contrast; no clean impact frame; feather not separable from hammer. |
| Timebase | progressive flags; 2997/100; no exact duplicate frames 58–62 s in crop (min mean diff 1.44, n=119) — archive TV cadence/fields still UNVERIFIED (noise may mask repeats). |
| Scale | none in plane; only NASA ~1.6 m release prior (S02a); camera fixed during window. |

Verdict: **LOCATED_NOT_TRACKABLE** — authentic, located, one trial, but object track not reliable from this file; cannot support a calibrated lunar g. Lunar, not Earth coverage. candidates.csv AP15 row updated (5 rows × 22 cols, N1–N3 parsed fields unchanged; text re-quoted by csv writer).

Evidence: AP15r2-asr.txt; AP15r2-0-48s-1fps.jpg; AP15r2-50.5-52.6s-allframes.jpg; AP15r2-58.4-61.4s-allframes.jpg; AP15r2-59.3-60.9s-allframes-crop.jpg (crop 240x330+220+130, key sheet); AP15r2-60.9-61.7s-allframes-crop.jpg.

## Commands (fresh)
ffprobe retained m4v + remote .mov; Invoke-WebRequest page + HEAD ×3; Get-FileHash; ffmpeg 1 fps / every-frame tiles with pts labels; ffmpeg tblend+signalstats motion profiles (48–70, 14–48, 58–62); faster-whisper small (cached, local_files_only, CPU) one-off ASR from TEMP; python csv shape check.

## Ponytail (actual)
Read/applied full C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.2/skills/ponytail/SKILL.md before work. Reused retained AP15 (no re-download), ffmpeg/ffprobe conventions from round1, installed faster-whisper with already-cached model (no new dependency). Simplest locator = audio narration timing, not tracking. No committed scripts (one-off TEMP ASR/csv commands), so no self-check file; csv shape checked after write. Deleted 4 uninformative own sheets. Skipped: tracking (objects not separable), ALSJ transcript/GET cross-check (page fetched, not parsed), Commons ogv comparison (primary's scope), .mov download (same master). Risks: release/impact frames approximate (±~3 frames); ASR is machine output.

## Next / questions
- Primary: keep AP15 uncounted as usable; if Mystery-g demo needs it, use window 59.8–61.0 as a qualitative/abstention example, or try manual click-labelling of the hammer head on the 59.3–60.9 crop (S02d) with explicit low confidence.
- Owner question: none.

Communication compliance: no chat narration beyond tool use; no messages to other chats; one final status line.

## Canonical FF handoff (controller request, 23:39:35Z)

- Backup branch codex/s02c1-r2-preaccept-1e3fe80 → 1e3fe80 (created before rebase).
- `git rebase --onto 0442e9dbec9f672dc07ef4790d3e8fc9d54eb4b1 449d36e run/S02c1`: 3/3 round2 commits applied, no conflicts (449d36e is not itself an ancestor of the pin; round1 content already on main). New SHAs 714d33f, 4e428c3, c59e6e8 + this clarification commit.
- Fresh checks: pin is ancestor of HEAD; main = pin (not checked out/updated/merged); `git diff --name-only pin HEAD` = 12 paths, all under evidence/clips/shards/NASA/; `git diff --check pin HEAD` clean; candidates.csv 5 rows × 22 cols, parsed N1–N3 rows identical to pin; candidates-round1.csv, REPORT-round1.md, PLAN-round1.md identical to pin's round1 versions; all AP15r2 evidence pointers in CSV and REPORT exist.
- No new acquisition, tracking, canonical controls or subagents.
