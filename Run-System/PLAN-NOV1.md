# PLAN-NOV1: live product pivot (owner GO, Nov 1 2026 ~16:30 Dhaka)

Goal: a real SaaS-feeling product. Signed-in users upload their own videos; the system processes them live.
Freeze Nov 4 10:00 Dhaka; stop-work Nov 4 18:00. Owner records a new voice-over and makes the final video himself.

## User flow
1. Sign up (Clerk). First-run screen: choose agent mode Standard or Contributor (Muse Spark 1.3 contributor:
   much cheaper, Meta may train on prompts and completions; show pros and cons; default Standard; changeable later).
   Every new account gets one finished sample project (recorded RM04 lab + OWN05 experiment, labelled SAMPLE).
2. New project: the agent asks "What are you uploading?" with options: Room video (build a virtual lab) or
   My experiment (measure it). It then shows filming instructions for that mode (duration, motion, light,
   reference object such as an A4 sheet).
3. Upload (any video; mp4/mov/webm; <= 200 MB, <= 120 s) into the user's storage (1 GB, 20 uploads/day).
   Files panel: list, preview, download, delete; available on any device.
4. Mode A, Room: live reconstruction (MapAnything on Modal, on demand) -> 3D room with floor and gravity
   direction; scale from the reference object (MEASURED) or MODEL-ESTIMATED with uncertainty. Then the lab
   editor: add ball, block, ramp, pendulum, spring, flywheel; move, rotate, resize; or ask the agent. "Run an
   experiment": the agent sets it up (asks questions with recommended options), the physics engine runs it,
   the fitter measures it, a report is written (optional Muse Image illustration).
5. Mode B, Experiment: user clicks the moving object on the first frame (or names it); hosted SAM 3.1 tracks it
   (Meta Model API; Modal SAM 3.1 as backup) -> scale (known size or MODEL-ESTIMATED) -> fitter (free fall,
   projectile, pendulum, incline; stretch: agent-proposed equation fitted in a sandbox, e.g. flywheel)
   -> result with uncertainty and the held-out prediction check -> 3D replay -> "Redo with changes" opens it
   as a virtual lab.
6. Agent sidebar everywhere: Muse Spark 1.3 with tools only, physics-only system prompt (polite refusal off
   topic, injection-resistant: tool allowlist, no free code execution), voice input (muse-voice-transcribe-1.0).
7. GPU status dot in the private workspace: red sleeping, yellow starting, green running; queue position.

