"""S21b: gravity and scene-scale errors, ONLY from the S21a frozen manifest's sha256-pinned evidence.

python Build/benchmark/errors.py [out.json]  -> writes evidence/S21/S21b-errors.json (deterministic).
python Build/benchmark/errors.py --md         -> prints the generated BENCHMARK.md results table.
Exit 1 if the freeze/leakage check fails. Fails closed if an "unavailable" value is not null in evidence.
"""
import hashlib, json, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import manifest as mf

OUT = mf.ROOT / "evidence/S21/S21b-errors.json"
ANGLE_TOL_DEG = 0.01  # recorded angles carry 3 decimals; recomputation must agree within rounding


def ref(ev, ptr):
    return {"evidence": ev, "pointer": ptr}


def _angle_deg(a, b):
    dot = sum(x * y for x, y in zip(a, b)) / (math.hypot(*a) * math.hypot(*b))
    return math.degrees(math.acos(max(-1.0, min(1.0, dot))))


def rows(docs):
    r = lambda ev, ptr: mf.resolve(docs, ref(ev, ptr))
    out = []

    def add(id, cls, unit, value=None, *, sources, uncertainty=None, uncertainty_kind=None, n=None,
            reason=None, reason_sources=(), note=None):
        if cls == "unavailable":
            if value is not None or not reason:
                raise ValueError(f"{id}: unavailable needs null value and a reason")
        elif not mf._num(value):
            raise ValueError(f"{id}: measured value must be a number from evidence")
        out.append({"id": id, "class": cls, "value": value, "unit": unit, "uncertainty": uncertainty,
                    "uncertainty_kind": uncertainty_kind, "n": n, "sources": list(sources),
                    "reason": reason, "reason_sources": list(reason_sources), "note": note})

    def null(ev, ptr):  # fail closed: never reinterpret a non-null "unavailable" value
        v = r(ev, ptr)
        if v is not None:
            raise ValueError(f"{ev}{ptr} expected null (unavailable), got {v!r}")
        return ref(ev, ptr)

    # gravity magnitude: needs metric scale + capture clock (Gate M)
    gm = ref("boundary_st03", "/gate_m_source/status")
    add("gravity_magnitude_error_m_s2", "unavailable", "m/s^2",
        sources=[null("scale_s05d", "/RM02/gravity/magnitude_m_s2"),
                 null("scale_s05d", "/RM04/gravity/magnitude_m_s2"),
                 null("scale_s05d", "/RM05/gravity/magnitude_m_s2")],
        reason=f"Gate M {mf.resolve(docs, gm)}: {r('gate_rs', '/limitations/0')}",
        reason_sources=[gm, ref("gate_rs", "/limitations/0"), ref("prediction_st03", "/limitations/1")],
        note="applies to ST03 and RM02/RM04/RM05; no clip has calibrated g")

    # ST03 image-space g: fit precision only (no true-g reference in image units)
    if r("prediction_st03", "/parameters/0/name") != "g":
        raise ValueError("prediction_st03 /parameters/0 is not g")
    g, gu = r("prediction_st03", "/parameters/0/value"), r("prediction_st03", "/parameters/0/uncertainty")
    add("st03_g_image_relative_uncertainty", "measured", "fraction (1-sigma / abs g)", gu / abs(g),
        sources=[ref("prediction_st03", "/parameters/0/value"), ref("prediction_st03", "/parameters/0/uncertainty")],
        uncertainty_kind=r("prediction_st03", "/parameters/0/uncertainty_kind"),
        n=r("prediction_st03", "/boundary/training_count"),
        note=f"g = {g} +/- {gu} {r('prediction_st03', '/parameters/0/unit')} (prefix fit, uncalibrated); "
             "precision of the fit, NOT an error vs true g")

    # gravity direction per scene (floor-normal estimate)
    for c in ("RM02", "RM04"):
        s, k = f"/{c}", c.lower()
        n_in, n_boot = r("scale_s05d", f"{s}/floor/inliers"), r("scale_s05d", f"{s}/params/bootstrap")
        std = r("scale_s05d", f"{s}/gravity/uncertainty_deg_1sd")
        basis = ref("scale_s05d", f"{s}/gravity/basis")
        add(f"{k}_gravity_direction_error_vs_truth", "unavailable", "deg", sources=[basis],
            reason=f"no independent ground-truth vertical in evidence; basis: {mf.resolve(docs, basis)}",
            reason_sources=[basis])
        add(f"{k}_gravity_direction_bootstrap_sd", "measured", "deg (1 sd)", std,
            sources=[ref("scale_s05d", f"{s}/gravity/uncertainty_deg_1sd"),
                     ref("scale_s05d", f"{s}/floor/normal_bootstrap_max_deg")],
            uncertainty=r("scale_s05d", f"{s}/floor/normal_bootstrap_max_deg"),
            uncertainty_kind=f"bootstrap max deviation over {n_boot} resamples", n=n_in,
            note="n = floor inlier points; precision, not accuracy")
        a = _angle_deg(r("scale_s05d", f"{s}/gravity/direction"), r("scale_s05d", f"{s}/camera_down_prior"))
        rec = r("scale_s05d", f"{s}/floor/angle_to_camera_down_prior_deg")
        if abs(a - rec) > ANGLE_TOL_DEG:
            raise ValueError(f"{c}: recomputed prior angle {a} != recorded {rec}")
        add(f"{k}_gravity_vs_camera_down_prior", "measured", "deg", a,
            sources=[ref("scale_s05d", f"{s}/gravity/direction"), ref("scale_s05d", f"{s}/camera_down_prior"),
                     ref("scale_s05d", f"{s}/floor/angle_to_camera_down_prior_deg")],
            uncertainty=std, uncertainty_kind="floor-normal bootstrap 1 sd (prior uncertainty unrecorded)", n=n_in,
            note="disagreement between two estimates, not error vs truth; recomputed from pinned vectors")
    add("rm05_gravity_direction", "unavailable", "deg",
        sources=[null("scale_s05d", "/RM05/gravity/direction")],
        reason=r("scale_s05d", "/RM05/gravity/reason"), reason_sources=[ref("scale_s05d", "/RM05/gravity/reason")])

    # scene scale
    for c in ("RM02", "RM04", "RM05"):
        s, k = f"/{c}", c.lower()
        add(f"{k}_metric_scale_error", "unavailable", "m per model unit",
            sources=[null("scale_s05d", f"{s}/metric_scale/metres_per_model_unit"),
                     ref("scale_s05d", f"{s}/mapanything_metric_scaling_factor")],
            reason=f"{r('scale_s05d', f'{s}/metric_scale/reason')}; {r('scale_s05d', f'{s}/metric_scale/missing_reference')}",
            reason_sources=[ref("scale_s05d", f"{s}/metric_scale/reason"),
                            ref("scale_s05d", f"{s}/metric_scale/missing_reference")],
            note="MapAnything's self-reported scaling factor has no reference to compare against")
        add(f"{k}_floor_plane_rms_residual", "measured", "model units (not metres)",
            r("scale_s05d", f"{s}/floor/rms_residual"),
            sources=[ref("scale_s05d", f"{s}/floor/rms_residual"), ref("scale_s05d", f"{s}/floor/p95_abs_residual")],
            uncertainty=r("scale_s05d", f"{s}/floor/p95_abs_residual"), uncertainty_kind="p95 abs residual",
            n=r("scale_s05d", f"{s}/floor/inliers"), note="geometric fit error in unscaled model units")
    add("st03_metric_scale_error", "unavailable", "m per image-height",
        sources=[ref("prediction_st03", "/parameters/0/unit")],
        reason=r("prediction_st03", "/limitations/1"), reason_sources=[ref("prediction_st03", "/limitations/1")])
    return out


