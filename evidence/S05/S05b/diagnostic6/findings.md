# Scheduling diagnostic: bounded UNKNOWN

## Reused facts, not rerun

- [Recovery5 report](../../../../Run-System/Runs/S05b/recovery5/REPORT.md): actual CPU imports PASS; one subsequent GPU RPC; no observed GPU startup/inference/output.
- [App snapshot](../recovery5/apps-after-gpu.json): GPU app created 12:41:20Z, stopped 12:51:08Z, tasks 0; CPU app stopped 12:40:49Z, tasks 0. App lifetime 588s is not billed GPU time.
- [Container snapshot](../recovery5/containers-after-gpu.json): []; historical final snapshot only, not refreshed here.
- [GPU client log](../recovery5/gpu-runtime.txt): initialized/created Function probe, then RemoteError after external stop; no pre-stop provider exception explains admission.
- [Fresh system logs](telemetry.md): CLI stop 12:51:08Z, SDK stop 12:51:10Z; consistent with manual stop followed by runner cleanup, not an independently diagnosed GPU error.

## Current official semantics, checked 2026-10-28

| Source | Narrow observation and implication |
|---|---|
| [Timeouts](https://modal.com/docs/guide/timeouts) | Execution timeout excludes scheduling. Startup has a separate timeout. A 900s function limit plus 90s startup limit is not a total RPC deadline. Timeouts may overrun by several seconds; prior 992s arithmetic is not a guaranteed hard stop. |
| [Scaling out](https://modal.com/docs/guide/scale) | Warm minimum, maximum running containers and idle buffer are separate controls. min0/buffer0 maintains no warm reserve; max1 limits concurrency, not admission latency. This configuration is not evidence of quota exhaustion or capacity failure. |
| [Resource requests/limits](https://modal.com/docs/guide/resources) | cpu=(1,2) is request/limit in physical cores; memory=(8192,16384) is request/limit in MiB. Memory limit is 16 GiB host RAM, NOT GPU VRAM. Valid resource request is not a guarantee of immediate scheduling. |
| [GPU acceleration](https://modal.com/docs/guide/gpu) | gpu="L4" requests an accelerator type; no proof of actual allocation or device compatibility follows merely from Function creation. No fallback/type/region changes tested or proposed here. |
| [App CLI logs](https://modal.com/docs/cli/latest/app#modal-app-logs) | Bounded date range, source, tail, timestamp and ID switches are documented; local 1.6.3 help agrees and actual command exit0 demonstrates this read-only surface works. |

Installed existing client inspected as text, not runner imports:
`C:/Users/HP/AppData/Local/uv/cache/archive-v0/fLq5XQNkIwPHWdoT/Lib/site-packages/modal/app.py`
lines 813–880/1024–1040 and `modal/cli/app.py` lines 623–710;
version confirmed in `modal-1.6.3.dist-info/METADATA`.
`startup_timeout` is separately forwarded; retries0 requests no input-failure
retry; single_use_containers closes a container after one input. Crucially,
`serialized=True` means **cloudpickle function transport**, not a serialization
or queue-deadline guarantee. The runner's sequential calls/max1 supply its actual
single-attempt scope. Supported parameters/source wiring are not GPU execution proof.

## What remains missing

No server-side function-call ID/input-enqueue acknowledgement or timestamp;
no queue position/wait breakdown, autoscaler/admission decision, placement attempt
or denial reason; no worker/container allocation and startup timestamps; no exact
per-call billed-resource record. The inspected system log surface supplied only
stop events. App accepted/Function created does not itself prove the input reached
the scheduler. Existing evidence cannot distinguish input handoff/admission delay,
placement/capacity delay, or another service-side condition. These are unresolved
possibilities, not established failures. No affirmative credit/quota, model,
dependency or GPU-capacity failure evidence. Root cause remains **UNKNOWN**.

## Smallest next scoped step, not performed

Controller should obtain the exact stopped app's existing per-call timeline and
scheduler/admission reason through the signed-in ChatGPT in-app browser only;
if absent, record that missing provider-side evidence rather than repeat these
same logs or launch an identical paid retry. No account-wide hunting or automatic
support message. No new paid action is genuinely ready from this diagnostic.

Before any later separately scoped continuation under existing GPU authority:

1. Resolve the missing scheduler evidence or establish a genuinely changed
   prerequisite. Reuse actual [CPU imports](../recovery5/cpu-import-result.json),
   lock/code/weight revisions and [four approved raw-input hashes](../recovery5/input-integrity.json); verify bytes/rights remain unchanged, no CPU reinstall by default.
2. Fresh authenticated headroom/no-paid-overage coverage, serialized resource
   check, and **<= $1 all-in reservation before launch**, covering queue-associated
   allocated resources, startup, execution, timeout/stop lag, and egress. Old
   $1.90 + recovery5 $.95 = **$2.85 retained**, authority **$30**, exact charges
   unknown; no reserve release or claim that $130 display expands permission.
3. A validated independent **TOTAL queue + startup + execution + cleanup**
   wall-clock stop and earlier admission cutoff fitting the future run's own
   timebox. Deduct 90s startup + 900s execution + conservative overrun/stop/check
   margin before choosing queue allowance; if that leaves no allowance, do not
   launch. Do not use `.remote()` blocking wait or 992s arithmetic as this guard.
   Deadline enforcement must stop/confirm the remote app, not just kill a client;
   inability to verify stop remains a resource/budget incident, not success.

No per-job owner-consent or grant-redemption gate invented. No change to physical
Gate R/metric-calibration holds, S05c lock, S07b custody, or S12 eligibility.
