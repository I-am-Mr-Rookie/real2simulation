"""S15az: add the RECORDED reference pixel length (scale_value_m / S07 m_per_px) to owner_clips.json. Idempotent."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWN = ROOT / "Build/api/workspace/owner_clips.json"


def reference_px(root=ROOT):
    """{clip: (px, source)} from the S07h per-clip m_per_px (S07i for OWN01); px = scale_value_m / m_per_px."""
    h = json.loads((root / "evidence/S07/S07h/results.json").read_text(encoding="utf-8"))["clips"]
    i = json.loads((root / "evidence/S07/S07i/result-own01.json").read_text(encoding="utf-8"))
    mpp = {c: (v["mask_centroid"]["m_per_px"], f"evidence/S07/S07h/results.json clips.{c}.mask_centroid.m_per_px")
           for c, v in h.items() if "m_per_px" in v.get("mask_centroid", {})}
    mpp["OWN01"] = (i["mask_centroid"]["m_per_px"], "evidence/S07/S07i/result-own01.json mask_centroid.m_per_px")
    clips = json.loads(OWN.read_text(encoding="utf-8"))["clips"]
    return {c: (clips[c]["scale_value_m"] / m, src) for c, (m, src) in mpp.items() if c in clips}


if __name__ == "__main__":
    doc = json.loads(OWN.read_text(encoding="utf-8"))
    for c, (px, src) in reference_px().items():
        doc["clips"][c]["scale_reference_px"] = px
        doc["clips"][c]["scale_reference_px_source"] = src + " (px = scale_value_m / m_per_px)"
    OWN.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

