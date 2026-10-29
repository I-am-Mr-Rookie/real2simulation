# Modal GPU image + dry-run contract (S06a, v1)

Owner of definitions: Build/gpu/. Inputs are referenced, not copied:
- Lock: Build/reconstruction/spike/requirements-linux-py311.txt (279 lines, uv-compiled for Linux py3.11;
  ran OK on A10G in S05b-orch14). Pinned by LF sha256 cc352969...183330 in Build/gpu/image_spec.py.
- Model: facebook/map-anything-apache @ 00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a (apache-2.0, ungated);
  code facebookresearch/map-anything @ 3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9. Must match
  evidence/S05/upstream/revisions.json. NC checkpoint facebook/map-anything is rejected.

## Image (Build/gpu/modal_image.py: IMAGE)
debian_slim py3.11 -> pip_install_from_requirements(lock) -> HF_HOME=/weights/hf -> snapshot_download(model, rev)
-> HF_HUB_OFFLINE=1 -> add_local_python_source(image_spec). Modal caches each layer by content; any pin edit rebuilds
only from that layer. Runtime never contacts PyPI or the Hub (offline env), so a job is the same bytes every run.

## Dry-run contract
1. Offline (no Modal, no network, CPU, free): python Build/gpu/image_spec.py [out.json]
   exit 0 only if: lock hash matches; every requirement is ==-pinned or the code-rev zip; torch 2.8.0 /
   torchvision 0.23.0 / torchaudio 2.8.0 / numpy 2.2.6 / timm 1.0.20 / huggingface-hub 2.3.0 present;
   mapanything pinned to code rev; revisions.json agrees; weights apache-2.0 + ungated. Tests: Build/gpu/test_image_spec.py.
   modal_image.py refuses to build if this fails.
2. Remote CPU (no GPU): modal run Build/gpu/modal_image.py --out <receipt.json>
   builds/reuses IMAGE, runs check() on 1 CPU / 4 GiB / 300 s / retries 0 / max 1 container: package versions,
   weights loadable with local_files_only, MapAnything importable. No frames, no inference, no CUDA.

## Using it in GPU jobs (S05c/S06b-d)
    from modal_image import IMAGE; import image_spec as s
    @app.function(image=IMAGE, gpu=s.GPU, retries=0, max_containers=1, ...)
    -> MapAnything.from_pretrained(s.MODEL_ID, revision=s.WEIGHT_REV) loads from the baked cache; drop the
       in-function pip install used by spike/modal_rm02.py.
Unchanged safeguards: standing auth evidence/owner/S05/GPU-AUTHORIZATION.md, reserve + ledger before each job,
billing headroom read-only, stop app and verify own containers [] after each job, approved licensed inputs only.

## Measured (S06a-orch19, 2026-10-29, CPU only; evidence/S06/S06a/)
Layers: pip lock im-q581Fc7gkhLxWxxCVcH28L 93.2 s; HF_HOME env 2.1 s; weights im-cUB9QQ0Dn3FkX30MLmIpf5 28.1 s
(4 files, 4,914,071,149 B); offline env im-y8LktidTUGB7wRgfptnz2w 1.5 s. App ap-Gf1f5xsIuhpOIGFiwLE1zr ran check()
OK and stopped; own containers []. Remote versions torch 2.8.0 / vision 0.23.0 / audio 2.8.0 / numpy 2.2.6 /
timm 1.0.20 / hf-hub 2.3.0 / mapanything 1.1.4; weights loaded with local_files_only under HF_HUB_OFFLINE=1.
NOT verified: GPU/CUDA use of this image, warm container start time with cached layers, inference, container
dependency licence audit (S06b), cache retention period on Modal.

## Runtime (S06b, Build/gpu/runtime.py)
RUNTIME_IMAGE = IMAGE + modal_image source mount (no layer rebuild). load_model(): exactly one CUDA device,
MapAnything.from_pretrained(apache @ 00f9c24, local_files_only=True). smoke(): A10G, cpu 2, 16 GiB, timeout 300 s,
startup 240 s, retries 0, max 1 container, single-use; nvidia-smi + model load + 2 SYNTHETIC noise frames forward
(runtime check only, no scene meaning) + importlib.metadata licence dump.  modal run Build/gpu/runtime.py --out <json>
Licence audit: python Build/gpu/licence_audit.py <smoke.json> [audit.json] (tests: Build/gpu/test_licence_audit.py).
Exit 0 iff every lock pin installed at its version, nothing NC/ND/proprietary outside NVIDIA CUDA wheels, and every
unknown/copyleft dist has a REVIEWED decision. NVIDIA CUDA wheels (14, proprietary EULA via torch): private runtime only.
plyfile 1.1.5 GPL-3.0 (mapanything dep): private runtime use, not vendored/redistributed; re-review before shipping
any image. mapanything metadata empty -> Apache-2.0 per evidence/S05/LICENSE_REVIEW.md.

