"""Offline Gate RS adversarial review. All generated tracks are SYNTHETIC, never scene evidence.

Run from any directory: python -B <this file>. Writes only beside this file.
"""
import copy
import csv
from dataclasses import replace
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from Build.real2sim import boundary as b, predict as p, score as s, overlay as o

spec = importlib.util.spec_from_file_location("previous_review", HERE.parent / "recheck2/review.py")
rv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rv)


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def fingerprint():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
            for folder in ("Build/real2sim", "evidence/S12")
            for path in sorted((ROOT / folder).rglob("*")) if path.is_file() and "__pycache__" not in str(path)}


def tracker(bd, pred, prefix_delta=0):
    # Deliberately hand-authored, including bogus checkpoint/frame hashes and full-image masks.
    rows = [(i, t, y + prefix_delta) for i, t, y in bd.training] + [(i, t, y) for i, t, y, _ in pred.trace]
    return {"review_warning": "SYNTHETIC HAND-AUTHORED: no media/checkpoint/GPU read",
            "stages": ["checkpoint", "model_loaded", "tracked"], "checkpoint": {"sha256": "e" * 64},
            "frame_map": [[i, t] for i, t, _ in rows], "frame_sha256": ["f" * 64] * len(rows),
            "record": {"clip_id": bd.clip_id, "source_sha256": bd.source_sha256,
                       "height_px": 1000, "width_px": 10, "tracking": {"object_id": 2},
                       "frames": [{"frame_index": i, "x_px": 5, "y_px": y * 1000} for i, _, y in rows]},
            "stream": [[j, [2], [[0, 0, 1, 1]]] for j in range(len(rows))],
            "masks": [[j, {"2": {"size": [1000, 10], "counts": [0, 10000]}}] for j in range(len(rows))]}


