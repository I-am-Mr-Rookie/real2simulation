"""Offline independent acceptance probes; synthetic results below are NOT real-scene evidence."""
from dataclasses import replace
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from Build.real2sim import boundary as b, predict as p, score as s, overlay as o


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


SHA = {f["clip_id"]: f["sha256"] for f in read(s.REGISTRY)["files"] if f.get("clip_id")}


def fixture(clip="REVIEW-SYNTHETIC", sha="a" * 64, shift=0):
    record = {"clip_id": clip, "source_sha256": sha, "last_training_frame": 9, "height_px": 1000,
              "frames": [{"frame_index": i, "pts_s": i / 30,
                          "y_px": 100 + 20 * i + 3 * i * i + shift} for i in range(10)]}
    bd, ids = b.split(record, [(i, i / 30) for i in range(10, 15)])
    return bd, ids, p.projectile(bd, ids)


def observe(pred):
    return {i: (t, y) for i, t, y, _ in pred.trace}


def refusal(fn):
    try:
        fn()
    except (ValueError, TypeError, KeyError, OSError) as error:
        return f"{type(error).__name__}: {error}"
    raise AssertionError("expected refusal")


def before_read(bd, ids, pred):
    called = []
    reason = refusal(lambda: s.score(bd, ids, pred, pred.sha256, lambda: called.append(True) or {}))
    assert not called, "suffix was read before refusal"
    return reason


def kind_prediction(kind, bd, ids, projectile):
    if kind == "projectile":
        return projectile
    if kind == "bounce":
        return p.bounce(bd, ids, {"name": "restitution", "value": 0.8,
                                  "provenance": {"input_provenance": "synthetic"}}, floor_y=0.95)
    return p.pendulum(bd, ids, {"name": "angular_frequency", "value": 3.0,
                              "provenance": {"input_provenance": "synthetic"}})


