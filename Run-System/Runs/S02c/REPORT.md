# S02c — PARTIAL

## Scope and receipt

Requested CODEX-2, GPT-6.1 Terra/high; delegated Codex runtime model and effort
not exposed, so exact routing cannot be verified. First clock 2026-10-27
18:16:19 UTC; receipt 18:26 UTC; initial main 13bc36b; claim 1ec5b8d. Partial task branch
`run/S02c` commit `79df318a104cd214cc6d66c84558266660a525e8`, worktree
`.worktrees/S02c`. **Not merged**: acceptance of at least ten usable clips
failed; preserve branch and worktree for authorized continuation. Plan is in
that branch. Existing untracked research/concept files were untouched.

## Results

Seven unapproved local candidate videos with source, licence, attribution,
SHA-256, ffprobe metadata and downloadable source URLs: AP15, FF01, FF02, PJ01,
BN01, BN02 and PD01. NASA source plus Commons source-specific CC BY-SA
declarations; BN02 is a new own-work bounce candidate. Total original files
approximately 205 MB; largest BN01 is 75,465,750 bytes. No Pexels file was
downloaded: its restrictions on unaltered sales and redistribution on other
stock/wallpaper platforms require a separate check for future public repository
distribution; do not assume raw stock redistribution is cleared. Commons FF03
and FF04 HEAD requests returned HTTP 429; no retry or bypass. Recheck availability
later. No owner approval or benchmark/gate success is claimed. Local acquisition
does not authorize product use, upload, deployment or publication.

**Approval-order conflict:** the S02b sourcing handoff says to acquire only with
owner approval, whereas the queue places acquisition in S02c before S02e approval.
These seven were downloaded locally without that explicit approval; they remain
unmerged and unused. This discrepancy should have been raised before download.
Stop further acquisition until Koushik clarifies the order; question in STATE.

Spot-viewed one frame each of AP15, FF01, BN02, PJ01 and PD01. They contain
overlays or mixed segments; that is not proof of trackable continuous motion,
physical scale or real-time cadence. FF01/FF02 may overlap, and are not
independent trials. New BN02 has source-reported 240 fps and frame-by-frame
segments, not a verified capture timebase. Seven files is not seven validated
physical clips, and it is below ten even before suitability screening.

## Checks

- `python evidence/clips/check_s02a_manifest.py` and `check_s02b_manifest.py`:
  PASS before and after acquisition. Historical checkers now permit real local
  files while retaining source/rights, status, scale and coverage assertions.
- `python evidence/clips/check_s02c_acquisition.py`: PASS, seven files match
  hashes and have source, licence, creator and attribution; all unapproved.
- Same command `--require-ten`: exit 1, **7/10 local files**; count alone does
  not establish physical usability. S02c acceptance is not met.
- `ffmpeg -v error -xerror -i <file> -map 0:v:0 -f null -` for all seven:
  exit 0; full video decode only, not segment suitability. ffprobe and SHA-256
  receipts at `evidence/clips/S02c-acquisition.json` on the task branch.
- `git diff --cached --check`: PASS; only owned paths and run plan staged.

## Skills, limitations and next

Read `Run-System/SKILLS_AND_PLUGINS.md`, Superpowers `using-git-worktrees` and
`verification-before-completion`; applied isolated worktree and fresh evidence.
Local Git worktree used because protocol specifies path and branch. Web source
pages/licence research, local ffprobe/ffmpeg, image spot checks and quota tool
actually used; no native-computer control requested, no GitHub or Railway action.
No credentials, private data, YouTube downloads, accounts, terms acceptance,
purchase, inference, GPU, uploads, deploys or publishing.

Shared Codex usage before/after: 70% five-hour / 50% weekly, not per-task attribution.
Tokens and task subscription dollars unknown;
Meta/service inference/GPU $0 this run, historical Meta balance unknown.
Next authorized continuation must source and verify additional genuinely usable
clips, resolve raw Pexels-repository rights if needed, and meet the >=10 check;
then S02d assesses all timing/scale and S02e requires Koushik's approval.

## Authorized continuation, 2026-10-27 19:06–19:09 UTC — PARTIAL

