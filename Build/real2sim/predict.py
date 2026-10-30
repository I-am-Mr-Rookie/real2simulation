"""S12c held-out prediction: prefix-only fit -> immutable predicted trace, hashed before any suffix read.

Scale-free image-height units only. Gate M is NOT_MET: no calibrated g, scale, clock or
physical-accuracy claim. Scoring against held-out observations is S12e, not here.
"""
from dataclasses import dataclass, replace
import hashlib
import json
import math
import sys

import numpy

from Build.fitter import jacobian_covariance
from Build.real2sim.boundary import GATE_M, LIMITS, _sha, fit_prefix, record_json, split
from Build.real2sim.params import ROOT, from_fit

COMMITMENT, LEGACY = "prediction/v2", "prediction/v1"


@dataclass(frozen=True)
class Prediction:
    """Immutable predicted trace: ((frame_index, pts_s, y_pred, sigma_or_None), ...).

    prediction/v2 (R-RS F1-R) commits kind, model, trace AND clip id, source sha, training sha, suffix seal
    hash and count. Defaults describe a legacy prediction/v1 object (digest over [kind, model, trace] only).
    """
    kind: str
    clip_id: str
    training_sha256: str
    suffix_identity_sha256: str
    model: str
    trace: tuple
    sha256: str
    gate_m: str = GATE_M
    source_sha256: str = None
    suffix_count: int = None
    commitment: str = LEGACY


def commitment_sha256(p):
    if p.commitment == COMMITMENT:
        return _sha([COMMITMENT, p.kind, p.model, p.trace, p.clip_id, p.source_sha256, p.training_sha256,
                     p.suffix_identity_sha256, p.suffix_count])
    if p.commitment == LEGACY:
        return _sha([p.kind, p.model, p.trace])
    raise ValueError(f"unknown prediction commitment {p.commitment!r}")


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
    p = Prediction(kind, boundary.clip_id, boundary.training_sha256, boundary.suffix_identity_sha256, model, trace,
                   "", source_sha256=boundary.source_sha256, suffix_count=boundary.suffix_count, commitment=COMMITMENT)
    return replace(p, sha256=commitment_sha256(p))


def check(prediction):
    """Raise unless the trace still matches the hash taken at prediction time."""
    if commitment_sha256(prediction) != prediction.sha256:
        raise ValueError("predicted trace changed after hashing")


def require_v2(prediction, boundary):
    """R-RS F1-R: new eligible evidence needs a v2 commitment whose bound custody equals this exact seal."""
    if prediction.commitment != COMMITMENT:
        raise ValueError("legacy prediction/v1 is audit-readable only, never newly eligible; re-commit as v2")
    check(prediction)
    bound = (prediction.clip_id, prediction.source_sha256, prediction.training_sha256,
             prediction.suffix_identity_sha256, prediction.suffix_count)
    if bound != (boundary.clip_id, boundary.source_sha256, boundary.training_sha256,
                 boundary.suffix_identity_sha256, boundary.suffix_count):
        raise ValueError("prediction/v2 commitment binds a different clip, source, training prefix or seal")
    ids = tuple((r[0], r[1]) for r in prediction.trace)
    if len(ids) != boundary.suffix_count or _sha(ids) != boundary.suffix_identity_sha256:
        raise ValueError("prediction trace does not cover the complete sealed suffix")


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


def pendulum(boundary, sealed, frequency):
    """Small-angle pendulum continuation of the tracked 1-D image coordinate.

    Same linearized solution as Build/templates/pendulum.analytic_pendulum
    (theta0 cos wt + omega0/w sin wt) projected onto one image coordinate:
    y = c + a cos(wt) + b sin(wt). w comes from a validated params angular_frequency record;
    (c, a, b) from the prefix by linear least squares with a 1-sigma OLS band (w held fixed).
    Undamped; no amplitude check in image units (Gate M NOT_MET).
    """
    ids = _identities(boundary, sealed)
    w = frequency["value"]
    if frequency.get("name") != "angular_frequency" or not w > 0:
        raise ValueError("positive angular_frequency record required")
    origin = boundary.training[0][1]
    basis = lambda t: numpy.array([1.0, math.cos(w * t), math.sin(w * t)])  # noqa: E731
    a = numpy.array([basis(p - origin) for _, p, _ in boundary.training])
    y = numpy.array([v for *_, v in boundary.training])
    coef, _, rank, _ = numpy.linalg.lstsq(a, y, rcond=None)
    if rank < 3:
        raise ValueError("prefix does not constrain pendulum amplitude and phase")
    dof = len(y) - 3
    cov = float(numpy.sum((y - a @ coef) ** 2)) / dof * numpy.linalg.inv(a.T @ a) if dof else None
    trace = []
    for i, p in ids:
        b = basis(p - origin)
        trace.append((i, p, float(b @ coef), math.sqrt(max(0.0, float(b @ cov @ b))) if dof else None))
    model = (f"small-angle pendulum y=c+a cos(wt)+b sin(wt), w={w} rad/s "
             f"({frequency['provenance']['input_provenance']}); 1-sigma OLS band, w fixed; t0=first training PTS")
    return _seal("pendulum", boundary, model, trace)


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
    # F1-R: v1 prediction-ST03.json is kept as legacy-audited; the v2 re-commit must be the same frozen trace.
    v1 = json.loads((root / "evidence/S12/prediction-ST03.json").read_text(encoding="utf-8"))["prediction"]["sha256"]
    if commitment_sha256(replace(prediction, commitment=LEGACY)) != v1:
        raise ValueError("re-derived trace differs from the legacy v1 commitment; refusing v2 re-commit")
    out = record_json(boundary, inputs=inputs, prediction=as_json(prediction),
                      parameters=from_fit(boundary, "image-derived"),
                      suffix_observations_read=False,
                      supersedes_s12a_seal={"suffix_identity_sha256": old["suffix_identity_sha256"],
                                            "suffix_count": old["suffix_count"],
                                            "reason": "frame 77 quarantine lifted: errata f76 PTS 2.535867 < f77 2.569233"},
                      legacy_v1_prediction={"path": "evidence/S12/prediction-ST03.json", "sha256": v1},
                      note=("prediction/v2 re-commit of the legacy v1 trace from the same frozen inputs. "
                            "Suffix observations NOT tracked; S12e must track exactly these sealed identities, "
                            "verify(), then score against prediction.sha256. y>1 is beyond the image bottom: "
                            "ballistic model has no floor (no ST03 bounce observation)."))
    path = root / "evidence/S12/prediction-ST03-v2.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"evidence/S12/prediction-ST03-v2.json gate_m={GATE_M} suffix={boundary.suffix_count} "
          f"sha256={prediction.sha256}")


if __name__ == "__main__":
    sys.exit(main())
