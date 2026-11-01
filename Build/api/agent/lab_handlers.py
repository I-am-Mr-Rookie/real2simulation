"""N12: agent lab tools (lab_add_object, lab_run, write_report) on a per-owner lab-scene-v1 JSON.

Scene validation and physics run server side in node (Build/web/src/lab-editor/agent-run.mjs: the editor's own
validateScene + Build/simulator/rk4.mjs). Build/fitter measures every trace. ask_user is handled by Build/agent/core.
Every number returned comes from the RK4 run or the fitter; everything here is SIMULATED.
"""
from __future__ import annotations

import hashlib
import json
import base64
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Depends, Query

from Build.api.workspace.auth import error, require_owner
from Build.fitter.api import handle as fit_handle
from Build.fitter.core import fit_least_squares, jacobian_covariance

ROOT = Path(__file__).resolve().parents[3]
BRIDGE = ROOT / "Build" / "web" / "src" / "lab-editor" / "agent-run.mjs"
DT = 1 / 120
POSITION_SIGMA_M = 0.001  # declared readout sigma for SIMULATED traces (assumption, stated in every result)
CROSSING_SIGMA_S = DT / math.sqrt(12)  # one-step quantization of an interpolated crossing time (assumption)
_PROJECT = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
# Agent params (SI names) -> scene fields. height_m is the centre height above the floor (anchor for pendulum/spring).
PARAMS = {
    "ball": {"radius_m", "diameter_m", "mass_kg", "height_m", "x_m", "z_m", "velocity_x_m_s", "velocity_y_m_s", "velocity_z_m_s", "restitution", "friction"},
    "block": {"size_m", "mass_kg", "height_m", "x_m", "z_m", "velocity_x_m_s", "velocity_y_m_s", "velocity_z_m_s", "friction"},
    "ramp": {"length_m", "angle_deg", "height_m", "x_m", "z_m", "friction"},
    "pendulum": {"length_m", "angle_deg", "mass_kg", "radius_m", "height_m", "x_m", "z_m"},
    "spring": {"rest_length_m", "stiffness_n_per_m", "damping_n_s_per_m", "stretch_m", "mass_kg", "height_m", "x_m", "z_m"},
    # N33 lab kit and probes
    "flywheel": {"radius_m", "mass_kg", "moment_of_inertia_kg_m2", "hanging_mass_kg", "string_length_m", "height_m", "x_m", "z_m"},
    "atwood": {"mass1_kg", "mass2_kg", "pulley_radius_m", "string_length_m", "height_m", "x_m", "z_m"},
    "cart": {"track_length_m", "angle_deg", "mass_kg", "friction", "velocity_x_m_s", "height_m", "x_m", "z_m"},
    "launcher": {"angle_deg", "speed_m_s", "diameter_m", "mass_kg", "height_m", "x_m", "z_m"},
    "cradle": {"count", "length_m", "angle_deg", "diameter_m", "mass_kg", "restitution", "height_m", "x_m", "z_m"},
    "mass": {"mass_kg", "height_m", "x_m", "z_m"},
    "ruler": {"length_m", "height_m", "x_m", "z_m"},
    "protractor": {"height_m", "x_m", "z_m"},
    "photogate": {"height_m", "x_m", "z_m"},
}
# Agent param -> scene params field, per kind (mass_kg of kind mass becomes params.grams).
SCENE_PARAMS = {
    "pendulum": (("length_m", "length"), ("angle_deg", "angle_deg")),
    "spring": (("rest_length_m", "rest_length"), ("stiffness_n_per_m", "stiffness"), ("damping_n_s_per_m", "damping"), ("stretch_m", "stretch")),
    "flywheel": (("radius_m", "radius"), ("moment_of_inertia_kg_m2", "inertia"), ("hanging_mass_kg", "hang_mass"), ("string_length_m", "hang_length")),
    "atwood": (("mass1_kg", "m1"), ("mass2_kg", "m2"), ("pulley_radius_m", "radius"), ("string_length_m", "hang_length")),
    "cart": (("track_length_m", "length"), ("angle_deg", "angle_deg")),
    "launcher": (("angle_deg", "angle_deg"), ("speed_m_s", "speed")),
    "cradle": (("count", "count"), ("length_m", "length"), ("angle_deg", "angle_deg")),
    "ruler": (("length_m", "length"),),
}
# Default centre height above the floor (anchor / axle / launch point) when height_m is not given.
HEIGHTS = {"flywheel": lambda p: p.get("string_length_m", 0.4) + 0.4, "atwood": lambda p: p.get("string_length_m", 0.5) + 0.6,
           "cart": lambda p: 0.4, "launcher": lambda p: 0.1, "cradle": lambda p: p.get("length_m", 0.5) + 0.3,
           "ruler": lambda p: 0.5, "photogate": lambda p: 0.5}
