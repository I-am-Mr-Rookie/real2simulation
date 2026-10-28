"""R10-gate-rereview: independent NumPy/SciPy checks of S11 fixes (pinned 72b1cbf)."""
import json, math, sys
import numpy as np
from scipy import special, stats
sys.path.insert(0, ".")
from Build.fitter.api import handle
from Build.fitter.core import coverage_regression, fit_least_squares, jacobian_covariance

out = {}
out["t_17_0975_scipy"] = float(special.stdtrit(17, 0.975))
out["t_matches_constant"] = out["t_17_0975_scipy"] == 2.1098155778333156
runs = [coverage_regression(seed=k) for k in range(200)]
out["batches_200"] = {"fail": sum(r.status == "FAIL" for r in runs), "mean": float(np.mean([r.coverage for r in runs])),
                      "expected_binomial_fail_p": float(stats.binom.cdf(89, 100, 0.95)),
                      "threshold": 0.90, "dof": runs[0].degrees_of_freedom, "multiplier": runs[0].interval_z}

def q(v, u, unit):
    return {"value": v, "unit": unit, "uncertainty": u, "source": {"label": "simulated", "evidence": "rereview"}}

def reference(t, y, sy, st, deg=2):
    t, y, sy, st = map(np.asarray, (t, y, sy, st))
    X = np.vander(t, deg + 1, increasing=True)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    dof = len(t) - (deg + 1)
    rss = float(np.sum((y - X @ beta) ** 2))
    vel = sum(j * beta[j] * t ** (j - 1) for j in range(1, deg + 1))
    v = np.maximum(rss / dof if dof > 0 else 0.0, sy ** 2 + (vel * st) ** 2)
    A = np.linalg.inv(X.T @ X)
    cov = A @ X.T @ np.diag(v) @ X @ A
    return 2 * beta[2], 2 * math.sqrt(cov[2, 2]), 2 * math.sqrt(A[2, 2] * max(np.max(sy), math.sqrt(rss / dof) if dof > 0 else 0) ** 2)

rng = np.random.default_rng(7)
t = np.linspace(0, 1.9, 20); y = 1 + 0.4 * t + 0.5 * 9.81 * t * t
cases = {
    "audit_noise_free_sy0.05_st0.01": (y, np.full(20, 0.05), np.full(20, 0.01)),
    "noisy_heteroscedastic": (y + rng.normal(0, 0.02, 20), np.linspace(0.001, 0.03, 20), np.linspace(0, 0.004, 20)),
    "residual_floor_dominates": (y + rng.normal(0, 0.05, 20), np.full(20, 1e-6), np.zeros(20)),
}
out["covariance"] = {}
for name, (yy, sy, st) in cases.items():
    g, se, legacy_se = reference(t, yy, sy, st)
    req = {"times": [q(float(a), float(b), "s") for a, b in zip(t, st)], "positions": [q(float(a), float(b), "m") for a, b in zip(yy, sy)], "degree": 2}
    new = handle(req)
    old = handle({**req, "uncertainty_model": "iid_fixed_clock_scale"})
    out["covariance"][name] = {"default_model": new["uncertainty"]["model"], "api_u": new["gravity"]["uncertainty"], "ref_u": se,
        "rel_err": abs(new["gravity"]["uncertainty"] - se) / se, "api_g": new["gravity"]["value"], "ref_g": g,
        "legacy_api_u": old["gravity"]["uncertainty"], "legacy_ref_u": legacy_se,
        "legacy_rel_err": abs(old["gravity"]["uncertainty"] - legacy_se) / legacy_se,
        "one_sigma_label": new["uncertainty"]["quantity_uncertainty"]}

def status(req):
    try:
        res = handle(req)
        return {"status": res.get("status"), "cov": (res.get("covariance") or {}).get("status"), "g": res.get("gravity") and res["gravity"]["uncertainty"], "err": res.get("error")}
    except Exception as exc:  # report raw
        return {"exception": repr(exc)}
t3 = [0.0, 0.5, 1.0]; y3 = [1 + 0.5 * 9.81 * x * x for x in t3]
mk = lambda tt, yy, sy, st: {"times": [q(a, st, "s") for a in tt], "positions": [q(b, sy, "m") for b in yy], "degree": 2}
out["edges"] = {
    "zero_dof_zero_sigma": status(mk(t3, y3, 0.0, 0.0)),
    "zero_dof_declared_sigma": status(mk(t3, y3, 0.01, 0.0)),
    "zero_dof_legacy_zero_sigma": status({**mk(t3, y3, 0.0, 0.0), "uncertainty_model": "iid_fixed_clock_scale"}),
    "underflow_sigma_1e-200": status(mk(t.tolist(), y.tolist(), 1e-200, 0.0)),
    "overflow_sigma_1e200": status(mk(t.tolist(), y.tolist(), 1e200, 0.0)),
    "overflow_time_sigma_1e200": status(mk(t.tolist(), y.tolist(), 0.0, 1e200)),
    "rank_deficient_same_time": status(mk([1.0] * 5, [1.0] * 5, 0.01, 0.0)),
    "unknown_model": status({**mk(t3, y3, 0.01, 0.0), "uncertainty_model": "bogus"}),
}
print(json.dumps(out, indent=1, default=str))
