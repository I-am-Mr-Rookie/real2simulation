"""S05c: batch the remaining approved scene clips in ONE private A10G container.

Reuses the RM02 deadline/watchdog/result harness; run only via
`python rm02_watchdog.py modal_scenes.py`. Never deploy an endpoint.
"""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import sys
import time

if not os.environ.get("RM02_WATCHDOG_RECEIPT"):
    raise RuntimeError("Use rm02_watchdog.py modal_scenes.py only in an authorized runtime continuation")

import modal
from rm02_deadline import guarded_probe, EXIT_SECONDS
from rm02_watchdog import atomic_json
from rm02_result import persist_result

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "evidence/S05/S05c/input.json"
EVIDENCE = Path(os.environ["RM02_WATCHDOG_RECEIPT"]).resolve().parent
CODE_REV = "3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9"
WEIGHT_REV = "00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a"
APPROVED_SCENES = {"RM04", "RM05"}  # evidence/owner/S02/APPROVAL.md scene-category IDs; RM02 done in S05b.
app = modal.App("s05c-scenes-private-batch")


@app.function(
    image=modal.Image.debian_slim(python_version="3.11"),
    gpu="A10G", cpu=(1, 2), memory=(8192, 16384),
    timeout=600, startup_timeout=90, retries=0,
    min_containers=0, max_containers=1, buffer_containers=0,
    scaledown_window=2, single_use_containers=True,
    serialized=True, include_source=False,
)
def probe(scenes, requirements, code_rev, weight_rev):
    import hashlib
    import io
    import json
    import os
    from pathlib import Path
    import subprocess
    import sys
    import time
    import zipfile

    started = time.monotonic()
    os.environ["OMP_NUM_THREADS"] = "2"
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    gpu = subprocess.check_output([
        "nvidia-smi", "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader",
    ], text=True, timeout=15).strip()
    print(json.dumps({"allocated_gpu": gpu}), flush=True)
    Path("/tmp/s05b-requirements.txt").write_text(requirements)
    subprocess.run([
        sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
        "--no-cache-dir", "-r", "/tmp/s05b-requirements.txt",
    ], check=True, timeout=480)
    import numpy as np
    import torch
    from mapanything.models import MapAnything
    from mapanything.utils.image import load_images

    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("Exactly one available CUDA device required")
    setup_s = time.monotonic() - started
    model = MapAnything.from_pretrained(
        "facebook/map-anything-apache", revision=weight_rev,
    ).eval().to("cuda")
    bundle, per_scene = io.BytesIO(), {}
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_STORED) as archive:
        for clip_id, frames in scenes:
            paths = []
            for index, (data, expected_hash) in enumerate(frames):
                if hashlib.sha256(data).hexdigest() != expected_hash:
                    raise ValueError("Remote frame SHA256 mismatch")
                path = Path(f"/tmp/{clip_id}-{index:02}.png")
                path.write_bytes(data)
                paths.append(str(path))
            views = load_images(paths)
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()
            inference_start = time.monotonic()
            with torch.inference_mode():
                predictions = model.infer(
                    views, memory_efficient_inference=True, minibatch_size=1,
                    use_amp=True, amp_dtype="bf16", apply_mask=True, mask_edges=True,
                    apply_confidence_mask=False, use_multiview_confidence=False,
                )
            torch.cuda.synchronize()
            inference_s = time.monotonic() - inference_start
            if len(predictions) != len(frames):
                raise ValueError("Prediction count does not match input frames")
            arrays, schema = {}, {}
            for index, prediction in enumerate(predictions):
                if not {"pts3d", "cam_trans", "cam_quats"} <= prediction.keys():
                    raise ValueError("Prediction missing required scene/camera fields")
                for key, value in prediction.items():
                    if not isinstance(value, torch.Tensor):
                        continue
                    value = value.detach().float().cpu().numpy()
                    name = f"view{index}_{key}"
                    arrays[name] = value
                    schema[name] = {"shape": list(value.shape), "dtype": str(value.dtype),
                                    "finite": int(np.isfinite(value).sum()), "size": int(value.size)}
            output = io.BytesIO()
            np.savez_compressed(output, **arrays)
            data = output.getvalue()
            archive.writestr(f"{clip_id}-mapanything.npz", data)
            per_scene[clip_id] = {
                "frames": len(frames), "inference_s": inference_s,
                "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
                "output_bytes": len(data), "output_sha256": hashlib.sha256(data).hexdigest(),
                "schema": schema,
            }
    data = bundle.getvalue()
    if len(data) > 256 * 1024 * 1024:
        raise ValueError("Result exceeds reserved egress bound")
    receipt = {
        "clip_ids": [clip_id for clip_id, _ in scenes], "scenes": per_scene,
        "model": "facebook/map-anything-apache",
        "code_revision": code_rev, "weight_revision": weight_rev,
        "gpu": gpu, "gpu_count": 1, "setup_s": setup_s,
        "function_elapsed_s": time.monotonic() - started,
        "output_bytes": len(data), "output_sha256": hashlib.sha256(data).hexdigest(),
        "gate_R": "NOT RUN", "physical_scale": "unverified",
        "capture_timebase": "unverified", "torch": str(torch.__version__),
    }
    print(json.dumps({k: v for k, v in receipt.items() if k != "scenes"}))
    return receipt, data