def run():
    out = {"warning": "review-only synthetic probes; no real gate success", "snapshot":
           subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
    bd, ids, pred = fixture()
    foreign_bd, foreign_ids, foreign = fixture("FOREIGN", "b" * 64, 50)
    closed = {}
    changes = {"clip_id": "FOREIGN", "source_sha256": "b" * 64,
               "training_sha256": "c" * 64, "suffix_identity_sha256": "d" * 64,
               "suffix_count": 4, "model": pred.model + " edited", "kind": "pendulum",
               "trace": pred.trace[:-1], "commitment": "prediction/v3"}
    for field, value in changes.items():
        edited = replace(pred, **{field: value})
        closed["v2_" + field] = before_read(bd, ids, edited)
    closed["foreign_unmodified"] = before_read(bd, ids, foreign)
    subset = replace(pred, trace=pred.trace[:1])
    subset = replace(subset, sha256=p.commitment_sha256(subset))
    closed["self_consistent_v2_subset"] = before_read(bd, ids, subset)
    edited = replace(foreign, clip_id=bd.clip_id, source_sha256=bd.source_sha256,
                     training_sha256=bd.training_sha256)
    closed["foreign_metadata_only"] = before_read(bd, ids, edited)
    closed["foreign_overlay_builder"] = refusal(lambda: o.build(bd, [edited], dict(ids), "image-derived"))
    doc = o.build(foreign_bd, [foreign], dict(foreign_ids), "image-derived")
    doc["clip_id"] = doc["traces"][0]["clip_id"] = bd.clip_id
    doc["source_sha256"] = doc["traces"][0]["source_sha256"] = bd.source_sha256
    doc["traces"][0]["training_sha256"] = bd.training_sha256
    closed["foreign_overlay_validator"] = refusal(lambda: o.validate(doc, bd.clip_id, bd.source_sha256, dict(ids)))
    legacy = replace(pred, commitment=p.LEGACY)
    legacy = replace(legacy, sha256=p.commitment_sha256(legacy))
    p.check(legacy)
    closed["legacy_score"] = before_read(bd, ids, legacy)
    closed["legacy_overlay_build"] = refusal(lambda: o.build(bd, [legacy], dict(ids), "synthetic"))
    for bad in (math.nan, math.inf, -math.inf):
        for slot in (0, 1):
            obs = observe(pred)
            row = list(obs[10])
            row[slot] = bad
            obs[10] = tuple(row)
            closed[f"nonfinite_{slot}_{bad}"] = refusal(lambda: s.score(bd, ids, pred, pred.sha256, lambda: obs))

    # Prior F2-R inputs stay closed. Then change only declared identity BEFORE committing v2.
    unknown, known = {}, {}
    clips = {"projectile": "PJ03", "bounce": "BN01", "pendulum": "PD02"}
    for kind in s.CATEGORIES:
        ub, ui, up = fixture("REVIEW-NONPUBLIC-" + kind)
        up = kind_prediction(kind, ub, ui, up)
        unknown[kind] = s.score(ub, ui, up, up.sha256, lambda up=up: observe(up), "image-derived")
        clip = clips[kind]
        kb, ki, kp = fixture(clip, SHA[clip])
        kp = kind_prediction(kind, kb, ki, kp)
        known[kind] = s.score(kb, ki, kp, kp.sha256, lambda kp=kp: observe(kp), "synthetic")
        assert known[kind]["input_receipt"] == s.public_receipt(clip, SHA[clip], kind)
    assert s.gate(unknown)["status"] == "NOT_MET"
    bypass = s.gate(known)
    assert bypass["status"] == "MET" and bypass["median"] == 0
    assert all(r["provenance"] == "synthetic" for r in known.values())
    out["known_public_identity_synthetic_observations"] = {"scores": known, "gate": bypass,
        "media_or_tracker_read": False, "prediction_committed_before_observation_loader": True}
    mislabeled = {kind: score | {"provenance": "image-derived"} for kind, score in known.items()}
    assert s.gate(mislabeled)["status"] == "MET"
    out["known_public_identity_false_image_label"] = s.gate(mislabeled)
    # The cited tracker validator is structural, not an observation/source-custody receipt.
    structural = {}
    for kind, clip in clips.items():
        kb, ki, kp = fixture(clip, SHA[clip])
        kp = kind_prediction(kind, kb, ki, kp)
        raw_fixture = {"stages": ["checkpoint", "model_loaded", "tracked"],
                       "checkpoint": {"sha256": "e" * 64}, "frame_map": list(ki),
                       "record": {"clip_id": "NOT-" + clip, "source_sha256": "f" * 64,
                                  "height_px": 1000, "width_px": 10, "tracking": {"object_id": 2},
                                  "frames": [{"frame_index": i, "x_px": 5, "y_px": y * 1000}
                                             for i, _, y, _ in kp.trace]},
                       "stream": [[index, [2], [[0, 0, 1, 1]]] for index in range(5)],
                       "masks": [[index, {"2": {"size": [1000, 10], "counts": [0, 10000]}}]
                                 for index in range(5)]}
        tracker_obs, why = s.st03_observations(json.dumps(raw_fixture), dict(ki), 1000)
        assert why == "validate_segment OK"
        structural[kind] = s.score(kb, ki, kp, kp.sha256, lambda: tracker_obs, "image-derived")
    structural_gate = s.gate(structural)
    assert structural_gate["status"] == "MET" and structural_gate["median"] < 1e-12
    out["synthetic_tracker_payload_wrong_source"] = {"gate": structural_gate,
        "validator": "validate_segment OK in all three categories",
        "all_raw_clip_and_source_identities_differ_from_receipt": True,
        "media_or_checkpoint_bytes_read": False}
    out["unknown_public_identity_refused"] = s.gate(unknown)

    for kind in s.CATEGORIES:
        bad = copy.deepcopy(known)
        bad[kind]["prediction_commitment"] = p.LEGACY
        assert s.gate(bad)["status"] == "NOT_MET"
        bad = copy.deepcopy(known)
        bad[kind]["coverage"] = 0.99
        assert s.gate(bad)["status"] == "NOT_MET"
        bad = copy.deepcopy(known)
        bad[kind]["prediction_sha256"] = known[next(c for c in s.CATEGORIES if c != kind)]["prediction_sha256"]
        assert s.gate(bad)["status"] == "NOT_MET"
        for value in (math.nan, math.inf, -math.inf, -0.01):
            invalid = copy.deepcopy(known)
            invalid[kind]["normalized_rms"] = value
            assert s.gate(invalid)["status"] == "NOT_MET"
        bad = copy.deepcopy(known)
        bad[kind]["input_receipt"] = known["projectile"]["input_receipt"]
        if kind != "projectile":
            assert s.gate(bad)["status"] == "NOT_MET"
    out["valid_receipt_f4_and_legacy_controls"] = "all three categories refuse v1, nonfinite/negative RMS, cross-category receipt"

    matrix = {}
    for clip in clips.values():
        matrix[clip] = {}
        for category in s.CATEGORIES:
            try:
                s.public_receipt(clip, SHA[clip], category)
                matrix[clip][category] = "accepted"
            except ValueError as error:
                matrix[clip][category] = str(error)
        closed["wrong_source_" + clip] = refusal(lambda clip=clip: s.public_receipt(clip, "f" * 64,
                                               next(k for k, v in clips.items() if v == clip)))
    out["category_matrix"] = matrix
    out["licence_regex"] = {licence: bool(s.LICENCE.fullmatch(licence)) for licence in
        ["CC-BY-SA-4.0", "CC-BY-4.0", "CC0-1.0", "Public Domain", "Pexels License", "Pixabay Content License",
         "CC-BY-NC-4.0", "CC-BY-ND-4.0", "CC-BY-NC-SA-4.0", "pd-nc", "pd-not-public", "CC-BY-999.99", "CC-BY-."]}

    # Trusted metadata corruption probes use only a temporary root below Owns, never the real registries.
    with tempfile.TemporaryDirectory(prefix="receipt-", dir=HERE) as tmp:
        root = Path(tmp)
        for rel in (s.APPROVAL, s.REGISTRY):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / rel).read_bytes())
        (root / "clips.csv").write_bytes((ROOT / "clips.csv").read_bytes())
        approval = root / s.APPROVAL
        original = approval.read_text(encoding="utf-8")
        rows = list(csv.DictReader((ROOT / "clips.csv").open(encoding="utf-8", newline="")))
        out["licence_full_receipt"] = {}
        for licence in ("CC-BY-NC-4.0", "CC-BY-ND-4.0", "pd-nc", "pd-not-public", "CC-BY-999.99", "CC-BY-."):
            modified = copy.deepcopy(rows)
            next(row for row in modified if row["clip_id"] == "PJ03")["licence"] = licence
            with (root / "clips.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(modified[0]))
                writer.writeheader()
                writer.writerows(modified)
            try:
                s.public_receipt("PJ03", SHA["PJ03"], "projectile", root)
                out["licence_full_receipt"][licence] = "accepted"
            except ValueError as error:
                out["licence_full_receipt"][licence] = str(error)
        (root / "clips.csv").write_bytes((ROOT / "clips.csv").read_bytes())
        variants = {"negated_use": original.replace("**Use:** local", "**Use:** NOT approved for local"),
                    "unrelated_use_mention": "**Approved IDs:** PJ03.\n**Use:** DENIED.\nPrior request: local scene/tracking pipeline work\n",
                    "ids_spaces": original.replace("RM02,RM04", "RM02, RM04")}
        out["approval_parser"] = {}
        for label, text in variants.items():
            approval.write_text(text, encoding="utf-8")
            try:
                s.public_receipt("PJ03", SHA["PJ03"], "projectile", root)
                out["approval_parser"][label] = "accepted"
            except ValueError as error:
                out["approval_parser"][label] = str(error)
        approval.write_text(original, encoding="utf-8")
        original_registry = read(s.REGISTRY)
        out["registry_controls"] = {}
        for label in ("missing_sha", "duplicate_clip", "duplicate_csv", "missing_approval", "wrong_category"):
            altered = copy.deepcopy(original_registry)
            if label == "missing_sha":
                next(f for f in altered["files"] if f.get("clip_id") == "PJ03").pop("sha256")
            elif label == "duplicate_clip":
                altered["files"].append(copy.deepcopy(next(f for f in altered["files"] if f.get("clip_id") == "PJ03")))
            (root / s.REGISTRY).write_text(json.dumps(altered), encoding="utf-8")
            modified = copy.deepcopy(rows)
            if label == "duplicate_csv":
                modified.append(copy.deepcopy(next(row for row in modified if row["clip_id"] == "PJ03")))
            elif label == "wrong_category":
                next(row for row in modified if row["clip_id"] == "PJ03")["experiment"] = "scene"
            with (root / "clips.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(modified[0]))
                writer.writeheader()
                writer.writerows(modified)
            approval.write_text("No approval" if label == "missing_approval" else original, encoding="utf-8")
            out["registry_controls"][label] = refusal(lambda: s.public_receipt("PJ03", SHA["PJ03"], "projectile", root))

    record, suffix, _ = p.st03_record(ROOT)
    real_bd, real_ids = b.split(record, suffix)
    real_pred = p.projectile(real_bd, real_ids)
    assert real_pred.sha256 == read("evidence/S12/prediction-ST03-v2.json")["prediction"]["sha256"]
    raw = read(s.ST03_TRACK)
    frame_map = o.st03_frame_map(ROOT)
    obs, note = s.st03_observations(json.dumps(raw), frame_map, record["height_px"])
    assert note == "validate_segment OK"
    real = s.score(real_bd, real_ids, real_pred, real_pred.sha256,
                   lambda: {i: row for i, row in obs.items() if i > real_bd.last_training_frame}, "image-derived")
    artifact = read("evidence/S12/gate-rs/gate-rs.json")
    assert all(artifact["clips"]["projectile"][k] == v for k, v in real.items())
    assert s.gate({"projectile": real}) == artifact["result"]
    for source in artifact["inputs"]:
        assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    out["real_evidence_recomputed"] = {"score": real, "gate": artifact["result"], "input_hashes_match": True}
    previous = json.loads(subprocess.check_output(["git", "show", "9d1a9ae:evidence/S12/gate-rs/gate-rs.json"],
                                                  cwd=ROOT, text=True))
    measurement_fields = ("sealed_frames", "scored_frames", "coverage", "normalized_rms",
                          "normalized_rms_first5_diagnostic", "max_abs", "scored")
    assert all(previous["clips"]["projectile"][key] == real[key] for key in measurement_fields)
    assert previous["result"]["status"] == artifact["result"]["status"] == "NOT_MET"
    out["measured_values_unchanged_vs_pre_fix2"] = list(measurement_fields)

    out["tracker_identity_probes"] = {}
    for field, value in (("clip_id", "OTHER-CLIP"), ("source_sha256", "f" * 64)):
        altered = copy.deepcopy(raw)
        altered["record"][field] = value
        accepted, why = s.st03_observations(json.dumps(altered), frame_map, record["height_px"])
        assert why == "validate_segment OK" and accepted == obs
        out["tracker_identity_probes"][field] = {"altered_value": value, "validator": why, "same_observations": accepted == obs}
    for label in ("wrong_object", "missing_stages", "missing_masks"):
        altered = copy.deepcopy(raw)
        if label == "wrong_object":
            altered["record"]["tracking"]["object_id"] = 999
        else:
            altered["stages" if label == "missing_stages" else "masks"] = []
        rejected, why = s.st03_observations(json.dumps(altered), frame_map, record["height_px"])
        assert rejected == {} and "rejected (unscored)" in why
        closed["F3_" + label] = why

    gate_labels = []
    def labels(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "gate_m":
                    assert value == "NOT_MET", value
                    gate_labels.append(value)
                labels(value)
        elif isinstance(node, list):
            for value in node:
                labels(value)
    paths = sorted((ROOT / "evidence/S12").rglob("*.json"))
    for path in paths:
        doc = json.loads(path.read_text(encoding="utf-8"))
        labels(doc)
    actual = read("evidence/S07/S07f/actual-gate-m.json")["gate"]
    assert actual["status"] == "NOT_MET_INPUT_READINESS" and actual["physics_evaluation"] == "NOT_RUN"
    out["gate_m"] = {"json_files_checked": [str(path.relative_to(ROOT)) for path in paths],
                     "gate_m_fields_checked": len(gate_labels), "owning_gate": actual}
    out["closed_probes"] = closed
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, allow_nan=False))