# N28 lab_update_object extras: relative moves (left = -x, up = +y, toward the viewer = +z) and a turn about the vertical axis.
UPDATE_EXTRA = {"dx_m", "dy_m", "dz_m", "yaw_deg"}


class LabError(ValueError):
    pass


def _dir(owner: str, project: str = "lab") -> Path:
    # shortcut: the agent tools have no project argument, so they use project "lab"; pass the project id once N03 projects reach the agent.
    if not _PROJECT.fullmatch(project):
        raise LabError("project id must match [A-Za-z0-9_-]{1,64}")
    base = Path(os.environ.get("R2S_DATA_DIR") or Path.home() / ".r2s-data")
    d = base / "lab" / hashlib.sha256(owner.encode()).hexdigest()[:24] / project
    d.mkdir(parents=True, exist_ok=True)
    return d


def _node(payload: dict[str, Any]) -> dict[str, Any]:
    proc = subprocess.run(["node", str(BRIDGE)], input=json.dumps(payload), capture_output=True, text=True,
                          timeout=60, encoding="utf-8")
    try:
        out = json.loads(proc.stdout)
    except ValueError:
        raise LabError("lab bridge failed") from None
    if out.get("status") != "ok":
        raise LabError(str(out.get("error", "lab bridge failed"))[:300])
    return out


def default_scene() -> dict[str, Any]:
    return {"version": "lab-scene-v1", "label": "SIMULATED", "units": "m", "gravity": [0, -9.81, 0],
            "room": {"kind": "plane", "floor_y": 0}, "objects": []}


def load_scene(owner: str, project: str = "lab") -> dict[str, Any]:
    f = _dir(owner, project) / "scene.json"
    return json.loads(f.read_text("utf-8")) if f.exists() else default_scene()


def save_scene(owner: str, scene: Any, project: str = "lab") -> dict[str, Any]:
    clean = _node({"op": "validate", "scene": scene})["scene"]
    (_dir(owner, project) / "scene.json").write_text(json.dumps(clean, indent=2), "utf-8")
    return clean


def _read(owner: str, name: str, project: str = "lab") -> Any:
    f = _dir(owner, project) / name
    return json.loads(f.read_text("utf-8")) if f.exists() else None


