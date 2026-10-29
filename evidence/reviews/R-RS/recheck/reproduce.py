"""Read-only offline recheck. Adapted fixture/probes from ../reproduce.py; no artifact regeneration.

Assertions establish observed refusals OR reproduced defects, not Gate RS acceptance.
Run from worktree root: python -B evidence/reviews/R-RS/recheck/reproduce.py
"""
from dataclasses import replace
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from Build.real2sim import boundary as b, predict as p, score as s, overlay as o


def fixture(clip="SYNTHETIC-review", shift=0):
    record = {"clip_id": clip, "source_sha256": hashlib.sha256(clip.encode()).hexdigest(),
              "height_px": 1000, "last_training_frame": 9,
              "frames": [{"frame_index": i, "pts_s": i / 30,
                          "y_px": 100 + 20 * i + 3 * i * i + shift} for i in range(10)]}
    boundary, sealed = b.split(record, [(i, i / 30) for i in range(10, 15)])
    return boundary, sealed, p.projectile(boundary, sealed)


def observe(pred):
    return {i: (t, y) for i, t, y, _ in pred.trace}


def refused_before_read(boundary, sealed, pred):
    calls = []
    try:
        s.score(boundary, sealed, pred, pred.sha256, lambda: calls.append(1) or observe(pred))
    except ValueError as error:
        assert not calls, "refusal happened after suffix read"
        return str(error)
    raise AssertionError("expected refusal")