Q2 explicitly permits provisional local downloads. Retained `run/S02c` worktree
continued from 79df318; canonical main at start fcb0530. Requested CODEX-2,
Terra/high; actual model/effort not observable. Commit e36efc7 adds
`evidence/clips/S02c-continuation.md` to the retained, unmerged branch.

- Normal GET requests for FF03 and FF04 returned HTTP 429; Pexels RM01 source
  page returned 403. No bypass and no further downloads. Two NASA educational
  leads documented, but source-specific rights/segments not established.
- Fresh coarse contact sheets of BN01, FF01 and PD01 reveal material suitability
  risks (lighting, multiple views, overlays, frame-by-frame/slow-motion edits);
  they do not verify usable continuous segments, scale or timebase. Seven
  candidates remain unapproved and must not be presented as seven usable clips.
- `python evidence/clips/check_s02c_acquisition.py --require-ten`: integrity
  check passes for 7 but count exits 1 (7/10); physical usability not checked.
  `python evidence/clips/check_s02a_manifest.py` and `check_s02b_manifest.py`
  pass their sourcing checks. `git diff --cached --check` passed before commit.
- Next: wait for normal source availability and find rights-cleared, genuinely
  usable footage; preserve branch until acceptance. S02d remains blocked by
  S02c; S02e owner approval is required before final use. No question needed.
- Skill: superpowers `verification-before-completion`, applied to distinguish
  attributed candidate counts from actual usability; web search, ffmpeg, image
  inspection and local Git used. No native control or service plugin was needed.
  Quota at end 70% five-hour/50% weekly; before this continuation unavailable.
  Tokens and subscription cost unknown; inference/GPU cost $0. No upload,
  deployment, publication, product use, or owner approval claimed.

## Authorized continuation, 2026-10-27 20:21 UTC — PARTIAL

- Requested CODEX-2 / GPT-6.1 Terra high; actual model and effort not observable.
  Started from retained branch e36efc7; canonical main f5df4b6. One bounded
  ordinary streaming GET at 20:21:47 UTC to FF03's recorded Wikimedia upload
  URL returned HTTP 403, `text/plain`, without Retry-After. No retries, bypass,
  or download. This does not establish whether other sources are accessible.
- Renew the hold until at least 21:21:47 UTC (03:21:47 Dhaka Oct 28).
  Evidence is in `evidence/clips/S02c-20261027-2021.md` on retained branch
  c1dd330. New independently rights-cleared sources may be assessed separately.
- Fresh S02a and S02b manifest checks passed; S02c `--require-ten` failed:
  seven attributed local candidates, not ten, and usability is not established.
  No clip added, no product use or S02e approval claimed.
- Applied installed Superpowers verification-before-completion: ran fresh
  checkers and distinguished integrity from physical usability. Used normal
  Python requests and local Git; no other plugin needed for the bounded request.
  No bypass, uploads, deployment, accounts, purchases, inference or GPU.
  OpenCodex-managed; quota not polled. Tokens/subscription cost unknown; Meta
  and GPU cost $0. Silent-workflow exception: mandatory skill announcement.
- Next: after the hold, seek and verify genuinely usable licensed footage;
  S02d and final use remain gated. No owner question required.
- Canonical QUEUE/STATE/report edits are uncommitted for the orchestrator's
  serialized control maintainer; RUNS was already independently modified and
  was not regenerated or staged here. RUN_LOG awaits that maintainer.

## Authorized continuation, 2026-10-27 21:23:46–21:27 UTC — PARTIAL

- Requested CODEX-2 GPT-6.1 Terra/high; actual runtime model/effort not
  observable. Canonical main e2c0784 at start; claim 76658b4; retained branch
  c1dd330 continued in its existing isolated worktree and committed 9b4f8f8.
