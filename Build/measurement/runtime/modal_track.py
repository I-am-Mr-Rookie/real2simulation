"""S07b: one bounded private Modal GPU tracking run on an approved clip prefix (default ST03).

Run: uv run --python 3.12 --with modal==1.6.3 --env-file <root>/.env modal run Build/measurement/runtime/modal_track.py
  Defaults reproduce accepted orch14 ST03 f58-76 "apple" obj 2 (refuses to overwrite existing --out).
  Other approved clips: ... modal_track.py --clip RM04 --first 0 --last 7 --prompt chair --object-id 0 --out evidence/... [--masks]
Ephemeral app only (never deploy). Returns centroids/provenance; masks only as opt-in COCO RLE, never media.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import modal

HERE = Path(__file__).resolve().parent
MEASUREMENT = HERE.parent
REPO = HERE.parents[2] if len(HERE.parents) > 2 else HERE  # container copy is /root/modal_track.py; REPO is local-only
CANONICAL = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon")
CLIP = CANONICAL / "test-data/public/ST03.mp4"
APPROVAL = "evidence/owner/S02/APPROVAL.md"
DEFAULT_OUT = "evidence/S07/S07b/orch14/result.json"
SAM_REV = "f1647e8d0c1d280991f4d1b7d974c2704537fe66"
CKPT_REPO, CKPT_FILE = "facebook/sam3.1", "sam3.1_multiplex.pt"
CKPT_REV = "daa63191845a41281374e725f4c9e51c7a824460"
FIRST, LAST = 58, 76  # continuous unoccluded fall f58-76 (clips.csv); prefix ends at frozen split
# orch14 run1 (prefix-only stream boxes): obj 0/1 are static ground apples (y~0.82-0.84); obj 2 falls y 0.32->0.77.
OBJECT_ID = 2


def mask_rle(mask):
    """COCO uncompressed RLE (column-major, starts with a zero run); pycocotools-decodable."""
    import numpy as np
    flat = np.asarray(mask, dtype=bool).ravel(order="F")
    bounds = np.concatenate(([0], np.flatnonzero(np.diff(flat)) + 1, [flat.size]))
    counts = np.diff(bounds).tolist()
    return {"size": list(np.shape(mask)), "counts": ([0] + counts) if flat.size and flat[0] else counts}


def chunk_spans(n, chunk):
    """[start, end) spans; consecutive spans share one frame (re-seed); every span >= 3 frames (tracking._context)."""
    if chunk < 3 or n < 3:
        raise ValueError("chunk >= 3 and >= 3 frames required")
    spans, start = [], 0
    while True:
        end = min(start + chunk, n)
        if n - end + 1 < 3:  # a tail shorter than 3 frames joins this span
            end = n
        spans.append((start, end))
        if end == n:
            return spans
        start = end - 1


def iou(a, b):
    import numpy as np
    union = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / union) if union else 0.0


MIN_RESEED_IOU = 0.5


def track_chunks(predictor, frames_dir, metadata, frame_map, frame_sha, prompt, object_id, chunk,
                 after_chunk=lambda k: {}):
    """Memory-bounded long segment: one SAM session per chunk (VRAM grows with session frames). Chunk k+1 starts on
    chunk k's last frame and keeps the text-prompt object whose mask best overlaps (IoU >= MIN_RESEED_IOU) chunk k's
    selected last-frame mask. Fails closed: below threshold, the remaining frames stay missing (never filled).
    Returns (merged per-frame responses holding only the selected object as object_id, per-chunk provenance)."""
    import shutil
    import time
    import numpy as np
    frames_dir = Path(frames_dir)
    height, width = metadata["height_px"], metadata["width_px"]
    selected, chunks, previous = {}, [], None
    for k, (start, end) in enumerate(chunk_spans(len(frame_map), chunk)):
        t = time.monotonic()
        part = frames_dir.parent / f"chunk{k:03d}"
        part.mkdir()
        for i in range(start, end):
            shutil.copyfile(frames_dir / f"{i:05d}.jpg", part / f"{i - start:05d}.jpg")
        session = predictor.handle_request(request={"type": "start_session", "resource_path": str(part)})["session_id"]
        try:
            predictor.handle_request(request={"type": "add_prompt", "session_id": session,
                                              "frame_index": 0, "text": prompt})
            rows = [(r["frame_index"], np.asarray(r["outputs"]["out_obj_ids"]),
                     np.asarray(r["outputs"]["out_binary_masks"]), r["outputs"].get("out_boxes_xywh", []))
                    for r in predictor.handle_stream_request(request={
                        "type": "propagate_in_video", "session_id": session,
                        "propagation_direction": "forward", "start_frame_index": 0})]
        finally:
            predictor.handle_request(request={"type": "close_session", "session_id": session})
        shutil.rmtree(part)
        if k == 0:
            chosen, score = object_id, None
        else:
            first = next((r for r in rows if r[0] == 0), None)
            cands = [] if first is None or previous is None else [
                (iou(m, previous), int(i)) for i, m in zip(first[1], first[2])]
            score, chosen = max(cands, default=(0.0, None))
        seal = [[frame_map[i][0], frame_map[i][1], frame_sha[i]] for i in range(start, end)]
        prov = {"chunk": k, "local_frames": [start, end - 1], "source_frames": [seal[0][0], seal[-1][0]],
                "pts_s": [seal[0][1], seal[-1][1]], "local_object_id": chosen, "reseed_iou": score,
                "seal_sha256": hashlib.sha256(json.dumps(seal).encode()).hexdigest()}
        if chosen is None or (k and score < MIN_RESEED_IOU):
            prov["stopped"] = "re-seed IoU below threshold; remaining frames missing"
            chunks.append({**prov, **after_chunk(k), "elapsed_s": round(time.monotonic() - t, 1)})
            break
        for local, ids, masks, boxes in rows:
            hit = np.flatnonzero(ids == chosen)
            if len(hit) and masks[hit[0]].any():  # overlap frame keeps the earlier chunk's propagated mask
                selected.setdefault(start + local, (masks[hit[0]].astype(bool), list(boxes[hit[0]])))
        previous = selected[end - 1][0] if end - 1 in selected else None
        prov["observed"] = sum(start <= i < end for i in selected)
        chunks.append({**prov, **after_chunk(k), "elapsed_s": round(time.monotonic() - t, 1)})
    none_ids, none_masks = np.zeros(0, dtype=np.int64), np.zeros((0, height, width), dtype=bool)
    merged = [{"frame_index": i, "outputs": {
        "out_obj_ids": np.array([object_id]) if i in selected else none_ids,
        "out_binary_masks": selected[i][0][None] if i in selected else none_masks,
        "out_boxes_xywh": [selected[i][1]] if i in selected else []}} for i in range(len(frame_map))]
    return merged, chunks


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
    gpu=["L4", "A10G"], cpu=2, memory=16384, timeout=1500, startup_timeout=300,
    retries=0, max_containers=1, scaledown_window=2, single_use_containers=True,
    secrets=[modal.Secret.from_name("real2simulation-hf-read")],
)
def track(frames, metadata, frame_map, prompt, object_id=OBJECT_ID, masks=False, chunk=0):
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

        if masks:
            out["masks"] = []

        def log(resp):  # per-frame object ids/boxes for object-id audit; RLE masks opt-in
            o = resp.get("outputs", {})
            out["stream"].append([resp.get("frame_index"),
                                  [int(i) for i in o.get("out_obj_ids", [])],
                                  [[round(float(v), 4) for v in b] for b in o.get("out_boxes_xywh", [])]])
            if masks:
                out["masks"].append([resp.get("frame_index"), {
                    str(int(i)): mask_rle(m) for i, m in
                    zip(o.get("out_obj_ids", []), o.get("out_binary_masks", []))}])

        def logged_stream(request):
            for resp in stream(request):
                log(resp)
                yield resp
        if not chunk:  # chunk mode logs the merged selected-object stream instead
            predictor.handle_stream_request = logged_stream
        out["load_s"] = round(time.monotonic() - t, 1)
        out["stages"].append("model_loaded")
        t = time.monotonic()
        if chunk:
            from measurement.tracking import sanitize_responses

            def vram(k):
                peak = torch.cuda.max_memory_allocated()
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats()
                return {"peak_vram_bytes": peak}
            merged, out["chunks"] = track_chunks(predictor, prefix, metadata, frame_map, [s for _, s in frames],
                                                 prompt, object_id, chunk, vram)
            for resp in merged:  # same row format as logged_stream; selected object only, as object_id
                log(resp)
            result = sanitize_responses(merged, metadata, frame_map, object_id=object_id)
            out["peak_vram_bytes"] = max(c["peak_vram_bytes"] for c in out["chunks"])
        else:
            result = track_training(predictor, prefix, metadata, frame_map, prompt=prompt,
                                    object_id=object_id, execute=True)
            out["peak_vram_bytes"] = torch.cuda.max_memory_allocated()
        out["track_s"] = round(time.monotonic() - t, 1)
        out["record"] = result.training_record()
        out["stages"].append("tracked")
    except BaseException:
        out["error"] = traceback.format_exc()[-4000:]
    out["remote_elapsed_s"] = round(time.monotonic() - start, 1)
    return json.dumps(out, default=str)  # plain JSON: local client has no torch to unpickle


def _frames(clip=CLIP, first=FIRST, last=LAST):
    tmp = Path(tempfile.mkdtemp(prefix="s07b-orch14-"))  # outside repo; media never committed
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-vf",
                    f"select=between(n\\,{first}\\,{last})", "-fps_mode", "passthrough",
                    "-q:v", "2", "-start_number", "0", str(tmp / "%05d.jpg")], check=True)
    pts = _pts(clip, last)
    files = sorted(tmp.glob("*.jpg"))
    assert len(files) == last - first + 1 and len(pts) == last + 1, (len(files), len(pts))
    data = [p.read_bytes() for p in files]
    return ([(d, hashlib.sha256(d).hexdigest()) for d in data],
            [(first + i, pts[first + i]) for i in range(len(files))])


REORDER_MARGIN = 32  # packets past last: >= any B-frame reorder depth (ST03 has_b_frames=2)


def _pts(clip, last):
    """Presentation PTS of frames 0..last. read_intervals #N counts packets in DECODE order, so
    reading exactly last+1 packets drops trailing B-frames (orch14 ST03 f76 got f77's PTS)."""
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                   "-show_entries", "frame=pts_time", "-of", "csv=p=0",
                                   "-read_intervals", f"%+#{last + 1 + REORDER_MARGIN}", str(clip)],
                                  text=True)
    pts = [float(x.strip().strip(",")) for x in out.split() if x.strip()][:last + 1]
    assert all(a < b for a, b in zip(pts, pts[1:])), "non-monotonic presentation PTS"
    return pts


