"""Offline review probes: assertions describe observed behavior, NOT product acceptance.

Run with python -B evidence/reviews/R-RS/reproduce.py from the review worktree.
No artifact regeneration, service calls, model inference, or product-file writes.
"""
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.real2sim import boundary as b, predict as p, score as s, overlay as o


def read(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def fixture(clip="SYNTHETIC-review", shift=0):
    record = {"clip_id": clip, "source_sha256": hashlib.sha256(clip.encode()).hexdigest(),
              "height_px": 1000, "last_training_frame": 9,
              "frames": [{"frame_index": i, "pts_s": i / 30,
                          "y_px": 100 + 20 * i + 3 * i * i + shift} for i in range(10)]}
    boundary, sealed = b.split(record, [(i, i / 30) for i in range(10, 15)])
    return boundary, sealed, p.projectile(boundary, sealed)


def observe(pred):
    return {i: (t, y) for i, t, y, _ in pred.trace}


out = {"purpose": "review reproductions; defect assertions passing means defects reproduced"}
boundary, sealed, pred = fixture()
truth = observe(pred)
offset = {i: (t, y + 0.03) for i, (t, y) in truth.items()}
good = s.score(boundary, sealed, pred, pred.sha256, lambda: offset)
assert math.isclose(good["normalized_rms"], 0.03, abs_tol=1e-12)
at80 = s.score(boundary, sealed, pred, pred.sha256, lambda: dict(list(offset.items())[:4]))
below80 = s.score(boundary, sealed, pred, pred.sha256, lambda: dict(list(offset.items())[:3]))
assert at80["scored"] and at80["coverage"] == 0.8 and not below80["scored"]
assert s.gate({"projectile": good})["status"] == "NOT_MET"
assert s.gate({c: {"scored": True, "normalized_rms": 0.05} for c in s.CATEGORIES})["status"] == "MET"
out["metric_sanity"] = {"rms_constant_offset": good["normalized_rms"],
                        "coverage_80_scored": at80["scored"], "coverage_60_scored": below80["scored"]}

foreign_boundary, _, foreign_pred = fixture("SYNTHETIC-other-clip", 10)
foreign = s.score(boundary, sealed, foreign_pred, foreign_pred.sha256, lambda: observe(foreign_pred))
assert foreign["scored"] and foreign["normalized_rms"] == 0
assert foreign_pred.training_sha256 != boundary.training_sha256 and foreign_pred.clip_id != boundary.clip_id
out["F1_wrong_clip_and_training_accepted"] = {"reported_clip": foreign["clip_id"],
    "prediction_clip": foreign_pred.clip_id, "scored": foreign["scored"], "rms": foreign["normalized_rms"]}

short_trace = pred.trace[:1]
short = replace(pred, trace=short_trace, sha256=b._sha([pred.kind, pred.model, short_trace]))
short_score = s.score(boundary, sealed, short, short.sha256, lambda: truth)
assert short_score["coverage"] == 1 and short_score["scored"] and boundary.suffix_count == 5
out["F1_precommitted_subset_coverage_inflation"] = {"true_sealed_frames": boundary.suffix_count, **short_score}

full = s.score(boundary, sealed, pred, pred.sha256, lambda: truth)
aliased_gate = s.gate({c: full for c in s.CATEGORIES})
assert aliased_gate["status"] == "MET" and full["kind"] == "projectile"
out["F2_one_synthetic_projectile_used_for_all_categories"] = aliased_gate

nonfinite = {i: (float("nan"), y) for i, (_, y) in truth.items()}
accepted_nan_pts = s.score(boundary, sealed, pred, pred.sha256, lambda: nonfinite)
assert accepted_nan_pts["scored"] and accepted_nan_pts["normalized_rms"] == 0
nan_gate = s.gate({"projectile": full, "bounce": full,
                   "pendulum": {"scored": True, "normalized_rms": float("nan")}})
assert nan_gate["status"] == "MET"
out["F4_nonfinite_data_accepted"] = {"nan_pts_scored": accepted_nan_pts["scored"],
    "nan_category_gate_status": nan_gate["status"], "nan_category_listed_as_shortfall": "pendulum" in nan_gate["shortfall"]}

fmap = dict(sealed)
forged = replace(pred, suffix_identity_sha256="0" * 64)
forged_doc = o.build(boundary, [forged], fmap, "synthetic")
assert forged_doc["traces"][0]["suffix_identity_sha256"] != boundary.suffix_identity_sha256
out["F1_overlay_accepts_unbound_suffix_metadata"] = True

record, suffix, _ = p.st03_record(ROOT)
real_boundary, real_sealed = b.split(record, suffix)
real_pred = p.projectile(real_boundary, real_sealed)
committed = read("evidence/S12/prediction-ST03.json")
assert real_pred.sha256 == committed["prediction"]["sha256"]
assert tuple((i, t) for i, t, *_ in real_pred.trace) == real_sealed
assert real_boundary.suffix_count == 466 and real_sealed[0][0] == 77
old = read("evidence/S12/boundary-ST03.json")
assert old["boundary"]["suffix_count"] == 465 and old["quarantined_suffix_frames"] == [77]
assert committed["supersedes_s12a_seal"]["suffix_identity_sha256"] == old["boundary"]["suffix_identity_sha256"]
assert not committed["suffix_observations_read"]
artifact = read("evidence/S12/gate-rs/gate-rs.json")
for src in artifact["inputs"]:
    assert hashlib.sha256((ROOT / src["path"]).read_bytes()).hexdigest() == src["sha256"]
frame_pts = o.st03_frame_map(ROOT)
raw = (ROOT / s.ST03_TRACK).read_text(encoding="utf-8")
obs, note = s.st03_observations(raw, frame_pts, record["height_px"])
assert note == "validate_segment OK"
real = s.score(real_boundary, real_sealed, real_pred, real_pred.sha256,
               lambda: {i: row for i, row in obs.items() if i > real_boundary.last_training_frame})
for key, value in real.items():
    assert artifact["clips"]["projectile"][key] == value, key
assert real["scored_frames"] == 7 and real["sealed_frames"] == 466 and not real["scored"]
assert s.gate({"projectile": real}) == artifact["result"]
out["real_evidence_recomputed"] = {**real, "validation": note, "all_input_hashes_match": True,
    "errata_reseal_old_count": 465, "errata_reseal_new_count": 466}

invalid = json.loads(raw)
invalid["record"]["tracking"]["object_id"] = 999
fallback, rejection = s.st03_observations(json.dumps(invalid), frame_pts, record["height_px"])
assert "expected 2" in rejection and fallback == obs
invalid_score = s.score(real_boundary, real_sealed, real_pred, real_pred.sha256, lambda: fallback)
assert invalid_score["scored_frames"] == real["scored_frames"]
out["F3_wrong_object_validation_failure_scores_anyway"] = {"validation": rejection,
    "observations_returned": len(fallback), "same_rms_as_valid_record": invalid_score["normalized_rms"] == real["normalized_rms"]}

original_plan = subprocess.check_output(["git", "show", "81996b0:Run-System/Runs/S12e-orch45/PLAN.md"], cwd=ROOT)
current_plan = subprocess.check_output(["git", "show", "HEAD:Run-System/Runs/S12e-orch45/PLAN.md"], cwd=ROOT)
assert original_plan == current_plan
out["original_preregistration_blob_matches_rebased_copy"] = True
derived = list((ROOT / "evidence/S12").glob("*.json")) + [ROOT / "evidence/S12/gate-rs/gate-rs.json"]
for path in derived:
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["gate_m"] == "NOT_MET", path
    def check_gate_values(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "gate_m":
                    assert value == "NOT_MET", path
                check_gate_values(value)
        elif isinstance(node, list):
            for value in node:
                check_gate_values(value)
    check_gate_values(doc)
out["all_derived_document_gate_m_labels_not_met"] = [str(path.relative_to(ROOT)) for path in derived]
out["completed_assertion_groups"] = 10
print(json.dumps(out, indent=2, allow_nan=False))