def read(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


out = {"purpose": "offline adversarial recheck; synthetic probes are NOT public clip evidence"}
boundary, sealed, pred = fixture()
truth = observe(pred)
offset = {i: (t, y + 0.03) for i, (t, y) in truth.items()}
good = s.score(boundary, sealed, pred, pred.sha256, lambda: offset)
assert math.isclose(good["normalized_rms"], 0.03, abs_tol=1e-12)
assert s.score(boundary, sealed, pred, pred.sha256, lambda: dict(list(offset.items())[:4]))["scored"]
assert not s.score(boundary, sealed, pred, pred.sha256, lambda: dict(list(offset.items())[:3]))["scored"]
out["metric_sanity"] = {"offset_rms": good["normalized_rms"], "inclusive_80_percent": True}

closed = {}
closed["F1_wrong_clip_and_training"] = refused_before_read(boundary, sealed, fixture("SYNTHETIC-other", 10)[2])
closed["F1_wrong_training_same_clip"] = refused_before_read(boundary, sealed, fixture(shift=10)[2])
short = replace(pred, trace=pred.trace[:1], sha256=b._sha([pred.kind, pred.model, pred.trace[:1]]))
closed["F1_precommitted_subset"] = refused_before_read(boundary, sealed, short)
for label, candidate in (("forged_suffix", replace(pred, suffix_identity_sha256="0" * 64)), ("subset", short)):
    try:
        o.build(boundary, [candidate], dict(sealed), "synthetic")
    except ValueError as error:
        closed["F1_overlay_build_" + label] = str(error)
    else:
        raise AssertionError("overlay accepted " + label)
doc = o.build(boundary, [pred], dict(sealed), "synthetic")
doc["traces"][0]["suffix_identity_sha256"] = "0" * 64
try:
    o.validate(doc, boundary.clip_id, boundary.source_sha256, dict(sealed))
except ValueError as error:
    closed["F1_overlay_contract_forged_suffix"] = str(error)
else:
    raise AssertionError("contract accepted forged suffix")
full = s.score(boundary, sealed, pred, pred.sha256, lambda: truth)
assert s.gate({c: full for c in s.CATEGORIES})["status"] == "NOT_MET"
closed["F2_one_projectile_aliased_x3"] = True
for bad in (float("nan"), float("inf"), -float("inf")):
    for slot in (0, 1):
        observations = {i: ((bad, y) if slot == 0 else (t, bad)) for i, (t, y) in truth.items()}
        try:
            s.score(boundary, sealed, pred, pred.sha256, lambda: observations)
        except ValueError:
            closed[f"F4_observed_slot_{slot}_{bad}"] = True
        else:
            raise AssertionError("accepted nonfinite observation")
    for category in s.CATEGORIES:
        results = {c: {"clip_id": c, "kind": c, "prediction_sha256": hashlib.sha256(c.encode()).hexdigest(),
                       "sealed_frames": 5, "scored_frames": 5, "coverage": 1.0, "normalized_rms": 0.0,
                       "scored": True, "provenance": "image-derived"} for c in s.CATEGORIES}
        results[category]["normalized_rms"] = bad
        assert s.gate(results)["status"] == "NOT_MET"
        closed[f"F4_gate_{category}_{bad}"] = True

# Commitment exists BEFORE metadata edits; trace, model, kind and supplied commitment stay unchanged.
target, target_sealed, target_pred = fixture("REVIEW-target", 0)
foreign_boundary, _, foreign = fixture("REVIEW-foreign", 100)
commitment = foreign.sha256
relabeled = replace(foreign, clip_id=target.clip_id, training_sha256=target.training_sha256)
p.check(relabeled)
calls = []
laundered = s.score(target, target_sealed, relabeled, commitment,
                    lambda: calls.append(1) or observe(foreign), "image-derived")
honest = s.score(target, target_sealed, target_pred, target_pred.sha256,
                lambda: observe(foreign), "image-derived")
assert calls == [1] and laundered["scored"] and laundered["normalized_rms"] == 0
assert honest["normalized_rms"] > s.THRESHOLD
assert foreign_boundary.training_sha256 != target.training_sha256
assert commitment == relabeled.sha256 and commitment != target_pred.sha256
overlay = o.build(target, [relabeled], dict(target_sealed), "image-derived")
assert o.validate(overlay, target.clip_id, target.source_sha256, dict(target_sealed))
same_target, same_sealed, _ = fixture(shift=0)
_, _, wrong_training = fixture(shift=10)
edited = replace(wrong_training, training_sha256=same_target.training_sha256)
assert s.score(same_target, same_sealed, edited, wrong_training.sha256,
               lambda: observe(wrong_training))["normalized_rms"] == 0
out["F1_residual_metadata_relabel_acceptance"] = {
    "commitment_before_and_after": commitment, "target_generated_commitment": target_pred.sha256,
    "original_clip": foreign.clip_id, "reported_clip": laundered["clip_id"],
    "training_hash_changed_without_digest_change": True, "scored": laundered["scored"],
    "coverage": laundered["coverage"], "laundered_rms": laundered["normalized_rms"],
    "honest_target_prediction_rms": honest["normalized_rms"], "suffix_loader_called": calls == [1],
    "overlay_builder_and_validator_accept": True, "same_clip_training_relabel_also_accepted": True}

# Each trace below is generated by the normal predictor, not made by forging a score dictionary.
# Deliberately false image-derived labels test the public-input eligibility boundary.
registry = {row["clip_id"] for row in csv.DictReader((ROOT / "clips.csv").open(encoding="utf-8-sig", newline=""))}
synthetic_results = {}
for kind in s.CATEGORIES:
    bd, ids, projectile = fixture("REVIEW-NONPUBLIC-" + kind)
    if kind == "projectile":
        candidate = projectile
    elif kind == "bounce":
        candidate = p.bounce(bd, ids, {"name": "restitution", "value": 0.8,
                                     "provenance": {"input_provenance": "synthetic"}}, floor_y=0.95)
    else:
        candidate = p.pendulum(bd, ids, {"name": "angular_frequency", "value": 3.0,
                                       "provenance": {"input_provenance": "synthetic"}})
    assert bd.clip_id not in registry
    synthetic_results[kind] = s.score(bd, ids, candidate, candidate.sha256,
                                      lambda candidate=candidate: observe(candidate), "image-derived")
bad_gate = s.gate(synthetic_results)
assert bad_gate["status"] == "MET" and bad_gate["median"] == 0
out["F2_nonpublic_synthetic_labeled_image_derived_gate"] = {
    "all_clip_ids_absent_from_clips_csv": True, "results": synthetic_results, "gate": bad_gate}

record, suffix, _ = p.st03_record(ROOT)
real_boundary, real_sealed = b.split(record, suffix)
real_pred = p.projectile(real_boundary, real_sealed)
committed = read("evidence/S12/prediction-ST03.json")
assert real_pred.sha256 == committed["prediction"]["sha256"]
artifact = read("evidence/S12/gate-rs/gate-rs.json")
for src in artifact["inputs"]:
    assert hashlib.sha256((ROOT / src["path"]).read_bytes()).hexdigest() == src["sha256"]
raw = (ROOT / s.ST03_TRACK).read_text(encoding="utf-8")
obs, note = s.st03_observations(raw, o.st03_frame_map(ROOT), record["height_px"])
assert note == "validate_segment OK"
real = s.score(real_boundary, real_sealed, real_pred, real_pred.sha256,
               lambda: {i: row for i, row in obs.items() if i > real_boundary.last_training_frame}, "image-derived")
for key, value in real.items():
    assert artifact["clips"]["projectile"][key] == value, key
assert s.gate({"projectile": real}) == artifact["result"]
assert real["scored_frames"] == 7 and real["sealed_frames"] == 466 and not real["scored"]
out["real_evidence_recomputed"] = {"score": real, "gate": artifact["result"], "input_hashes_match": True}

raw_doc = json.loads(raw)
for label in ("wrong_object", "missing_stage", "missing_mask"):
    invalid = copy.deepcopy(raw_doc)
    if label == "wrong_object":
        invalid["record"]["tracking"]["object_id"] = 999
    elif label == "missing_stage":
        invalid["stages"] = []
    else:
        invalid["masks"] = []
    rejected, rejection = s.st03_observations(json.dumps(invalid), o.st03_frame_map(ROOT), record["height_px"])
    assert rejected == {} and "rejected (unscored)" in rejection
    invalid_score = s.score(real_boundary, real_sealed, real_pred, real_pred.sha256, lambda: rejected)
    assert not invalid_score["scored"] and invalid_score["normalized_rms"] is None
    closed["F3_" + label] = rejection


def check_gate_m(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "gate_m":
                assert value == "NOT_MET", value
            check_gate_m(value)
    elif isinstance(node, list):
        for value in node:
            check_gate_m(value)


derived = list((ROOT / "evidence/S12").glob("*.json")) + [ROOT / "evidence/S12/gate-rs/gate-rs.json"]
for path in derived:
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["gate_m"] == "NOT_MET"
    check_gate_m(doc)
out["gate_m_all_derived_labels_not_met"] = [path.relative_to(ROOT).as_posix() for path in derived]
actual_m = read("evidence/S07/S07f/actual-gate-m.json")
assert actual_m["gate"]["status"] == "NOT_MET_INPUT_READINESS"
assert actual_m["gate"]["physics_evaluation"] == "NOT_RUN"
out["owning_gate_m"] = actual_m["gate"]
out["closed_original_and_extended_probes"] = closed
print(json.dumps(out, indent=2, allow_nan=False))
