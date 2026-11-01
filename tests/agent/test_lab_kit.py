"""N33: every lab kit kind runs in the editor's Rapier world and gets a fitter-checked number against theory."""
import math

from Build.api.agent.lab_handlers import _node, default_scene, make_object, measure, update_object

G = 9.81


def _run(*specs):
    scene = default_scene()
    for kind, params in specs:
        scene["objects"].append(make_object(kind, params, scene))
    run = _node({"op": "run", "scene": scene, "duration_s": 4})
    return {t["object_id"]: measure(t, run["scene"]) for t in run["traces"]}


def test_kit_numbers_match_theory():
    r = _run(("atwood", {"mass1_kg": 0.2, "mass2_kg": 0.15}),
             ("flywheel", {"x_m": 2, "hanging_mass_kg": 0.05, "radius_m": 0.15, "mass_kg": 1}),
             ("cart", {"x_m": 4, "angle_deg": 10}),
             ("launcher", {"x_m": 7, "angle_deg": 45, "speed_m_s": 3}),
             ("cradle", {"x_m": 10}),
             ("mass", {"x_m": 13, "mass_kg": 0.2}),
             ("photogate", {"x_m": 13, "height_m": 0.5}))
    at = r["atwood-1"]
    assert at["status"] == "ok" and at["label"] == "SIMULATED"
    assert math.isclose(at["acceleration"]["value"], G * 0.05 / 0.35, rel_tol=0.01)
    fw = r["flywheel-1"]
    assert math.isclose(fw["moment_of_inertia"]["value"], 0.5 * 1 * 0.15 ** 2, rel_tol=0.02)
    assert math.isclose(fw["acceleration"]["value"], fw["theory_acceleration_m_s2"]["value"], rel_tol=0.01)
    ct = r["cart-1"]
    assert math.isclose(ct["acceleration"]["value"], ct["theory_acceleration_m_s2"]["value"], rel_tol=0.05)
    ln = r["launcher-1"]
    assert math.isclose(ln["range_m"]["value"], 9 / G, rel_tol=0.02) and math.isclose(ln["g"]["value"], G, rel_tol=0.01)
    cr = r["cradle-1"]
    # Rapier's solver is not an ideal elastic cradle (about 0.6 of the impact speed reaches the last ball); see REPORT.
    assert 0.3 < cr["transfer_ratio"] <= 1.02 and cr["exit_speed"]["value"] > 0
    ms = r["mass-1"]
    assert math.isclose(ms["g"]["value"], G, rel_tol=0.01)
    pg = r["photogate-1"]
    assert pg["target"] == "mass-1" and math.isclose(pg["gate_times_s"][0], math.sqrt(2 * 0.5 / G), abs_tol=0.01)


def test_probes_read_pendulum_and_drop():
    r = _run(("pendulum", {"angle_deg": 30, "height_m": 1.3}), ("protractor", {"height_m": 1.3}),
             ("ball", {"x_m": 3, "height_m": 1.0}), ("ruler", {"x_m": 3.1, "height_m": 0.5}))
    pr = r["protractor-1"]
    assert pr["target"] == "pendulum-1" and math.isclose(pr["max"], 30, abs_tol=1) and math.isclose(pr["min"], -30, abs_tol=1.5)
    assert r["ruler-1"]["target"] == "ball-1" and r["ruler-1"]["unit"] == "m"


def test_agent_params_map_to_scene():
    scene = default_scene()
    m = make_object("mass", {"mass_kg": 0.5}, scene)
    assert m["params"] == {"grams": 500}
    fw = make_object("flywheel", {"moment_of_inertia_kg_m2": 0.02, "hanging_mass_kg": 0.1}, scene)
    assert fw["params"] == {"inertia": 0.02, "hang_mass": 0.1} and fw["fixed"] is True
    up = update_object({**fw, "params": {"inertia": 0.02, "hang_mass": 0.1}}, {"radius_m": 0.2, "dx_m": 1}, scene)
    assert up["params"]["radius"] == 0.2 and up["position"][0] == 1
    try:
        make_object("atwood", {"bogus": 1}, scene)
        raise AssertionError("unknown param accepted")
    except ValueError:
        pass
