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

