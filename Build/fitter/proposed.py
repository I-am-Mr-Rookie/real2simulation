"""N15: fit an agent-proposed equation y(t) safely.

The equation is parsed with ast and compiled to closures over an allowlist (never eval): variable t, the agent's
parameter names, numbers, pi, + - * / ^ (literal exponent, |e| <= 10), sin cos exp sqrt log. Levenberg-Marquardt
least squares, 1 sigma from s^2 (J^T J)^-1, AIC against the built-in degree 1 and 2 fits (Build/fitter.core).
"""
import ast
import math
import operator
import re
from types import SimpleNamespace

from .core import FitError, _aic, _finite, _invert, select_model

FUNCS = {"sin": math.sin, "cos": math.cos, "exp": math.exp, "sqrt": math.sqrt, "log": math.log}
CONSTS = {"pi": math.pi}
MAX_CHARS, MAX_NODES, MAX_PARAMS, MAX_EXPONENT, MAX_POINTS, MAX_ITER = 200, 120, 8, 10.0, 5000, 200
_PARAM = re.compile(r"[A-Za-z][A-Za-z0-9]{0,15}")
_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: math.pow}  # math.pow: float only, raises instead of returning complex
UNCERTAINTY = "1 sigma from s^2 (J^T J)^-1; Gaussian iid residuals, local linearisation, clock and scale held fixed"


def _literal(node):
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        v = _literal(node.operand)
        return None if v is None else (-v if isinstance(node.op, ast.USub) else v)
    ok = isinstance(node, ast.Constant) and type(node.value) in (int, float)
    return float(node.value) if ok and math.isfinite(node.value) else None


def compile_equation(equation, parameters):
    """Return f(env) for the equation; env maps t and each parameter to a float. Raises FitError."""
    if not isinstance(equation, str) or not equation.strip() or len(equation) > MAX_CHARS:
        raise FitError("equation_must_be_1_to_200_characters")
    if not isinstance(parameters, (list, tuple)):
        raise FitError("parameters_must_be_a_list_of_names")
    names = tuple(parameters)
    if not 1 <= len(names) <= MAX_PARAMS or len(set(names)) != len(names) or any(
            not isinstance(p, str) or not _PARAM.fullmatch(p) or p == "t" or p in FUNCS or p in CONSTS for p in names):
        raise FitError("parameters_must_be_1_to_8_unique_names_not_t_or_a_function")
    try:
        tree = ast.parse(equation.replace("^", "**"), mode="eval")
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        raise FitError("equation_syntax_error") from None
    if sum(1 for _ in ast.walk(tree)) > MAX_NODES:
        raise FitError("equation_too_long")
    used = set()

    def build(node):
        value = _literal(node) if isinstance(node, ast.Constant) else None
        if value is not None:
            return lambda env: value
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id == "t" or node.id in names:
                used.add(node.id)
                key = node.id
                return lambda env: env[key]
            if node.id in CONSTS:
                c = CONSTS[node.id]
                return lambda env: c
            raise FitError(f"name_not_allowed:{node.id[:20]}")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            f = build(node.operand)
            return (lambda env: -f(env)) if isinstance(node.op, ast.USub) else f
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
            if isinstance(node.op, ast.Pow):
                e = _literal(node.right)
                if e is None or abs(e) > MAX_EXPONENT:
                    raise FitError("exponent_must_be_a_number_with_magnitude_at_most_10")
            left, right, op = build(node.left), build(node.right), _BIN[type(node.op)]
            return lambda env: op(left(env), right(env))
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCS
                and len(node.args) == 1 and not node.keywords):
            f, arg = FUNCS[node.func.id], build(node.args[0])
            return lambda env: f(arg(env))
        raise FitError(f"syntax_not_allowed:{type(node).__name__}")

    model = build(tree.body)
    missing = [p for p in names if p not in used]
    if missing:
        raise FitError(f"parameter_not_in_equation:{missing[0]}")
    return model


def _residuals(model, names, theta, t, y):
    env = dict(zip(names, theta))
    out = []
    try:
        for ti, yi in zip(t, y):
            env["t"] = ti
            r = yi - model(env)
            if not math.isfinite(r):
                return None
            out.append(r)
    except (OverflowError, ValueError, ZeroDivisionError, TypeError):
        return None
    return out


def _jacobian(model, names, theta, t, y, r0):
    """Columns of d(model)/d(theta_j) by central differences (forward if one side is undefined)."""
    cols = []
    for j, v in enumerate(theta):
        h = 1e-6 * max(1.0, abs(v))
        up, dn = list(theta), list(theta)
        up[j], dn[j] = v + h, v - h
        ru, rd = _residuals(model, names, up, t, y), _residuals(model, names, dn, t, y)
        if ru and rd:
            cols.append([(a - b) / (2 * h) for a, b in zip(rd, ru)])  # model = y - r
        elif ru or rd:
            rs, s = (ru, 1.0) if ru else (rd, -1.0)
            cols.append([s * (a - b) / h for a, b in zip(r0, rs)])
        else:
            return None
    return cols


