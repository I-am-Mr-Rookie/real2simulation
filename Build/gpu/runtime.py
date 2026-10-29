"""S06b MapAnything GPU runtime on the S06a pinned IMAGE (deps + Apache weights baked; offline at run).

Smoke (one A10G job, visibly synthetic frames, no real scene):  modal run Build/gpu/runtime.py --out <receipt.json>
Scene jobs (S06d) reuse RUNTIME_IMAGE + load_model(); never pip-install inside a function.
"""
import json
import sys
import time
from pathlib import Path

T_IMPORT = time.time()  # in-container: first user-code moment after image/container start
sys.path.insert(0, str(Path(__file__).resolve().parent))
import modal
import image_spec as s
from modal_image import IMAGE

RUNTIME_IMAGE = IMAGE.add_local_python_source("modal_image")  # mount only; no layer rebuild
app = modal.App("s06b-mapanything-runtime")


def load_model():
    """MapAnything (Apache weights @ pinned revision) on the single CUDA device, from the baked cache only."""
    import torch
    from mapanything.models import MapAnything
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("Exactly one available CUDA device required")
    return MapAnything.from_pretrained(s.MODEL_ID, revision=s.WEIGHT_REV, local_files_only=True).eval().to("cuda")


def installed_licences():
    import importlib.metadata as md
    out = []
    for d in md.distributions():
        m = d.metadata
        out.append({"name": m["Name"], "version": d.version,
                    "license_expression": m.get("License-Expression"),
                    "license": (m.get("License") or "")[:200] or None,
                    "classifiers": [c for c in (m.get_all("Classifier") or []) if c.startswith("License ::")]})
    return sorted(out, key=lambda r: (r["name"] or "").lower())


@app.function(image=RUNTIME_IMAGE, gpu=s.GPU, cpu=2, memory=16384, timeout=300, startup_timeout=240,
              retries=0, min_containers=0, max_containers=1, buffer_containers=0, scaledown_window=2,
              single_use_containers=True)
def smoke():
    import subprocess
    import numpy as np
    import torch
    from PIL import Image
    from mapanything.utils.image import load_images
    t_call = time.time()
    gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                                   "--format=csv,noheader"], text=True, timeout=15).strip()
    model = load_model()
    torch.cuda.synchronize()
    t_loaded = time.time()
    rng = np.random.default_rng(0)  # SYNTHETIC noise frames: runtime check only, no scene/geometry meaning
    paths = []
    for i in range(2):
        p = f"/tmp/synthetic-{i}.png"
        Image.fromarray(rng.integers(0, 256, (392, 518, 3), dtype=np.uint8)).save(p)
        paths.append(p)
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    with torch.inference_mode():
        preds = model.infer(load_images(paths), memory_efficient_inference=True, minibatch_size=1,
                            use_amp=True, amp_dtype="bf16", apply_mask=True, mask_edges=True,
                            apply_confidence_mask=False, use_multiview_confidence=False)
    torch.cuda.synchronize()
    t1 = time.time()
    return {
        "input": "SYNTHETIC random-noise frames (2 x 518x392); not a scene", "gpu": gpu,
        "torch": str(torch.__version__), "cuda": str(torch.version.cuda),
        "module_import_unix": T_IMPORT, "call_start_unix": t_call,
        "model_load_s": t_loaded - t_call, "inference_s": t1 - t0, "function_elapsed_s": t1 - t_call,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "pred_keys": sorted(k for k in preds[0] if isinstance(preds[0][k], torch.Tensor)),
        "pts3d_shape": list(preds[0]["pts3d"].shape),
        "pts3d_finite_fraction": float(torch.isfinite(preds[0]["pts3d"]).float().mean()),
        "licences": installed_licences(),
    }


@app.local_entrypoint()
def main(out: str = ""):
    t = time.time()
    r = smoke.remote()
    r["client_launch_unix"], r["client_return_unix"] = t, time.time()
    r["client_roundtrip_s"] = r["client_return_unix"] - t
    text = json.dumps(r, indent=1)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text + "\n")
    print(json.dumps({k: v for k, v in r.items() if k != "licences"}, indent=1))