def plan(clip="ST03", first=FIRST, last=LAST, prompt="apple", out=DEFAULT_OUT):
    """Validate a run before any GPU spend; returns (clip_path, metadata_without_sha, dest)."""
    approved = re.search(r"\*\*Approved IDs:\*\*\s*([A-Z0-9,]+)", (REPO / APPROVAL).read_text("utf-8"))
    if not approved or clip not in approved.group(1).split(","):
        raise ValueError(f"{clip} not in scoped owner approval {APPROVAL}")
    if type(first) is not int or type(last) is not int or not 0 <= first <= last - 2:
        raise ValueError("need integer 0 <= first and at least three frames")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("nonempty text prompt required")
    dest = (REPO / out).resolve()
    if dest.exists():
        raise FileExistsError(f"refusing to overwrite existing evidence {dest}")
    with (REPO / "clips.csv").open(encoding="utf-8", newline="") as stream:
        row = next((r for r in csv.DictReader(stream) if r["clip_id"] == clip), None)
    if row is None:
        raise ValueError(f"{clip} missing from clips.csv")
    path = CLIP if clip == "ST03" else CANONICAL / row["local_path"]
    width, height = map(int, subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(path)], text=True).strip().split(",")[:2])
    metadata = {
        "clip_id": clip, "licence": f"{row['licence']} {row['licence_url']}",
        "provenance": f"{row['source_url']} ({row['creator']}); local {width}x{height} rendition",
        "motion": row["experiment"],
        "approval": {"scope": "scene_tracking", "evidence": APPROVAL},
        "width_px": width, "height_px": height, "last_training_frame": last,
    }
    return path, metadata, dest