def build(m=None):
    m = m or json.loads(mf.DEFAULT.read_text(encoding="utf-8"))
    chk = mf.check(m)
    if not chk["ok"]:
        raise ValueError(f"frozen manifest check failed: {chk['errors']}")
    docs, _ = mf._load(m)
    rs = rows(docs)
    return {"schema": "s21b-errors/1", "generated_by": "Build/benchmark/errors.py",
            "manifest_sha256": hashlib.sha256(mf.DEFAULT.read_bytes()).hexdigest(),
            "evidence_sha256": {k: e["sha256"] for k, e in m["evidence"].items()},
            "gates": chk["gates"],
            "summary": {k: sum(x["class"] == k for x in rs) for k in ("measured", "unavailable")},
            "rows": rs}


def markdown(doc):
    """Generated table pasted verbatim into BENCHMARK.md; test_errors checks it is current."""
    f = lambda v: "UNAVAILABLE" if v is None else (f"{v:.4g}" if mf._num(v) else str(v))
    lines = ["| id | class | value | unit | uncertainty (kind) | n | reason |", "|---|---|---|---|---|---|---|"]
    for x in doc["rows"]:
        unc = "" if x["uncertainty"] is None else f"{f(x['uncertainty'])} ({x['uncertainty_kind']})"
        lines.append(f"| {x['id']} | {x['class']} | {f(x['value'])} | {x['unit']} | {unc} | "
                     f"{'' if x['n'] is None else x['n']} | {x['reason'] or ''} |")
    return "\n".join(lines)


if __name__ == "__main__":
    if sys.argv[1:] == ["--md"]:
        sys.exit(print(markdown(build())))
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    try:
        doc = build()
    except ValueError as e:
        sys.exit(str(e))
    out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(doc["summary"]), out)