- Provisional local Pexels acquisition succeeded for three newly sourced,
  independently attributed clips: classroom RM04, Foucault pendulum PD02 and
  Newton cradle PD03. Coarse contact sheets and ffprobe expose potential issues:
  weak parallax, people, unknown scale/capture timebase, slow motion. No clip is
  counted as usable on contact sheets alone; PD03 sheet covers first 16 s only.
  Licence, source links, metadata, hashes and open rights questions are in
  `evidence/clips/S02c-alternate-sources.md` and acquisition receipt on branch.
  Three Pexels downloads returned 200; one new, separately sourced Wikimedia
  pendulum original returned 403. No FF03 retry or access bypass. Working Pexels
  demonstrates the previous Wikimedia error is not a general network block.
- `python evidence/clips/check_s02a_manifest.py` and `check_s02b_manifest.py`
  pass; `check_s02c_acquisition.py` verifies ten local hashes/attribution;
  `--require-ten` now correctly fails 0/10 individually usability-verified
  despite ten candidates. Added explicit proof/evidence gate to prevent a
  candidate-count false positive. `git diff --cached --check` passed. No full
  physical playback/measurement, owner approval, Gate R/M or public use claimed.
- S02c remains PARTIAL rather than BLOCKED because a normal alternate route
  made concrete acquisition progress. Next: full segment/trackability and
  capture-timebase review, independent scale, new actual physics clips and
  moving-camera scenes; resolve Pexels raw-file public-repository rights and
  depicted rights. S02d and S02e remain gated; no owner question needed now.
- Applied installed Superpowers systematic-debugging (separate source-page,
  CDN/access and physical-usability evidence; normal alternate hypothesis) and
  verification-before-completion (fresh checks, no candidate-as-usable claim).
  Used web source research, ordinary requests, ffprobe/ffmpeg, contact-sheet
  visual inspection and Git. No native control requested. OpenCodex-managed;
  quota not polled. Tokens/subscription cost unknown; Meta/inference/GPU $0.
  No upload, publication, deployment, purchase or change to access policies.
  Communication: silent default except mandatory brief progress and skill
  announcements; final worker signal only. Existing unrelated work preserved.

## Authorized continuation, 2026-10-27 21:31:53–21:35 UTC — PARTIAL

- Requested CODEX-2 Terra/high; actual runtime model/effort and tokens/coding
  cost unavailable. Started main cc23753, reused retained worktree at 9b4f8f8;
  claim d6df3f9, new unmerged evidence commit 34728e3. No merge or product edit.
- Full-duration sampled contact sheets generated for all ten; all sheets viewed
  for RM04, PD02, PD03, BN02, selected sheets for remaining six. **Not full
  frame playback or proven tracking**: no new individually verified clips.
  Evidence per ID and reproducible commands: `.worktrees/S02c/evidence/clips/S02c-20261027-continuation-review.md`.
  RM04 shows relative foreground/background motion, not proven translation;
  PD02 is a promising visible-bob lead; PD03 cradle has an unknown slow-motion
  factor. BN02 end card's CC BY 4.0 differs from Commons manifest CC BY-SA 4.0;
  reconcile before use. No measurements invented, S02d calibration not repeated.
- S02a/S02b manifest checks passed; acquisition `--require-ten` integrity
  passed for ten but exited 1: 0/10 individually usability-verified. `git diff
  --cached --check` passed on evidence. Ten candidates are not success.
- Search found existing RM02 listing as a possible tracking-shot lead and an
  unvetted Commons cup-drop lead; neither was acquired or treated as verified.
  No 403/429 source retried, no new download, upload, deployment, publication,
  approval, account, purchase, inference or GPU. Q2 local-only; S02e remains.
- Superpowers `verification-before-completion` applied to distinguish hash
  integrity from usability; web search, ffmpeg and image inspection actually
  used. No native control or deployment plugin relevant. OpenCodex-managed;
  not polled; new Meta/inference/GPU calls $0. Silent-workflow exception:
  mandatory initial progress update. Final signal only. Concurrent orchestrator
  state edits left untouched. No owner question required.
- Next: view full continuous segments at original fidelity and test tracking;
  seek independent real fall/bounce/projectile and genuine room parallax;
  investigate rights/timebase/scale as separately scoped. Retain branch.

## Same-run correction handoff — 2026-10-27 21:56 UTC

