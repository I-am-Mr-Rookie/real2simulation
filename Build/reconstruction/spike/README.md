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

### Recovery8: LOCAL-ONLY independent process watchdog

Recovery7's cooperative `asyncio.wait_for` was not a hard deadline: cancellation
can return late, and its expired clock could skip stop entirely. Recovery8 fixes
the late stop and adds `rm02_watchdog.py`, a stdlib parent process that imports
neither Modal nor the runner. **Do not execute it in this local-only run.**
Direct runner execution now refuses without the parent's per-attempt environment.
The environment check prevents accidental bypass, not a security/auth boundary.

The **1200s total** starts in the parent before client imports/setup. The child
gets at most1140s, reserving60s independently for emergency stop/verification.
Its inner budget1140 reserves90s startup +900s execution +60s cleanup: setup,
enqueue and running-input observation must finish in its first90s. Results must
arrive by1080s. This intentionally conservative admission window can reject a
healthy slow job; it does not diagnose scheduler capacity. A fast completed
result remains valid without a running snapshot. One app, one spawn, retries0.

After any late inner overshoot, stop gets a fresh20s attempt within a fresh60s
cleanup allowance; the parent1140s kill still bounds this allowance independently.
Inner `worker.json` distinguishes stop attempted/requested, dispatched (unknown
until acknowledged), acknowledged, and same-client fresh-state confirmation.
It publishes app ID during setup when observable, before `app.run()` returns.
Atomic replacement keeps an earlier complete receipt on write/replace failure.
An unknown/lost ID is an incident; never guess by name or list other apps.

After **every** child exit/kill, the parent starts separate fresh CLI processes
using the same Python/environment and the exact published `ap-` +22 alphanumeric
ID, as required by installed Modal1.6.3 (otherwise CLI treats it as a name):

```text
python -m modal app stop <exact-own-app-ID> --yes
python -m modal app info <exact-own-app-ID> --json
python -m modal container list --app-id <exact-own-app-ID> --json
```

These are source/procedure only, **not commands executed during recovery8**.
Stop has at most20s; each fresh app info/exact-app container query at most15s.
Recovery9 repeats both exact-app queries (up to1s between rounds) while the
**original** parent reserve remains, keeping2s for process kill/dispatch at the
production60s reserve. Each subprocess is killed on its timeout; polling never
restarts the reserve or repeats stop. CLI stdout/stderr use explicit UTF-8 even
on Windows. A failed stop never skips the fresh verification. Confirmation requires matching app ID,
state `stopped`, successful info/container commands and containers exactly `[]`.
Stop exit0 acknowledges the RPC; already-stopped CLI exits nonzero, so independent
confirmation can be true without claiming a dispatched/acknowledged stop RPC.
Child failure stays failure even after independently confirmed cleanup. A child
`gpu-result.json` alone is never acceptance: require parent exit0 and the matching
per-attempt independent watchdog receipt as well as the ordinary result checks.

Per-attempt unique directories under `evidence/S05/S05b/recovery8/attempt-*` hold
atomic `worker.json`/`watchdog.json`, client log and independent CLI stdout/stderr.
The parent prewrites an incident receipt before launching; broken storage blocks
admission. Later evidence failure never skips stop and never yields success.
Missing ID, failed/ambiguous verification or parent death requires operator
resource-incident reconciliation; no retry/reserve release/success claim. The
parent is independent of the child event loop, **not** an immortal supervisor or
provider-enforced remote deadline. OS stalls, parent death, network partitions,
and delayed provider state can still prevent confirmed shutdown.

Future admission (controller only, not this run): reconcile live budget/headroom
and no-paid-overage, current licensed/approved input custody, SDK1.6.3/Python3.11
availability including CLI/auth in that same environment, independent CLI JSON
semantics and writable receipts, one-job resource limits, enough session time
for full1200s plus reporting, and a human resource-incident recovery path. Reuse
the CPU import proof; no reinstall. Local doubles are **not runtime remote-stop
proof or paid-ready evidence**. Do not blindly run the old direct entry point.