def main():
    before = fingerprint()
    out = {"warning": "Review fixtures only; reproduced MET values below are BYPASSES, not Gate RS evidence.",
           "base": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
    bd, ids, pred = rv.fixture()
    foreign_bd, foreign_ids, foreign = rv.fixture("FOREIGN", "b" * 64, 50)
    closed = {}
    changes = {"clip_id": "FOREIGN", "source_sha256": "b" * 64, "training_sha256": "c" * 64,
               "suffix_identity_sha256": "d" * 64, "suffix_count": 4, "model": pred.model + " edited",
               "kind": "pendulum", "trace": pred.trace[:-1], "commitment": "prediction/v3"}
    for field, value in changes.items():
        closed["v2_" + field] = rv.before_read(bd, ids, replace(pred, **{field: value}))
    closed["foreign_unmodified"] = rv.before_read(bd, ids, foreign)
    subset = replace(pred, trace=pred.trace[:1])
    subset = replace(subset, sha256=p.commitment_sha256(subset))
    closed["self_consistent_subset"] = rv.before_read(bd, ids, subset)
    edited = replace(foreign, clip_id=bd.clip_id, source_sha256=bd.source_sha256,
                     training_sha256=bd.training_sha256)
    closed["foreign_metadata_only"] = rv.before_read(bd, ids, edited)
    closed["overlay_builder"] = rv.refusal(lambda: o.build(bd, [edited], dict(ids), "image-derived"))
    doc = o.build(foreign_bd, [foreign], dict(foreign_ids), "image-derived")
    doc["clip_id"] = doc["traces"][0]["clip_id"] = bd.clip_id
    doc["source_sha256"] = doc["traces"][0]["source_sha256"] = bd.source_sha256
    doc["traces"][0]["training_sha256"] = bd.training_sha256
    closed["overlay_validator"] = rv.refusal(lambda: o.validate(doc, bd.clip_id, bd.source_sha256, dict(ids)))
    legacy = replace(pred, commitment=p.LEGACY)
    legacy = replace(legacy, sha256=p.commitment_sha256(legacy))
    p.check(legacy)
    closed["legacy_score"] = rv.before_read(bd, ids, legacy)
    for bad in (math.nan, math.inf, -math.inf):
        for slot in (0, 1):
            obs = rv.observe(pred)
            row = list(obs[10]); row[slot] = bad; obs[10] = tuple(row)
            closed[f"nonfinite_{slot}_{bad}"] = rv.refusal(lambda: s.score(bd, ids, pred, pred.sha256, lambda: obs))
    out["F1_R_F1_F4_refusals"] = closed

    pairs = {"projectile": "PJ03", "bounce": "BN01", "pendulum": "PD02"}
    generic, forged, boundaries, predictions = {}, {}, {}, {}
    for kind, clip in pairs.items():
        kb, ki, kp = rv.fixture(clip, rv.SHA[clip])
        kp = rv.kind_prediction(kind, kb, ki, kp)
        boundaries[kind], predictions[kind] = (kb, ki), kp
        generic[kind] = s.score(kb, ki, kp, kp.sha256, lambda kp=kp: rv.observe(kp), "image-derived")
        assert generic[kind]["tracking_evidence"] is None
        rel = (HERE / (kind + "-SYNTHETIC-track.json")).relative_to(ROOT).as_posix()
        save(kind + "-SYNTHETIC-track.json", tracker(kb, kp))
        # No score, receipt, evidence dictionary or gate return is edited; use native Tracked.
        loader = s.Tracked(kb, rel, dict(list((i, t) for i, t, _ in kb.training) + list(ki)))
        forged[kind] = s.score(kb, ki, kp, kp.sha256, loader, "image-derived")
        assert forged[kind]["scored"] and forged[kind]["input_receipt"] and s._tracking_ok(forged[kind], ROOT)
        assert forged[kind]["tracking_evidence"]["prefix_max_abs"] < 1e-12
    assert s.gate(generic)["shortfall"] == list(s.CATEGORIES)
    attack = s.gate(forged)
    assert attack["status"] == "MET" and attack["median"] < 1e-12
    out["F2_R3_forged_native_Tracked"] = {"scores": forged, "gate": attack,
        "genuine_public_receipts": True, "predictions_committed_before_loaders": True,
        "media_checkpoint_gpu_used": False, "score_results_edited": False}
    out["F2_R2_narrow_fixes"] = {"generic_loader": s.gate(generic),
        "explicit_synthetic": s.gate({k: r | {"provenance": "synthetic"} for k, r in forged.items()})}
    assert out["F2_R2_narrow_fixes"]["explicit_synthetic"]["shortfall"] == list(s.CATEGORIES)

    controls = {}
    for kind, original in forged.items():
        for field, value in (("prediction_commitment", p.LEGACY), ("coverage", 0.99),
                             ("normalized_rms", math.nan), ("normalized_rms", math.inf),
                             ("normalized_rms", -0.01), ("scored_frames", 100)):
            modified = copy.deepcopy(forged); modified[kind][field] = value
            assert s.gate(modified)["status"] == "NOT_MET"
            controls[f"{kind}_{field}_{value}"] = "refused"
        other = next(k for k in s.CATEGORIES if k != kind)
        modified = copy.deepcopy(forged); modified[kind]["prediction_sha256"] = forged[other]["prediction_sha256"]
        assert s.gate(modified)["status"] == "NOT_MET"
        for label, edit in {"bad_digest": {"sha256": "0" * 64}, "path_escape": {"path": "../outside.json"},
                            "absolute_escape": {"path": str(ROOT.parent / "outside.json")},
                            "wrong_identity": {"clip_id": "OTHER"}}.items():
            result = original | {"tracking_evidence": original["tracking_evidence"] | edit}
            assert not s._eligible(kind, result)
            controls[kind + "_" + label] = "refused"
        assert not s._eligible(kind, original | {"observations_sha256": "0" * 64})
    out["gate_digest_identity_path_F4_controls"] = controls

    kb, ki = boundaries["projectile"]; kp = predictions["projectile"]
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        temp = Path(tmp); rel = (temp / "track.json").relative_to(ROOT).as_posix()
        frame_pts = dict([(i, t) for i, t, _ in kb.training] + list(ki))
        prefix = {}
        for delta in (0.0019, 0.0021):
            (temp / "track.json").write_text(json.dumps(tracker(kb, kp, delta)), encoding="utf-8")
            loader = s.Tracked(kb, rel, frame_pts)
            if delta < s.PREFIX_TOL:
                loader(); prefix[str(delta)] = loader.evidence["prefix_max_abs"]
            else:
                prefix[str(delta)] = rv.refusal(loader)
        wrong = tracker(kb, kp); wrong["record"]["clip_id"] = "OTHER"
        (temp / "track.json").write_text(json.dumps(wrong), encoding="utf-8")
        prefix["wrong_artifact_identity"] = rv.refusal(s.Tracked(kb, rel, frame_pts))
        # Different training prefix, same clip/source: score accepts a loader bound to the OLD boundary.
        # Native public constructors only, no subclass or result edits.
        (temp / "track.json").write_text(json.dumps(tracker(kb, kp)), encoding="utf-8")
        shifted, shifted_ids, shifted_pred = rv.fixture(kb.clip_id, kb.source_sha256, shift=30)
        prefix["correctly_bound_shifted_loader"] = rv.refusal(s.Tracked(shifted, rel, frame_pts))
        transplanted = s.score(shifted, shifted_ids, shifted_pred, shifted_pred.sha256,
                              s.Tracked(kb, rel, frame_pts), "image-derived")
        assert s._eligible("projectile", transplanted)
        prefix["wrong_boundary_loader_accepted"] = {"eligible": True,
            "training_shift_H": 0.03, "threshold_H": s.PREFIX_TOL,
            "normalized_rms": transplanted["normalized_rms"], "score": transplanted}
        bypass = dict(forged, projectile=transplanted)
        assert s.gate(bypass)["status"] == "MET"
        prefix["wrong_boundary_loader_gate"] = s.gate(bypass)
        out["prefix_custody"] = prefix

    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        root = Path(tmp)
        for rel in ("clips.csv", s.APPROVAL, s.REGISTRY):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes((ROOT / rel).read_bytes())
        approval = root / s.APPROVAL; original = approval.read_text(encoding="utf-8")
        approvals = {"negated": original.replace("**Use:** local", "**Use:** NOT approved for local"),
                     "unrelated": "**Approved IDs:** PJ03.\n**Use:** DENIED.\nPrior request: local scene/tracking pipeline work\n",
                     "duplicate_grant": original + "\n" + original,
                     "no_grant": "**Approved IDs:** PJ03.\nNo use grant.\n",
                     "revoked_same_line": original.replace("work ONLY", "work ONLY revoked")}
        out["F2_A"] = {}
        for label, text in approvals.items():
            approval.write_text(text, encoding="utf-8")
            out["F2_A"][label] = rv.refusal(lambda: s.public_receipt("PJ03", rv.SHA["PJ03"], "projectile", root))
        approval.write_text(original, encoding="utf-8")
        assert s.public_receipt("PJ03", rv.SHA["PJ03"], "projectile", root)["clip_id"] == "PJ03"
        rows = list(csv.DictReader((ROOT / "clips.csv").open(encoding="utf-8", newline="")))
        out["F2_L"] = {}
        for licence in ("CC-BY-NC-4.0", "CC-BY-ND-4.0", "pd-nc", "pd-not-public", "CC-BY-999.99", "CC-BY-.", "CC-BY-", "CC-BY-SA-9.0"):
            modified = copy.deepcopy(rows); next(r for r in modified if r["clip_id"] == "PJ03")["licence"] = licence
            with (root / "clips.csv").open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(modified[0])); w.writeheader(); w.writerows(modified)
            out["F2_L"][licence] = rv.refusal(lambda: s.public_receipt("PJ03", rv.SHA["PJ03"], "projectile", root))

    record, suffix, _ = p.st03_record(ROOT); real_bd, real_ids = b.split(record, suffix)
    real_pred = p.projectile(real_bd, real_ids)
    committed = rv.read("evidence/S12/prediction-ST03-v2.json")["prediction"]["sha256"]
    real = s.score(real_bd, real_ids, real_pred, committed, s.Tracked(real_bd, s.ST03_TRACK, o.st03_frame_map(ROOT)), "image-derived")
    saved = rv.read("evidence/S12/gate-rs/gate-rs.json")
    assert all(saved["clips"]["projectile"][k] == v for k, v in real.items())
    assert s.gate({"projectile": real}) == saved["result"]
    assert (real["scored_frames"], real["sealed_frames"], saved["result"]["status"]) == (7, 466, "NOT_MET")
    out["actual_gate_unchanged"] = {"result": saved["result"], "scored_frames": real["scored_frames"],
        "sealed_frames": real["sealed_frames"], "normalized_rms": real["normalized_rms"], "coverage": real["coverage"]}
    # Independent boundary mismatch with the EXISTING genuine ST03 artifact (no forged track).
    real_map = o.st03_frame_map(ROOT)
    shifted_record = copy.deepcopy(record)
    for frame in shifted_record["frames"]:
        frame["y_px"] += shifted_record["height_px"] * 0.01
    shifted_bd, shifted_seal = b.split(shifted_record, suffix)
    shifted_pred = p.projectile(shifted_bd, shifted_seal)
    honest_refusal = rv.refusal(s.Tracked(shifted_bd, s.ST03_TRACK, real_map))
    wrong_loader_result = s.score(shifted_bd, shifted_seal, shifted_pred, shifted_pred.sha256,
                                  s.Tracked(real_bd, s.ST03_TRACK, real_map), "image-derived")
    assert s._tracking_ok(wrong_loader_result, ROOT)
    assert wrong_loader_result["scored_frames"] == 7
    out["F2_C_real_artifact_wrong_boundary"] = {"training_shift_H": 0.01, "threshold_H": s.PREFIX_TOL,
        "correct_loader_refused": honest_refusal, "wrong_loader_score_accepted": True,
        "gate_tracking_recheck_accepts": True, "actual_coverage_still_shortfall": not wrong_loader_result["scored"]}
    # F3: invalid structural tracker output remains unscored rather than fallback centroids.
    raw_real = rv.read(s.ST03_TRACK)
    f3 = {}
    for label, mutate in (("wrong_object", lambda x: x["record"]["tracking"].update(object_id=999)),
                          ("missing_masks", lambda x: x.update(masks=[])),
                          ("missing_stages", lambda x: x.update(stages=[]))):
        damaged = copy.deepcopy(raw_real); mutate(damaged)
        obs, reason = s.st03_observations(json.dumps(damaged), real_map, real_bd.clip_id, real_bd.source_sha256)
        assert not obs and "rejected (unscored)" in reason
        f3[label] = reason
    out["F3_invalid_tracker_rejected"] = f3
    labels = []
    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "gate_m":
                    assert child == "NOT_MET"; labels.append(child)
                walk(child)
        elif isinstance(value, list):
            for child in value: walk(child)
    for path in (ROOT / "evidence/S12").rglob("*.json"):
        walk(json.loads(path.read_text(encoding="utf-8")))
    actual_m = rv.read("evidence/S07/S07f/actual-gate-m.json")["gate"]
    assert actual_m["status"] == "NOT_MET_INPUT_READINESS" and actual_m["physics_evaluation"] == "NOT_RUN"
    out["gate_m"] = {"all_S12_gate_m_fields_NOT_MET": len(labels), "owning_gate": actual_m["status"], "physics": "NOT_RUN"}
    assert fingerprint() == before, "Read-only source/evidence drifted during review"
    save("source-hashes.json", before)
    save("results.json", out)
    print("REVIEW COMPLETE: CHANGES_REQUIRED; forged native Tracked -> MET; wrong-boundary loader eligible; actual NOT_MET 7/466")


if __name__ == "__main__":
    main()
