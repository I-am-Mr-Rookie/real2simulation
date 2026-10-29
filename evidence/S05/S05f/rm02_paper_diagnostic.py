"""S05f identity diagnostic for the only standard-object candidate seen: RM02 view0 right paper sheet.

NOT a Gate R measurement. Tests whether the sheet can be identified as ISO 216 A4 (aspect 297/210=1.414)
rather than e.g. US Letter (279.4/215.9=1.294) using the scale-free 3D aspect of the annotated corners.
Corners were hand-picked on evidence/S05/S05f/rm02-view0-paper-zoom.png (NPZ 294x518 pixel grid); +-2 px jitter.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Build/reconstruction/spike"))
import scene_frame as sf  # noqa: E402

CORNERS = [[226, 257], [202, 343], [217, 435], [247, 357]]  # near-left, far-left, far-right, near-right (row, col)


def edges(P, C):
    p = [P[tuple(c)] for c in C]
    a = (np.linalg.norm(p[0] - p[1]) + np.linalg.norm(p[2] - p[3])) / 2
    b = (np.linalg.norm(p[1] - p[2]) + np.linalg.norm(p[3] - p[0])) / 2
    return max(a, b), min(a, b)


def main():
    m = json.loads(Path("evidence/S05/S05d/manifest.json").read_text())[0]
    assert m["clip_id"] == "RM02"
    views = sf.load_views(m["npz"])
    P = views[0]["pts_img"]
    long_, short = edges(P, CORNERS)
    rng = np.random.default_rng(0)
    jit = [edges(P, [[r + int(rng.integers(-2, 3)), c + int(rng.integers(-2, 3))] for r, c in CORNERS])
           for _ in range(500)]
    asp = np.array([a / b for a, b in jit])
    lo, hi = np.percentile(asp, [5, 95])
    n, meta = sf.a4_plane(views, {"view": 0, "corners": CORNERS, "source": "diagnostic only"})
    out = {"clip": "RM02", "view": 0, "npz_sha256": hashlib.sha256(Path(m["npz"]).read_bytes()).hexdigest(),
           "image_rows_cols": [294, 518], "corners_row_col": CORNERS, "corner_jitter_px": 2,
           "model_long_edge": float(long_), "model_short_edge": float(short),
           "aspect": float(long_ / short), "aspect_p5_p95": [float(lo), float(hi)],
           "A4_aspect": 297 / 210, "US_letter_aspect": 279.4 / 215.9,
           "A4_inside_interval": bool(lo <= 297 / 210 <= hi),
           "sheet_plane_fit": {k: meta[k] for k in ("samples", "rms_residual")},
           "decision": "ABSTAIN",
           "why": "3D aspect interval excludes A4 1.414 (and includes US Letter 1.294); paper size unspecified by source; "
                  "identity ambiguous -> owner rule Q-S05e: abstain. No scale/orientation counted."}
    Path(__file__).with_name("rm02-paper-diagnostic.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
