"""S14i: zero-cost analysis routes — interview questions, spec validation, fit, HTML report (S15m §2).

Every number comes from existing modules (interview/validate_setup, fitter.api.handle, reports.number_entry);
this file adds routing, auth and error mapping only. No model, GPU or paid call; no storage.
"""
import re
import types
from pathlib import Path
from typing import Any, Callable, Mapping

from fastapi import APIRouter, Body, Depends

from Build.agent import interview
from Build.api.workspace.auth import error, require_owner
from Build.fitter.api import handle as fit_handle
from Build.fitter.core import FitError, fit_least_squares, gravity_quantity, jacobian_covariance
from Build.reports import SCHEMA, ReportError, digest, number_entry, render_html
from Build.reports.typeset import TEMPLATE_TEXT
from contracts.agent.validate import AgentContractError
from contracts.experiment.validate_experiment import validate

# (owner, scene_id) -> (base_spec, scene, scene_root) for a scene this owner may read, else None.
SceneResolver = Callable[[str, str], "tuple[Mapping[str, Any], Mapping[str, Any], Path] | None"]
_SCENE_ID = re.compile(r"[A-Za-z0-9._-]{1,128}")
# Report placeholders -> fitter paths (value, uncertainty). reports tables/charts require gravity, so degree-1 fits 422.
_REFS = {"g": ("gravity.value", "gravity.uncertainty"), "rmse": ("fit.rmse", None), "n": ("fit.n", None)}
# Owner Q16=A (Gate A MET_AMENDED_Q16): recorded scenes with no authoritative bundle get numeric-contract validation only.
Q16_LABEL = "scale unverified, not setup-validated"
# Owner Q20=A: Run on a Q16 scene is only a labelled what-if; this exact label travels with run/fit/report numbers.
WHAT_IF_LABEL = "SIMULATED what-if of your described setup; scale unverified; not measured from the clip"
_NO_BUNDLE = "$.scene: invalid authoritative bundle:"
# S15v: one free-text question for an object of known size; its answer is user-declared scale, never verified.
KNOWN_SIZE = {"id": "known_size", "kind": "free_text", "chips": [], "prompt": [{"type": "text", "text":
              "Name one object of known size in the fall plane and its length with units, e.g. book cover edge in cm."}]}
_LENGTH = re.compile(r"(\d+(?:\.\d+)?)\s*(mm|cm|m)\b", re.I)
SCALE_LABEL_USER = "user-declared, not verified"
# S15az (Gate D D1/D6): owner clips get a fit run now on the stored track points; numbers come only from Build/fitter/core.py.
LIVE_FIT_LABEL = "SIMULATED fit (fitter, run now) to RECORDED MEASURED SAM 3.1 track points"
TRACK_LABEL = "Track: RECORDED (precomputed SAM 3.1, not run live)"
OWNER_SCALE_LABEL = "owner-declared scale (recorded)"
# The exact answers_to_spec code with Gate A's spec_only stand-in (numeric validate()) as validate_setup; no global patch.
_numeric_answers_to_spec = types.FunctionType(
    interview.answers_to_spec.__code__,
    {**interview.answers_to_spec.__globals__, "validate_setup": lambda spec, _scene, _root: validate(spec)},
    "numeric_answers_to_spec")


def _no_scenes(owner: str, scene_id: str):
    return None  # shortcut: no scene store until S13i injects one; every scene is NOT_FOUND


def user_scale(answer: Any) -> dict[str, Any] | None:
    """known_size answer {text: 'book cover edge, 20.28 cm'} -> labelled user-declared scale, or an abstain (never an error)."""
    if answer is None:
        return None
    text = answer.get("text") if isinstance(answer, dict) else None
    m = _LENGTH.search(text) if isinstance(text, str) else None
    if not m or float(m[1]) <= 0:
        return {"status": "abstain", "label": "UNCERTAIN: no usable known size; metric scale unknown"}
    length_m = float(m[1]) / {"mm": 1000, "cm": 100, "m": 1}[m[2].lower()]
    return {"status": "declared", "object": text.strip()[:200], "length_m": length_m, "label": SCALE_LABEL_USER}


def _scene(scenes: SceneResolver, owner: str, scene_id: str):
    found = scenes(owner, scene_id) if _SCENE_ID.fullmatch(scene_id) else None
    if found is None:  # other owners' scenes are indistinguishable from missing ones
        raise error(404, "NOT_FOUND", "scene not found")
    return found