No resource/dependency/revision/retry/rights changes. Four hash-checked recovery5
RM02 frames and historical manifest unchanged. Illustrative1200s compute remains
$0.340464, not current pricing/all-in billing or a termination guarantee. Full
$2.85 retained reserves /$30 authority unchanged; no new paid reservation/attempt.
Remote stop/runtime NOT_VERIFIED; parent S05b PARTIAL, Gate R NOT_RUN; S05c,
physical/calibration and S12 holds unchanged.

## Recovery9 review limits — local fixes, NOT paid-ready

F1 transient `stopping...` or nonempty containers is polled until fresh info and
containers agree; reserve exhaustion remains a resource incident. The receipt
records verification rounds and preserves stop acknowledgement versus independent
confirmation. F2 real timer tests use >=100ms budgets on Windows Python3.11
(15.6ms monotonic ticks); app-ID publication uses explicit event synchronization.
Production1200/90/900/60/20/10-second constants are unchanged. F5 CLI encoding is
UTF-8. F6 only `recovery8/attempt-*/local/` generated bytes are ignored; source,
worker/watchdog receipts and GPU-result metadata remain visible.

**F3 local repair (recovery10; not paid admission):** parent passes its absolute
monotonic child deadline, so imports and input hashing consume the same clock.
Runner subtracts the existing10s exit margin for final local publication. Admission
fails before app setup if startup/execution/cleanup no longer fit. Relative budgets
cannot extend the absolute cutoff. Received payload integrity is checked, then
bytes are atomically renamed and `result-received.json` commits them with cleanup
PENDING, BEFORE potentially blocking cleanup. Only successful guarded cleanup
permits atomic `gpu-result.json` with CONFIRMED status. Parent kill/nonzero remains
failure even when saved payload and independently confirmed shutdown coexist.
Atomicity is per-file, not crash durability or a multi-file transaction; a killed
write may leave ignored temporary bytes. Filesystem/OS stalls, parent death and
unreceived remote results remain outside this local preservation guarantee.
Independent review and actual provider/environment/budget checks are still needed
before paid execution; this repair does not release that hold.

**F4 lifecycle receipt guard:** the child writes an atomic, per-attempt,
token-and-PID-bound phase receipt. A valid `preflight_failed` receipt records
`no_remote_creation_confirmed` without claiming a remote stop; missing,
malformed, stale/replaced, or post-validation receipts remain
`app_id:unknown_remote_state`, resource incident, no guessed ID or broad listing.
Any app-creation boundary still requires the existing independent stop and exact
ID verification.

Local synthetic tests cover transient states, bounded persistent state, Unicode,
late-result rejection and preflight failure. Remote stop/lifecycle timing, real
CLI/auth, live headroom/no-paid-overage and physical results remain NOT_VERIFIED.
Parent S05b stays PARTIAL; this review-fix child cannot release paid readiness.

**Optimization-safe input/result gates (recovery11):** runtime exceptions, not
Python assertions, enforce local frame size/hash, approved RM02 identity/count,
pinned runtime, one CUDA device, remote frame hash, prediction count/required
fields and256MiB egress ceiling. `python -O` cannot remove these boundaries.
This does not attest input-manifest authority or provider behavior; all existing
independent review/live-admission/stop/budget holds continue. Optimized AST-body
tests use tiny synthetic data and fake external GPU/model/codec interfaces only.


### S05b-orch13 (Oct29) - first live RM02 admissions

Two L4 attempts (admission 90s, then controller-approved 210s) got NO container; both apps
stopped/containers [] by exact ID. No GPU/VRAM/output. Bounds now TOTAL 900s / execution 480s so one
bounded attempt fits a 30-minute session. Phase receipt also records `ppid`: on Windows the uv/venv
`Scripts/python.exe` launcher spawns the interpreter, so Popen PID may equal the receipt's ppid.
Receipts: `evidence/S05/S05b/orch13/` and `Run-System/Runs/S05b-orch13/REPORT.md`.
