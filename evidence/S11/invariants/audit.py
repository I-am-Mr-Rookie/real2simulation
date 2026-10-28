"""Run from the repository root; print deterministic synthetic audit evidence."""
from decimal import Decimal as D, localcontext
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "tests/fitter")]
from Build.fitter.core import FitError, fit_least_squares, jacobian_covariance
from test_invariants import reference


def high_precision_known_covariance(fit, sigma):
    """Diagnostic only: same *observed* float R, but 80-digit covariance algebra."""
    with localcontext() as ctx:
        ctx.prec = 80
        n = fit.rank
        r = [[D(v) for v in row] for row in fit._r]
        inverse = [[D(0)] * n for _ in range(n)]
        for column in range(n):
            for i in reversed(range(n)):
                inverse[i][column] = (D(i == column) - sum(
                    r[i][j] * inverse[j][column] for j in range(i + 1, n))) / r[i][i]
        center, scale = D(fit._center), D(fit._scale)
        transform = [[D(1), -center/scale, center*center/(scale*scale)],
                     [D(0), 1/scale, -2*center/(scale*scale)],
                     [D(0), D(0), 1/(scale*scale)]]
        physical = [[sum(transform[i][j]*inverse[j][k] for j in range(n))
                     for k in range(n)] for i in range(n)]
        return [[float(D(sigma)**2 * sum(physical[i][k]*physical[j][k] for k in range(n)))
                 for j in range(n)] for i in range(n)]


def main():
    data = {"source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "units": {"time": "s", "position": "m"}, "provenance": "simulated",
            "known_noise_analytic_identity": "3-point quadratic at t0=0 has c0=y0, Var(c0)=sigma**2",
            "cases": []}
    numpy = None
    if importlib.util.find_spec("numpy") is not None:
        import numpy
        data["optional_numpy_version"] = numpy.__version__
    for n, exponent in ((3, 20), (3, 28), (4, 28), (4, 30), (4, 36)):
        epsilon = 2.**-exponent
        times = (0., epsilon, 1.) if n == 3 else (0., epsilon, 2*epsilon, 1.)
        positions = (0.,)*n
        fit = fit_least_squares(times, positions)
        exact = reference(times, positions, sigma=.125)[1]
        entry = {"n": n, "epsilon": epsilon, "times": times, "positions": positions,
                 "sigma_m": .125, "exact_covariance": [[float(v) for v in row] for row in exact],
                 "high_precision_same_QR_covariance": high_precision_known_covariance(fit, .125),
                 "outputs": {}}
        for mode, options in (("known_sigma", {"sigma": .125}),
                              ("declared_position_sigma", {"position_sigmas": (.125,)*n})):
            entry["outputs"][mode] = []
            for index in range(3):
                result = jacobian_covariance(fit, parameter_index=index, **options)
                entry["outputs"][mode].append({"parameter_index": index, "valid": result.valid,
                    "variance": result.variance, "covariance": result.covariance})
        if numpy is not None:
            x = numpy.column_stack([numpy.ones(n), numpy.array(times), numpy.array(times)**2])
            influence = numpy.linalg.pinv(x)
            entry["optional_svd_condition_number"] = float(numpy.linalg.cond(x))
            entry["optional_svd_covariance"] = (.125**2 * influence @ influence.T).tolist()
        data["cases"].append(entry)
    times, positions = (0., 1., 2., 3.), (0., 0., 1e-165, 0.)
    fit = fit_least_squares(times, positions)
    _, exact, residuals = reference(times, positions)
    data["residual_underflow"] = {"times": times, "positions": positions,
        "computed_rss": fit.rss, "computed_residuals": fit.residuals,
        "exact_nonzero_residual_count": sum(r != 0 for r in residuals),
        "exact_variance_positive": exact[2][2] > 0,
        "exact_variance_as_binary64": float(exact[2][2]),
        "result": jacobian_covariance(fit).__dict__,
        "explicit_known_zero_result": jacobian_covariance(fit, sigma=0).__dict__}
    print(json.dumps(data, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
