"""Hosted Meta SAM 3.1 tracker (Meta Model API /v1/files + /v1/responses).

Network only in upload() and track(); parsing and selection are pure. Points are box centres in source
pixels (x right, y down), not mask centroids, metric positions or centres of mass. Masks are not decoded.
Missing object on a frame stays missing. Output plugs into the S07a record shape (tracking.TrainingTrack).
Transport is stdlib urllib (no requests on the API image); every track() call reserves/settles the global daily cap.
"""
import json
import math
import os
import re
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

USD_PER_FRAME = 0.20 / 1000  # sam-3.1 price, $0.20 per 1k video frames processed
MAX_FRAMES = 3600  # default reservation: 120 s upload limit at 30 fps
_FRAME = re.compile(r"<(\d+)f>")
_OBJECT = re.compile(r"(\d+)<\|box;([^|]*)\|>")
# Mask payloads may contain "|" and ">", so a mask ends only where the next object or the line ends.
_MASK = re.compile(r"<\|mask;.*?\|>(?=,\d+<\|box;|$)", re.M)


def _base():
    return os.environ.get("MODEL_API_BASE_URL", "https://api.meta.ai/v1").rstrip("/")


def _headers():
    # N23: Railway egress cannot see Meta models; MODEL_PROXY_TOKEN set means the base URL is Build/gpu/meta_proxy.py
    return {"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}", "X-R2S-Proxy": os.environ.get("MODEL_PROXY_TOKEN", "")}


def _post(path, data, content_type, timeout):
    request = Request(f"{_base()}{path}", data=data, method="POST", headers={**_headers(), "Content-Type": content_type})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read())
    except HTTPError as exc:  # status only; the body may echo request details
        raise RuntimeError(f"Meta Model API HTTP {exc.code} on {path}") from None


def upload(path, timeout=300):
    """POST /files (purpose user_data) -> file id."""
    b = uuid.uuid4().hex
    with open(path, "rb") as f:  # uploads are capped at 200 MB by N03, so one in-memory body is fine
        data = (f'--{b}\r\nContent-Disposition: form-data; name="purpose"\r\n\r\nuser_data\r\n--{b}\r\n'
                f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\n'
                f'Content-Type: application/octet-stream\r\n\r\n').encode() + f.read() + f"\r\n--{b}--\r\n".encode()
    return _post("/files", data, f"multipart/form-data; boundary={b}", timeout)["id"]


def box_prompt(object_id, box, width, height, frame=0):
    """Box prompt (x1, y1, x2, y2 inclusive source pixels) on one frame, Meta token grammar."""
    x1, y1, x2, y2 = (int(v) for v in box)
    return f"<{frame}f>{int(object_id)}<|box;x1={x1};y1={y1};x2={x2};y2={y2};w={width};h={height}|>"


def point_prompt(object_id, points, width, height, frame=0):
    """points: [(x, y, positive)], e.g. one user click on the first frame."""
    tokens = "".join(("" if pos else "-") + f"<|point;x={int(x)};y={int(y)};w={width};h={height}|>"
                     for x, y, pos in points)
    return f"<{frame}f>{int(object_id)}{tokens}"


def track(file_id, prompt, timeout=900, max_frames=MAX_FRAMES, cap_path=None):
    """One sam-3.1 call: prompt is a noun phrase or a box/point prompt. Returns the raw response JSON.

    Reserves max_frames x price on the daily cap first (raises CapExceeded before any spend); settles the billed
    video_frames_processed, or the full reservation when the call fails (cost unknown, so count it).
    """
    from Build.guardrails import daily_cap
    cost = max_frames * USD_PER_FRAME
    rid = daily_cap.reserve("Meta Model API", cost, f"sam-3.1 track {max_frames} frames", path=cap_path)
    body = {"model": "sam-3.1", "metadata": {"mask_encoding": "one_bit"},
            "input": [{"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": prompt}, {"type": "input_video", "file_id": file_id}]}]}
    try:
        response = _post("/responses", json.dumps(body).encode(), "application/json", timeout)
        cost = int((response.get("usage") or {}).get("video_frames_processed") or 0) * USD_PER_FRAME
        return response
    finally:
        daily_cap.settle(rid, cost, path=cap_path)