@app.local_entrypoint()
def main(clip: str = "ST03", first: int = FIRST, last: int = LAST, prompt: str = "apple",
         object_id: int = OBJECT_ID, out: str = DEFAULT_OUT, masks: bool = False, chunk: int = 0):
    if type(object_id) is not int or object_id < 0:  # fail before frames/GPU, not inside the container
        raise ValueError("nonnegative integer object_id required")
    if chunk:
        chunk_spans(last - first + 1, chunk)  # validate before frames/GPU
    path, metadata, dest = plan(clip, first, last, prompt, out)
    frames, frame_map = _frames(path, first, last)
    if os.environ.get("S07B_DRY"):
        print(json.dumps({"frames": len(frames), "frame_map": frame_map}))
        return
    with path.open("rb") as stream:
        metadata["source_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
    sys.path.insert(0, str(REPO))
    from Build.guardrails.standalone import admit_standalone
    admit_standalone("modal-track:" + clip)
    result = json.loads(track.remote(frames, metadata, frame_map, prompt, object_id, masks, chunk))
    result["frame_sha256"] = [sha for _, sha in frames]
    result["frame_map"] = frame_map
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("x") as stream:  # never overwrite accepted evidence
        stream.write(json.dumps(result, indent=1))
    print(json.dumps({k: result.get(k) for k in ("stages", "gpu", "preflight_exit", "checkpoint", "error")})[:3000])

