"""S15aa: copy frozen-v1 g ± u and the S07m v3 verdict (or the S07h abstain reason) into Build/api/workspace/owner_clips.json.
Run from the repo root: python evidence/S15aa/sync_owner_measurements.py. Numbers come only from the evidence JSON (never retyped);
v2 windows are deliberately NOT copied into the product. tests/api-workspace re-derives every value with measurement_of/abstain_of."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S07M = "evidence/S07/S07m/results.json"
S07H = "evidence/S07/S07h/results.json"
OUT = ROOT / "Build/api/workspace/owner_clips.json"


def measurement_of(clip, scale_m, root=ROOT):
    raw = (root / S07M).read_bytes()
    row = next((r for r in json.loads(raw)["rows"] if r["clip"] == clip and r["analysis"] == "v1"), None)
    if row is None:
        return None
    return {"source": S07M, "source_sha256": hashlib.sha256(raw).hexdigest(), "analysis": "v1 (frozen S07h pipeline)",
            "measured_label": f"MEASURED (owner clip {clip}, user-declared scale {scale_m} m, phone clock not externally verified)",
            "g": round(row["g"], 2), "u": round(row["u"], 2), "unit": "m/s^2", "held_out_rmse_px": round(row["held_rmse_px"], 1),
            "v3": {"verdict": "PASS" if row["v3_pass"] else "FAIL", "chi2": round(row["chi2"], 2), "dof": row["dof"],
                   "chi2_per_dof": round(row["chi2"] / row["dof"], 2), "p": float(f"{row['p']:.2g}")}}


def abstain_of(clip, root=ROOT):
    """S07h reason a clip has no v1 product value; None if v1 measured it validly."""
    h = json.loads((root / S07H).read_text(encoding="utf-8"))
    if clip in h["excluded"]:
        return f"excluded (S07h): {h['excluded'][clip]}"
    if clip in h["repeatability_05"]["invalid_flagged"]:
        return f"invalid (S07h): v1 value flagged invalid ({h['clips'][clip]['scene']}); g not reported"
    if "abstain" in h["clips"].get(clip, {}):
        return f"v1 abstain (S07h): frozen v1 pipeline stopped ({h['clips'][clip]['abstain'].strip(': ')}); g not reported"
    return None


if __name__ == "__main__":
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    for clip, e in doc["clips"].items():
        e.pop("measurement", None), e.pop("abstain", None)
        reason = abstain_of(clip)
        m = None if reason else measurement_of(clip, e["scale_value_m"])
        if m:
            e["measurement"] = m
        else:
            e["abstain"] = reason or "no v1 measurement in evidence/S07/S07m/results.json"
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
