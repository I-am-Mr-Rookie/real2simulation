# S05 reconstruction spike boundary

S05a supplies **contracts and licence evidence only**, not a working reconstructor.
Read `evidence/S05/LICENSE_REVIEW.md` before installing any upstream package.

Primary candidate: `facebook/map-anything-apache`, pinned in
`evidence/S05/upstream/revisions.json`. The ordinary `facebook/map-anything`
checkpoint and its default quick-start are NC, so do not use those defaults.
Use the explicit Apache model ID/revision; do not fetch optional external-model
extras or checkpoints without reviewing their own dependencies and licences.

Output: `contracts/scene/scene.schema.json` v1.0.0, starting with points and primitive
box colliders. The upstream point maps, depths, camera calibration/poses must be
converted into the documented world convention. Keep unknown scale/gravity unknown.
This README deliberately contains no auto-downloader or model-loading stub.

SAM 3D Objects is optional and **blocked pending owner approval/acceptance and
gated weight access**, not covered by the Apache decision. If unavailable, retain
MapAnything points/primitive meshes; later Gate R can choose the planned plane/box
fallback. No change to Gate R thresholds has been approved.

S05b additionally requires **S02 DONE**, including owner-approved licensed clips.
No downloads of footage, inference, GPU, AWS, Modal or deployment occurred in S05a.
Later runtime/VRAM claims require actual measurements; published examples are not
our performance evidence. Recheck container dependency licences before S06.

S05b: `evidence/S05/S05b/PROBE.md` and `input.json` retain four real RM02 frames
locally/gitignored. Standing GPU/private-transfer permission is answered in
`evidence/owner/S05/GPU-AUTHORIZATION.md`; no repeated permission question.
The authorized remote attempt failed dependency resolution BEFORE inference;
`evidence/S05/S05b/gpu-attempt.txt` records it, and app/container stop is verified.
`modal_rm02.py` is a one-shot private probe, not a deployed service. Its corrected
Linux/Python3.11 requirements resolve locally but are NOT remotely runtime-tested.
Before a separately scheduled continuation, read current controls, reconcile the
$0.95 reservation/headroom, and retain all one-job/resource/rights safeguards.
No model output, measured VRAM/runtime, calibrated scale or Gate R pass exists.

Latest continuation pins torchaudio2.8.0 to the official torch2.8.0/vision0.23.0
binary family; configuration regression passes, installed imports remain unverified.
Current billing UI verification hit a native browser-URL safety stop; no CPU/GPU
job launched. Restore a supported verifiable surface in a fresh session, not a
guard bypass; retain the previous$0.95 reservation until exact reconciliation.

### Latest S05b recovery5 (Oct28)

Trusted controller billing receipt restored the supported prerequisite. Actual
installed CPU imports now PASS: Torch2.8.0/vision0.23.0/audio2.8.0, NumPy2.2.6,
MapAnything1.1.4; CPU app stopped. One subsequent L4 RPC remained pending with
no container/allocation log observed; stopped to preserve the session timebox,
both apps stopped/tasks0 and containers[]. No inference/output/VRAM/Gate R result.
See `Run-System/Runs/S05b/recovery5/REPORT.md` and recovery5 evidence. Runners now
isolate receipts/results into recovery5 (manifest stays historical input.json),
verify recovered approved frames there, and explicitly stop apps on all outcomes.
Full$2.85 retained reserves pending exact billing. Do not repeat CPU installs,
ask renewed consent or infer a model-compatibility/capacity diagnosis from waiting;
controller decides any separately authorized scheduling follow-up. S05c stays locked.

### Recovery7: LOCAL-ONLY caller deadline guard (not remotely verified)

`rm02_deadline.py` replaces the unbounded `remote()` wait with one `spawn()` and
one bounded result retrieval. Its monotonic **1200s total** starts before
`app.run()` setup. It reserves 90s startup + 900s execution + 60s cleanup before
admission: setup/enqueue and observation of a running input must finish within
the first 150s. No observed admission by then means stop, not a scheduler diagnosis.
A very fast completed result is also accepted; a missed running-input snapshot
can conservatively reject a healthy job. No call-graph timing assumptions.

Queue time, setup, result retrieval, explicit stop, fresh stop verification and
context exit all consume the same caller budget. A result must arrive by 1140s;
the remaining 60s reserves up to 20s for stop acknowledgement, verification through
1190s, 5s for context exit and 5s for timer dispatch/local unwinding. Earlier
failure/success starts cleanup immediately.
Stop is attempted even when enqueue fails without returning a call ID. Unknown
setup state, stop/verification/exit failure is a **resource incident**, not success.
`deadline.json` distinguishes stop requested, acknowledged and confirmed. Confirmation
requires refreshed app state `stopped` AND function runners/running inputs/backlog
all zero. Stopping a client alone never confirms a remote stop.

The SDK's asynchronous RPCs must cooperate with asyncio cancellation; this is
local policy, **not a provider-enforced hard stop or a proven remote guarantee**.
Event-loop scheduling/cancellation can overrun a timeout; network partitions,
server lag and process death can leave remote state unknown.
Do not release reservations or retry after an incident without reconciliation.
The old 992s execution+startup+idle calculation was not an end-to-end deadline or
guaranteed billing bound. A 1200s illustrative compute-rate calculation is about
$0.340464, not current pricing, all-in cost, or proof of resource termination.
Keep the $0.95 attempt reserve and full historical $2.85 pending actual billing.

Read-only installed Modal1.6.3 source supports `App.run.aio`, `spawn.aio`,
`FunctionCall.get.aio(timeout=...)`, `App.stop.aio`, `App.info.aio(refresh=True)`
and `get_current_stats.aio`. Fake-only regressions do not verify cloud behavior.
Inputs remain the four hash-checked recovery5 RM02 frames and historical manifest;
new runtime receipts/results would be isolated under recovery7. No resources,
dependencies, revisions, retries or licence approvals changed. This local change
authorizes **no paid run**. Remote stop/runtime NOT_VERIFIED; parent S05b PARTIAL,
Gate R NOT_RUN, S05c and physical/calibration/S12 holds unchanged.