def make_object(kind: str, params: dict[str, float], scene: dict[str, Any]) -> dict[str, Any]:
    if kind not in PARAMS:
        raise LabError(f"{kind} is not in the lab editor yet; use one of {', '.join(PARAMS)}")
    unknown = sorted(set(params) - PARAMS[kind])
    if unknown:
        raise LabError(f"unknown params {unknown} for {kind}; allowed: {sorted(PARAMS[kind])}")
    p = params
    used = {o["id"] for o in scene["objects"]}
    n = 1
    while f"{kind}-{n}" in used:
        n += 1
    floor = scene.get("room", {}).get("floor_y", 0) or 0
    anchor = p.get("length_m", 0.8) + 0.5 if kind == "pendulum" else p.get("rest_length_m", 0.4) + p.get("stretch_m", 0.15) + 0.6
    height = p.get("height_m", anchor if kind in ("pendulum", "spring") else HEIGHTS[kind](p) if kind in HEIGHTS else 1.0)
    o: dict[str, Any] = {"id": f"{kind}-{n}", "kind": kind, "position": [p.get("x_m", 0.0), floor + height, p.get("z_m", 0.0)]}
    for k, field in (("mass_kg", "mass"), ("friction", "friction"), ("restitution", "restitution")):
        if k in p and kind != "mass":
            o[field] = p[k]
    if "radius_m" in p:
        o["size"] = [2 * p["radius_m"]] * 3
    if "diameter_m" in p:
        o["size"] = [p["diameter_m"]] * 3
    if "size_m" in p:
        o["size"] = [p["size_m"]] * 3
    if any(k.startswith("velocity_") for k in p):
        o["velocity"] = [p.get(f"velocity_{a}_m_s", 0.0) for a in "xyz"]
    if kind in SCENE_PARAMS:
        o["params"] = {k: p[a] for a, k in SCENE_PARAMS[kind] if a in p}
    if kind == "mass" and "mass_kg" in p:
        o["params"] = {"grams": p["mass_kg"] * 1000}
    if kind in ("flywheel", "atwood", "cart", "launcher", "cradle", "ruler", "protractor", "photogate"):
        o["fixed"] = True
    if kind == "cradle":
        o.setdefault("restitution", 1.0)
        o["friction"] = 0.0
    if kind == "cart":
        o.setdefault("friction", 0.01)
    if kind == "ramp":
        a = math.radians(p.get("angle_deg", 15.0)) / 2
        o.update(fixed=True, sensor=False, rotation=[0, 0, math.sin(a), math.cos(a)], size=[p.get("length_m", 1.2), 0.05, 0.4])
    return o


def _find(scene: dict[str, Any], ref: Any) -> dict[str, Any]:
    """Object by exact id, else by kind when exactly one object of that kind exists (the model rarely keeps ids)."""
    objs = scene["objects"]
    hit = [o for o in objs if o["id"] == ref] or [o for o in objs if o["kind"] == ref]
    if len(hit) != 1:
        listed = ", ".join(f"{o['id']} ({o['kind']})" for o in objs) or "none"
        raise LabError(f"no single object matches {str(ref)[:40]!r}; objects in the scene: {listed}")
    return hit[0]


def _qmul(a: list[float], b: list[float]) -> list[float]:
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return [aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz]


def update_object(o: dict[str, Any], p: dict[str, float], scene: dict[str, Any]) -> dict[str, Any]:
    """Apply agent params to a copy of a scene object; absolute values override, d*_m values move relative."""
    allowed = PARAMS[o["kind"]] | UPDATE_EXTRA
    unknown = sorted(set(p) - allowed)
    if unknown or not p:
        raise LabError(f"unknown or no params {unknown} for {o['kind']}; allowed: {sorted(allowed)}")
    o = json.loads(json.dumps(o))
    floor = scene.get("room", {}).get("floor_y", 0) or 0
    pos = o.get("position") or [0.0, 1.0, 0.0]
    pos = [p.get("x_m", pos[0]), floor + p["height_m"] if "height_m" in p else pos[1], p.get("z_m", pos[2])]
    o["position"] = [pos[0] + p.get("dx_m", 0.0), pos[1] + p.get("dy_m", 0.0), pos[2] + p.get("dz_m", 0.0)]
    for k, field in (("mass_kg", "mass"), ("friction", "friction"), ("restitution", "restitution")):
        if k in p and o["kind"] != "mass":
            o[field] = p[k]
    for k, scale in (("radius_m", 2), ("diameter_m", 1), ("size_m", 1)):
        if k in p:
            o["size"] = [scale * p[k]] * 3
    if any(k.startswith("velocity_") for k in p):
        v = o.get("velocity") or [0.0, 0.0, 0.0]
        o["velocity"] = [p.get(f"velocity_{a}_m_s", v[i]) for i, a in enumerate("xyz")]
    o["params"] = {**(o.get("params") or {}), **{k: p[a] for a, k in SCENE_PARAMS.get(o["kind"], ()) if a in p}}
    if o["kind"] == "mass" and "mass_kg" in p:
        o["params"]["grams"] = p["mass_kg"] * 1000
    if o["kind"] == "ramp":
        size = o.get("size") or [1.2, 0.05, 0.4]
        o["size"] = [p.get("length_m", size[0]), size[1], size[2]]
        if "angle_deg" in p:
            a = math.radians(p["angle_deg"]) / 2
            o["rotation"] = [0, 0, math.sin(a), math.cos(a)]  # tilt replaces any earlier yaw
    if "yaw_deg" in p:
        a = math.radians(p["yaw_deg"]) / 2
        o["rotation"] = _qmul([0, math.sin(a), 0, math.cos(a)], o.get("rotation") or [0, 0, 0, 1])
    return o