def _normal(cols, r):
    a = [[math.fsum(x * z for x, z in zip(ci, cj)) for cj in cols] for ci in cols]
    return a, [math.fsum(x * e for x, e in zip(c, r)) for c in cols]


def _scaled_inverse(a, damping=0.0):
    """(A + damping diag A)^-1 via the unit-diagonal scaled matrix, so badly scaled parameters do not look singular."""
    d = [math.sqrt(a[i][i]) if a[i][i] > 0 else 0.0 for i in range(len(a))]
    if not all(math.isfinite(v) and v > 0 for v in d):
        return None
    c = [[a[i][j] / (d[i] * d[j]) + (damping if i == j else 0.0) for j in range(len(a))] for i in range(len(a))]
    inv = _invert(c)
    return None if inv is None else [[inv[i][j] / (d[i] * d[j]) for j in range(len(a))] for i in range(len(a))]


def _json(v):
    return v if v is not None and math.isfinite(v) else None


def fit_equation(times, values, equation, parameters, initial_guess):
    """Fit equation(t; parameters) to (times, values); return parameters +/- 1 sigma and an AIC comparison."""
    model = compile_equation(equation, parameters)
    names = tuple(parameters)
    t, y = _finite(times, "times"), _finite(values, "values")
    theta = list(_finite(initial_guess, "initial_guess"))
    n, k = len(t), len(names)
    if len(y) != n or n > MAX_POINTS:
        raise FitError("times_values_length_mismatch_or_over_5000")
    if len(theta) != k:
        raise FitError("initial_guess_must_match_parameters")
    if n <= k + 1:
        raise FitError("insufficient_observations")
    r = _residuals(model, names, theta, t, y)
    if r is None:
        raise FitError("equation_undefined_at_initial_guess")
    rss, lam, converged, it = math.fsum(e * e for e in r), 1e-3, False, 0
    for it in range(1, MAX_ITER + 1):
        cols = _jacobian(model, names, theta, t, y, r)
        if cols is None:
            raise FitError("equation_undefined_near_guess")
        a, g = _normal(cols, r)
        for j, name in enumerate(names):
            if not a[j][j] > 0:
                raise FitError(f"parameter_has_no_effect_at_guess:{name}")
        step = None
        while lam < 1e12:
            inv = _scaled_inverse(a, lam)
            if inv is not None:
                trial = [v + math.fsum(inv[j][m] * g[m] for m in range(k)) for j, v in enumerate(theta)]
                rt = _residuals(model, names, trial, t, y)
                if rt is not None and math.fsum(e * e for e in rt) < rss:
                    step = trial, rt
                    break
            lam *= 10
        if step is None:  # no downhill step even with heavy damping: at a (local) minimum
            converged = True
            break
        old, (theta, r) = rss, step
        rss, lam = math.fsum(e * e for e in r), max(lam / 10, 1e-12)
        if old - rss <= 1e-12 * old:
            converged = True
            break
    cols = _jacobian(model, names, theta, t, y, r)
    inv = _scaled_inverse(_normal(cols, r)[0]) if cols else None
    s2 = rss / (n - k)
    sigma = [math.sqrt(s2 * inv[j][j]) if inv and inv[j][j] > 0 else None for j in range(k)]
    aic = _json(_aic(SimpleNamespace(residuals=tuple(r), n=n, k=k)))
    comparison = [{"model": f"proposed: {equation}", "k": k, "aic": aic}]
    try:
        sel = select_model(t, y, (1, 2))
        comparison += [{"model": "built-in line (degree 1)" if f.degree == 1 else "built-in parabola (degree 2)",
                        "k": f.k, "aic": _json(s)} for f, s in zip(sel.candidates, sel.aic)]
    except FitError as exc:
        comparison.append({"model": "built-in degree 1 and 2", "aic": None, "error": str(exc)})
    scored = [c for c in comparison if c["aic"] is not None]
    builtin = [c["aic"] for c in comparison[1:] if c["aic"] is not None]
    return {
        "equation": equation, "converged": converged, "iterations": it, "n": n, "k": k,
        "parameters": {p: {"value": v, "sigma_1": s} for p, v, s in zip(names, theta, sigma)},
        "rss": rss, "rmse": math.sqrt(rss / n), "aic": aic, "comparison": comparison,
        "best_by_aic": min(scored, key=lambda c: c["aic"])["model"] if scored else None,
        "delta_aic_vs_best_builtin": aic - min(builtin) if builtin and aic is not None else None,
        "uncertainty": UNCERTAINTY if None not in sigma else UNCERTAINTY + "; unavailable for unidentifiable parameters",
    }
