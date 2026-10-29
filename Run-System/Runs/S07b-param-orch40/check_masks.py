"""S07b-param-orch40: offline re-check of live RLE masks through the accepted tracking.sanitize_responses."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.measurement.tracking import sanitize_responses  # noqa: E402


def decode(rle):  # COCO uncompressed RLE: column-major, counts alternate starting with zeros
    h, w = rle["size"]
    flat = np.repeat(np.arange(len(rle["counts"])) % 2 == 1, rle["counts"])
    assert flat.size == h * w, "RLE length mismatch"
    return flat.reshape(w, h).T


res = json.loads((ROOT / sys.argv[1]).read_text("utf-8"))
rec = res["record"]
md = {k: v for k, v in rec.items() if k not in ("frames", "tracking")}
responses = []
for index, per_obj in res["masks"]:
    ids = sorted(per_obj, key=int)
    responses.append({"frame_index": index, "outputs": {
        "out_obj_ids": np.array([int(i) for i in ids], dtype=np.int64),
        "out_binary_masks": np.stack([decode(per_obj[i]) for i in ids]) if ids
        else np.zeros((0, rec["height_px"], rec["width_px"]), bool)}})
track = sanitize_responses(responses, md, [tuple(x) for x in res["frame_map"]], object_id=0)
got = [(f["frame_index"], f["pts_s"], round(f["x_px"], 6), round(f["y_px"], 6))
       for f in track.training_record()["frames"]]
want = [(f["frame_index"], f["pts_s"], round(f["x_px"], 6), round(f["y_px"], 6)) for f in rec["frames"]]
print(json.dumps({"frames": len(got), "objects_per_frame": sorted({len(p) for _, p in res["masks"]}),
                  "centroids_match_record": got == want}))
assert got == want

