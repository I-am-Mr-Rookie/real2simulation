"""R12 covariance re-review probe: independent exact-Fraction oracle vs fitter (simulation only)."""
import sys, math
from fractions import Fraction as F
sys.path.insert(0, "Build")
from fitter import fit_least_squares, jacobian_covariance

def inv(m):
    n = len(m); a = [list(r) + [F(int(i == j)) for j in range(n)] for i, r in enumerate(m)]
    for c in range(n):
        p = next(i for i in range(c, n) if a[i][c] != 0); a[c], a[p] = a[p], a[c]
        d = a[c][c]; a[c] = [v / d for v in a[c]]
        for i in range(n):
            if i != c: f = a[i][c]; a[i] = [u - f * v for u, v in zip(a[i], a[c])]
    return [r[n:] for r in a]

def exact(times, s2, deg=2):
    X = [[F(t) ** j for j in range(deg + 1)] for t in times]; p = deg + 1
    G = inv([[sum(r[i] * r[j] for r in X) for j in range(p)] for i in range(p)])
    A = [[sum(G[i][k] * X[r][k] for k in range(p)) for r in range(len(X))] for i in range(p)]
    return [[sum(A[i][r] * A[j][r] * F(s2[r]) for r in range(len(X))) for j in range(p)] for i in range(p)]

def check(times, s, label):
    fit = fit_least_squares(times, (0.,) * len(times))
    worst, out = 0.0, []
    for mode, kw in (("known", {"sigma": s}), ("declared", {"position_sigmas": (s,) * len(times)})):
        r = jacobian_covariance(fit, **kw)
        if not r.valid:
            assert r.covariance is None and r.standard_error is None; out.append(f"{mode}=UNAVAILABLE"); continue
        ex = exact(times, [s * s] * len(times))
        d = [float(ex[i][i]) for i in range(3)]
        assert all(r.covariance[i][i] > 0 for i in range(3)), (label, mode, "nonpositive diag")
        rel = max(abs(r.covariance[i][j] - float(ex[i][j])) / math.sqrt(d[i] * d[j]) for i in range(3) for j in range(3))
        worst = max(worst, rel); out.append(f"{mode}=valid relerr_corr_scaled={rel:.2e}")
    print(label, *out); return worst

w = 0.0
for k in range(1, 53):
    e = 2.0 ** -k
    try:
        w = max(w, check((0., e, 1.), .125, f"3pt e=2^-{k}"))
        w = max(w, check((0., e, 2 * e, 1.), .125, f"4pt e=2^-{k}"))
    except Exception as exc:
        print(f"e=2^-{k} {type(exc).__name__}: {exc}")
print(f"WORST valid scaled full-matrix error={w:.2e} (bound target << 1e-6)")
assert w < 1e-6

fit = fit_least_squares((0., 1., 2., 3.), (0., 0., 1e-165, 0.))
for kw in ({}, {"position_sigmas": (0.,) * 4}, {"time_sigmas": (.1,) * 4}):
    r = jacobian_covariance(fit, **kw); print("underflow", kw, "valid", r.valid, "se", r.standard_error)
    assert not r.valid or (r.standard_error or 0) > 0
z = jacobian_covariance(fit, sigma=0); print("underflow sigma=0 valid", z.valid, "se", z.standard_error)
assert z.valid and z.standard_error == 0
p = jacobian_covariance(fit, position_sigmas=(.1,) * 4); print("underflow declared .1 valid", p.valid, "se", p.standard_error)
assert p.valid and p.standard_error > 0
print("PROBE PASS")