Stopped new work on Koushik's Opus 5.5/medium override. Prior requested route
was CODEX-2 Terra/high; actual runtime identity/effort unobservable. Next turn
requested CODEX-2 Opus 5.5/medium, not a lane reassignment. Original run start
21:31:53 UTC, no new implementation after 21:56:53, stop 22:01:53 UTC.

Retained clean worktree `.worktrees/S02c`, branch `run/S02c` commit `3361a27`;
no merge. Detailed reproducible evidence:
`.worktrees/S02c/evidence/clips/S02c-frame-evidence.md` and per-frame CSV.
PD02: all 439 original frames processed, every target crop viewed; approximate
2-D bob track, not calibrated physics. RM04: all 231 original frames processed,
half-resolution feature flow, table/board relative residual consistent with
parallax but not proof of translation/reconstruction. Two scoped local visual
usability flags, not broad physics or approved public use. RM02: one ordinary
Pexels GET200, 12,422,117 bytes, complete decode and attribution receipt; only
coarse/still inspection, not verified. Pexels distribution and third-party
rights, scale, capture timebase and S02e owner approval remain open.

Fresh S02a/S02b checks passed; acquisition integrity 11 attributed hashes passed,
`--require-ten` failed **2/10 narrowly verified**. `git diff --cached --check`
passed before branch commit. Superpowers verification-before-completion and
systematic-debugging applied to per-frame evidence and narrowed claims. OpenCV,
ffmpeg/ffprobe, web source metadata and Git used; no quota polling, new Meta or
GPU calls, uploads or publication. Mandatory initial progress update was the
only communication exception. Canonical QUEUE/status and orchestrator checkpoint
are controller-owned during override and intentionally not edited here. Earlier
21:35 handoff was premature and superseded by this correction.


## Authorized continuation, 2026-10-27 22:00:42–22:10:25 UTC — PARTIAL

- Requested: CODEX-2 ownership, owner override Opus 5.5/medium. Actual runtime
  model/effort not observable. Main 87e279c at start; retained worktree
  `.worktrees/S02c` continued from 3361a27; commits f4cc06a, 54460a5 on
  `run/S02c` (unmerged).
- Evidence (`evidence/clips/S02c-frame-evidence-v3.md`, scripts
  `s02c_v3_analysis.py`, `s02c_rm02_flow.py`; derived files local in
  `%TEMP%/s02c-v3/`, not committed):
  - PJ01: all 3635 frames decoded; live rocket motion only ~frames 456–491
    (15.2–16.4 s), object ~3–15 px; not a usable tracked trajectory. Overlay
    metre coordinates are creator-authored.
  - BN02: all 2029 frames decoded; ball top cropped throughout, apex out of
    frame; green mask contaminated by floor lighting. Not usable for
    height/restitution; 240 fps is a source claim.
  - AP15: drop segment not located in 1 fps overview or 4 fps 28–50 s sheet;
    unresolved.
  - RM02: LK flow on all 426 frames (half-res): median 228 tracked features
    (min 137), median dx ≈3.0 px/frame, dy ≈−0.17; single homography inlier
    ratio median 0.92 (2 frames <0.6). Mostly planar/pan-consistent motion;
    camera translation/parallax **not** established. No scale/timebase.
  - FFmpeg scene-score >0.3: no cuts in AP15, BN02, PJ01.
- Checks: `check_s02c_acquisition.py --require-ten` exit 1 (2/10 verified,
  11 local candidates, integrity PASS); S02a/S02b manifest checks pass.
- Unverified source leads (search summaries only; no page/licence read by me,
  no download): Commons NUSTEM "Finding a value for g using a free fall
  method" (reported CC BY 3.0), "Zeitsymmetrie (freier Fall)", "Time ball drop
  only", "Ballistische Kurve" (reported CC BY-SA 4.0). Sports leads named in an
  earlier chat reply are excluded by hard boundaries and were not acquired.
- Skills: no SKILL.md read or applied this window (not evidenced). Tools used:
  local shell, ffmpeg/ffprobe, OpenCV, image view, web search.
- Corrections: v3 evidence heading previously stated "22:00–22:20 UTC", an
  unobserved future end; corrected to recorded start, end not recorded.
