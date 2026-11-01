"""S15bb: copy the RECORDED S07h/S07i uncertainty budget (frozen into S07m v1) into owner_clips.json clips.<ID>.u_budget.

S07h/S07i rule (evidence/S07/S07i/measure_own01.py): u_total = hypot(u_fit_detection, u_timing, u_scale, u_model_centroid_vs_box),
u_scale = g * hypot(u_width_px / mean_px, EDGE_U_M / length_m). Idempotent; asserts the copied terms reproduce the recorded total.
Run from repo root: python -B evidence/S15bb/add_u_budget.py
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWN = ROOT / "Build/api/workspace/owner_clips.json"
EDGE_U_M = 0.0005  # = evidence/S07/S07i/measure_own01.py EDGE_U_M (ruler-reading ASSUMPTION used by S07h/S07m)


def budgets(root=ROOT):
    h = json.loads((root / "evidence/S07/S07h/results.json").read_text(encoding="utf-8"))["clips"]
    srcs = {c: (v, f"evidence/S07/S07h/results.json clips.{c}") for c, v in h.items()}
    srcs["OWN01"] = (json.loads((root / "evidence/S07/S07i/result-own01.json").read_text(encoding="utf-8")),
                     "evidence/S07/S07i/result-own01.json")
    out = {}
    for c, (v, src) in srcs.items():
        mc, res = v.get("mask_centroid") or {}, v.get("result") or {}
        if "u_total" not in res:
            continue
        b = {"m_per_px": mc["m_per_px"], "g": mc["g"], "detection": mc["u_fit"], "clock": mc["u_timing"], "scale": mc["u_scale"],
             "centroid_vs_box": res["u_model_centroid_vs_box"], "total": res["u_total"],
             "scale_rel_width": mc["scale"]["u_width_px"] / mc["scale"]["mean_px"], "edge_u_m": EDGE_U_M,
             "source": src + " mask_centroid.{u_fit,u_timing,u_scale,m_per_px} + result.{u_model_centroid_vs_box,u_total}"}
        assert abs(math.sqrt(sum(b[k] ** 2 for k in ("detection", "clock", "scale", "centroid_vs_box"))) - b["total"]) < 1e-9, c
        assert abs(b["g"] * math.hypot(b["scale_rel_width"], EDGE_U_M / 0.2028) - b["scale"]) < 1e-9, c
        out[c] = b
    return out


if __name__ == "__main__":
    doc = json.loads(OWN.read_text(encoding="utf-8"))
    for c, b in budgets().items():
        if (doc["clips"].get(c) or {}).get("measurement"):
            doc["clips"][c]["u_budget"] = b
    OWN.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