## Architecture (smallest that works)
- Storage: Railway volume on the API service + SQLite metadata (files, projects, quotas, spend ledger).
- Meta Model API (MODEL_API_KEY, https://api.meta.ai/v1): sam-3.1 ($0.20 per 1k video frames), muse-spark-1.3
  (+ -contributor), muse-image-1.0, muse-voice-transcribe-1.0 ($0.18/h). Muse Wonder is a reasoning model, not video gen.
- Modal (existing Build/gpu, Build/reconstruction, Build/measurement/runtime/modal_track.py): deployed app,
  scale to zero after 900 s idle, max one container, our job queue; web endpoint with a shared secret.
- Spend guard: SQLite ledger checked before every paid call; global $10/day ($20/day Nov 5 to 8).
- Web: existing Next.js workspace shell (left sidebar, centre, agent panel). Lab editor: existing three.js viewer
  + TransformControls + Rapier (@dimforge/rapier3d-compat, allowed new dependency).

## Rows (QUEUE section "Nov 1 pivot")
Wave 1 (parallel now): N01 Meta API probe + hosted SAM 3.1 test; N02 ST03 full tracking on a large GPU;
N03 storage/files/quotas; N04 Modal on-demand reconstruction service + GPU status; N05 agent core; N10 lab editor.
Wave 2: N07 Mode B live pipeline; N08 Mode A live pipeline; N09 workspace UI (mode chooser, agent chat, voice,
status dot, contributor screen); N11 sample project + DEV infra; N12 experiments in the lab + report.
Wave 3: N13 end-to-end QA; stretch N14 SAM 3D Objects, N15 agent-proposed equations, N16 share challenge;
N17 new demo script + read sheet for the owner's voice-over; N18 freeze + judging deploy (needs S23a).
Owner: N06 film new clips (guide: media/owner-clips/FILMING_GUIDE.md).


## Owner decisions (Nov 1, binding for every row)
- Users upload their OWN videos; no approved-list gate in the private workspace. Two modes: Room -> virtual lab; My experiment -> measure.
- No fixed experiment dictionary: the agent handles any physics experiment it can within the tool allowlist; off-topic requests refused.
- Live processing is the product (no replay-only). Hosted Meta SAM 3.1 = default tracker; Modal GPU = backup and room reconstruction.
- Modal on demand: wakes on a job, sleeps after 15 idle min, one GPU + simple queue with position; red/yellow/green dot in private workspace only.
- Paid-call cap: $10/day global; $20/day Thu Nov 5 to Sun Nov 8 (Dhaka). Low-cost GPU/API work needs no owner ask (credits expire at event end).
- Sign-up open to anyone; per user 20 uploads/day, 1 GB storage, file manager (upload, preview, download, delete), any device.
- Contributor mode asked at account creation with pros (much cheaper Muse Spark 1.3 contributor) and cons (Meta trains on prompts); changeable.
- Agent: Muse Spark 1.3, physics-only, ask-back questions with recommended options; voice typing via muse-voice-transcribe-1.0.
- Muse Image: lab-report illustrations; image -> SAM 3.1 cut-out -> 3D object (stretch). SAM 3D Objects room object -> lab object (stretch).
- Sample project on every new account. "Guess the Gravity" share challenge. Imperfect clips are fine with clear caveats and uncertainty.
- Licensing: any licence permitting reuse; never no-licence, YouTube, NC or ND. Owner and user footage fine (owner clips private except OWN07 snippets).
- Final demo video (owner correction Nov 1 ~17:20): Koushik records the voice-overs (N18, click to click); Claude Code (local CLI)
  records the screen captures and edits the video (N20: trims, loudness, music, zooms, captions). Agents also supply script + read sheet (N17).
- Earlier UI decisions stay (collapsible icon rail with hover-temporary panes, top-right tools button, dark mode + colour modes,
  pendulum logo with wordmark, scroll-craft homepage, GitHub button, no em dashes, myfront + make-interfaces-feel-better, Mobbin refs).
- Run system: save quota; lean WORKER_CONTRACT.md; 30 or 60 min runs; cross-vendor review only for security/spend code.

## Owner away rule (Nov 1 ~17:10 Dhaka)
Koushik is away. Continue all work and dispatch new rows of this plan. Anything that genuinely needs his supervision
(new spend beyond the caps above, judging/production deploy, public posts or submission, account/billing/terms changes,
publishing private clips, destructive actions, or a product-direction choice not covered here) is PAUSED, not guessed:
write it under "Reviews for Koushik" (STATE Owner questions -> RUNS.md) and keep working on everything else.
## Owner decisions (Nov 2, binding)
- GPU for room rebuild (MapAnything): L4 (measured peak 7.78 GB on 8 frames at 518x392 bf16, fits 24 GB); A10G kept as fallback.
- Clicked room objects: Stable Fast 3D (stabilityai/stable-fast-3d) on its own on-demand Modal L4 function: SAM 3.1 crop -> textured 3D model.
  The measured box stays for physics and collisions; the SF3D model is drawn on top, labelled "MODEL-GENERATED shape" plus "Powered by Stability AI".
  On failure keep the box and show the reason. Every job ledgered under the daily GPU cap; scale to zero when idle. Replaces the blocked SAM 3D Objects path.
- Licence: Stability AI Community License accepted and registered by Koushik; receipt and duties in evidence/owner/S06/SF3D-LICENCE.md.
- Lab apparatus: add a flywheel and a standard physics-lab kit (controller chooses the set).
- GPU queue: a crashed job must free the queue in minutes, not 30.
- Agent models: user picks a tier. Contributor: Muse Spark 1.3 contributor (cheapest). Standard: Muse Open (Baseten) or Muse Spark 1.3
  standard, user-selectable. GPT-6.1 Sol (Merge gateway, MERGE_API_KEY, $20 credit) is never user-selectable: it is a hidden fallback
  only for the turn that failed on a Meta model. Spend code: cross-vendor review required.
- Region: N23 showed Meta API returns 0 models from Railway egress in both SG and US, so the Modal relay stays. Move Postgres/Redis to the
  US region next to the api, safely (backup, restore, verify, keep SG until verified).
- Demo video: Koushik makes it himself after the product is built (N20 is his row now).
- N36 fallback rule (Koushik, Nov 2): GPT-6.1 Sol fires for any of these failures on a Meta model: an API error or timeout, a reply
  with no usable tool call, or the number guard blocking the answer twice. It does not fire for off-topic refusals, cap or quota limits,
  or bad user input. Sol answers only that failed turn, under the same physics-only prompt and number guard. Sol limit $2/day.
- Virtual lab is a simplified room, not a carbon copy (Koushik, Nov 2): keep the main elements (floor, walls, tables, chairs, balls,
  ramps, pendulums and other lab-relevant objects); drop personal items and clutter. The system/agent picks the elements automatically
  (detect -> keep lab-relevant -> box for physics + SF3D shape on top); collisions come from the kept elements plus floor and walls.
  The raw point cloud is at most an optional faint backdrop.
- 3D objects are real lab objects (Koushik, Nov 2, replaces "box for physics + SF3D on top"): the SF3D mesh is the object's physics
  shape too. Size and position come from the measured box (SF3D output is unit-scale); the mesh is decimated to average detail
  (about 1 to 3k triangles) and used as a Rapier trimesh collider for static room objects (table, chair) and a convex hull for movable
  ones; mass and friction from the object category, labelled MODEL-ESTIMATED. The measured box is only the fallback when SF3D fails
  (reason shown). Label "MODEL-GENERATED shape" + "Powered by Stability AI" stays.
- Room lab content (Koushik, Nov 2, with N06_room.mp4): the room becomes a simple lab shell: floor, walls, windows, doors, and the
  main furniture (tables, chairs, sofa, shelves) with average detail and real measurements; nothing else. Personal items and clutter
  are dropped. Physics equipment is not expected in home rooms: users add it with the editor or the agent from the standard lab kit
  (N33). N39 must not try to detect equipment in the clip; windows and doors are wall features.
- Dispatch freeze lifted by Koushik ("Go", Nov 2). To save Koushik's Claude quota for study, infra rows N30, N34, N38 run on GPT-6.1 Sol.