def load_scenes(manifest_path=MANIFEST):
    """Local preflight: approved IDs only, byte/hash-verified frames."""
    manifest = json.loads(Path(manifest_path).read_text())
    scenes = []
    for scene in manifest["scenes"]:
        if scene["clip_id"] not in APPROVED_SCENES:
            raise ValueError("Scene clip is outside the approved S05c scope")
        frames = []
        for frame in scene["frames"]:
            data = (Path(manifest_path).parent / frame["path"]).read_bytes()
            if len(data) != frame["bytes"] or hashlib.sha256(data).hexdigest() != frame["sha256"]:
                raise ValueError("Local frame size/SHA256 mismatch")
            frames.append((data, frame["sha256"]))
        if len(frames) < 2:
            raise ValueError("Need at least two views per scene")
        scenes.append((scene["clip_id"], frames))
    if len({clip_id for clip_id, _ in scenes}) != len(scenes) or not scenes:
        raise ValueError("Need distinct approved scenes")
    return scenes


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    phase_path = Path(os.environ["RM02_PHASE_RECEIPT"]) if os.environ.get("RM02_PHASE_RECEIPT") else None
    phase_token = os.environ.get("RM02_PHASE_TOKEN")
    def phase(name, remote_creation_started, history):
        if phase_path is not None and phase_token:
            atomic_json(phase_path, {"version": 1, "token": phase_token,
                                     "pid": os.getpid(), "ppid": os.getppid(), "phase": name,
                                     "remote_creation_started": remote_creation_started,
                                     "history": history})
    try:
        scenes = load_scenes()
        requirements = Path(__file__).with_name("requirements-linux-py311.txt").read_text()
        if CODE_REV not in requirements or "numpy==2.2.6" not in requirements:
            raise ValueError("Pinned reconstruction runtime requirements mismatch")
    except Exception:
        phase("preflight_failed", False, ["preflight_failed"])
        raise
    phase("preflight_validated", False, ["preflight_validated"])
    started = time.time()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    def record_guard(state):
        atomic_json(Path(os.environ["RM02_WATCHDOG_RECEIPT"]), state)

    sys.path.insert(0, str(ROOT))
    from Build.guardrails.standalone import admit_standalone
    admit_standalone("spike-scenes")
    phase("remote_creation_started", True, ["preflight_validated", "remote_creation_started"])
    with modal.enable_output():
        receipt, data = asyncio.run(guarded_probe(
            app, probe, (scenes, requirements, CODE_REV, WEIGHT_REV), record_guard,
            total_seconds=float(os.environ["RM02_CHILD_BUDGET"]),
            deadline=float(os.environ["RM02_CHILD_DEADLINE"]) - EXIT_SECONDS,
            save_result=lambda result: persist_result(EVIDENCE, result, "S05c-scenes.zip"),
        ))
    receipt.update(client_start_unix=started, client_end_unix=time.time(),
                   remote_cleanup_status="CONFIRMED")
    atomic_json(EVIDENCE / "gpu-result.json", receipt)


if __name__ == "__main__":
    main()

