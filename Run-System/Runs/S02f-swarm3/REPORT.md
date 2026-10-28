# S02f-swarm3 DONE — primary-source replacement recovery

## Result

Completed a targeted primary-source search and falsification pass. **No new approval-ready Earth free-fall candidate** was found. The strongest new lead, NASA Glenn/CWRU drop-tower material, has declared tower dimensions and camera cadence but measures relative motion inside a freely falling rig, not an Earth-g trajectory in a stationary camera frame. The exact unmet facts and safe next route are recorded in `evidence/clips/calibration-recovery/S02f/swarm3/RESEARCH.md`.

This is a local child research result only. It does not pass S07a, approve an input, establish a metric, or change Gate M.

## Evidence written

- `evidence/clips/calibration-recovery/S02f/swarm3/RESEARCH.md`: source-backed table covering metric scale, clock, trajectory, rights, and independence; explicit FPS/known-size falsifications.
- `evidence/clips/calibration-recovery/S02f/swarm3/candidates.json`: machine-readable 0-qualified result and dispositions.
- `evidence/clips/calibration-recovery/S02f/swarm3/SOURCES.md`: primary-source URLs and scope notes.
- `Run-System/Runs/S02f-swarm3/HANDOUT.md`, `PLAN.md`, `TIMEBOX.json`: exact handout and timebox custody.

## Fresh checks

| Check | Result |
|---|---|
| Public primary-source reads | NASA Glenn drop-tower pages, NASA NTRS paper, NASA Science Apollo source, UAA physics page, NASA media guidance, and Pexels/Pixabay result pages inspected. |
| JSON parse | `candidates.json` and `TIMEBOX.json` parse successfully with PowerShell `ConvertFrom-Json`. |
| Evidence consistency | `rg` confirmed declared 30 fps, apparatus dimensions, edited-video limitation, disallowed CC BY-NC-SA, and Earth-g rejection text. |
| Git hygiene | `git diff --check` PASS; only owned evidence and run files are untracked/staged for this commit. No shared controls, CSV, media, credentials, or product code changed. |

## Ponytail full application

- Reused the existing S02f evidence shape and did not add a downloader, schema, dependency, media fixture, or abstraction.
- Chose a compact source table plus JSON because the acceptance needs auditable claims and machine-readable dispositions.
- Skipped generic stock hunting, asset downloads, frame extraction, and duplicate Wikimedia audits because they could not repair the missing scale/clock/trajectory/rights intersection within this objective.

## Limits / next action

Search coverage is targeted, not exhaustive. NASA generic media guidance was not treated as asset-level clearance for participant footage. A declared delivery FPS is not proof of an uncut source clock; tower height and known bead size are not image-plane calibration. No footage was downloaded or uploaded, no paid/model job ran, and no approvals or parent controls were edited.

The safe next route is a rights-cleared original participant file with raw-frame/camera receipts, followed by a check that the camera is independently stationary relative to the Earth-g trajectory. If the camera falls with the object, retain the rejection. This proposes no outreach/acquisition authority. Accepted S07f still leads with virtual lab/Mystery-g simulated-only; only calibrated table-plane Measure is UNAVAILABLE. Physical Gate M/S12 remain unmet, not the simulated-lab lead.

## Controller acceptance corrections

Original administrative close was withdrawn; original deadline remains 17:31:19Z. Only the three requested inaccuracies were corrected; no new candidate research or authority expansion:

1. UAA rights rejection is **NC only**, not SA. CC BY-SA is allowed. Matching machine-readable reason added.
2. Removed the blanket small-sample-fallback lock; read and cited owning S07f DECISION and CONTROLLER_ACCEPTANCE, preserving simulated-only lead versus unavailable table-plane Measure.
3. Reopened the NTRS paper (not footage); added printed/PDF page, section/paragraph, exact short snippets and extraction locations for rate/edit claims in SOURCES.md. Source's 30 fps versus 1080/60p wording remains unresolved, not a verified frame clock.

Ponytail correction choice: edited existing Markdown/JSON only; reused stdlib assertions and the existing timebox checker. No new downloader, test framework or dependency. Initial receipt timestamps remain historical; resumed completion is recorded separately in TIMEBOX.json. The prior extra chat summary broke the required one-line handoff format; final response corrects that, rather than claiming perfect communication compliance.

Fresh correction checks (2026-10-28 17:22 UTC): stdlib assertions PASS for all owned files' C0 scan, both JSON roundtrips, removal of NC/SA and blanket fallback-lock wording, presence of corrected NC-only and simulated-only/UNAVAILABLE distinction, both local source links resolving, and unchanged 0-qualified/approval-false/physical-gate-false output. Existing `worker_timebox.py check` PASS; `git diff --check` PASS. NTRS primary-text recheck supports both short snippets at printed page4. No broad test suite or actual video/measurement check was run.

## Run metadata

- RID: `S02f-swarm3`
- Requested lane: CODEX-2 S02f recovery child; backend/effort and monetary cost are not independently observable. OpenCodex-managed; not polled.
- Issued: `2026-10-28T17:01:19Z`
- Initial receipt: `2026-10-28T17:08:30Z`, returned for correction; administrative close withdrawn. Resumed first observed tool time: `2026-10-28T17:17:27Z`. Final timestamps in TIMEBOX.json, unchanged original deadline.
- Absolute deadline: `2026-10-28T17:31:19Z` (`2026-10-28T23:31:19+06:00` Dhaka)
- Minute-25 cutoff: `2026-10-28T17:26:19Z`
- Worktree: `C:\Users\HP\.codex\worktrees\swarm-s02f-calibration\2026-10-26 - Meta Global AI Developer Hackathon`
- Communication: silent-by-default complied with; no other-chat message sent. Final controller line is the required handoff.
