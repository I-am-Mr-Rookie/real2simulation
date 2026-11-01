"""N15 agent tool fit_equation: fit an agent-proposed equation to a stored trajectory (no new SAM call, no spend)."""
from Build.api import experiment
from Build.api.agent.handlers import _safe, _store
from Build.fitter.core import FitError
from Build.fitter.proposed import fit_equation as _fit
from Build.pipeline import live_experiment


@_safe
def fit_equation(owner, args):
    e = experiment.get(_store(), owner, args["trajectory_id"])["experiment"]
    if e["status"] != "done" or not (e["result"] or {}).get("track"):
        return {"status": e["status"], "trajectory_id": e["id"], "error": e["error"],
                "detail": "tracking has not finished, so there is nothing to fit yet"}
    a = live_experiment.analyse(e["result"]["track"], (e["request"] or {}).get("known_size"))
    if "trajectory" not in a:
        return {"status": a["status"], "trajectory_id": e["id"], "detail": a.get("reason", "")}
    tr, axis = a["trajectory"], args.get("axis", "y")
    try:
        fit = _fit(tr["t_s"], tr[axis], args["equation"], args["parameters"], args["initial_guess"])
    except FitError as exc:
        return {"status": "error", "error": {"code": "BAD_EQUATION", "detail": str(exc)}}
    return {"status": "ok", "trajectory_id": e["id"], "label": a["label"], "units": a["units"], "axis": axis,
            "axes": tr["axes"], "segment": a["segment"], "fit": fit,
            "note": "the equation is agent-proposed; parameters are fitted to the tracked positions, not a known law"}


HANDLERS = {"fit_equation": fit_equation}
