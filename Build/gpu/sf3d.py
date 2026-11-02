"""N31 Stable Fast 3D (stabilityai/stable-fast-3d, Stability AI Community License; duties in
evidence/owner/S06/SF3D-LICENCE.md): SAM 3.1 RGBA cut-out of a clicked room object -> textured, remeshed GLB.

Own on-demand Modal app (L4 preferred, Modal's own A10G fallback when no L4 capacity, as seen live on Nov 2;
min_containers 0, max_containers 1, scale to zero after IDLE_S idle seconds).
Gated weights come from HF with HF_TOKEN in the Modal secret SECRET (key name only).
Deploy: uv run --python 3.12 --with modal==1.6.3 --env-file .env modal deploy Build/gpu/sf3d.py
Callers use generate_remote(): one daily_cap reservation per job at the A10G worst case, settled with the
Build/gpu/cost_log.py rate of the GPU that ran (bounded call wall time + idle window). Not a provider bill.
Background room upgrades join the shared GPU job queue and status dot; the Modal function keeps its own pool.
"""
import io
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # local only: cost_log
from cost_log import cost  # noqa: E402

APP, SECRET, CPU, MEM_GIB = "r2s-sf3d", "r2s-hf-sf3d", 2, 16
GPUS = ["L4", "A10G"]  # Modal tries in order; the container reports which one ran
REV = "ff21fc491b4dc5314bf6734c7c0dabd86b5f5bb2"  # Stability-AI/stable-fast-3d main, 2026-11-02
TIMEOUT_S, STARTUP_S, IDLE_S = 300, 300, 900
BACKGROUND_BUDGET_S = TIMEOUT_S + STARTUP_S + 60
# N53: optional shape must not hold the whole lab for the remote 300 s function timeout.
CLIENT_BUDGET_S = 90
VERTEX_COUNT = 1000  # SF3D triangle remesh target: about 2k triangles (lab "average detail", 1 to 3k)
ESTIMATE_USD = cost(BACKGROUND_BUDGET_S + IDLE_S + 60, "A10G", CPU, MEM_GIB)["total_usd"]
LICENCE = {"model": "stabilityai/stable-fast-3d", "licence": "Stability AI Community License",
           "label": "MODEL-GENERATED shape", "credit": "Powered by Stability AI"}


class GenerationTimeout(RuntimeError):
    """The optional shape exhausted its client budget; retain the labelled box."""


try:
    import modal
except ImportError:  # API process without modal: generate_remote raises at call time
    modal = None

if modal:
    image = (
        modal.Image.from_registry("nvidia/cuda:12.4.1-devel-ubuntu22.04", add_python="3.11")
        .apt_install("git", "build-essential", "libgl1", "libglib2.0-0")
        .pip_install("torch==2.5.1", "torchvision==0.20.1", index_url="https://download.pytorch.org/whl/cu124")
        .pip_install("setuptools==69.5.1", "wheel")
        # A10G 8.6, L4 8.9; the add_python interpreter was built with clang, which the image lacks: use gcc
        .env({"USE_CUDA": "1", "TORCH_CUDA_ARCH_LIST": "8.6;8.9", "CUDA_HOME": "/usr/local/cuda", "CC": "gcc", "CXX": "g++"})
        .run_commands(f"git clone https://github.com/Stability-AI/stable-fast-3d /opt/sf3d && git -C /opt/sf3d checkout {REV}",
                      "cd /opt/sf3d && pip install --no-cache-dir --no-build-isolation -r requirements.txt")
        .add_local_python_source("cost_log")  # this module imports it at load time in the container too
    )
    app = modal.App(APP)
    _model = {}

    @app.function(image=image, gpu=GPUS, cpu=CPU, memory=MEM_GIB * 1024, timeout=TIMEOUT_S, startup_timeout=STARTUP_S,
                  min_containers=0, max_containers=1, buffer_containers=0, scaledown_window=IDLE_S, retries=0,
                  secrets=[modal.Secret.from_name(SECRET)])
    def generate(rgba_png: bytes, vertex_count: int = VERTEX_COUNT):
        t0 = time.time()
        if not hasattr(sys.modules.get("sf3d"), "__path__"):
            # this file is module "sf3d" (/root/sf3d.py) and Stability's sf3d/ has no __init__.py (namespace package,
            # which loses to a plain module on sys.path): register the package by hand
            import types
            pkg = types.ModuleType("sf3d")
            pkg.__path__ = ["/opt/sf3d/sf3d"]
            sys.modules["sf3d"] = pkg
        import torch
        from PIL import Image
        from sf3d.system import SF3D
        from sf3d.utils import resize_foreground
        if "m" not in _model:  # weights stay loaded while the container is warm
            _model["m"] = SF3D.from_pretrained("stabilityai/stable-fast-3d", config_name="config.yaml",
                                               weight_name="model.safetensors").to("cuda").eval()
        t1 = time.time()
        img = resize_foreground(Image.open(io.BytesIO(rgba_png)).convert("RGBA"), 0.85)
        torch.cuda.reset_peak_memory_stats()
        with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            mesh, _ = _model["m"].run_image(img, bake_resolution=1024, remesh="triangle", vertex_count=vertex_count)
        glb = mesh.export(file_type="glb", include_normals=True)
        return {"glb": glb, "vertices": mesh.vertices.tolist(), "faces": mesh.faces.tolist(),
                "model_load_s": round(t1 - t0, 3), "inference_s": round(time.time() - t1, 3),
                "peak_allocated_bytes": torch.cuda.max_memory_allocated(), "gpu_name": torch.cuda.get_device_name(0)}


