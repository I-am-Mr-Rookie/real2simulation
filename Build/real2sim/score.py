"""S12e Gate RS: score sealed, pre-committed held-out predictions against tracked suffix observations.

Metric (pre-registered in Run-System/Runs/S12e-orch45/PLAN.md before any suffix was tracked):
per clip, RMS over sealed suffix frames of |y_pred - y_obs| in image-height fractions (scale-free, Q15=A);
Gate RS = median over projectile/bounce/pendulum <= 5%; a category without a scored clip is a measured
shortfall. Gate M is NOT_MET: no calibrated g, scale, clock or physical-accuracy claim.
Eligibility (R-RS F1-R/F2-R): a prediction/v2 commitment bound to the seal, and an independent public-input
receipt from clips.csv + evidence/owner/S02/APPROVAL.md + the S02c acquisition hash registry.
F2-R2: observations must come through Tracked (accepted tracker artifact: path+sha custody, validate_segment,
tracker clip/source identity == receipt, prefix re-tracked); gate() re-derives them. Generic/synthetic scoring
still works but is never gate-eligible.
F2-R3/F2-C: Tracked must be bound to the scored boundary, and its artifact must have exactly one entry in the
controller-reviewed accepted-tracking registry (artifact sha + seal + presentation map + frame range); unknown
caller-authored trackers are diagnostic-only.
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
# F2-A: the authoritative grant is the Use line directly under Approved IDs, phrased exactly as owner-approved.
GRANT = re.compile(r"^\*\*Approved IDs:\*\*\s*([A-Z0-9,]+)\.?[ \t]*\r?\n\*\*Use:\*\*[ \t]*(.*)$", re.M)
NEGATION = re.compile(r"\b(not|no|denied|deny|revoked|withdrawn|never|except)\b", re.I)
# clips.csv experiment -> Gate RS category (ST03 free fall is the ballistic/projectile case, as pre-registered).
CATEGORY_EXPERIMENTS = {"projectile": {"projectile", "free_fall"}, "bounce": {"bounce"}, "pendulum": {"pendulum"}}
# F2-L: finite allowlist per AGENTS.md (NASA PD, Commons PD, CC0, CC BY, CC BY-SA, Pexels, Pixabay); NC/ND never listed.
CC_VERSIONS = ("1.0", "2.0", "2.5", "3.0", "4.0")
LICENCES = frozenset({"pexels", "pexels license", "pixabay", "pixabay license", "pixabay content license",
                      "public domain", "pd-usgov-nasa", "pd-usgov", "pd-self", "pd-old", "cc0", "cc0-1.0"}
                     | {f"cc-by{sa}-{v}" for sa in ("", "-sa") for v in CC_VERSIONS})
PREFIX_TOL = 0.002  # image heights; ST03 f58-83 re-track vs orch14 prefix measured 0.00045
# F2-R3: independent, controller-reviewed custody. Only entries built from accepted run evidence are listed; any other
# artifact (even internally consistent, correct ids, validate_segment OK) is diagnostic-only, never gate-eligible.
TRACKING_REGISTRY = "evidence/S12/accepted-tracking.json"


def seal_identity(b):
    """F2-C: the boundary/prediction-commitment identity a tracking artifact must be bound to."""
    return {"clip_id": b.clip_id, "source_sha256": b.source_sha256, "last_training_frame": b.last_training_frame,
            "training_sha256": b.training_sha256, "suffix_identity_sha256": b.suffix_identity_sha256,
            "suffix_count": b.suffix_count}


def accepted_tracking(rel, sha256, seal, frame_pts, root=ROOT):
    """F2-R3: exactly one accepted registry entry binding artifact path+sha, seal identity, presentation map, frames."""
    raw = (root / TRACKING_REGISTRY).read_bytes()
    hits = [e for e in json.loads(raw)["accepted"] if e.get("artifact") == rel and e.get("artifact_sha256") == sha256]
    if len(hits) != 1:
        raise ValueError(f"tracker artifact {rel!r} has no accepted tracking custody in {TRACKING_REGISTRY}")
    e = hits[0]
    if e.get("seal") != seal:
        raise ValueError("accepted tracking custody binds a different clip/source/training prefix/seal")
    pmap = _artifact(root, e["presentation_map"])
    if hashlib.sha256(pmap).hexdigest() != e.get("presentation_map_sha256"):
        raise ValueError("presentation map digest differs from accepted custody")
    pts = {f["source_frame_index"]: float(f["pts_time"]) for f in json.loads(pmap)["frames"]}
    first, last = e["frame_range"]
    if [list(r) for r in frame_pts] != [[i, pts[i]] for i in range(first, last + 1)]:
        raise ValueError("tracker frames/PTS differ from the accepted frame range and presentation map")
    return {"registry": TRACKING_REGISTRY, "registry_sha256": hashlib.sha256(raw).hexdigest(), "entry": e["id"]}


def approved(clip_id, text):
    """F2-A: True only for a positive scoped grant in the single authoritative Approved IDs/Use block."""
    blocks = GRANT.findall(text)
    if len(blocks) != 1:
        return False
    ids, use = blocks[0]
    return clip_id in ids.split(",") and use.startswith(APPROVED_USE + " ONLY") and not NEGATION.search(use)


def public_receipt(clip_id, source_sha256, category, root=ROOT):
    """R-RS F2-R: independent receipt for an approved, licensed public clip; raise ValueError otherwise.

    Never consults caller provenance strings or clip-name patterns: unknown/missing/synthetic clips fail closed.
    """
    with open(root / "clips.csv", encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["clip_id"] == clip_id]
    if len(rows) != 1:
        raise ValueError(f"clip {clip_id!r} is not exactly one clips.csv row")
    row, raw = rows[0], (root / APPROVAL).read_bytes()
    if not approved(clip_id, raw.decode("utf-8")):
        raise ValueError(f"clip {clip_id!r} is not owner-approved for {APPROVED_USE} in {APPROVAL}")
    if row["licence"].strip().lower() not in LICENCES:
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


def _obs_sha(observed):
    return hashlib.sha256(json.dumps(sorted([i, *v] for i, v in observed.items())).encode()).hexdigest()


class Tracked:
    """The only gate-eligible observation loader: accepted tracker artifact under root (F2-R2).

    Custody = artifact path + sha256; validate_segment outcome; tracker clip/source == the boundary's (receipt) identity;
    every training (prefix) frame re-tracked within PREFIX_TOL. Returns suffix observations; .evidence goes to score().
    """

    def __init__(self, boundary, rel, frame_pts, root=ROOT, object_id=2, prompt="apple"):
        self.boundary, self.rel, self.frame_pts, self.root, self.evidence = boundary, rel, frame_pts, root, None
        self.object_id, self.prompt = object_id, prompt

    def __call__(self):
        b, raw = self.boundary, _artifact(self.root, self.rel)
        source = [i for i, _ in json.loads(raw)["frame_map"]]
        fpts = [[i, self.frame_pts[i]] for i in source]
        obs, note = st03_observations(raw.decode(), dict(fpts), b.clip_id, b.source_sha256, self.object_id, self.prompt)
        diffs = [abs(obs[i][1] - y) for i, _, y in b.training if i in obs]
        if obs and (len(diffs) != len(b.training) or max(diffs) > PREFIX_TOL):
            raise ValueError("tracker artifact does not re-track the committed prefix (prefix custody)")
        sha, seal = hashlib.sha256(raw).hexdigest(), seal_identity(b)
        try:
            custody, custody_error = accepted_tracking(self.rel, sha, seal, fpts, self.root), None
        except (ValueError, KeyError, TypeError, OSError) as error:  # unknown artifact: diagnostic-only
            custody, custody_error = None, f"no accepted tracking custody: {error}"
        self.evidence = {"path": self.rel, "sha256": sha, "clip_id": b.clip_id,
                         "source_sha256": b.source_sha256, "object_id": self.object_id, "prompt": self.prompt,
                         "validate": note, "frame_pts": fpts,
                         "after_frame": b.last_training_frame, "prefix_frames": len(diffs),
                         "prefix_max_abs": max(diffs) if diffs else None, "seal": seal,
                         "custody": custody, "custody_error": custody_error}
        return {i: v for i, v in obs.items() if i > b.last_training_frame}


def _artifact(root, rel):
    path = (root / rel).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"tracker artifact {rel!r} is outside the evidence root")
    return path.read_bytes()


def _tracking_ok(r, root):
    """gate(): re-read the carried artifact, re-check sha/validation/identity and the scored observation digest."""
    e = r.get("tracking_evidence")
    if r.get("provenance") == "synthetic" or not isinstance(e, dict) or e.get("validate") != "validate_segment OK":
        return False
    if (e.get("clip_id"), e.get("source_sha256")) != (r.get("clip_id"), r.get("source_sha256")):
        return False
    seal = e.get("seal")  # F2-C: tracking bound to the same seal the committed prediction was scored against
    if not isinstance(seal, dict) or e.get("after_frame") != seal.get("last_training_frame") or \
            (seal.get("clip_id"), seal.get("source_sha256"), seal.get("training_sha256"),
             seal.get("suffix_identity_sha256"), seal.get("suffix_count")) != \
            (r.get("clip_id"), r.get("source_sha256"), r.get("training_sha256"), r.get("suffix_identity_sha256"),
             r.get("sealed_frames")):
        return False
    raw = _artifact(root, e["path"])
    if hashlib.sha256(raw).hexdigest() != e.get("sha256"):
        return False
    try:  # F2-R3: independent accepted custody, never the artifact's own location/hash/validation
        if accepted_tracking(e["path"], e["sha256"], seal, e["frame_pts"], root) != e.get("custody"):
            return False
    except (ValueError, KeyError, TypeError, OSError):
        return False
    obs, note = st03_observations(raw.decode(), {i: p for i, p in e["frame_pts"]}, r["clip_id"], r["source_sha256"],
                                  e["object_id"], e["prompt"])
    suffix = {i: v for i, v in obs.items() if i > e["after_frame"]}
    return note == "validate_segment OK" and _obs_sha(suffix) == r.get("observations_sha256")


def score(boundary, sealed, prediction, committed_sha256, load_observations, provenance="synthetic"):
    """Verify seal + v2 committed prediction, THEN call load_observations() -> {frame: (pts_s, y_norm)}.

    provenance is descriptive except 'synthetic' (never eligible); eligibility needs public_receipt() AND a Tracked loader.
    """
    verify(boundary, sealed)
    require_v2(prediction, boundary)  # R-RS F1-R: custody bound into the commitment, checked before any read
    if prediction.sha256 != committed_sha256:
        raise ValueError("prediction is not the committed one for this seal")
    if len(sealed) != boundary.suffix_count:
        raise ValueError("prediction trace does not cover the complete sealed suffix")
    if not all(_finite(r[2]) for r in prediction.trace):
        raise ValueError("prediction trace has non-finite values")
    if isinstance(load_observations, Tracked) and load_observations.boundary != boundary:  # F2-C, before any read
        raise ValueError("Tracked loader is bound to a different boundary than the one being scored")
    try:
        receipt, ineligible = public_receipt(boundary.clip_id, boundary.source_sha256, prediction.kind), None
    except ValueError as error:
        receipt, ineligible = None, str(error)
    observed = load_observations()  # first suffix read: only after both checks passed
    tracking = load_observations.evidence if isinstance(load_observations, Tracked) else None
    if tracking is None and ineligible is None:
        ineligible = "observations did not come through the accepted tracking-evidence path (Tracked)"
    if tracking is not None and tracking["custody"] is None and ineligible is None:
        ineligible = tracking["custody_error"]
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
            "training_sha256": prediction.training_sha256,
            "suffix_identity_sha256": boundary.suffix_identity_sha256, "sealed_frames": boundary.suffix_count,
            "scored_frames": len(errors), "coverage": coverage, "normalized_rms": rms,
            "normalized_rms_first5_diagnostic": _rms(errors[:EARLY]),
            "max_abs": max(map(abs, errors)) if errors else None,
            "scored": coverage >= MIN_COVERAGE and rms is not None, "provenance": provenance,
            "input_receipt": receipt, "ineligible_reason": ineligible, "tracking_evidence": tracking,
            "observations_sha256": _obs_sha(observed), "gate_m": GATE_M}


def _eligible(category, r, root=ROOT):
    """R-RS F2/F2-R/F2-R2/F4: recompute eligibility, re-deriving the receipt and tracking evidence independently."""
    if not isinstance(r, dict) or r.get("kind") != category:
        return False
    if r.get("prediction_commitment") != "prediction/v2":  # F1-R: legacy v1 results are audit-only
        return False
    try:
        if r.get("input_receipt") != public_receipt(r.get("clip_id"), r.get("source_sha256"), category, root):
            return False
        if not _tracking_ok(r, root):
            return False
    except (ValueError, TypeError, KeyError, OSError, IndexError):
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


def st03_observations(raw, frame_pts, clip_id, source_sha256, object_id=2, prompt="apple"):
    """Tracked centroids via Build/pipeline validate_segment; frame_pts = presentation-map PTS.

    modal_track streams/masks use segment-relative indices 0..n-1 while record frames use source indices;
    validate_segment assumes they coincide (true only for first=0), so relative k is mapped to frame_map[k].
    F2-R2: tracker clip/source must equal the expected (receipt) identity, frame_sha256 one per frame; else ValueError.
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
        seg = validate_segment(json.dumps(out), prompt, object_id, fmap)
    except StageError as error:  # R-RS F3: a rejected segment is an explicit unscored shortfall, never scored
        return {}, f"validate_segment rejected (unscored): {error}"
    if (seg["clip_id"], seg["source_sha256"]) != (clip_id, source_sha256):
        raise ValueError(f"tracker identity {seg['clip_id']!r}/{seg['source_sha256']!r} != expected {clip_id!r}")
    fsha = seg["frame_sha256"]
    if fsha is not None and not (isinstance(fsha, list) and len(fsha) == len(source)
                                 and all(isinstance(h, str) and len(h) == 64 for h in fsha)):
        raise ValueError("tracker frame_sha256 is not one sha256 per extracted frame")
    height = out["record"]["height_px"]  # validate_segment checked every mask against this
    return {f["frame_index"]: (f["pts_s"], f["centroid_px"][1] / height) for f in seg["frames"]}, "validate_segment OK"


def main(root=ROOT):
    record, suffix, inputs = st03_record(root)
    boundary, sealed = split(record, suffix)
    committed = json.loads((root / "evidence/S12/prediction-ST03-v2.json").read_text(encoding="utf-8"))
    prediction = projectile(boundary, sealed)
    raw = (root / ST03_TRACK).read_bytes()
    pmap = json.loads((root / "evidence/S07/S07b/recovery3/presentation-map.json").read_text(encoding="utf-8"))
    frame_pts = {f["source_frame_index"]: float(f["pts_time"]) for f in pmap["frames"]}
    load = Tracked(boundary, ST03_TRACK, frame_pts, root)
    st03 = score(boundary, sealed, prediction, committed["prediction"]["sha256"], load, "image-derived")
    notes = {"validate": load.evidence["validate"], "prefix_retrack_max_abs_vs_orch14": load.evidence["prefix_max_abs"]}
    result = gate({"projectile": st03}, root)
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