def owner_live_fit(m: Any, scale: Any) -> dict[str, Any]:
    """Quadratic fit of the RECORDED prefix points (held-out points excluded, used only for held-out residuals).

    metres per px = declared length / RECORDED reference px; if the user gave no usable length, the owner's recorded
    declaration is used and labelled so. Missing points or reference -> an error status, never a number.
    """
    m = m if isinstance(m, dict) else {}
    pts = ((m.get("series") or {}).get("points")) or []
    train = [(p["t_s"], p["y_px"]) for p in pts if not p.get("held_out")]
    held = [(p["t_s"], p["y_px"]) for p in pts if p.get("held_out")]
    ref = m.get("scale") or {}
    ref_px = ref.get("reference_px")
    if len(train) < 4:  # quadratic + at least one residual degree of freedom
        return {"status": "error", "error": "no_recorded_track_points",
                "message": "No stored track points for this clip, so no fit ran; g is not reported."}
    if not ref_px:
        return {"status": "error", "error": "no_recorded_reference_px",
                "message": "No recorded reference pixel length for this clip, so metres per pixel is unknown; g is not reported."}
    declared = isinstance(scale, dict) and scale.get("status") == "declared"
    length_m, who = (scale["length_m"], "user-declared scale") if declared else (ref.get("value_m"), OWNER_SCALE_LABEL)
    if not length_m:
        return {"status": "error", "error": "no_scale", "message": "No declared length, so metres per pixel is unknown."}
    mpp = length_m / ref_px
    try:
        fit = fit_least_squares([t for t, _ in train], [y * mpp for _, y in train], 2)
        g = gravity_quantity(fit, jacobian_covariance(fit, parameter_index=2), provenance=LIVE_FIT_LABEL)
    except FitError as exc:
        return {"status": "error", "error": str(exc), "message": "The fitter rejected the stored points; g is not reported."}
    held_res = [y - p / mpp for (_, y), p in zip(held, fit.predict([t for t, _ in held]))] if held else []
    return {"status": "ok", "label": LIVE_FIT_LABEL, "track_label": TRACK_LABEL, "stage": {"track": "recorded", "fit": "done"},
            "fitter": "Build/fitter/core.py fit_least_squares(degree 2) + jacobian_covariance (OLS, RSS/dof)",
            "g": g.value, "u": g.uncertainty, "unit": "m/s^2", "coefficients": list(fit.coefficients),
            "residuals_px": [r / mpp for r in fit.residuals], "rmse_px": fit.rmse / mpp, "rmse_m": fit.rmse,
            "dof": fit.dof, "n_fit": fit.n, "held_out_residuals_px": held_res, "n_held_out": len(held),
            "scale": {"length_m": length_m, "reference_px": ref_px, "m_per_px": mpp, "source": ref.get("reference_px_source"),
                      "label": f"{who} {length_m} m over a RECORDED {ref_px:.1f} px reference; scale unverified"},
            "caveat": f"Held-out points ({len(held)}) were excluded from this fit and only score it. "
                      f"Few fitted points (dof = {fit.dof}); the uncertainty is the fit's residual scatter only (no scale or "
                      "clock uncertainty), so it is not comparable to the recorded reference u; not a validated measurement."}


def _s10_artifact(spec: Mapping[str, Any], scene: Mapping[str, Any]) -> dict[str, Any]:
    """Same shape as Build/simulator/export_validated_setup.export (validate_setup already ran on spec+scene)."""
    return {"artifact_version": "s10-validated-setup-v1", "validation": "validate_setup",
            "producer": "contracts/experiment/validate_experiment.py", "spec": spec, "scene": scene}


