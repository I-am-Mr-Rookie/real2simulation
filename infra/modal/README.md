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