def _q(value: float, sigma: float | None, unit: str, method: str) -> dict[str, Any]:
    # Value kept to the uncertainty's 2nd significant digit (plus guard digits) so replies quote readable numbers.
    sig = lambda x, n: float(f"{x:.{n}g}")
    return {"value": sig(value, 7), "uncertainty": sig(sigma, 2) if sigma else sigma, "unit": unit, "label": "SIMULATED",
            "method": method}


def _crossings(samples: list[dict[str, Any]], axis: int) -> list[float]:
    ys = [s["p"][axis] for s in samples]
    mid = sum(ys) / len(ys)
    out = []
    for a, b in zip(samples, samples[1:]):
        ya, yb = a["p"][axis] - mid, b["p"][axis] - mid
        if ya == 0 or ya * yb < 0:
            out.append(a["t"] + (b["t"] - a["t"]) * (ya / (ya - yb) if ya != yb else 0))
    return out


def measure(trace: dict[str, Any], scene: dict[str, Any]) -> dict[str, Any]:
    """Fit one SIMULATED trace with Build/fitter; returns quantities with one-sigma uncertainty."""
    samples, kind = trace["samples"], trace["kind"]
    base = {"object_id": trace["object_id"], "kind": kind, "samples": len(samples), "label": "SIMULATED",
            "duration_s": samples[-1]["t"] if samples else 0}
    o = next((x for x in scene["objects"] if x["id"] == trace["object_id"]), None)
    if kind in KIT and o:
        return {**base, **_measure_kit(trace, o, scene)}
    if kind in ("ball", "block", "mass", "launcher"):
        if len(samples) < 4:
            return {**base, "status": "error", "error": "too few samples before floor contact"}
        q = lambda v, u, s: {"value": v, "unit": u, "uncertainty": s, "source": {"label": "simulated", "evidence": "N12 lab_run"}}
        fit = fit_handle({"times": [q(s["t"], "s", 0) for s in samples],
                          "positions": [q(s["p"][1], "m", POSITION_SIGMA_M) for s in samples], "degree": 2})
        if fit.get("status") != "ok" or not fit.get("gravity"):
            return {**base, "status": "error", "error": "fit failed", "fit": fit.get("error")}
        g = fit["gravity"]
        out = {**base, "status": "ok", "ended": trace.get("ended"),
                "drop_height_m": samples[0]["p"][1] - samples[-1]["p"][1],
                "g": _q(abs(g["value"]), g["uncertainty"], "m/s^2", "Build/fitter degree-2 fit of height vs time"),
                "rmse_m": fit["fit"].get("rmse"), "declared_position_sigma_m": POSITION_SIGMA_M}
        if kind == "launcher" and o:
            out.update(_launch(samples, o, scene))
        return out
    axis = 0 if kind == "pendulum" else 1
    t = _crossings(samples, axis)
    if len(t) < 3:
        return {**base, "status": "error", "error": "fewer than 3 crossings; run longer"}
    fit = fit_least_squares(list(range(len(t))), t, 1)
    cov = jacobian_covariance(fit, position_sigmas=(CROSSING_SIGMA_S,) * len(t), parameter_index=1)
    half = fit.coefficients[1]
    out = {**base, "status": "ok", "crossings": len(t),
           "period": _q(2 * half, 2 * cov.standard_error if cov.valid else None, "s",
                        "Build/fitter linear fit of mid-line crossing times vs crossing index"),
           "declared_crossing_sigma_s": CROSSING_SIGMA_S}
    g_abs = math.hypot(*scene["gravity"])
    if kind == "pendulum" and o:
        L, a = o["params"]["length"], math.radians(o["params"]["angle_deg"])
        out["small_angle_period_s"] = {"value": 2 * math.pi * math.sqrt(L / g_abs), "label": "THEORY", "unit": "s"}
        out["large_angle_period_s"] = {"value": 2 * math.pi * math.sqrt(L / g_abs) * (1 + a * a / 16 + 11 * a ** 4 / 3072),
                                       "label": "THEORY", "unit": "s"}
    if kind == "spring" and o:
        out["undamped_period_s"] = {"value": 2 * math.pi * math.sqrt(o["mass"] / o["params"]["stiffness"]), "label": "THEORY", "unit": "s"}
    return out


