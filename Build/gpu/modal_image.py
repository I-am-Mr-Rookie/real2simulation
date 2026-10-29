"""Pinned MapAnything Modal image: locked deps + Apache weights baked at build, offline at run.

CPU dry run (no GPU):  modal run Build/gpu/modal_image.py --out <receipt.json>
GPU jobs reuse IMAGE with gpu=image_spec.GPU; the model then loads offline from the baked cache.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modal
import image_spec as s

_spec = s.dry_run() if modal.is_local() else None  # lock/revisions exist only on the client
if _spec and not _spec["ok"]:  # refuse to build from drifted pins
    raise SystemExit(f"S06a dry run failed: {_spec['errors']}")

IMAGE = (
    modal.Image.debian_slim(python_version=s.PYTHON)
    .pip_install_from_requirements(str(s.LOCK))
    .env({"HF_HOME": s.HF_HOME})
    .run_commands("python -c \"from huggingface_hub import snapshot_download as d; "
                  f"d('{s.MODEL_ID}', revision='{s.WEIGHT_REV}')\"")
    .env({"HF_HUB_OFFLINE": "1"})
    .add_local_python_source("image_spec")
)
app = modal.App("s06a-image-dryrun")


@app.function(image=IMAGE, cpu=1, memory=4096, timeout=300, retries=0,
              min_containers=0, max_containers=1, scaledown_window=2,
              single_use_containers=True)
def check():
    import importlib.metadata as md
    import os
    from huggingface_hub import snapshot_download
    import image_spec as spec
    path = snapshot_download(spec.MODEL_ID, revision=spec.WEIGHT_REV, local_files_only=True)
    from mapanything.models import MapAnything  # import only; CPU container has no CUDA
    return {
        "versions": {p: md.version(p) for p in ("torch", "torchvision", "torchaudio", "numpy",
                                                 "timm", "huggingface-hub", "mapanything")},
        "weights_path": path, "weights_files": sorted(os.listdir(path)),
        "weights_bytes": sum(f.stat().st_size for f in Path(path).rglob("*") if f.is_file()),
        "hf_hub_offline": os.environ.get("HF_HUB_OFFLINE"), "model_class": MapAnything.__name__,
    }


@app.local_entrypoint()
def main(out: str = ""):
    result = {"spec": _spec, "remote": check.remote()}
    text = json.dumps(result, indent=1)
    if out:
        Path(out).write_text(text + "\n")
    print(text)
