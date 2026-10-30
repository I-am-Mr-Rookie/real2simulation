"""S21c: held-out prediction errors (Gate RS, scale-free image-height fraction, Q15=A), ONLY from pinned evidence.

python Build/benchmark/predictions.py [out.json]  -> writes evidence/S21/S21c-predictions.json (deterministic).
python Build/benchmark/predictions.py --md         -> prints the generated BENCHMARK.md results table.
Runs the S21a freeze + leakage check first; recomputes the ST03 suffix error from the sealed prediction trace and
the held-out track and fails closed if it disagrees with the recorded Gate RS value or touches a training frame.
"""
import hashlib, json, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import manifest as mf
from errors import markdown, ref

OUT = mf.ROOT / "evidence/S21/S21c-predictions.json"
TOL = 1e-12  # same float inputs and formula as Gate RS scoring; only summation-order noise allowed
# S12f (accepted Oct30) post-dates the frozen S21a manifest; pinned here instead of re-freezing the manifest.
EXTRA = {"fallback_s12f": {"path": "evidence/S12/S12f-fallback.json",
                           "sha256": "a83af728ffe7822f651f9743f3529c1c9ba4ce010c3a9cf0eec067bd315aee8d"}}


def suffix_errors(docs, split):
    """(frame, y_pred - y_obs, pred 1-sigma) for scored held-out frames; all in image-height fractions."""
    r = lambda ev, ptr: mf.resolve(docs, ref(ev, ptr))
    after, h = split["after"], r("heldout_track_st03", "/record/height_px")
    pred = {f[0]: f for f in r("prediction_st03", "/prediction/trace")}
    obs = [f for f in r("heldout_track_st03", "/record/frames") if f["frame_index"] > after]
    train = {f["frame_index"] for f in r("training_st03", "/record/frames")}
    if not obs or any(f["frame_index"] in train or f["frame_index"] not in pred for f in obs):
        raise ValueError("scored frame is a training frame or outside the sealed prediction")
    return [(f["frame_index"], pred[f["frame_index"]][2] - f["y_px"] / h, pred[f["frame_index"]][3]) for f in obs]


def rows(docs, split):
    r = lambda ev, ptr: mf.resolve(docs, ref(ev, ptr))
    out, unit = [], r("prediction_st03", "/units")

    def add(id, cls, value=None, *, sources, uncertainty=None, uncertainty_kind=None, n=None,
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

    # projectile ST03: recomputed suffix error, cross-checked against the recorded Gate RS diagnostic
    p = "/clips/projectile"
    e = suffix_errors(docs, split)
    rms = math.sqrt(sum(d * d for _, d, _ in e) / len(e))
    mx = max(abs(d) for _, d, _ in e)
    for got, ptr in ((rms, f"{p}/normalized_rms"), (mx, f"{p}/max_abs"), (len(e), f"{p}/scored_frames")):
        if abs(got - r("gate_rs", ptr)) > TOL:
            raise ValueError(f"recomputed {got} != recorded gate_rs{ptr} {r('gate_rs', ptr)}")
    if r("gate_rs", f"{p}/scored") is not False:
        raise ValueError("ST03 unexpectedly gate-scored; re-review before reporting as diagnostic")
    src = [ref("prediction_st03", "/prediction/trace"), ref("heldout_track_st03", "/record/frames"),
           ref("heldout_track_st03", "/record/height_px")]
    band = max(s for _, _, s in e)
    cov = (f"diagnostic only, not gate-scored: {len(e)}/{r('gate_rs', f'{p}/sealed_frames')} sealed suffix frames "
           f"(frames {e[0][0]}-{e[-1][0]}, all after last training frame {split['after']})")
    add("st03_heldout_normalized_rms", "measured", rms, sources=src + [ref("gate_rs", f"{p}/normalized_rms")],
        uncertainty=band, uncertainty_kind="max prediction 1-sigma OLS band over scored frames (model band only)",
        n=len(e), note=f"{cov}; tracking re-track repeatability "
                       f"{r('gate_rs', f'{p}/prefix_retrack_max_abs_vs_orch14')} (max abs, prefix frames)")
    add("st03_heldout_max_abs_error", "measured", mx, sources=src + [ref("gate_rs", f"{p}/max_abs")],
        uncertainty=band, uncertainty_kind="max prediction 1-sigma OLS band over scored frames (model band only)",
        n=len(e), note=cov)
    add("st03_range_error", "unavailable",
        sources=[null("gate_rs", "/result/per_category_normalized_rms/projectile")],
        reason=r("gate_rs", "/shortfall_reasons/projectile"),
        reason_sources=[ref("gate_rs", "/shortfall_reasons/projectile"), ref("gate_rs", "/limitations/0")],
        note="prefix ballistic fit has no floor model, so no predicted landing/range to compare; not gate-scored")
    add("bounce_height_error", "unavailable",
        sources=[null("gate_rs", "/result/per_category_normalized_rms/bounce"), null("gate_rs", "/clips/bounce")],
        reason=r("gate_rs", "/shortfall_reasons/bounce"), reason_sources=[ref("gate_rs", "/shortfall_reasons/bounce")])
    add("pendulum_period_error", "unavailable",
        sources=[null("gate_rs", "/result/per_category_normalized_rms/pendulum"), null("gate_rs", "/clips/pendulum")],
        reason=r("gate_rs", "/shortfall_reasons/pendulum"),
        reason_sources=[ref("gate_rs", "/shortfall_reasons/pendulum")])
    add("gate_rs_median_heldout_error", "unavailable",
        sources=[null("gate_rs", "/result/median"), null("fallback_s12f", "/gate_rs/median")],
        reason=f"Gate RS {r('gate_rs', '/result/status')}; S12f {r('fallback_s12f', '/decision/tier')}: "
               f"{r('fallback_s12f', '/decision/reason')}",
        reason_sources=[ref("gate_rs", "/result/status"), ref("fallback_s12f", "/decision/tier"),
                        ref("fallback_s12f", "/decision/reason")],
        note=f"threshold {r('gate_rs', '/result/threshold')}; {r('gate_rs', '/claims')}")
    return out


def build(m=None):
    m = m or json.loads(mf.DEFAULT.read_text(encoding="utf-8"))
    chk = mf.check(m)  # sha pins + leakage (held-out frames never in the fitting prefix)
    if not chk["ok"]:
        raise ValueError(f"frozen manifest check failed: {chk['errors']}")
    docs, errs = mf._load({"evidence": {**m["evidence"], **EXTRA}})
    if errs:
        raise ValueError(f"evidence pin failed: {errs}")
    if docs["fallback_s12f"]["gate_rs"]["sha256"] != m["evidence"]["gate_rs"]["sha256"]:
        raise ValueError("S12f decision was made on a different gate_rs evidence file")
    split = {**chk["split"], "after": mf.resolve(docs, m["split"]["scored_frames"]["after"])}
    rs = rows(docs, split)
    return {"schema": "s21c-predictions/1", "generated_by": "Build/benchmark/predictions.py",
            "manifest_sha256": hashlib.sha256(mf.DEFAULT.read_bytes()).hexdigest(),
            "evidence_sha256": {k: e["sha256"] for k, e in {**m["evidence"], **EXTRA}.items()},
            "gates": chk["gates"], "split": chk["split"],
            "summary": {k: sum(x["class"] == k for x in rs) for k in ("measured", "simulated", "unavailable")},
            "rows": rs}


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
