"""N15: agent-proposed equation fitter (grammar safety, damped oscillation recovery, tool wiring)."""
import math
import random

import pytest

from Build.agent import core
from Build.fitter.core import FitError
from Build.fitter.proposed import compile_equation, fit_equation


@pytest.mark.parametrize("eq,params", [
    ("t.__class__", ["a"]),                      # attribute access
    ("a*__import__('os')", ["a"]),               # call outside the allowlist
    ("a*abs(t)", ["a"]),
    ("a*math.sin(t)", ["a"]),
    ("a*t^1000", ["a"]),                         # huge exponent
    ("a*2^2^2^2^2", ["a"]),                      # tower: exponent is not a literal
    ("a*t^b", ["a", "b"]),                       # parameter exponent
    ("a*t[0]", ["a"]),
    ("(lambda: a)()", ["a"]),
    ("a*x", ["a"]),                              # unknown name
    ("a*sin(t, t)", ["a"]),
    ("a if t else a", ["a"]),
    ("a*t", ["a", "b"]),                         # declared but unused parameter
    ("a*t", ["t"]), ("a*t", ["sin"]), ("a*t", ["__class__"]),
    ("a*True", ["a"]), ("a*'s'", ["a"]), ("", ["a"]), ("a*t" + "+t" * 200, ["a"]),
])
def test_grammar_rejects(eq, params):
    with pytest.raises(FitError):
        compile_equation(eq, params)


def test_grammar_accepts_and_evaluates_floats():
    f = compile_equation("a*exp(-b*t)*cos(2*pi*c*t) + sqrt(t)^3 - log(t)/a", ["a", "b", "c"])
    v = f({"t": 2.0, "a": 1.5, "b": 0.1, "c": 0.25})
    want = 1.5 * math.exp(-0.2) * math.cos(math.pi) + 2.0 ** 1.5 - math.log(2.0) / 1.5
    assert type(v) is float and abs(v - want) < 1e-12


def test_damped_oscillation_recovers_known_parameters():
    true = {"A": 0.12, "g": 0.3, "w": 4.4, "p": 0.2}
    rng = random.Random(0)
    t = [i * 0.03 for i in range(200)]
    y = [true["A"] * math.exp(-true["g"] * s) * math.cos(true["w"] * s + true["p"]) + rng.gauss(0, 0.002) for s in t]
    out = fit_equation(t, y, "A*exp(-g*t)*cos(w*t + p)", ["A", "g", "w", "p"], [0.1, 0.2, 4.2, 0.0])
    assert out["converged"]
    for name, value in true.items():
        est = out["parameters"][name]
        assert est["sigma_1"] and 0 < est["sigma_1"] < 0.05
        assert abs(est["value"] - value) < 4 * est["sigma_1"], (name, est)
    assert abs(out["rmse"] - 0.002) < 0.0005
    assert out["best_by_aic"].startswith("proposed") and out["delta_aic_vs_best_builtin"] < -100
    assert [c["k"] for c in out["comparison"]] == [4, 2, 3]


def test_undefined_regions_do_not_crash():
    with pytest.raises(FitError, match="undefined_at_initial_guess"):
        fit_equation([0.0, 1.0, 2.0, 3.0], [1.0, 2.0, 3.0, 4.0], "a*log(t)", ["a"], [1.0])
    with pytest.raises(FitError, match="no_effect"):
        fit_equation([0.0, 1.0, 2.0, 3.0], [1.0, 2.0, 3.0, 4.0], "a*sin(w*t)", ["a", "w"], [0.0, 1.0])


def test_tool_schema_and_handler(monkeypatch):
    from Build.api.agent import equation_handlers as h
    args = {"trajectory_id": "e1", "equation": "a*t^2 + b*t", "parameters": ["a", "b"], "initial_guess": [1, 0]}
    assert core.validate_call("fit_equation", args)[1] == []
    assert core.validate_call("fit_equation", {**args, "parameters": ["os.path"]})[1]
    t = [i * 0.05 for i in range(30)]
    traj = {"axes": "x right, y up", "unit": "px", "t_s": t, "x": t, "y": [-4.9 * s * s + 2 * s for s in t]}
    monkeypatch.setattr(h, "_store", lambda: None)
    monkeypatch.setattr(h.experiment, "get", lambda store, owner, eid: {"experiment": {
        "id": eid, "status": "done", "error": None, "result": {"track": {"frames": []}}, "request": {}}})
    monkeypatch.setattr(h.live_experiment, "analyse", lambda track, size: {
        "status": "ok", "label": "MEASURED, scale unverified", "units": "px", "segment": {}, "trajectory": traj})
    out = h.fit_equation("u1", args)
    assert out["status"] == "ok" and out["label"] == "MEASURED, scale unverified"
    assert abs(out["fit"]["parameters"]["a"]["value"] + 4.9) < 1e-6
    assert h.fit_equation("u1", {**args, "equation": "a*t.real + b"})["error"]["code"] == "BAD_EQUATION"