KIT = ("flywheel", "atwood", "cart", "cradle", "ruler", "protractor", "photogate")


def _accel(samples: list[dict[str, Any]], values: list[float]) -> dict[str, Any] | None:
    """Build/fitter degree-2 fit of one coordinate vs time; returns the fitted acceleration (value, sigma)."""
    if len(samples) < 4:
        return None
    q = lambda v, u, s: {"value": v, "unit": u, "uncertainty": s, "source": {"label": "simulated", "evidence": "N33 lab_run"}}
    fit = fit_handle({"times": [q(s["t"], "s", 0) for s in samples], "positions": [q(v, "m", POSITION_SIGMA_M) for v in values], "degree": 2})
    return fit.get("gravity") if fit.get("status") == "ok" else None


def _launch(samples: list[dict[str, Any]], o: dict[str, Any], scene: dict[str, Any]) -> dict[str, Any]:
    """Range back to the launch height, interpolated from the trace, plus the fitted horizontal speed."""
    y0, p0 = samples[0]["p"][1], samples[0]["p"]
    flat = lambda p: math.hypot(p[0] - p0[0], p[2] - p0[2])
    hit = next((i for i in range(1, len(samples)) if samples[i]["p"][1] < y0 <= samples[i - 1]["p"][1] and i > 2), None)
    g_abs, a, v = math.hypot(*scene["gravity"]), math.radians(o["params"]["angle_deg"]), o["params"]["speed"]
    fit = fit_least_squares([s["t"] for s in samples], [flat(s["p"]) for s in samples], 1)
    out = {"horizontal_speed": _q(fit.coefficients[1], None, "m/s", "Build/fitter linear fit of horizontal distance vs time"),
           "theory_range_m": {"value": v * v * math.sin(2 * a) / g_abs, "label": "THEORY", "unit": "m"}}
    if hit is not None:
        s0, s1 = samples[hit - 1], samples[hit]
        f = (s0["p"][1] - y0) / (s0["p"][1] - s1["p"][1])
        out["range_m"] = _q(flat(s0["p"]) + f * (flat(s1["p"]) - flat(s0["p"])), POSITION_SIGMA_M, "m",
                            "trace interpolated back to the launch height")
    return out