- Communication noncompliance: the first handoff was a long chat-only summary
  with REPORT/controls left stale, and a later chat reply repeated this; both
  violate the silent workflow. Canonical QUEUE/STATE/RUN_LOG left to the
  controller per its instruction; this REPORT edit is uncommitted on main.
- No uploads, acquisitions, calibration, gate or approval claims; no secrets;
  coding quota OpenCodex-managed, not polled. Tokens/cost unknown; Meta/GPU $0.
- Blocker: no individually verified real fall/bounce/projectile clip. Unblock:
  confirm rights on a non-sports educational source page and obtain it via an
  ordinary unbypassed fetch, then full-rate frame review.
## Verification correction, 2026-10-27 22:12:19–22:12:26 UTC

- Read at 22:12 UTC: `Run-System/SKILLS_AND_PLUGINS.md` and Superpowers
  `C:/Users/HP/.codex/plugins/cache/openai-curated-remote/superpowers/7.0.1/skills/verification-before-completion/SKILL.md`.
  First used in this correction only. This does not make earlier work in this run compliant.
- Applied the gate (identify, run, read exit, then state): fresh run in the retained worktree at 54460a5:
  - `python evidence/clips/check_s02a_manifest.py`: exit 0, PASS (4 fall candidates / 3 groups + Apollo 15); NOT VERIFIED calibration/playback/approval/Gate M.
  - `python evidence/clips/check_s02b_manifest.py`: exit 0, PASS (3 motion + 3 room candidates); NOT VERIFIED playback/rights/calibration/approval.
  - `python evidence/clips/check_s02c_acquisition.py --require-ten`: **exit 1**. Integrity PASS for 11 local files, but only 2 of 10 required clips are individually checked as usable.
- Conclusion supported by that output: S02c acceptance is not met, so the status stays PARTIAL. No success, gate or approval claim.

## Medium-turn stop handoff, 2026-10-27 22:15:07–22:16 UTC — PARTIAL

- Requested Opus 5.5/medium (CODEX-2 ownership); actual runtime model/effort unobservable.
  Superseded mid-preflight by Koushik's Opus 5.5 HIGH instruction; new work stopped per that instruction.
- Done this turn: read-only preflight only. Main 6299bc8; retained worktree `.worktrees/S02c`
  clean at 54460a5 (`run/S02c`, unmerged). Read PLAN, this REPORT, STATE S02c rows, clips.csv,
  evidence list, `Run-System/SKILLS_AND_PLUGINS.md`, Superpowers `verification-before-completion`.
  No download, source vetting, evidence edit, commit, merge, upload or control-file edit.
- Status unchanged from 22:12 fresh check: `--require-ten` exit 1, 2/10 narrowly verified (PD02, RM04);
  not re-run this turn. No new usability/rights/calibration claim.
- Next (HIGH turn): read actual Commons file pages/extmetadata licence for new non-sports leads
  (NUSTEM "Finding a value for g using a free fall method", "Time ball drop only", "Ballistische Kurve",
  FF03 "Zeitsymmetrie (freier Fall)"), ordinary GET only, then full-rate original-frame review;
  also seek genuine moving-camera room scenes. Do not repeat PJ01/BN02/AP15/RM02 conclusions.
- Quota OpenCodex-managed, not polled; tokens/cost unknown; Meta/GPU $0. Communication: silent; final line only.

## Opus 5.5 HIGH continuation, 2026-10-27 22:16:37–22:44 UTC — PARTIAL (7/10)

- Requested Opus 5.5 high, CODEX-2 ownership; runtime model/effort unobservable. Worktree `.worktrees/S02c`,
  branch `run/S02c` 54460a5 → **8c6e486** (4787c12 evidence, 8c6e486 whitespace). Not merged. Main at start c236d57.
- Plan (this window): vet NEW non-sports Commons/NASA sources from actual metadata, ordinary GET, full-decode
  original-frame review, narrow usability flags; no repeat of PJ01/BN02/AP15 reviews.
