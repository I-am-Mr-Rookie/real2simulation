"""S12e Gate RS: score sealed, pre-committed held-out predictions against tracked suffix observations.

Metric (pre-registered in Run-System/Runs/S12e-orch45/PLAN.md before any suffix was tracked):
per clip, RMS over sealed suffix frames of |y_pred - y_obs| in image-height fractions (scale-free, Q15=A);
Gate RS = median over projectile/bounce/pendulum <= 5%; a category without a scored clip is a measured
shortfall. Gate M is NOT_MET: no calibrated g, scale, clock or physical-accuracy claim.
"""
import hashlib
import json
import math
import statistics
import sys

from Build.real2sim.boundary import GATE_M, LIMITS, split, verify
from Build.real2sim.predict import check, projectile, st03_record
from Build.real2sim.params import ROOT

CATEGORIES = ("projectile", "bounce", "pendulum")
THRESHOLD, MIN_COVERAGE, EARLY = 0.05, 0.8, 5
# Full f58-542 job OOMed on A10G (evidence/S12/gate-rs/ST03-f58-542); 26-frame job fits (orch14 19 frames = 17.1 GB).
ST03_TRACK = "evidence/S12/gate-rs/ST03-f58-83/result.json"


def _rms(errors):
    return math.sqrt(sum(e * e for e in errors) / len(errors)) if errors else None


def score(boundary, sealed, prediction, committed_sha256, load_observations):
    """Verify seal + committed prediction, THEN call load_observations() -> {frame: (pts_s, y_norm)}."""
    verify(boundary, sealed)
    check(prediction)
    if prediction.sha256 != committed_sha256 or \
            prediction.suffix_identity_sha256 != boundary.suffix_identity_sha256:
        raise ValueError("prediction is not the committed one for this seal")
    observed = load_observations()  # first suffix read: only after both checks passed
    errors = []
    for i, p, y, _ in prediction.trace:
        if i in observed:
            if abs(observed[i][0] - p) > 1e-6:
                raise ValueError(f"frame {i}: observed PTS {observed[i][0]} != sealed {p}")
            errors.append(y - observed[i][1])
    coverage = len(errors) / len(prediction.trace)
    rms = _rms(errors)
    return {"clip_id": boundary.clip_id, "kind": prediction.kind, "prediction_sha256": prediction.sha256,
            "suffix_identity_sha256": boundary.suffix_identity_sha256, "sealed_frames": len(prediction.trace),
            "scored_frames": len(errors), "coverage": coverage, "normalized_rms": rms,
            "normalized_rms_first5_diagnostic": _rms(errors[:EARLY]),
            "max_abs": max(map(abs, errors)) if errors else None,
            "scored": coverage >= MIN_COVERAGE and rms is not None, "gate_m": GATE_M}


def gate(results):
    """results: {category: clip score or None}. Missing/unscored category => measured shortfall."""
    per = {c: (results.get(c) or {}).get("normalized_rms") if (results.get(c) or {}).get("scored") else None
           for c in CATEGORIES}
    complete = all(v is not None for v in per.values())
    value = statistics.median(per.values()) if complete else None
    return {"per_category_normalized_rms": per, "median": value, "threshold": THRESHOLD,
            "status": "MET" if complete and value <= THRESHOLD else "NOT_MET",
            "shortfall": [c for c, v in per.items() if v is None or v > THRESHOLD], "gate_m": GATE_M}


