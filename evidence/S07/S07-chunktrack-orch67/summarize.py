"""Measured coverage/VRAM/estimated cost of a chunked modal_track result; validate_segment called, not edited.
Usage: python evidence/S07/S07-chunktrack-orch67/summarize.py <result.json> <prompt> <object_id> <axis x|y>"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.gpu.cost_log import cost  # noqa: E402
from Build.pipeline.gpu_stages import StageError, validate_segment  # noqa: E402


def check(out, prompt, object_id, keep):
    """validate_segment assumes stream index == source index (S12e finding); map relative k -> frame_map[k]."""
    fmap = out["frame_map"]
    doc = {**out, "frame_map": [fmap[k] for k in keep],
           "stream": [[fmap[r[0]][0], *r[1:]] for r in out["stream"] if r[0] in keep],
           "masks": [[fmap[r[0]][0], r[1]] for r in out.get("masks", []) if r[0] in keep]}
    try:
        return "OK", validate_segment(json.dumps(doc), prompt, object_id)["frames"]
    except StageError as error:
        return f"rejected: {error}", []


def main(path, prompt, object_id, axis):
    out = json.loads(Path(path).read_text(encoding="utf-8"))
    s = {k: out.get(k) for k in ("stages", "gpu", "error", "peak_vram_bytes", "load_s", "track_s", "remote_elapsed_s")}
    fmap, rec = out.get("frame_map", []), out.get("record") or {}
    s["frames_total"] = len(fmap)
    if "tracked" in (out.get("stages") or []):
        observed = {k for k, r in enumerate(out["stream"]) if object_id in r[1]}
        s["frames_observed"] = len(observed)
        s["validate_full"], _ = check(out, prompt, object_id, set(range(len(fmap))))
        s["validate_observed_subset"], frames = check(out, prompt, object_id, observed)
        if frames:
            s["observed_pts_span_s"] = [frames[0]["pts_s"], frames[-1]["pts_s"]]
            v = [f["centroid_px"][0 if axis == "x" else 1] for f in frames]
            d = [b - a for a, b in zip(v, v[1:]) if abs(b - a) > 0.5]  # ignore sub-pixel jitter
            s[f"{axis}_reversals"] = sum(1 for a, b in zip(d, d[1:]) if a * b < 0)
            s[f"{axis}_range_px"] = [round(min(v), 1), round(max(v), 1)]
        ch = out.get("chunks") or []
        s["chunks"] = len(ch)
        s["chunk_peak_vram_bytes_max"] = max((c["peak_vram_bytes"] for c in ch), default=None)
        s["reseed_iou_min"] = min((c["reseed_iou"] for c in ch if c["reseed_iou"] is not None), default=None)
        s["stopped"] = [c for c in ch if "stopped" in c]
    gpu = "L4" if "L4" in (out.get("gpu") or "") else "A10G"
    s["estimated_usd_remote_elapsed_only"] = cost(out.get("remote_elapsed_s") or 0, gpu, 2, 16)["total_usd"]
    return s


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]), indent=1))
