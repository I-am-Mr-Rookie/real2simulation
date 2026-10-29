"""S12c held-out prediction: prefix-only fit -> immutable predicted trace, hashed before any suffix read.

Scale-free image-height units only. Gate M is NOT_MET: no calibrated g, scale, clock or
physical-accuracy claim. Scoring against held-out observations is S12e, not here.
"""
from dataclasses import dataclass
import hashlib
import json
import math
import sys

from Build.fitter import jacobian_covariance
from Build.real2sim.boundary import GATE_M, LIMITS, _sha, fit_prefix, record_json, split
from Build.real2sim.params import ROOT, from_fit


@dataclass(frozen=True)
class Prediction:
    """Immutable predicted trace: ((frame_index, pts_s, y_pred, sigma_or_None), ...)."""
    kind: str
    clip_id: str
    training_sha256: str
    suffix_identity_sha256: str
    model: str
    trace: tuple
    sha256: str
    gate_m: str = GATE_M


def _identities(boundary, sealed):
    if _sha(boundary.training) != boundary.training_sha256:
        raise ValueError("training prefix changed after freeze")
    # Index access only: held-out observation values (row[2:]) are never touched here.
    ids = tuple((row[0], row[1]) for row in sealed)
    if _sha(ids) != boundary.suffix_identity_sha256:
        raise ValueError("suffix identities differ from the frozen seal")
    return ids


def _seal(kind, boundary, model, trace):
    trace = tuple(tuple(row) for row in trace)
    return Prediction(kind, boundary.clip_id, boundary.training_sha256,
                      boundary.suffix_identity_sha256, model, trace, _sha([kind, model, trace]))


def check(prediction):
    """Raise unless the trace still matches the hash taken at prediction time."""
    if _sha([prediction.kind, prediction.model, prediction.trace]) != prediction.sha256:
        raise ValueError("predicted trace changed after hashing")


def projectile(boundary, sealed):
    """Ballistic (AIC-selected prefix polynomial) extrapolation to the sealed suffix times."""
    ids = _identities(boundary, sealed)
    selection = fit_prefix(boundary)
    fit = next(c for c in selection.candidates if c.degree == selection.selected_degree)
    origin = boundary.training[0][1]
    times = [p - origin for _, p in ids]
    cov = jacobian_covariance(fit)
    sigma = [math.sqrt(max(0.0, sum(t ** a * t ** b * cov.covariance[a][b]
                                    for a in range(fit.rank) for b in range(fit.rank))))
             if cov.valid else None for t in times]
    model = f"prefix polynomial degree {fit.degree} (AIC), 1-sigma OLS band, t0=first training PTS"
    return _seal("projectile", boundary, model,
                 ((i, p, y, s) for (i, p), y, s in zip(ids, fit.predict(times), sigma)))


def bounce(boundary, sealed, restitution, floor_y, max_bounces=1000):
    """Prefix ballistic fit + restitution record; floor contact reflects v -> -e v (1-D, image-down).

    restitution: validated params.parameter record. Friction is irrelevant for a vertical bounce.
    """
    ids = _identities(boundary, sealed)
    e = restitution["value"]
    if restitution.get("name") != "restitution" or not 0 <= e <= 1:
        raise ValueError("restitution record in [0,1] required")
    selection = fit_prefix(boundary, degrees=(2,))
    c0, c1, c2 = selection.candidates[0].coefficients
    g, origin = 2 * c2, boundary.training[0][1]
    if g <= 0 or c0 >= floor_y:
        raise ValueError("bounce needs downward prefix acceleration and a start above the floor")
    trace, start, y0, v0, bounces = [], 0.0, c0, c1, 0
    for i, p in ids:
        t = p - origin
        while bounces < max_bounces:
            disc = v0 * v0 + 2 * g * (floor_y - y0)
            hit = start + (-v0 + math.sqrt(max(0.0, disc))) / g
            if t < hit or (v0 == 0 and y0 == floor_y):
                break
            v0, y0, start, bounces = -e * (v0 + g * (hit - start)), floor_y, hit, bounces + 1
        dt = t - start
        trace.append((i, p, min(floor_y, y0 + v0 * dt + 0.5 * g * dt * dt), None))
    model = (f"prefix quadratic + floor y={floor_y} restitution={e} ({restitution['provenance']['input_provenance']});"
             " sigma not propagated")
    return _seal("bounce", boundary, model, trace)


def as_json(prediction):
    return dict(prediction.__dict__, trace=[list(r) for r in prediction.trace])


def st03_record(root=ROOT):
    """Accepted orch14 ST03 record with the S07b-param-orch40 errata PTS applied (orch14 untouched)."""
    def load(rel):
        raw = (root / rel).read_bytes()
        return json.loads(raw), {"path": rel, "sha256": hashlib.sha256(raw).hexdigest()}
    result, track_src = load("evidence/S07/S07b/orch14/result.json")
    errata, errata_src = load("evidence/S07/S07b-errata/ST03-orch14-frame_map.json")
    pmap, map_src = load("evidence/S07/S07b/recovery3/presentation-map.json")
    record = json.loads(json.dumps(result["record"]))
    fixed = dict(errata["frame_map"])
    if errata["errata_for"] != track_src["path"] or errata["source_sha256"] != record["source_sha256"] \
            or sorted(fixed) != [f["frame_index"] for f in record["frames"]]:
        raise ValueError("errata does not match the orch14 record")
    source_pts = {f["source_frame_index"]: float(f["pts_time"]) for f in pmap["frames"]}
    for f in record["frames"]:
        f["pts_s"] = fixed[f["frame_index"]]
        if abs(f["pts_s"] - source_pts[f["frame_index"]]) > 1e-6:
            raise ValueError(f"errata PTS disagrees with presentation map at frame {f['frame_index']}")
    suffix = [(i, p) for i, p in sorted(source_pts.items()) if i > record["last_training_frame"]]
    return record, suffix, [track_src, errata_src, map_src]


def main(root=ROOT):
    """Real ST03: freeze errata-corrected boundary, predict, hash. Suffix observations do not exist yet."""
    record, suffix, inputs = st03_record(root)
    boundary, sealed = split(record, suffix)
    prediction = projectile(boundary, sealed)
    old = json.loads((root / "evidence/S12/boundary-ST03.json").read_text(encoding="utf-8"))["boundary"]
    out = record_json(boundary, inputs=inputs, prediction=as_json(prediction),
                      parameters=from_fit(boundary, "image-derived"),
                      suffix_observations_read=False,
                      supersedes_s12a_seal={"suffix_identity_sha256": old["suffix_identity_sha256"],
                                            "suffix_count": old["suffix_count"],
                                            "reason": "frame 77 quarantine lifted: errata f76 PTS 2.535867 < f77 2.569233"},
                      note=("Suffix observations NOT tracked; S12e must track exactly these sealed identities, "
                            "verify(), then score against prediction.sha256. y>1 is beyond the image bottom: "
                            "ballistic model has no floor (no ST03 bounce observation)."))
    path = root / "evidence/S12/prediction-ST03.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"evidence/S12/prediction-ST03.json gate_m={GATE_M} suffix={boundary.suffix_count} "
          f"sha256={prediction.sha256}")


if __name__ == "__main__":
    sys.exit(main())