def _what_if_artifact(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Q16 recorded scene: numeric-contract spec only. Explicitly non-synthetic and scale-unverified; scene ids copied from spec."""
    ref = spec.get("scene") or {}
    return {"artifact_version": "s15r-what-if-setup-v1", "validation": "numeric_contract_only", "what_if": True,
            "label": WHAT_IF_LABEL, "producer": "contracts/experiment/validate_experiment.py#validate", "spec": spec,
            "scene": {"id": ref.get("scene_id"), "schema_version": ref.get("schema_version"), "synthetic": False,
                      "scale_verified": False}}


def _report(template: str, fit: Mapping[str, Any]) -> dict[str, Any]:
    """Number-free prose + numbers copied from the fitter result (reports contract)."""
    numbers = {k: number_entry(fit, *ref) for k, ref in _REFS.items()}
    labels = sorted({n["label"] for n in numbers.values()})
    text = ["Fitted gravity is {{g}}; residual RMS is {{rmse}} over {{n}} samples.",
        f"All numbers are labelled {' and '.join(labels)} fitter output; this is not a physical measurement."]
    return {"schema": SCHEMA, "template": template, "fitter_digest": digest(fit),
            "title": f"{TEMPLATE_TEXT[template]['name']} report",
            "sections": [{"id": "results", "title": "Results", "text": text}], "numbers": numbers}


def create_router(scenes: SceneResolver = _no_scenes) -> APIRouter:
    router = APIRouter(prefix="/internal/workspace", dependencies=[Depends(require_owner)])

    @router.get("/scenes/{scene_id}/questions")
    def questions(scene_id: str, owner: str = Depends(require_owner)):
        base_spec, scene, _ = _scene(scenes, owner, scene_id)
        if scene is None and "owner_clip" in base_spec:  # S15y: no scene, so only the scene-free known-size question
            return {"schema_version": "agent-response/1.0.0", "scene_id": scene_id, "questions": [KNOWN_SIZE]}
        try:
            out = interview.questions(scene_id, base_spec.get("template"))
        except AgentContractError as exc:
            raise error(422, "INVALID_INPUT", "no interview for this scene", errors=list(exc.issues))
        if len(out.get("questions", [])) < 3:  # web parseQuestions allows at most 3
            out = {**out, "questions": [*out["questions"], KNOWN_SIZE]}
        return out

    @router.post("/scenes/{scene_id}/spec")
    def spec(scene_id: str, body: Any = Body(...), owner: str = Depends(require_owner)):
        base_spec, scene, root = _scene(scenes, owner, scene_id)
        answers = body.get("answers") if isinstance(body, dict) else None
        if not isinstance(answers, dict):
            raise error(422, "INVALID_INPUT", "body must be {answers: {...}}", ok=False, errors=["answers: expected object"])
        answers = dict(answers)
        scale = user_scale(answers.pop(KNOWN_SIZE["id"], None))
        if scene is None and "owner_clip" in base_spec:  # S15y: stored result (or abstain) + declared scale; no spec, no run
            scale = scale or user_scale({})
            return {"ok": True, "owner_clip": True, "measurement": base_spec["owner_clip"],
                    "user_scale": scale, "live_fit": owner_live_fit(base_spec["owner_clip"], scale)}
        extra = {"user_scale": scale} if scale else {}
        try:
            validated = interview.answers_to_spec(base_spec, scene, root, answers)
        except AgentContractError as exc:  # invalid answers never fall back to default numbers
            issues = list(exc.issues)
            if not (issues and all(str(i).startswith(_NO_BUNDLE) for i in issues)):
                raise error(422, "INVALID_INPUT", "spec did not validate", ok=False, errors=issues)
            try:  # only the bundle is missing (answers mapped, numeric validate() already ran first in validate_setup)
                validated = _numeric_answers_to_spec(base_spec, scene, root, answers)
            except AgentContractError as exc2:  # answers_to_spec wraps validate()'s ValueError
                raise error(422, "INVALID_INPUT", "spec did not validate", ok=False, errors=list(exc2.issues))
            return {"ok": True, "spec": validated, "validated_setup": _what_if_artifact(validated), "label": Q16_LABEL,
                    "setup_validated": False, "what_if_label": WHAT_IF_LABEL, **extra}
        return {"ok": True, "spec": validated, "validated_setup": _s10_artifact(validated, scene), **extra}

    @router.post("/fit")
    def fit(body: Any = Body(...)):
        out = fit_handle(body)
        if out.get("status") != "ok":
            raise error(422, "INVALID_INPUT", "fit failed", error=out.get("error"))
        return out

    @router.post("/report")
    def report(body: Any = Body(...)):
        spec_doc = body.get("spec") if isinstance(body, dict) else None
        fit_doc = body.get("fit") if isinstance(body, dict) else None
        template = spec_doc.get("template") if isinstance(spec_doc, dict) else None
        if template not in TEMPLATE_TEXT or not isinstance(fit_doc, dict) or fit_doc.get("status") != "ok":
            raise error(422, "INVALID_INPUT", "body must be {spec: {template}, fit: ok fitter result}")
        what_if = body.get("label")  # only the exact Q20 label may be passed through; anything else is rejected
        if what_if is not None and what_if != WHAT_IF_LABEL:
            raise error(422, "INVALID_INPUT", "label must be absent or the exact what-if label")
        try:
            doc = _report(template, fit_doc)
            if what_if:
                doc["sections"][0]["text"].insert(0, WHAT_IF_LABEL + ".")
            html = render_html(doc, fit_doc)  # validates numbers against the fit before rendering
        except (ReportError, KeyError, TypeError, ValueError) as exc:
            raise error(422, "INVALID_INPUT", "report did not validate", errors=[str(exc)])
        labels = sorted({n["label"] for n in doc["numbers"].values()})
        # PDF needs pdflatex (absent in the API image): same explicit fallback status as reports/compile.py.
        out = {"status": "html-print-fallback", "labels": labels, "fitter_digest": doc["fitter_digest"], "html": html}
        return {**out, "what_if_label": WHAT_IF_LABEL} if what_if else out

    return router