def _measure_kit(trace: dict[str, Any], o: dict[str, Any], scene: dict[str, Any]) -> dict[str, Any]:
    s, kind, P = trace["samples"], trace["kind"], o["params"]
    g_abs = math.hypot(*scene["gravity"])
    if kind in ("ruler", "protractor", "photogate"):
        if not s:
            return {"status": "error", "error": "the probe saw nothing; put it next to a moving object"}
        unit = trace.get("units", {}).get("value")
        vals = [x["value"] for x in s]
        if kind == "photogate":
            return {"status": "ok", "target": trace.get("target"), "gate_times_s": [round(v, 6) for v in vals[:20]],
                    "intervals_s": [round(b - a, 6) for a, b in zip(vals, vals[1:])][:20], "time_sigma_s": CROSSING_SIGMA_S}
        return {"status": "ok", "target": trace.get("target"), "unit": unit, "start": vals[0], "end": vals[-1],
                "min": min(vals), "max": max(vals), "reading_sigma": POSITION_SIGMA_M if kind == "ruler" else None}
    if kind == "cradle":
        # Exit speed of the last ball: Build/fitter linear fit of x over the 7 samples around its fastest step.
        if len(s) < 10:
            return {"status": "error", "error": "too few samples"}
        steps = [abs(b["p"][0] - a["p"][0]) for a, b in zip(s, s[1:])]
        i = max(3, min(len(s) - 4, steps.index(max(steps))))
        win = s[i - 3:i + 4]
        fit = fit_least_squares([x["t"] for x in win], [x["p"][0] for x in win], 1)
        a = math.radians(P["angle_deg"])
        v, vi = abs(fit.coefficients[1]), math.sqrt(2 * g_abs * P["length"] * (1 - math.cos(a)))
        return {"status": "ok", "exit_speed": _q(v, None, "m/s", "Build/fitter linear fit of the last ball x vs time at its fastest"),
                "theory_impact_speed_m_s": {"value": vi, "label": "THEORY", "unit": "m/s"}, "transfer_ratio": round(v / vi, 3),
                "note": "the engine's contact solver does not transfer momentum fully elastically along a touching row; ideal is 1"}
    if kind == "cart":
        d = [b - a for a, b in zip(s[0]["p"], s[-1]["p"])] if len(s) > 1 else [1, 0, 0]
        n = math.hypot(*d) or 1
        acc = _accel(s, [sum((x["p"][i] - s[0]["p"][i]) * d[i] / n for i in range(3)) for x in s])
        if not acc:
            return {"status": "error", "error": "fit failed"}
        a = math.radians(P["angle_deg"])
        return {"status": "ok", "ended": trace.get("ended"), "acceleration": _q(abs(acc["value"]), acc["uncertainty"], "m/s^2", "Build/fitter degree-2 fit of distance along the track vs time"),
                "theory_acceleration_m_s2": {"value": g_abs * (math.sin(a) - o["friction"] * math.cos(a)), "label": "THEORY", "unit": "m/s^2"}}
    acc = _accel(s, [x["p"][1] for x in s])
    if not acc:
        return {"status": "error", "error": "too few samples or fit failed"}
    a, sa = abs(acc["value"]), acc["uncertainty"]
    out = {"status": "ok", "ended": trace.get("ended"), "acceleration": _q(a, sa, "m/s^2", "Build/fitter degree-2 fit of height vs time")}
    if kind == "atwood":
        out["theory_acceleration_m_s2"] = {"value": g_abs * abs(P["m1"] - P["m2"]) / (P["m1"] + P["m2"]), "label": "THEORY", "unit": "m/s^2"}
    if kind == "flywheel" and a > 0:
        m, r = P["hang_mass"], P["radius"]
        set_i = P["inertia"] or 0.5 * o["mass"] * r * r
        out["angular_acceleration"] = _q(a / r, sa / r, "rad/s^2", "fitted acceleration / radius")
        out["moment_of_inertia"] = _q(m * r * r * (g_abs / a - 1), m * r * r * g_abs * sa / (a * a), "kg m^2", "I = m r^2 (g / a - 1) from the fitted a")
        out["scene_moment_of_inertia_kg_m2"] = {"value": set_i, "label": "SIMULATED", "unit": "kg m^2"}
        out["theory_acceleration_m_s2"] = {"value": m * g_abs * r * r / (m * r * r + set_i), "label": "THEORY", "unit": "m/s^2"}
    return out


def _err(exc: Exception) -> dict[str, Any]:
    return {"status": "error", "error": {"code": "LAB_INPUT", "detail": str(exc)[:300]}}


def lab_add_object(owner: str, args: dict[str, Any]) -> dict[str, Any]:
    try:
        scene = load_scene(owner)
        obj = make_object(args["kind"], args.get("params") or {}, scene)
        scene = save_scene(owner, {**scene, "objects": [*scene["objects"], obj]})
    except (LabError, subprocess.TimeoutExpired) as exc:
        return _err(exc)
    added = next(o for o in scene["objects"] if o["id"] == obj["id"])
    return {"status": "ok", "label": "SIMULATED", "object": added, "objects_in_scene": len(scene["objects"])}


def lab_update_object(owner: str, args: dict[str, Any]) -> dict[str, Any]:
    try:
        scene = load_scene(owner)
        old = _find(scene, args.get("id") or args.get("kind"))
        new = update_object(old, args.get("params") or {}, scene)
        scene = save_scene(owner, {**scene, "objects": [new if o is old else o for o in scene["objects"]]})
    except (LabError, subprocess.TimeoutExpired) as exc:
        return _err(exc)
    return {"status": "ok", "label": "SIMULATED", "object": next(o for o in scene["objects"] if o["id"] == old["id"])}