def st03_observations(raw, frame_pts, height):
    """Tracked obj-2 centroids via Build/pipeline validate_segment; frame_pts = presentation-map PTS.

    modal_track streams/masks use segment-relative indices 0..n-1 while record frames use source indices;
    validate_segment assumes they coincide (true only for first=0), so relative k is mapped to frame_map[k].
    """
    from Build.pipeline.gpu_stages import validate_segment
    out = json.loads(raw)
    source = [i for i, _ in out["frame_map"]]
    if [s[0] for s in out["stream"]] != list(range(len(source))):
        raise ValueError("stream is not one row per extracted frame")
    for row in out["stream"] + out.get("masks", []):
        row[0] = source[row[0]]
    fmap = [(i, frame_pts[i]) for i in source]
    try:
        frames = validate_segment(json.dumps(out), "apple", 2, fmap)["frames"]
        note = "validate_segment OK"
        obs = {f["frame_index"]: (f["pts_s"], f["centroid_px"][1] / height) for f in frames}
    except Exception as error:  # noqa: BLE001 - record the rejection, score only object-2 frames present
        note = f"validate_segment rejected: {error}"
        ids = {i for i, objs, _ in out["stream"] if 2 in objs}
        obs = {f["frame_index"]: (frame_pts[f["frame_index"]], f["y_px"] / height)
               for f in out["record"]["frames"] if f["frame_index"] in ids}
    return obs, note


def main(root=ROOT):
    record, suffix, inputs = st03_record(root)
    boundary, sealed = split(record, suffix)
    committed = json.loads((root / "evidence/S12/prediction-ST03.json").read_text(encoding="utf-8"))
    prediction = projectile(boundary, sealed)
    raw = (root / ST03_TRACK).read_bytes()
    pmap = json.loads((root / "evidence/S07/S07b/recovery3/presentation-map.json").read_text(encoding="utf-8"))
    frame_pts = {f["source_frame_index"]: float(f["pts_time"]) for f in pmap["frames"]}
    notes = {}

    def load():
        obs, notes["validate"] = st03_observations(raw.decode(), frame_pts, record["height_px"])
        prefix = {i: y for i, _, y in boundary.training}
        diffs = [abs(obs[i][1] - y) for i, y in prefix.items() if i in obs]
        notes["prefix_retrack_max_abs_vs_orch14"] = max(diffs) if diffs else None
        return {i: v for i, v in obs.items() if i > boundary.last_training_frame}

    st03 = score(boundary, sealed, prediction, committed["prediction"]["sha256"], load)
    result = gate({"projectile": st03})
    out = {"gate": "RS", "gate_m": GATE_M, "limitations": list(LIMITS), "result": result,
           "metric": "per clip RMS |y_pred - y_obs| / image height over sealed suffix; median over categories",
           "clips": {"projectile": st03 | notes, "bounce": None, "pendulum": None},
           "shortfall_reasons": {
               "projectile": ("ST03 scored 7/466 sealed frames (coverage < 80%): full f58-542 job hit CUDA OOM on A10G "
                              "24 GB; 26 frames is the measured fit. Ballistic prefix fit has no floor: apple is on the "
                              "ground from f77 (y~0.80-0.82) while prediction leaves the image at f81 (y>1)."),
               "bounce": ("BN01 approved, but no prefix tracking and no sourced restitution/floor record; ~26 contiguous "
                          "frames/job (0.11 s at 240 fps) cannot span its 0.67 s contact-to-contact arc; strict prefix job "
                          "-> committed prediction -> suffix job not run"),
               "pendulum": ("PD02/03/04/06 approved, but no prefix tracking and no sourced angular-frequency record; ~26 "
                            "contiguous frames/job (~0.9 s at 30 fps) is far below one period; not run")},
           "jobs": "evidence/S12/gate-rs/gpu-ledger.jsonl (2 Modal jobs, retries 0)",
           "inputs": inputs + [{"path": ST03_TRACK, "sha256": hashlib.sha256(raw).hexdigest()}],
           "claims": "scale-free image-plane agreement only; not calibrated, not physical accuracy"}
    path = root / "evidence/S12/gate-rs/gate-rs.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"gate RS {result['status']} median={result['median']} projectile={st03['normalized_rms']} "
          f"coverage={st03['coverage']:.3f} gate_m={GATE_M}")


if __name__ == "__main__":
    sys.exit(main())
