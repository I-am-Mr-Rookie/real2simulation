"""S12e Gate RS: score sealed, pre-committed held-out predictions against tracked suffix observations.

Metric (pre-registered in Run-System/Runs/S12e-orch45/PLAN.md before any suffix was tracked):
per clip, RMS over sealed suffix frames of |y_pred - y_obs| in image-height fractions (scale-free, Q15=A);
Gate RS = median over projectile/bounce/pendulum <= 5%; a category without a scored clip is a measured
shortfall. Gate M is NOT_MET: no calibrated g, scale, clock or physical-accuracy claim.
Eligibility (R-RS F1-R/F2-R): a prediction/v2 commitment bound to the seal, and an independent public-input
receipt from clips.csv + evidence/owner/S02/APPROVAL.md + the S02c acquisition hash registry.
"""
import csv
import hashlib
import json
import math
import re
import statistics
import sys

from Build.real2sim.boundary import GATE_M, LIMITS, split, verify
from Build.real2sim.predict import projectile, require_v2, st03_record
from Build.real2sim.params import ROOT

CATEGORIES = ("projectile", "bounce", "pendulum")
THRESHOLD, MIN_COVERAGE, EARLY = 0.05, 0.8, 5
# Full f58-542 job OOMed on A10G (evidence/S12/gate-rs/ST03-f58-542); 26-frame job fits (orch14 19 frames = 17.1 GB).
ST03_TRACK = "evidence/S12/gate-rs/ST03-f58-83/result.json"
APPROVAL, REGISTRY = "evidence/owner/S02/APPROVAL.md", "evidence/clips/S02c-acquisition.json"
APPROVED_USE = "local scene/tracking pipeline work"
# clips.csv experiment -> Gate RS category (ST03 free fall is the ballistic/projectile case, as pre-registered).
CATEGORY_EXPERIMENTS = {"projectile": {"projectile", "free_fall"}, "bounce": {"bounce"}, "pendulum": {"pendulum"}}
# Allowed by AGENTS.md: NASA/US-Gov PD, CC0, CC BY, CC BY-SA, Pexels, Pixabay. NC/ND never match.
LICENCE = re.compile(r"pexels( license)?|pixabay( (content )?license)?|pd-[a-z-]+|public domain|cc0(-1\.0)?"
                     r"|cc-by(-sa)?-[0-9.]+", re.I)


def public_receipt(clip_id, source_sha256, category, root=ROOT):
    """R-RS F2-R: independent receipt for an approved, licensed public clip; raise ValueError otherwise.

    Never consults caller provenance strings or clip-name patterns: unknown/missing/synthetic clips fail closed.
    """
    with open(root / "clips.csv", encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["clip_id"] == clip_id]
    if len(rows) != 1:
        raise ValueError(f"clip {clip_id!r} is not exactly one clips.csv row")
    row, raw = rows[0], (root / APPROVAL).read_bytes()
    approved = re.search(r"\*\*Approved IDs:\*\*\s*([A-Z0-9,]+)", raw.decode("utf-8"))
    if not approved or clip_id not in approved.group(1).split(",") or APPROVED_USE not in raw.decode("utf-8"):
        raise ValueError(f"clip {clip_id!r} is not owner-approved for {APPROVED_USE} in {APPROVAL}")
    if not LICENCE.fullmatch(row["licence"].strip()):
        raise ValueError(f"clip {clip_id!r} licence {row['licence']!r} is not an allowed public licence")
    hashes = [f.get("sha256") for f in json.loads((root / REGISTRY).read_text(encoding="utf-8"))["files"]
              if f.get("clip_id") == clip_id]
    if hashes != [source_sha256]:
        raise ValueError(f"clip {clip_id!r} source sha does not match the acquisition registry")
    if row["experiment"] not in CATEGORY_EXPERIMENTS.get(category, ()):
        raise ValueError(f"clip {clip_id!r} experiment {row['experiment']!r} is not eligible for {category!r}")
    return {"clip_id": clip_id, "category": category, "experiment": row["experiment"], "licence": row["licence"],
            "approval_ref": APPROVAL, "approval_sha256": hashlib.sha256(raw).hexdigest(),
            "registry_ref": REGISTRY, "source_sha256": source_sha256}


def _rms(errors):
    return math.sqrt(sum(e * e for e in errors) / len(errors)) if errors else None


def _finite(v):
    return type(v) in (int, float) and math.isfinite(v)