def lab_remove_object(owner: str, args: dict[str, Any]) -> dict[str, Any]:
    try:
        scene = load_scene(owner)
        gone = _find(scene, args.get("id") or args.get("kind"))
        scene = save_scene(owner, {**scene, "objects": [o for o in scene["objects"] if o is not gone]})
    except (LabError, subprocess.TimeoutExpired) as exc:
        return _err(exc)
    return {"status": "ok", "label": "SIMULATED", "removed": gone["id"],
            "objects": [{"id": o["id"], "kind": o["kind"]} for o in scene["objects"]]}


def lab_run(owner: str, args: dict[str, Any]) -> dict[str, Any]:
    try:
        scene = load_scene(owner)
        if not scene["objects"]:
            return {"status": "error", "error": {"code": "EMPTY_SCENE", "detail": "add an object first"}}
        run = _node({"op": "run", "scene": scene, "duration_s": 10})
    except (LabError, subprocess.TimeoutExpired) as exc:
        return _err(exc)
    results = [measure(t, run["scene"]) for t in run["traces"]]
    (_dir(owner) / "run.json").write_text(json.dumps({"scene": run["scene"], "engine": run["engine"], "traces": run["traces"],
                                                     "results": results}), "utf-8")
    return {"status": "ok", "label": "SIMULATED", "engine": run["engine"], "results": results}


def write_report(owner: str, args: dict[str, Any]) -> dict[str, Any]:
    from Build.reports.lab_report import illustrate, render
    run = _read(owner, "run.json")
    if not run:
        return {"status": "error", "error": {"code": "NO_RUN", "detail": "run the lab first"}}
    rep = render(run["scene"], run["engine"], run["results"])
    # Opt-in: a paid ($0.01) image call adds latency; skipped silently on any error or cap.
    image = illustrate(rep["title"]) if os.environ.get("R2S_LAB_REPORT_IMAGE") == "1" else None
    if image:
        rep = render(run["scene"], run["engine"], run["results"], image_b64=image)
    d = _dir(owner)
    if image:
        (d / "report.webp").write_bytes(base64.b64decode(image))
    (d / "report.md").write_text(rep["markdown"], "utf-8")
    (d / "report.html").write_text(rep["html"], "utf-8")
    return {"status": "ok", "label": "SIMULATED", "title": rep["title"], "report_url": "/workspace/agent/lab/report",
            "conclusion": rep["conclusion"], "illustration": bool(image)}


HANDLERS = {"lab_add_object": lab_add_object, "lab_update_object": lab_update_object,
            "lab_remove_object": lab_remove_object, "lab_run": lab_run, "write_report": write_report}


def create_router() -> APIRouter:
    """Editor side: load/save the project scene, read the last run traces and the report."""
    router = APIRouter(prefix="/workspace/agent/lab")

    def guard(fn):
        try:
            return fn()
        except LabError as exc:
            raise error(422, "LAB_INPUT", str(exc)) from None

    @router.get("/scene")
    def get_scene(project: str = Query("lab"), owner: str = Depends(require_owner)):
        return guard(lambda: {"scene": load_scene(owner, project)})

    @router.post("/scene")
    def put_scene(scene: dict[str, Any] = Body(...), project: str = Query("lab"), owner: str = Depends(require_owner)):
        if len(json.dumps(scene)) > 512 * 1024:
            raise error(413, "TOO_LARGE", "scene JSON must be under 512 KiB")
        return guard(lambda: {"scene": save_scene(owner, scene, project)})

    @router.get("/report")
    def get_report(project: str = Query("lab"), owner: str = Depends(require_owner)):
        def read():
            d = _dir(owner, project)
            if not (d / "report.md").exists():
                raise error(404, "NO_REPORT", "ask the agent to write a report first")
            return {"markdown": (d / "report.md").read_text("utf-8"), "html": (d / "report.html").read_text("utf-8")}
        return guard(read)

    @router.get("/run")
    def get_run(project: str = Query("lab"), owner: str = Depends(require_owner)):
        return guard(lambda: _read(owner, "run.json", project) or {"traces": [], "results": []})

    return router
