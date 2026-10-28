# S02c1 REPORT — NASA real Earth drop/trajectory shard

Status: **PARTIAL** (bounded shard investigation complete; 3 provisional narrow NASA Earth candidates, 0 calibrated/gate-ready; not S02c success).

- Lane CODEX-2; orchestrator-assigned Opus 5.5 / high (runtime model/effort not independently observable). UTC start 2026-10-27T22:46:36Z, end ~22:56Z.
- Worktree `.worktrees/S02c1`, branch `run/S02c1` from retained 8c6e486. Not merged; no clips.csv, canonical controls or parent edits.
- Tokens/cost: unknown; coding quota OpenCodex-managed, not polled. Meta/GPU/AWS spend $0. No uploads, secrets, GPU.

## Result

| ID | NASA source (all LaRC, NASA-produced) | Best segment (file s) | Verdict |
|---|---|---|---|
| N3 | 2022-H1_V_Lift&CruiseDropTest-5 (eVTOL fuselage) | 62.70–72.80 wide fixed shot, descent+ground impact 66.8–70.3 every frame | best; object visible throughout |
| N1 | ORION10ftSwingDrop_Documentation (Orion test article into Hydro Impact Basin) | 68.87–85.90 wide fixed shot; swing/descent/splash 72–77.3 every frame | low contrast near tree line; splash occludes entry |
| N2 | LRC-2025 RVLT Gantry Drop Test (air-taxi fuselage) | 87.30–99.20; fall ~91.6–92.6 (~30 frames) then impact/tumble | short fall |
| AP15 | Apollo 15 (primary's file) | no better NASA original in Images API; drop still not located at 720×480 | UNRESOLVED |

Details, hashes, URLs, credits, limitations: [candidates.csv](candidates.csv). Rights read **before** download from each item's NASA `metadata.json` (saved as N1/N2/N3-metadata.json): NASA centre/photographer credits, SecondaryCreator empty, no third-party copyright note; N2 XMP UsageTerms "Released to the Public". Treated as PD-USGov-NASA under NASA media guidelines; no endorsement; people visible.

Key physics limitations (apply to all three): LandIR swing tests are cable-constrained pendulum swings with release at an unidentified frame, so the free-flight part may be short; edited multi-cut documentaries (20–27 scene cuts), file 30/1 vs master 29.97 and possible speed edits → timebase UNVERIFIED; no verified object/height/grid-cell dimensions; impacts are crash/deformation or water splash, not rigid bounces. No calibrated measurement, fit or gate claim. Downloaded `~medium` 1280×720 renditions; 1080p/4K `~orig` exist if integrator needs resolution.

## Commands / checks (fresh)
- images-api.nasa.gov search (video): drop test, water impact, Hydro Impact Basin, drop, bounce, Apollo 15, crash test, parachute, landing test, hammer feather → picked real test-documentation items; animations/ISS/launch/parachute coverage skipped.
- asset + metadata.json per item (HTTP OK); `Invoke-WebRequest` ~medium.mp4 ×3 → HTTP 200; ffprobe (wh/fps/frames/duration); SHA-256; ffmpeg scene>0.3 cut lists; 1 fps sheets; every-frame strips of the motion windows; viewed all sheets.
- Duplicate check: rg for the three nasa_ids and hashes outside shard dir → none; not RM05/FF05/RM06.
- candidates.csv parses: 5 rows × 22 columns.

## Ponytail (actual)
Read and applied `C:/Users/HP/.codex/plugins/cache/workspace-directory/ponytail/5.3.2/skills/ponytail/SKILL.md` (full) before work. Reuse: ffmpeg/ffprobe and existing evidence conventions (contact sheets, scene cuts, hashes, clips.csv-like columns); NASA API/metadata as used by primary for RM05. No new scripts/dependencies, so no self-check needed. Skipped: template tracking (existing `s02c_opus_track.py` loads whole clip at 960 px ≈ 6 GB for 4k frames; would need trimmed temp segments) — integrator may run it on N3 62.7–72.8. Deleted one uninformative own AP15 crop. Risks: committed ~140 MB media following the tracked test-data/public pattern (455 MB already); swing-release ≠ free fall; timebase unverified.

## Next / questions
- Integrator (S02c primary): review N3 first, then N1/N2; decide whether pendulum-plus-release trajectories count as "usable"; if so, add clips.csv rows with NASA credit; S02d timebase/scale; S02e owner final-use approval.
- Owner question: none new.

Communication compliance: no chat narration beyond tool use; no messages to other chats; final one status line.