def score(boundary, sealed, prediction, committed_sha256, load_observations, provenance="synthetic"):
    """Verify seal + v2 committed prediction, THEN call load_observations() -> {frame: (pts_s, y_norm)}.

    provenance is a descriptive label only; gate eligibility comes from public_receipt(), never from it.
    """
    verify(boundary, sealed)
    require_v2(prediction, boundary)  # R-RS F1-R: custody bound into the commitment, checked before any read
    if prediction.sha256 != committed_sha256:
        raise ValueError("prediction is not the committed one for this seal")
    if len(sealed) != boundary.suffix_count:
        raise ValueError("prediction trace does not cover the complete sealed suffix")
    if not all(_finite(r[2]) for r in prediction.trace):
        raise ValueError("prediction trace has non-finite values")
    try:
        receipt, ineligible = public_receipt(boundary.clip_id, boundary.source_sha256, prediction.kind), None
    except ValueError as error:
        receipt, ineligible = None, str(error)
    observed = load_observations()  # first suffix read: only after both checks passed
    errors = []
    for i, p, y, _ in prediction.trace:
        if i in observed:
            if not (len(observed[i]) == 2 and all(_finite(v) for v in observed[i])):
                raise ValueError(f"frame {i}: observation must be finite (pts_s, y_norm)")
            if abs(observed[i][0] - p) > 1e-6:
                raise ValueError(f"frame {i}: observed PTS {observed[i][0]} != sealed {p}")
            errors.append(y - observed[i][1])
    coverage = len(errors) / boundary.suffix_count
    rms = _rms(errors)
    return {"clip_id": boundary.clip_id, "source_sha256": boundary.source_sha256, "kind": prediction.kind,
            "prediction_sha256": prediction.sha256, "prediction_commitment": prediction.commitment,
            "suffix_identity_sha256": boundary.suffix_identity_sha256, "sealed_frames": boundary.suffix_count,
            "scored_frames": len(errors), "coverage": coverage, "normalized_rms": rms,
            "normalized_rms_first5_diagnostic": _rms(errors[:EARLY]),
            "max_abs": max(map(abs, errors)) if errors else None,
            "scored": coverage >= MIN_COVERAGE and rms is not None, "provenance": provenance,
            "input_receipt": receipt, "ineligible_reason": ineligible, "gate_m": GATE_M}


def _eligible(category, r, root=ROOT):
    """R-RS F2/F2-R/F4: recompute eligibility, re-deriving the public-input receipt independently."""
    if not isinstance(r, dict) or r.get("kind") != category:
        return False
    if r.get("prediction_commitment") != "prediction/v2":  # F1-R: legacy v1 results are audit-only
        return False
    try:
        if r.get("input_receipt") != public_receipt(r.get("clip_id"), r.get("source_sha256"), category, root):
            return False
    except (ValueError, TypeError, KeyError, OSError):
        return False
    n, k, rms = r.get("sealed_frames"), r.get("scored_frames"), r.get("normalized_rms")
    if type(n) is not int or type(k) is not int or not 0 < k <= n or not _finite(rms) or rms < 0:
        return False
    return r.get("scored") is True and k / n >= MIN_COVERAGE and r.get("coverage") == k / n


def gate(results, root=ROOT):
    """results: {category: clip score or None}. Missing/unscored/ineligible category => measured shortfall.

    Eligible = kind matches category, independently re-derived public-input receipt equals the carried one,
    finite nonnegative RMS, recomputed coverage >= 80%; one clip/prediction may not stand in for two categories.
    """
    per, receipts, seen = {}, {}, set()
    for c in CATEGORIES:
        r = results.get(c)
        ok = _eligible(c, r, root) and r["clip_id"] not in seen and r.get("prediction_sha256") not in seen
        per[c] = r["normalized_rms"] if ok else None
        receipts[c] = r["input_receipt"] if ok else None
        if ok:
            seen |= {r["clip_id"], r.get("prediction_sha256")}
    complete = all(v is not None for v in per.values())
    value = statistics.median(per.values()) if complete else None
    return {"per_category_normalized_rms": per, "input_receipts": receipts, "median": value, "threshold": THRESHOLD,
            "status": "MET" if complete and value <= THRESHOLD else "NOT_MET",
            "shortfall": [c for c, v in per.items() if v is None or v > THRESHOLD], "gate_m": GATE_M}


def st03_observations(raw, frame_pts, height):
    """Tracked obj-2 centroids via Build/pipeline validate_segment; frame_pts = presentation-map PTS.

    modal_track streams/masks use segment-relative indices 0..n-1 while record frames use source indices;
    validate_segment assumes they coincide (true only for first=0), so relative k is mapped to frame_map[k].
    """
    from Build.pipeline.gpu_stages import validate_segment
    from Build.pipeline.gpu_stages import StageError
    out = json.loads(raw)
    source = [i for i, _ in out["frame_map"]]
    if [s[0] for s in out["stream"]] != list(range(len(source))):
        raise ValueError("stream is not one row per extracted frame")
    for row in out["stream"] + out.get("masks", []):
        row[0] = source[row[0]]
    fmap = [(i, frame_pts[i]) for i in source]
    try:
        frames = validate_segment(json.dumps(out), "apple", 2, fmap)["frames"]
    except StageError as error:  # R-RS F3: a rejected segment is an explicit unscored shortfall, never scored
        return {}, f"validate_segment rejected (unscored): {error}"
    return {f["frame_index"]: (f["pts_s"], f["centroid_px"][1] / height) for f in frames}, "validate_segment OK"


def main(root=ROOT):
    record, suffix, inputs = st03_record(root)
    boundary, sealed = split(record, suffix)
    committed = json.loads((root / "evidence/S12/prediction-ST03-v2.json").read_text(encoding="utf-8"))
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

    st03 = score(boundary, sealed, prediction, committed["prediction"]["sha256"], load, "image-derived")
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