## Measured (S06b-orch20, 2026-10-29, one A10G job; evidence/S06/S06b/)
App ap-vaD1cV50rPyWL1yzQggQ6g 12:15:43Z -> stopped 12:16:27Z, rc 0, no image rebuild (S06a layers cached), own
containers [] after. GPU NVIDIA A10G 23028 MiB, driver 610.57.04; torch 2.8.0+cu128, CUDA 12.8.
In-function: model load 23.0 s, forward 1.6 s, function 24.7 s, peak alloc 7.78 GB; client round trip 36.3 s.
Baseline S05b recovery8 (in-function pip) function 161.7 s => ~137 s less in-function setup per cold job.
Cost $0.0118 (hourly billing CSV, may lag). Audit: 116 dists (111 unique), 96 lock pins all present at version;
100 permissive, 14 vendor_eula, 2 reviewed. Duplicates attrs/certifi/idna/protobuf/typing-extensions at a second
(older) version = Modal-injected client deps, plus 15 extras (aiohttp, grpclib, ...); the lock versions are present.
NOT verified: which duplicate wins on sys.path; image cache retention; real-scene inference/quality (S05c/S06d-f).

## Optional SAM 3D Objects path (S06c, Build/gpu/sam3d_option.py) — DISABLED
Default and every failure -> primitive box colliders (scene-schema `collider`). SAM 3D runs only if ALL hold:
R2S_ENABLE_SAM3D=1; owner-created evidence/owner/S06/SAM3D-ACCESS.md (custom SAM License + manual HF gate; agents
never create it); GPU >= 32768 MiB (A10G 23028 MiB fails); a packaged runner (none: upstream torch 2.5.1/cu121 +
pytorch3d env conflicts with this lock, needs its own image + audit). S06d calls object_meshes(objects, vram_mib)
once an object-bounds source exists (not yet: S06d emits empty colliders/surfaces).
Review: evidence/S06/S06c/REVIEW.md. Offline receipt: python Build/gpu/sam3d_option.py <out.json>.

## Scene job entry point (S06d, Build/gpu/scene_job.py)
Approved room-scene id (RM02/RM04/RM05 per evidence/owner/S02/APPROVAL.md + allowlisted clips.csv licence)
-> hash-verified frames from an S05 input manifest -> scene_job on RUNTIME_IMAGE (A10G, retries 0, max 1
container, single-use) -> npz -> contracts/scene bundle (points.ply + mobile LOD + scene.json), validated
before return. OpenCV axes converted once (diag(1,-1,-1)); scale "estimated" (nominal MapAnything), gravity
unknown, no surfaces/colliders, camera time_s = view index (not capture time). Not Gate R evidence.
    modal run Build/gpu/scene_job.py --scene RM02 --out <dir> --manifest <S05 input.json>
    python Build/gpu/scene_job.py RM02 <dir> --npz <existing MapAnything npz>   # offline, no Modal
Bundle media stays gitignored (evidence/S06/S06d/local/); only scene.json manifests are committed.
RM02 A10G run 2026-10-29: rc 0, function 21.0 s, peak 7.78 GB, $0.0066 billed (hourly CSV, may lag).

## Cold-start timing and cost receipt (S06e, Build/gpu/cost_log.py)
modal run scene_job.py also writes <out>/<scene>-scene-log.json (schema s06e-scene-log/1): client round trip,
container_boot_s (call -> module import in container), cold_start_s (call -> function body), model_load_s,
cold_start_to_model_ready_s, inference_s, function_s; GPU seconds estimated (container python lifetime + scaledown)
and upper bound (round trip + scaledown); cost at Modal list rates A10G $0.000306/s, CPU $0.0000131/core-s,
Memory $0.00000222/GiB-s (back-solved S06d bill agrees). Billed comes ONLY from Modal's own report, read-only:
    modal billing report --for today -r h --json --show-resources > billing.json
    python Build/gpu/cost_log.py <scene-log.json> billing.json   # no rows yet -> billed stays "unavailable"
Run from the event root (uv --env-file splits paths with spaces); the local entrypoint needs jsonschema:
    uv run --no-project --python 3.11 --with modal==1.6.3 --with numpy --with jsonschema --env-file .env modal run ...
Client vs container clocks are separate NTP-synced hosts; sub-second skew is possible.
RM02 A10G run 2026-10-29 (ap-HT56BJbqGtr7qg1pdadmu0): boot 6.5 s, cold start 10.8 s, model load 19.7 s (ready 30.5 s),
inference 1.4 s, round trip 39.6 s; GPU s est 28.1 / billed 30.0; cost est $0.0103 vs billed $0.0113 (15:18Z read;
15:12Z read was partial $0.0051 - report lags). Not Gate R / calibration / physical evidence.
