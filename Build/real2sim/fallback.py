"""S12f honest prediction fallback: code-owned display decision from the scored Gate RS evidence + output labels.

Owner rule: <=5% shown; 5-10% shown honestly with its measured error; >10% or unmeasured (null median,
insufficient coverage) limits demo prediction to the virtual lab. Numbers only come from the scorer's gate-rs.json.
"""
import hashlib
import json
import math
import sys

from Build.real2sim.boundary import GATE_M, LIMITS
from Build.real2sim.params import ROOT
from Build.real2sim.score import CATEGORIES, THRESHOLD, gate

HONEST_LIMIT = 0.10  # owner rule upper bound; THRESHOLD (0.05) is the Gate RS bound reused from score.py
GATE_RS = "evidence/S12/gate-rs/gate-rs.json"
OUTPUTS = ("evidence/S12/overlay-ST03-v2.json", "evidence/S12/overlay-pendulum-SYNTHETIC-v2.json")


def decide(median):
    """Normalized-error median (image-height fraction) or None -> display tier for real-scene prediction."""
    if median is None or isinstance(median, bool) or not isinstance(median, (int, float)) \
            or not math.isfinite(median) or median < 0:
        return {"tier": "VIRTUAL_LAB_ONLY", "real_scene_prediction": "WITHHELD", "error_label": "unmeasured",
                "reason": "no measured median (missing category or coverage < 80%): unmeasured"}
    if median <= THRESHOLD:
        return {"tier": "SHOWN", "real_scene_prediction": "SHOWN", "error_label": "measured",
                "reason": f"measured median {median} <= {THRESHOLD}"}
    if median <= HONEST_LIMIT:
        return {"tier": "SHOWN_WITH_ERROR", "real_scene_prediction": "SHOWN_WITH_MEASURED_ERROR",
                "error_label": "measured", "reason": f"measured median {median} in ({THRESHOLD}, {HONEST_LIMIT}]"}
    return {"tier": "VIRTUAL_LAB_ONLY", "real_scene_prediction": "WITHHELD", "error_label": "measured",
            "reason": f"measured median {median} > {HONEST_LIMIT}"}


def label(doc, decision):
    """Explicit per-output labels. Synthetic stays SYNTHETIC; real-clip traces are simulated, scale unverified."""
    scale = "SCALE_VERIFIED" if doc.get("gate_m") == "MET" else "SCALE_UNVERIFIED"
    common = {"clip_id": doc["clip_id"], "provenance": doc["provenance"], "units": doc["units"],
              "gate_m": doc["gate_m"], "scale_label": scale, "limits": doc["limits"]}
    if doc["provenance"] == "synthetic":
        return common | {"banner": "SYNTHETIC", "trace_label": "simulated", "observation_label": "synthetic",
                         "error_label": "not applicable (synthetic fixture)", "display": "VIRTUAL_LAB"}
    return common | {"banner": "REAL CLIP - PREDICTION " + decision["real_scene_prediction"],
                     "trace_label": "simulated", "observation_label": "measured (image-derived tracking)",
                     "error_label": decision["error_label"],
                     "display": "REAL_SCENE" if decision["tier"] != "VIRTUAL_LAB_ONLY" else "VIRTUAL_LAB_ONLY"}


def from_evidence(root=ROOT):
    """Re-run score.gate on the stored clip scores; refuse if the stored result disagrees with the code."""
    doc = json.loads((root / GATE_RS).read_text(encoding="utf-8"))
    result = gate({c: doc["clips"].get(c) for c in CATEGORIES}, root)
    if result != doc["result"]:
        raise ValueError("gate-rs.json result disagrees with score.gate recomputation")
    return doc, result


def main(root=ROOT):
    doc, result = from_evidence(root)
    decision = decide(result["median"])
    outputs = []
    for rel in OUTPUTS:
        raw = (root / rel).read_bytes()
        outputs.append({"path": rel, "sha256": hashlib.sha256(raw).hexdigest()} | label(json.loads(raw), decision))
    clips = {c: None if v is None else {k: v[k] for k in ("clip_id", "scored_frames", "sealed_frames", "coverage",
                                                         "normalized_rms", "scored")}
             for c, v in doc["clips"].items()}
    out = {"task": "S12f", "rule": f"<= {THRESHOLD} shown; ({THRESHOLD}, {HONEST_LIMIT}] shown with measured error; "
                                   f"> {HONEST_LIMIT} or unmeasured -> virtual lab only",
           "gate_rs": {"path": GATE_RS, "sha256": hashlib.sha256((root / GATE_RS).read_bytes()).hexdigest(),
                       "status": result["status"], "median": result["median"], "shortfall": result["shortfall"],
                       "recomputed_by": "Build.real2sim.score.gate"},
           "gate_m": GATE_M, "limits": list(LIMITS), "decision": decision,
           "clip_scores_diagnostic": clips, "outputs": outputs}
    (root / "evidence/S12/S12f-fallback.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"S12f decision={decision['tier']} real_scene={decision['real_scene_prediction']} "
          f"gate_rs={result['status']} median={result['median']} gate_m={GATE_M}")


if __name__ == "__main__":
    sys.exit(main())
