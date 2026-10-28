"""One authorized private RM02 probe; run locally, never deploy an endpoint."""
import hashlib
import asyncio
import json
from pathlib import Path
import time
import sys
import os

# Direct execution would bypass the independent process deadline.
if not os.environ.get("RM02_WATCHDOG_RECEIPT"):
    raise RuntimeError("Use rm02_watchdog.py only in an authorized runtime continuation")

import modal
from rm02_deadline import guarded_probe
from rm02_watchdog import atomic_json

ROOT = Path(__file__).resolve().parents[3]
INPUT_EVIDENCE = ROOT / "evidence/S05/S05b"
FRAME_EVIDENCE = ROOT / "evidence/S05/S05b/recovery5"
EVIDENCE = Path(os.environ["RM02_WATCHDOG_RECEIPT"]).resolve().parent
CODE_REV = "3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9"
WEIGHT_REV = "00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a"
app = modal.App("s05b-recovery5-rm02-private-probe")


@app.function(
    image=modal.Image.debian_slim(python_version="3.11"),
    gpu="L4", cpu=(1, 2), memory=(8192, 16384),
    timeout=900, startup_timeout=90, retries=0,
    min_containers=0, max_containers=1, buffer_containers=0,
    scaledown_window=2, single_use_containers=True,
    serialized=True, include_source=False,
)
def probe(frames, requirements, code_rev, weight_rev):
    import hashlib
    import io
    import json
    import os
    from pathlib import Path
    import subprocess
    import sys
    import time

    started = time.monotonic()
    os.environ["OMP_NUM_THREADS"] = "2"
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    gpu = subprocess.check_output([
        "nvidia-smi", "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader",
    ], text=True, timeout=15).strip()
    print(json.dumps({"allocated_gpu": gpu}), flush=True)
    Path("/tmp/s05b-requirements.txt").write_text(requirements)
    # Setup shares the same hard function timeout and resource caps as inference.
    subprocess.run([
        sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
        "--no-cache-dir", "-r", "/tmp/s05b-requirements.txt",
    ], check=True, timeout=480)
    import numpy as np
    import torch
    from mapanything.models import MapAnything
    from mapanything.utils.image import load_images

    assert torch.cuda.is_available() and torch.cuda.device_count() == 1
    paths = []
    for index, (data, expected_hash) in enumerate(frames):
        assert hashlib.sha256(data).hexdigest() == expected_hash
        path = Path(f"/tmp/RM02-{index:02}.png")
        path.write_bytes(data)
        paths.append(str(path))
    model = MapAnything.from_pretrained(
        "facebook/map-anything-apache", revision=weight_rev,
    ).eval().to("cuda")
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
    assert len(predictions) == len(frames)
    arrays, schema = {}, {}
    for index, prediction in enumerate(predictions):
        assert {"pts3d", "cam_trans", "cam_quats"} <= prediction.keys()
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
    assert len(data) <= 256 * 1024 * 1024, "Result exceeds reserved egress bound"
    receipt = {
        "clip_id": "RM02", "model": "facebook/map-anything-apache",
        "code_revision": code_rev, "weight_revision": weight_rev,
        "gpu": gpu, "gpu_count": 1, "inference_s": inference_s,
        "function_elapsed_s": time.monotonic() - started,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "output_bytes": len(data), "output_sha256": hashlib.sha256(data).hexdigest(),
        "schema": schema, "gate_R": "NOT RUN", "physical_scale": "unverified",
        "capture_timebase": "unverified", "torch": torch.__version__,
    }
    print(json.dumps({k: v for k, v in receipt.items() if k != "schema"}))
    return receipt, data


def main():
    # Modal's status output includes Unicode even when Windows pipes use cp1252.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    manifest = json.loads((INPUT_EVIDENCE / "input.json").read_text())
    frames = []
    for frame in manifest["sample"]["frames"]:
        data = (FRAME_EVIDENCE / frame["path"]).read_bytes()
        assert len(data) == frame["bytes"]
        assert hashlib.sha256(data).hexdigest() == frame["sha256"]
        frames.append((data, frame["sha256"]))
    assert len(frames) == 4 and manifest["clip_id"] == "RM02"
    requirements = Path(__file__).with_name("requirements-linux-py311.txt").read_text()
    assert CODE_REV in requirements and "numpy==2.2.6" in requirements
    started = time.time()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    def record_guard(state):
        atomic_json(Path(os.environ["RM02_WATCHDOG_RECEIPT"]), state)

    with modal.enable_output():
        receipt, data = asyncio.run(guarded_probe(
            app, probe, (frames, requirements, CODE_REV, WEIGHT_REV), record_guard,
            total_seconds=float(os.environ["RM02_CHILD_BUDGET"]),
        ))
    local = EVIDENCE / "local"
    local.mkdir(parents=True, exist_ok=True)
    (local / "RM02-mapanything.npz").write_bytes(data)
    receipt.update(client_start_unix=started, client_end_unix=time.time())
    (EVIDENCE / "gpu-result.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
