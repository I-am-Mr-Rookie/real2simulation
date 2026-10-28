# S05b — RM02 local preparation; MapAnything execution NOT RUN

**Historical preparation receipt.** Standing authorization now permits the
bounded private RM02 Modal route; old pending-Q8/no-upload/no-GPU statements
below are superseded by `evidence/owner/S05/GPU-AUTHORIZATION.md`. The Oct28
continuation made one remote setup attempt, failed dependency resolution before
inference, and verified all apps/containers stopped. Current result and exact
remaining technical limits: `Run-System/Runs/S05b/REPORT.md`, `GPU-PREFLIGHT.md`
and `gpu-attempt.txt`. No new permission/redemption question is needed.

Observed 2026-10-28 UTC. **PARTIAL**: real approved input prepared; no model output,
GPU runtime/VRAM, reconstruction accuracy or Gate R result exists.

## Input and rights

RM02, Andy Barbour's Pexels classroom, is one of the ten approved local inputs in
`evidence/owner/S02/APPROVAL.md`. Old CSV NO/UNAPPROVED labels are unchanged: the
new approval allows this local work, not final/public distribution or upload.
The source file/hash and four decoded frames are recorded in `input.json`.
Frame images/contact sheet remain in gitignored `local/`, not committed.

Selected RM02 over RM04 (zoom-dominant/weak translation) and RM05 (ISS, not Earth).
Reuse `evidence/clips/S02c-opus-frame-evidence.md` RM02: its earlier nonplanar-flow
evidence supports trying reconstruction but does not prove it. Locally inspected
the 2x2 sheet: same classroom/desk, small changing viewpoint, no visible cut in
these four samples; distant furniture is soft-focus. No claim of adequate
baseline, full-clip continuity, A4 identity/size or metric calibration. Papers on
the desk are NOT verified A4 references. Reject any automatic metric gate pass.

## Actual local commands and observations

Run at repository root. Existing tools only; no install, weights or cloud job.

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory
Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM
where.exe nvidia-smi
python -c "import mapanything"
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate,avg_frame_rate,nb_frames,duration -of json test-data/public/RM02.mp4
New-Item -ItemType Directory -Path evidence/S05/S05b/local -Force
ffmpeg -hide_banner -loglevel error -threads 1 -i test-data/public/RM02.mp4 -vf "select='eq(n,0)+eq(n,24)+eq(n,48)+eq(n,72)',scale=518:-2:flags=lanczos,showinfo" -fps_mode vfr -frames:v 4 -threads 1 evidence/S05/S05b/local/RM02-%02d.png
```

- RAM snapshot: total 12,359,472 KiB; available 2,570,176 KiB (~2.45 GiB).
- VideoController: Intel UHD Graphics only; AdapterRAM property 1,073,741,824 bytes
  is device metadata, **not measured free/dedicated VRAM**. NVIDIA CLI not found.
- Python 3.14.5; `find_spec`: torch=false, mapanything=false; PIL/jsonschema and
  huggingface_hub=true. Actual `import mapanything` raises ModuleNotFoundError.
  Python launcher also lists 3.13 and 3.11; no 3.12 environment observed. Upstream
  recommends 3.12 but declares >=3.10: no blanket incompatibility claim for 3.14.
- ffprobe exit0: h264, 3840x2160, 24/1 average and nominal file FPS, 426 frames,
  17.75s. ffmpeg 8.1.1 exit0, four 518x292 PNGs. Observed extraction wall time
  **1.7639308s is CPU frame preparation only**, not model or GPU latency.
- Contact sheet: second ffmpeg invocation uses the same selection/scaling plus
  `tile=2x2`, `-frames:v 1`; locally inspected through view_image.

## Pinned model/runtime readiness

Reuse S05a Apache decision: code `3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9`,
weights `facebook/map-anything-apache` at
`00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a`. Never use README's NC default.

Fresh public metadata only: `weight-metadata.json` records the same ungated
Apache revision and **4,914,062,480-byte** safetensors file (~4.58 GiB on disk,
NOT a VRAM estimate). No weight downloaded. With only ~2.45 GiB available RAM,
no installed runtime and no exposed NVIDIA device, do not attempt a multi-GB
model/build or speculative CPU load on this PC. No CUDA query/peak measurement
was possible; actual GPU type/count/VRAM/runtime/billing/output are **unmeasured**.

`upstream-pyproject.toml` is the exact public pinned source (2,883 bytes;
SHA256 `6f857380c9f4e09f7990f3d5cf6764950f211b68df29b59c77a47337edda09a0`).
Its base includes uniception==0.1.7 and opencv-python-headless==4.10.0.84; it does
not pin/install torch or CUDA. Many dependencies are unpinned. Do not install
`[all]`, COLMAP, external models, SAM or UI extras for this first image-only probe.
This is prerequisite inspection, **not a completed dependency licence/lock audit**.

For an authorized compatible runtime, upstream's image-only path is
`MapAnything.from_pretrained` + `load_images` + `infer`. Resolve only the exact
Apache revision; verify the actual library's revision pin support before loading,
or preload the pinned snapshot locally. Begin with these four ordered images,
`memory_efficient_inference=True`, `minibatch_size=1`; precision/device depend on
the actual authorized hardware. No executable runner or unsupported revision
flag is claimed tested here. Before a job, finish dependency/weight integrity
checks and reserve bounded worst-case spend within existing authorization.

Raw expected outputs (not observed): pts3d/depth/confidence/masks, intrinsics,
OpenCV camera-to-world poses. The S05a scene contract is right-handed +Y-up,
camera -Z-forward: raw poses must NOT be handed directly to its viewer. Conversion,
unknown-scale/gravity semantics and metric checks remain S05c–e, not this receipt.

## Exact blocker and next action

Local model execution is unavailable without a large new runtime/resource route.
Q7 does **not** authorize GPU execution/spend or third-party footage upload.
No remote job, image build, deployment, AWS, terms, credential access or billing
change occurred. S06p account readiness is reused, not re-polled. The $130 credit
receipt is not new spend authority; retain $30 ceiling/no-overage and job ledger.

STATE owner fallback requests the execution-route decision. After explicit
scoped approval (or a supplied adequate local runtime), resume S05b, recheck
actual resource/budget/rights, run ONE bounded RM02 probe, record measured output
hashes, runtime, GPU/peak VRAM and stopped-resource receipt. No automatic launch
on an unanswered question. Parent S05/Gate R and S05c remain unpassed.

Sources: [pinned package manifest](https://raw.githubusercontent.com/facebookresearch/map-anything/3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9/pyproject.toml),
[pinned weight metadata](https://huggingface.co/api/models/facebook/map-anything-apache/revision/00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a?blobs=true),
S05a saved README/licence snapshots. Web metadata endpoint failed in web open;
one bounded stdlib HTTPS metadata read succeeded; no authentication used.