- Result: `check_s02c_acquisition.py --require-ten` **exit 1, 7/10** verified (was 2): PD02, RM04 (unchanged),
  **PD04** (Commons MikeRun blocked pendulum, all 600 frames template-tracked), **PD06** (Commons UTexas Foucault,
  280 frames), **PD03** (Pexels Newton cradle, 1793 frames blob-tracked, 48 crops inspected), **RM05** (NASA ISS
  float-through, 60–90 s full rate: H inlier 0.48 vs F 0.96 at 10-frame baseline), **RM02** (new 10-frame-baseline
  flow: H 0.45 vs F 0.86). Scope = image-space tracking / parallax-consistent motion only.
- Rejected after full-decode review (moved to `%TEMP%/s02c-rejected/`, hashes in evidence): FF04, BN03, PD08, PJ02,
  FF03, PD07, PD05, FF05, RM06. PJ03 Ballistische Kurve downloaded but review killed (memory) — open.
  PD01/BN01 triaged, not usable as is.
- Rights finding: Rhetos Commons uploads carry a Mathe-AC Lernwerkstatt Aachen CC BY 4.0 end card vs Commons
  CC BY-SA 4.0/Rhetos; credit both (S02d/S02e).
- Access: Commons upload 429 (PD09 twice, Retry-After 600) then API 429; stopped, no bypass/churn.
- Evidence: `evidence/clips/S02c-opus-frame-evidence.md` (table, metrics, hashes, unfetched leads), track/flow CSVs,
  crop sheets, `S02c-opus-commons-metadata.json`, NASA metadata JSONs, download log.
- Checks (fresh, 22:38–22:43): s02a/s02b manifest exit 0; acquisition integrity PASS 14 files; --require-ten exit 1;
  ffmpeg full decode exit 0 for PD04, PD06, RM05; `git diff --cached --check` exit 0 after trim; ast syntax OK.
- **Skills/plugins:** Superpowers `verification-before-completion` (read 22:17; applied: every count above from a
  fresh command exit). Ponytail `C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.2/skills/ponytail/SKILL.md`
  read **22:42, after the minute-25 implementation stop** — not applied to the implementation; no retroactive claim.
  Applied after reading: no further scripts/refactors, trivial whitespace fix only, rejected media moved not re-reviewed.
  Ponytail gaps to fix later: 5 new scripts (`s02c_opus_{review,track,blobcrops,flow,record}.py`) partly duplicate
  `s02c_frame_analysis.py`/`s02c_rm02_flow.py`/`record_s02c_acquisition.py` (those are hard-coded to PD02/RM04/RM02,
  so not directly reusable) and lack assert self-checks beyond decode-count asserts; candidates for consolidation.
- Parallel split (S02C_PARALLEL.md, received 22:42): RM05 (NASA) and RM02 room work were done before the split;
  S02c1 NASA / S02c2 ROOMS shards should not redo RM05/RM02, FF05, RM06. No shard started by me; one worker only.
- Next to reach 10: (1) review PJ03 at 480 px (file in %TEMP%/s02c-rejected, sha 8a24c5f3…); (2) after Commons
  hold clears, fetch Kugelstoßpendel TSD, "Newton's - Balls", "Pendolo di Newton" (CC0), "Model of Foucault's
  pendulum 1", PD09; reuse `s02c_opus_review.py`+`s02c_opus_track.py`; (3) shards for NASA drop / Pexels rooms.
  Earth fall/projectile/bounce still has **zero** verified clips — a coverage gap even at 10.
- Controls: STATE/QUEUE/RUN_LOG left to controller (serialized acceptance). No uploads, approvals, calibration,
  secrets, purchases. Coding quota OpenCodex-managed; not polled. Tokens/cost unknown; Meta/GPU $0.
- Communication: silent; final pointer line only.


## Opus integration round 1, 2026-10-27 23:07:44–23:22 UTC — PARTIAL (9/10)