def gpu_of(name):
    """Cost-rate GPU from torch's device name; unknown = the dearer A10G (conservative)."""
    return "L4" if name and "L4" in name else "A10G"


def generate_remote(rgba_png, cap_path=None, fn=None, timeout_s=CLIENT_BUDGET_S, *, owner=None, gpu_path=None, abort=None):
    """One SF3D job, reserved in daily_cap at the A10G worst case, settled at the rate of the GPU that ran (cost_log
    rates; A10G when unknown). Unconfirmed cancellation retains the full estimate.
    Returns the remote result plus gpu, wall_s, estimated_usd."""
    from Build.guardrails import daily_cap
    from Build.api import gpu as jobs
    if not 0 < timeout_s <= BACKGROUND_BUDGET_S:
        raise ValueError("SF3D client budget must be positive and within the reserved background budget")
    rid = daily_cap.reserve("Modal", ESTIMATE_USD, "N31 sf3d", path=cap_path)
    call, r, cancellation_unconfirmed, jid, spawned = time.monotonic(), {}, False, None, False
    try:  # failed or not, the GPU may have run: settle wall time + the idle window
        if owner is not None:
            jid = jobs.enqueue(owner, "sf3d", gpu_path, reservation=rid, cap_db=cap_path)
            jobs.start(jid, gpu_path)
        if fn is None:
            fn = modal.Function.from_name(APP, "generate")
        call = time.monotonic()
        spawned = True  # spawn failure can be ambiguous: retain the upper bound
        handle = fn.spawn(rgba_png)
        try:
            while True:
                if abort and abort():
                    raise RuntimeError("SF3D cancelled (shell rebuilt)")
                remaining = timeout_s - (time.monotonic() - call)
                if remaining <= 0:
                    raise GenerationTimeout(f"SF3D gave no result within {timeout_s}s (startup/inference budget)")
                try:
                    r = handle.get(timeout=min(10, remaining))
                    break
                except Exception as e:  # Modal's polling timeout is distinct from its execution timeout.
                    if type(e).__name__ != "TimeoutError":
                        raise
        except Exception as e:  # by name: tests run without modal installed
            try:
                handle.cancel(terminate_containers=True)
            except Exception as cancel_error:
                cancellation_unconfirmed = True
                raise GenerationTimeout("SF3D cancellation unconfirmed; full reservation retained") from cancel_error
            if type(e).__name__ == "FunctionTimeoutError":
                raise GenerationTimeout("SF3D execution timed out") from e
            raise
    finally:
        wall = time.monotonic() - call
        # Provider startup and execution timeouts bound GPU life; network/queue waits are not additional GPU time.
        billed_bound_s = min(wall, STARTUP_S + TIMEOUT_S) + IDLE_S
        usd = (ESTIMATE_USD if cancellation_unconfirmed or (spawned and not r) else
               cost(billed_bound_s, gpu_of(r.get("gpu_name")), CPU, MEM_GIB)["total_usd"] if spawned else 0)
        try:
            daily_cap.settle(rid, usd, path=cap_path)
        except ValueError:
            if not jid:
                raise
            raise RuntimeError(jobs.REASON) from None  # lease reaper settled it; never release or charge twice
        finally:
            if jid and not jobs.finish(jid, gpu_path):
                raise RuntimeError(jobs.REASON)
    return {**r, "gpu": gpu_of(r.get("gpu_name")), "wall_s": round(wall, 3), "estimated_usd": usd}

