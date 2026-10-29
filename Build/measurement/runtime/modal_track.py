"""S07b: one bounded private Modal GPU tracking run on approved ST03 prefix.

Run: uv run --python 3.12 --with modal==1.6.3 --env-file <root>/.env modal run Build/measurement/runtime/modal_track.py
Ephemeral app only (never deploy). Returns centroids/provenance, never masks/media.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import modal

HERE = Path(__file__).resolve().parent
MEASUREMENT = HERE.parent
CANONICAL = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon")
CLIP = CANONICAL / "test-data/public/ST03.mp4"
SAM_REV = "f1647e8d0c1d280991f4d1b7d974c2704537fe66"
CKPT_REPO, CKPT_FILE = "facebook/sam3.1", "sam3.1_multiplex.pt"
CKPT_REV = "daa63191845a41281374e725f4c9e51c7a824460"
FIRST, LAST = 58, 76  # continuous unoccluded fall f58-76 (clips.csv); prefix ends at frozen split
# orch14 run1 (prefix-only stream boxes): obj 0/1 are static ground apples (y~0.82-0.84); obj 2 falls y 0.32->0.77.
OBJECT_ID = 2

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git")
    .add_local_file(HERE / "requirements-linux-py312.txt", "/tmp/req.txt", copy=True)
    .run_commands(
        "pip install --no-cache-dir --require-hashes --no-deps -r /tmp/req.txt",
        f"git clone https://github.com/facebookresearch/sam3 /opt/sam3 && git -C /opt/sam3 checkout {SAM_REV}",
        "pip install --no-cache-dir --no-deps --no-build-isolation /opt/sam3",
        # sam3 model_builder imports pkg_resources, removed from the locked setuptools 84.
        "pip install --no-cache-dir --no-deps setuptools==80.9.0",
    )
    # Runtime imports not declared by sam3 base deps (found by run5); separate cached layer.
    .run_commands("pip install --no-cache-dir --no-deps einops==0.8.1 psutil==7.1.0 pycocotools==2.0.11")
    .add_local_file(HERE / "resolve_imports.py", "/tmp/resolve_imports.py", copy=True)
    .run_commands("python /tmp/resolve_imports.py && pip freeze > /tmp/freeze.txt")
    .add_local_dir(MEASUREMENT, "/root/measurement", ignore=["__pycache__"])
)
app = modal.App("s07b-orch14-sam31-track", image=image)


@app.function(
    gpu=["L4", "A10G"], cpu=2, memory=16384, timeout=900, startup_timeout=300,
    retries=0, max_containers=1, scaledown_window=2, single_use_containers=True,
    secrets=[modal.Secret.from_name("real2simulation-hf-read")],
)
def track(frames, metadata, frame_map, prompt):
    import sys
    import time
    import traceback

    out = {"stages": []}
    start = time.monotonic()
    try:
        out["gpu"] = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
             "--format=csv,noheader"], text=True, timeout=15).strip()
        pf = subprocess.run([sys.executable, "/root/measurement/runtime/preflight.py",
                             "/opt/sam3", "--json"], capture_output=True, text=True)
        out["preflight_exit"] = pf.returncode
        try:
            out["preflight"] = json.loads(pf.stdout)
        except ValueError:
            out["preflight"] = (pf.stdout + pf.stderr)[-3000:]
        out["stages"].append("preflight")
        import torch
        out["torch"] = [torch.__version__, torch.version.cuda, torch.cuda.is_available()]
        out["freeze"] = Path("/tmp/freeze.txt").read_text().split()
        from huggingface_hub import hf_hub_download
        t = time.monotonic()
        path = Path(hf_hub_download(CKPT_REPO, CKPT_FILE, revision=CKPT_REV,
                                    local_dir="/tmp/ckpt", token=os.environ["HF_TOKEN"]))
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        out["checkpoint"] = {"repo": CKPT_REPO, "file": CKPT_FILE, "revision": CKPT_REV,
                             "bytes": path.stat().st_size, "sha256": digest,
                             "download_s": round(time.monotonic() - t, 1)}
        out["stages"].append("checkpoint")
        prefix = Path("/tmp/prefix")
        prefix.mkdir()
        for i, (data, sha) in enumerate(frames):
            if hashlib.sha256(data).hexdigest() != sha:
                raise ValueError("frame SHA256 mismatch after transfer")
            (prefix / f"{i:05d}.jpg").write_bytes(data)
        sys.path.insert(0, "/root")
        from measurement.tracking import load_local_predictor, track_training
        t = time.monotonic()
        import functools
        import sam3.model_builder as builder
        # FA3 kernel is Hopper-only and not installed (run8 failed in sam3/perflib/fa3.py on A10/L4).
        build = builder.build_sam3_multiplex_video_predictor
        builder.build_sam3_multiplex_video_predictor = lambda **kw: build(
            **{**kw, "use_fa3": False})
        out["builder_override"] = "use_fa3=False"
        predictor = load_local_predictor(path, execute=True)  # re-verifies size+SHA
        import inspect
        init = predictor.model.init_state
        if "offload_state_to_cpu" not in inspect.signature(init).parameters:
            # Upstream f1647e8 base start_session always passes it; multiplex init_state rejects it (run7).
            predictor.model.init_state = lambda **kw: init(
                **{k: v for k, v in kw.items() if k != "offload_state_to_cpu"})
            out["shim"] = "dropped unsupported offload_state_to_cpu=False kwarg"
        handle, out["requests"] = predictor.handle_request, []

        def logged(request):  # diagnostic: object count per request (run9 0-batch error)
            resp = handle(request)
            ids = (resp or {}).get("outputs", {}).get("out_obj_ids") if isinstance(resp, dict) else None
            out["requests"].append([request["type"], None if ids is None else len(ids)])
            return resp
        predictor.handle_request = logged
        stream, out["stream"] = predictor.handle_stream_request, []

        def logged_stream(request):  # per-frame object ids/boxes (no masks) for object-id audit
            for resp in stream(request):
                o = resp.get("outputs", {})
                out["stream"].append([resp.get("frame_index"),
                                      [int(i) for i in o.get("out_obj_ids", [])],
                                      [[round(float(v), 4) for v in b] for b in o.get("out_boxes_xywh", [])]])
                yield resp
        predictor.handle_stream_request = logged_stream
        out["load_s"] = round(time.monotonic() - t, 1)
        out["stages"].append("model_loaded")
        t = time.monotonic()
        result = track_training(predictor, prefix, metadata, frame_map, prompt=prompt,
                                object_id=OBJECT_ID, execute=True)
        out["track_s"] = round(time.monotonic() - t, 1)
        out["peak_vram_bytes"] = torch.cuda.max_memory_allocated()
        out["record"] = result.training_record()
        out["stages"].append("tracked")
    except BaseException:
        out["error"] = traceback.format_exc()[-4000:]
    out["remote_elapsed_s"] = round(time.monotonic() - start, 1)
    return json.dumps(out, default=str)  # plain JSON: local client has no torch to unpickle


def _frames():
    tmp = Path(tempfile.mkdtemp(prefix="s07b-orch14-"))  # outside repo; media never committed
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(CLIP), "-vf",
                    f"select=between(n\\,{FIRST}\\,{LAST})", "-fps_mode", "passthrough",
                    "-q:v", "2", "-start_number", "0", str(tmp / "%05d.jpg")], check=True)
    pts = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                   "-show_entries", "frame=pts_time", "-of", "csv=p=0",
                                   "-read_intervals", f"%+#{LAST + 1}", str(CLIP)], text=True)
    pts = [float(x.strip().strip(",")) for x in pts.split() if x.strip()]
    files = sorted(tmp.glob("*.jpg"))
    assert len(files) == LAST - FIRST + 1 and len(pts) == LAST + 1, (len(files), len(pts))
    data = [p.read_bytes() for p in files]
    return ([(d, hashlib.sha256(d).hexdigest()) for d in data],
            [(FIRST + i, pts[FIRST + i]) for i in range(len(files))])


@app.local_entrypoint()
def main():
    frames, frame_map = _frames()
    if os.environ.get("S07B_DRY"):
        print(json.dumps({"frames": len(frames), "frame_map": frame_map}))
        return
    with CLIP.open("rb") as stream:
        source_sha = hashlib.file_digest(stream, "sha256").hexdigest()
    metadata = {
        "clip_id": "ST03", "licence": "Pexels License https://www.pexels.com/license/",
        "provenance": "https://www.pexels.com/video/woman-dropping-apple-on-ground-12723966/ (Roman Odintsov); local 720x1366 rendition",
        "motion": "free_fall", "source_sha256": source_sha,
        "approval": {"scope": "scene_tracking", "evidence": "evidence/owner/S02/APPROVAL.md"},
        "width_px": 720, "height_px": 1366, "last_training_frame": LAST,
    }
    out = json.loads(track.remote(frames, metadata, frame_map, "apple"))
    out["frame_sha256"] = [sha for _, sha in frames]
    out["frame_map"] = frame_map
    dest = MEASUREMENT.parents[1] / "evidence/S07/S07b/orch14/result.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out.get(k) for k in ("stages", "gpu", "preflight_exit", "checkpoint", "error")})[:3000])

