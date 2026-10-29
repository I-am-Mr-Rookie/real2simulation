"""Replay each R-RS reproduction (evidence/reviews/R-RS/reproduce.py, read-only) against fixed code.

reproduce.py asserts the DEFECTS exist, so after the fix it stops at its first now-false assertion;
this script repeats the same probes and records the refusal. Offline; no service calls.
Run: python -B Run-System/Runs/S12e-fix-orch52/refusals.py  (from the worktree root)
"""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.real2sim import boundary as b, predict as p, score as s, overlay as o  # noqa: E402


def fixture(clip="SYNTHETIC-review", shift=0):  # identical to reproduce.py fixture()
    record = {"clip_id": clip, "source_sha256": hashlib.sha256(clip.encode()).hexdigest(),
              "height_px": 1000, "last_training_frame": 9,
              "frames": [{"frame_index": i, "pts_s": i / 30,
                          "y_px": 100 + 20 * i + 3 * i * i + shift} for i in range(10)]}
    boundary, sealed = b.split(record, [(i, i / 30) for i in range(10, 15)])
    return boundary, sealed, p.projectile(boundary, sealed)


def observe(pred):
    return {i: (t, y) for i, t, y, _ in pred.trace}


def refused(fn):
    try:
        return {"refused": False, "returned": fn()}
    except ValueError as error:
        return {"refused": True, "error": str(error)}


out = {}
boundary, sealed, pred = fixture()
truth = observe(pred)
_, _, foreign = fixture("SYNTHETIC-other-clip", 10)
out["F1_wrong_clip_and_training"] = refused(lambda: s.score(boundary, sealed, foreign, foreign.sha256,
                                                            lambda: observe(foreign)))
_, _, wrong_training = fixture(shift=10)
out["F1_wrong_training_same_clip"] = refused(lambda: s.score(boundary, sealed, wrong_training,
                                                             wrong_training.sha256, lambda: observe(wrong_training)))
short = replace(pred, trace=pred.trace[:1], sha256=b._sha([pred.kind, pred.model, pred.trace[:1]]))
out["F1_precommitted_subset"] = refused(lambda: s.score(boundary, sealed, short, short.sha256, lambda: truth))
forged = replace(pred, suffix_identity_sha256="0" * 64)
out["F1_overlay_forged_suffix_hash_build"] = refused(lambda: o.build(boundary, [forged], dict(sealed), "synthetic"))
doc = o.build(boundary, [pred], dict(sealed), "synthetic")
doc["traces"][0]["suffix_identity_sha256"] = "0" * 64
out["F1_overlay_forged_suffix_hash_validate"] = refused(
    lambda: o.validate(doc, boundary.clip_id, boundary.source_sha256, dict(sealed)) and "accepted")

full = s.score(boundary, sealed, pred, pred.sha256, lambda: truth)
g = s.gate({c: full for c in s.CATEGORIES})
out["F2_one_synthetic_projectile_aliased_x3"] = {"refused": g["status"] == "NOT_MET", "gate": g}

nan_rows = {i: (float("nan"), y) for i, (_, y) in truth.items()}
out["F4_nan_pts"] = refused(lambda: s.score(boundary, sealed, pred, pred.sha256, lambda: nan_rows))
inf_rows = {i: (t, float("inf")) for i, (t, _) in truth.items()}
out["F4_inf_y"] = refused(lambda: s.score(boundary, sealed, pred, pred.sha256, lambda: inf_rows))
g = s.gate({"projectile": full, "bounce": full, "pendulum": {"scored": True, "normalized_rms": float("nan")}})
out["F4_nan_category_metric"] = {"refused": g["status"] == "NOT_MET" and "pendulum" in g["shortfall"], "gate": g}

record, suffix, _ = p.st03_record(ROOT)
real_boundary, real_sealed = b.split(record, suffix)
real_pred = p.projectile(real_boundary, real_sealed)
raw = json.loads((ROOT / s.ST03_TRACK).read_text(encoding="utf-8"))
raw["record"]["tracking"]["object_id"] = 999
obs, note = s.st03_observations(json.dumps(raw), o.st03_frame_map(ROOT), record["height_px"])
r = s.score(real_boundary, real_sealed, real_pred, real_pred.sha256, lambda: obs, "image-derived")
out["F3_wrong_record_object"] = {"refused": obs == {} and not r["scored"] and r["normalized_rms"] is None,
                                 "validation": note, "scored_frames": r["scored_frames"]}

assert all(v["refused"] for v in out.values()), [k for k, v in out.items() if not v["refused"]]
print(json.dumps(out, indent=2, default=str))