- Requested Opus 5.5 high, CODEX-2, sole primary/integrator (orchestrator mode); runtime model/effort not observable. Retained `.worktrees/S02c`, `run/S02c` 8c6e486 → **f7a4af0** (unmerged; no canonical control edits, no main merge). Main at start 0b09677.
- Plan: per delegation + S02C_PARALLEL "Next fresh sessions" (no separate PLAN file written this round — gap noted). Mid-run controller message added pinned STOCK d6eedf5; handled inside the same timebox.
- Imports (scope inspected first: only shard-owned paths): octopus merge 8f99662 of pinned NASA 449d36e + STOCK 3bbf2dc; merge 1b6dad3 of pinned STOCK d6eedf5. Shard history/evidence preserved; no unpinned STOCK files read.
- Commits: b53111f (shard integration, PJ03 flag), b4848b4 (whitespace), a38c6c6 (ST03 flag, FF06 deferred), f7a4af0 (BN04 reject).
- Results ([evidence/clips/S02c-integration-r1.md](../../../.worktrees/S02c/evidence/clips/S02c-integration-r1.md); derived sheets/tracks in `evidence/clips/S02c-int1/`):
  - N3 (reviewed first), N1, N2: NOT counted — cable swing with unidentifiable release (N3; final descent/impact occluded by foreground tripod), ≈0.5 s post-release flight hidden by splash (N1), off-frame release ≈0.8 s fall (N2). Added to clips.csv as unapproved `swing_drop_impact` rows for rights completeness; hashes = shard.
  - **PJ03** Commons/Rhetos "Ballistische Kurve" (CC BY-SA 4.0 + Mathe-AC CC BY 4.0 end card): COUNTED narrow — real thrown paper bag, 20 fps resample of file 15–36 s on 640 px (bounded; previous whole-file attempt was killed for memory); template track holds f0–320/420 (release→apex→early descent); final descent lost to burnt-in strobe dots. Air-drag case, not vacuum g.
  - **ST03** Pexels apple drop (pinned d6eedf5): COUNTED narrow, playback-time only. Integrator pixel diff confirms the dropped rows are near-identical repeats every 6th frame (25p-in-30p; not bit-identical; one irregular gap). Capture slow motion and scale unknown; apple-size conversion ≈2.9–3.5 m/s² is assumed, so this is not g. Role: Mystery-g / timebase-abstention example.
  - FF06 (NUSTEM g lecture, CC BY 3.0) deferred: cut-heavy, no continuous drop located; BN04 (ScienceCOLA) rejected as an electrostatic pendulum. Both remain in %TEMP% only.
- Fresh checks (23:20–23:21): s02a exit 0 (5 fall candidates); s02b exit 0; `check_s02c_acquisition.py` integrity PASS 19 files; `--require-ten` **exit 1, 9/10**; recorder hash asserts for N1–N3/PJ03/ST03 passed; `git diff --cached --check` exit 0 before each commit (b53111f was committed before its check finished; b4848b4 fixed one EOF blank line).
- Coverage: Earth projectile 1 (drag-dominated), Earth free fall 1 (playback-time only), Earth bounce 0. Pexels redistribution, S02d calibration/timebase and S02e owner approval are still open.
- **Ponytail** (`C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.2/skills/ponytail/SKILL.md`, full; read 23:08 before work): no new scripts. Reused `s02c_opus_review.py`, `s02c_opus_track.py` (manual seeds), `s02c_opus_record.py` (extended with 5 NEW rows, 2 FLAGS and a per-clip evidence map), ffmpeg trim/downscale and the existing checker. The self-check was the integrity checker plus explicit hash asserts. Skipped: whole-file decodes, ST03 f144–230, FF06 segment hunt, script consolidation. Risk: ST03 and PJ03 narrow flags rest on visual crop inspection plus short tracks; the counted ten must not be read as calibrated physics.
- Concurrency: only small trimmed decodes (≤420 frames at 640 px) ran; no heavy decode was deferred. No uploads, approvals, purchases, GPU or secrets. Coding quota is OpenCodex-managed and was not polled. Tokens/cost unknown; Meta/GPU $0.
- Next: one more independently verified clip, preferably an Earth bounce, or FF06 drop-insert segment search; then the integrator can rerun `--require-ten`. Owner question: none new.
- Communication: silent; one final pointer line.