def output_text(response):
    if response.get("status") != "completed" or response.get("error"):
        raise ValueError(f"sam-3.1 response not completed: {response.get('status')} {response.get('error')}")
    return "".join(c.get("text", "") for item in response.get("output", []) if item.get("type") == "message"
                   for c in item.get("content", []) if c.get("type") == "output_text")


def parse(text):
    """-> ({frame: {object_id: (x1, y1, x2, y2)}}, (width, height)); every object on every line."""
    frames, size = {}, None
    for line in text.splitlines():
        m = _FRAME.match(line.strip())
        if not m:
            continue
        k = int(m.group(1))
        if k in frames:
            raise ValueError(f"duplicate frame {k}")
        frames[k] = {}
        for oid, fields in _OBJECT.findall(_MASK.sub("", line.strip()[m.end():])):
            v = dict(kv.split("=", 1) for kv in fields.split(";"))
            box = tuple(float(v[key]) for key in ("x1", "y1", "x2", "y2"))
            wh = (int(v["w"]), int(v["h"]))
            if size not in (None, wh) or not all(map(math.isfinite, box)) or int(oid) in frames[k]:
                raise ValueError(f"frame {k}: inconsistent size, nonfinite box or duplicate id {oid}")
            size = wh
            frames[k][int(oid)] = box
    return frames, size


def _centre(box):
    return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2


def travel(frames):
    """{object_id: max distance of its box centre from its first observed centre (px)}; jitter-robust."""
    first, out = {}, {}
    for k in sorted(frames):
        for oid, box in frames[k].items():
            c = _centre(box)
            out[oid] = max(out.get(oid, 0.0), math.dist(c, first.setdefault(oid, c)))
    return out


def result(response, object_id=None):
    """Parsed track of one object: the given id, else the moving one (largest centroid travel)."""
    frames, size = parse(output_text(response))
    moves = travel(frames)
    if not moves:
        raise ValueError("sam-3.1 returned no objects")
    oid = max(moves, key=moves.get) if object_id is None else object_id
    if oid not in moves:
        raise ValueError(f"object {oid} not in response")
    n = int((response.get("usage") or {}).get("video_frames_processed") or 0)
    return {"object_id": oid, "travel_px": moves, "width": size[0], "height": size[1], "frame_count": len(frames),
            "points": [(k, *_centre(frames[k][oid]), frames[k][oid]) for k in sorted(frames) if oid in frames[k]],
            "missing": [k for k in sorted(frames) if oid not in frames[k]],
            "video_frames_processed": n, "cost_usd": n * USD_PER_FRAME}


def to_record(track_result, metadata, frame_map):
    """S07a-style record (metadata + frames x_px/y_px) for inputs.validate_input / real2sim.boundary.split.

    frame_map[k] = (source_frame_index, pts_s) for decoded video frame k; no clock is inferred here.
    """
    if track_result["frame_count"] != len(frame_map):
        raise ValueError(f"response has {track_result['frame_count']} frames, frame_map {len(frame_map)}")
    if (metadata.get("width_px"), metadata.get("height_px")) != (track_result["width"], track_result["height"]):
        raise ValueError("response size differs from the source dimensions")
    record = dict(metadata)
    record["frames"] = [{"frame_index": frame_map[k][0], "pts_s": frame_map[k][1], "x_px": x, "y_px": y}
                        for k, x, y, _ in track_result["points"]]
    record["tracking"] = {"adapter": "sam3.1-hosted-meta-model-api", "object_id": track_result["object_id"],
                          "point_method": "box_centre",
                          "missing_frames": [frame_map[k][0] for k in track_result["missing"]]}
    return record
