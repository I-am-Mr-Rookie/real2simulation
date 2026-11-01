"""N02 Gate RS rerun with hosted SAM 3.1 observations of full ST03 (no network, no spend).

Same check as evidence/S12/gate-rs: the committed prediction/v2 (orch14 prefix f58-76, sealed suffix f77-542)
scored by Build/real2sim.score against suffix observations, now from the hosted tracker. Plus a hosted-only
prefix fit with 1-sigma band and the Build/measurement free-fall fitter outcome. Units: image-height fraction.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.fitter import jacobian_covariance  # noqa: E402
from Build.measurement import hosted_sam  # noqa: E402
from Build.measurement.free_fall import FitAbstention, fit_free_fall  # noqa: E402
from Build.real2sim.boundary import GATE_M, LIMITS, fit_prefix, split  # noqa: E402
from Build.real2sim.fallback import decide  # noqa: E402
from Build.real2sim.predict import projectile, st03_record  # noqa: E402
from Build.real2sim.score import PREFIX_TOL, _rms, gate, score  # noqa: E402

OUT = ROOT / "evidence/N02"


def main():
    record, suffix, inputs = st03_record(ROOT)
    boundary, sealed = split(record, suffix)
    committed = json.loads((ROOT / "evidence/S12/prediction-ST03-v2.json").read_text(encoding="utf-8"))
    prediction = projectile(boundary, sealed)
    pmap = json.loads((ROOT / "evidence/S07/S07b/recovery3/presentation-map.json").read_text(encoding="utf-8"))
    frame_map = [(f["source_frame_index"], float(f["pts_time"])) for f in pmap["frames"]]
    resp = json.loads((OUT / "resp-apple.json").read_text(encoding="utf-8"))
    track = hosted_sam.result(resp)  # moving object chosen by largest centroid travel
    meta = {k: v for k, v in record.items() if k not in ("frames", "tracking")}
    hosted = hosted_sam.to_record(track, meta, frame_map)
    height = hosted["height_px"]
    by_index = {f["frame_index"]: f for f in hosted["frames"]}

    # 1. prefix custody: hosted box centre vs orch14 mask centroid on the committed training frames
    prefix_diff = [abs(by_index[i]["y_px"] / height - y) for i, _, y in boundary.training]
    # 2. committed prediction scored against hosted suffix observations
    obs = {i: (by_index[i]["pts_s"], by_index[i]["y_px"] / height) for i, _ in sealed if i in by_index}
    st03 = score(boundary, sealed, prediction, committed["prediction"]["sha256"], lambda: obs, "image-derived")
    result = gate({"projectile": st03, "bounce": None, "pendulum": None}, ROOT)

    # 3. hosted-only: same training frame indices, prefix fit with 1-sigma, prediction scored on hosted suffix
    train_ids = {i for i, _, _ in boundary.training}
    h_record = dict(hosted, frames=[f for f in hosted["frames"] if f["frame_index"] in train_ids
                                    or f["frame_index"] > boundary.last_training_frame])
    hb, hs = split(h_record)
    selection = fit_prefix(hb)
    fit = next(c for c in selection.candidates if c.degree == selection.selected_degree)
    cov = jacobian_covariance(fit)
    hp = projectile(hb, hs)
    h_err = [p[2] - o[2] for p, o in zip(hp.trace, hs)]
    land = next(i for i, (_, _, y) in enumerate(hs[1:], 1) if y < hs[i - 1][2])  # first upward step = impact
    accel = sigma = None
    if fit.degree == 2:
        accel = 2 * fit.coefficients[2] * height
        sigma = 2 * math.sqrt(cov.covariance[2][2]) * height if cov.valid else None
    try:
        fit_free_fall(hosted)
        ff = "fitted"
    except FitAbstention as error:
        ff = {"abstained": list(error.blockers)}

    out = {"run": "N02-orch250", "gate": "RS", "gate_m": GATE_M, "limitations": list(LIMITS) + [
               "hosted points are box centres; orch14 prefix points are mask centroids",
               "hosted artifact has no accepted-tracking custody entry (evidence/S12/accepted-tracking.json); "
               "controller review needed before it can be gate-eligible"],
           "tracker": {"model": "sam-3.1 (Meta Model API, hosted)", "prompt": "apple",
                       "frames_returned": track["frame_count"], "moving_object_id": track["object_id"],
                       "travel_px": track["travel_px"], "missing_frames": len(track["missing"]),
                       "video_frames_processed": track["video_frames_processed"],
                       "response": "evidence/N02/resp-apple.json"},
           "prefix_retrack": {"frames": len(prefix_diff), "max_abs": max(prefix_diff), "tolerance": PREFIX_TOL,
                              "within_tolerance": max(prefix_diff) <= PREFIX_TOL},
           "committed_prediction_score": {k: v for k, v in st03.items() if k != "tracking_evidence"},
           "gate_rs": result, "display_decision": decide(result["median"]),
           "display_decision_projectile_only_diagnostic": decide(st03["normalized_rms"]),
           "hosted_only_fit": {
               "training_frames": len(hb.training), "selected_degree": fit.degree, "aic_criterion": selection.criterion,
               "coefficients_image_height": fit.coefficients, "rmse_image_height": fit.rmse,
               "covariance_valid": cov.valid, "noise_model": cov.noise_model,
               "playback_accel_px_s2": accel, "playback_accel_sigma_px_s2": sigma,
               "accel_label": "pixels per playback second squared; not g (scale and capture clock unverified)",
               "suffix_frames": len(hs), "suffix_rms": _rms(h_err), "suffix_rms_first5": _rms(h_err[:5]),
               "suffix_rms_until_impact": _rms(h_err[:land]), "impact_suffix_frames": land,
               "max_abs": max(map(abs, h_err))},
           "measurement_free_fall_fitter": ff}
    (OUT / "gate-rs.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"prefix_max_abs": max(prefix_diff), "committed_rms": st03["normalized_rms"],
                      "coverage": st03["coverage"], "scored": st03["scored"], "gate": result["status"],
                      "ineligible": st03["ineligible_reason"], "hosted_fit_deg": fit.degree, "accel": accel,
                      "sigma": sigma, "hosted_rms": _rms(h_err), "until_impact": _rms(h_err[:land]),
                      "land": land, "ff": ff}, default=str))


if __name__ == "__main__":
    main()
