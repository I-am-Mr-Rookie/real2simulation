"""S12d overlay builder: immutable predicted traces + clip id + source sha + PTS frame timebase.

Scale-free image-height units; Gate M NOT_MET. Contract and validator: contracts/overlay.
"""
import json
import math
import sys

from Build.real2sim.boundary import GATE_M, LIMITS, _sha, split
from Build.real2sim.params import ROOT, parameter
from Build.real2sim.predict import as_json, check, pendulum, projectile, st03_record
from contracts.overlay.validate import VERSION, frame_map_sha256, validate


def build(boundary, predictions, frame_map, provenance, sources=()):
    """Overlay document for predictions made from this boundary; validated before return."""
    for p in predictions:
        check(p)
        if p.clip_id != boundary.clip_id or p.training_sha256 != boundary.training_sha256 \
                or p.suffix_identity_sha256 != boundary.suffix_identity_sha256:
            raise ValueError("prediction was not made from this clip boundary")
        # R-RS F1: trace identities must equal the complete seal (count + hash), not merely align to PTS.
        if len(p.trace) != boundary.suffix_count or \
                _sha(tuple((r[0], r[1]) for r in p.trace)) != boundary.suffix_identity_sha256:
            raise ValueError("prediction trace does not cover the complete sealed suffix")
    doc = {"contract_version": VERSION, "clip_id": boundary.clip_id, "source_sha256": boundary.source_sha256,
           "provenance": provenance, "units": "image-height fraction", "gate_m": GATE_M, "limits": list(LIMITS),
           "timebase": {"kind": "pts_s", "frame_map_sha256": frame_map_sha256(frame_map), "sources": list(sources)},
           "traces": [as_json(p) for p in predictions]}
    validate(json.loads(json.dumps(doc)), boundary.clip_id, boundary.source_sha256, frame_map)
    return doc


def st03_frame_map(root=ROOT):
    """Source PTS per frame (presentation map; the ST03 errata agrees with it to 1e-6 s, checked in st03_record)."""
    pmap = json.loads((root / "evidence/S07/S07b/recovery3/presentation-map.json").read_text(encoding="utf-8"))
    return {f["source_frame_index"]: float(f["pts_time"]) for f in pmap["frames"]}


W_SYNTH = 2 * math.pi / 1.6  # SYNTHETIC: 1.6 s period


def synthetic_pendulum(n=90, last=23, fps=30.0):
    """SYNTHETIC fixture (no approved pendulum clip has tracking): bob horizontal pixel x carried in the
    S12a boundary's 1-D y_px slot, x_px = 240 + 40 sin(w t + 0.3), height 480, 30 fps, noise-free."""
    definition = {"fixture": "SYNTHETIC pendulum v1", "n": n, "fps": fps, "w": W_SYNTH,
                  "x_px": "240 + 40 sin(w t + 0.3)", "height_px": 480}
    frames = [{"frame_index": i, "pts_s": i / fps, "y_px": 240 + 40 * math.sin(W_SYNTH * i / fps + 0.3)}
              for i in range(n)]
    record = {"clip_id": "SYNTHETIC-pendulum-v1", "source_sha256": _sha(definition), "height_px": 480,
              "last_training_frame": last, "frames": frames}
    freq = parameter("angular_frequency", W_SYNTH, 0.0, {"input_provenance": "synthetic",
                                                         "method": "fixture definition",
                                                         "source_sha256": record["source_sha256"]})
    return record, freq


def main(root=ROOT):
    record, suffix, inputs = st03_record(root)
    boundary, sealed = split(record, suffix)
    prediction = projectile(boundary, sealed)
    committed = json.loads((root / "evidence/S12/prediction-ST03.json").read_text(encoding="utf-8"))
    if committed["prediction"]["sha256"] != prediction.sha256:
        raise ValueError("ST03 prediction no longer matches committed S12c evidence")
    docs = {"overlay-ST03.json": build(boundary, [prediction], st03_frame_map(root), "image-derived", inputs[1:])}
    record, freq = synthetic_pendulum()
    boundary, sealed = split(record)
    fmap = {f["frame_index"]: f["pts_s"] for f in record["frames"]}
    docs["overlay-pendulum-SYNTHETIC.json"] = build(boundary, [pendulum(boundary, sealed, freq)], fmap, "synthetic")
    for name, doc in docs.items():
        (root / "evidence/S12" / name).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        print(f"evidence/S12/{name} {doc['contract_version']} gate_m={doc['gate_m']} "
              + " ".join(f"{t['kind']}={t['sha256'][:12]} rows={len(t['trace'])}" for t in doc["traces"]))


if __name__ == "__main__":
    sys.exit(main())
