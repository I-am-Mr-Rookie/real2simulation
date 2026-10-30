"""S12e-fix3 replay: R-RS recheck2 defect probes, inverted (each must now refuse / shortfall). Offline, no GPU."""
import copy
import csv
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from Build.real2sim import boundary as b, predict as p, score as s, overlay as o  # noqa: E402
sys.path.insert(0, str(ROOT / "evidence/reviews/R-RS/recheck2"))
import review as rv  # noqa: E402  reviewer's own fixture/kind_prediction/observe helpers, read-only

out, clips = {}, {"projectile": "PJ03", "bounce": "BN01", "pendulum": "PD02"}
known = {}
for kind, clip in clips.items():
    kb, ki, kp = rv.fixture(clip, rv.SHA[clip])
    kp = rv.kind_prediction(kind, kb, ki, kp)
    known[kind] = s.score(kb, ki, kp, kp.sha256, lambda kp=kp: rv.observe(kp), "synthetic")
    assert known[kind]["input_receipt"] == s.public_receipt(clip, rv.SHA[clip], kind)
for label, results in (("known_public_identity_synthetic_observations", known),
                       ("known_public_identity_false_image_label",
                        {k: r | {"provenance": "image-derived"} for k, r in known.items()})):
    g = s.gate(results)
    assert g["status"] == "NOT_MET" and g["median"] is None and g["shortfall"] == list(s.CATEGORIES), g
    out[label] = {"gate": g, "ineligible": {k: r["ineligible_reason"] for k, r in results.items()}}

record, suffix, _ = p.st03_record(ROOT)
bd, ids = b.split(record, suffix)
pred = p.projectile(bd, ids)
raw, fmap = rv.read(s.ST03_TRACK), o.st03_frame_map(ROOT)
out["tracker_identity_probes"] = {}
for label, field, value in (("wrong_clip", "clip_id", "NOT-ST03"), ("wrong_source", "source_sha256", "f" * 64),
                            ("other_public_clip", "clip_id", "PJ03")):
    mutated = copy.deepcopy(raw)
    mutated["record"][field] = value
    out["tracker_identity_probes"][label] = rv.refusal(
        lambda m=mutated: s.st03_observations(json.dumps(m), fmap, "ST03", bd.source_sha256))
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        Path(tmp, "t.json").write_text(json.dumps(mutated), encoding="utf-8")
        out["tracker_identity_probes"][label + "_score"] = rv.refusal(lambda tmp=tmp: s.score(
            bd, ids, pred, pred.sha256, s.Tracked(bd, "t.json", fmap, Path(tmp)), "image-derived"))
out["tracker_identity_probes"]["legacy_3arg_call"] = rv.refusal(
    lambda: s.st03_observations(json.dumps(raw), fmap, record["height_px"]))

real = s.score(bd, ids, pred, pred.sha256, s.Tracked(bd, s.ST03_TRACK, fmap), "image-derived")
artifact = rv.read("evidence/S12/gate-rs/gate-rs.json")
assert all(artifact["clips"]["projectile"][k] == v for k, v in real.items())
assert s.gate({"projectile": real}) == artifact["result"] and artifact["result"]["status"] == "NOT_MET"
transplant = {k: r | {"tracking_evidence": real["tracking_evidence"], "observations_sha256": real["observations_sha256"]}
              for k, r in known.items()}
assert s.gate(transplant)["shortfall"] == list(s.CATEGORIES)
out["real_evidence"] = {k: real[k] for k in ("normalized_rms", "scored_frames", "sealed_frames", "coverage", "scored")}
out["real_evidence"]["tracking_ok"] = s._tracking_ok(real, ROOT)
out["transplanted_real_evidence_onto_synthetic"] = "shortfall (all categories)"

with tempfile.TemporaryDirectory(dir=HERE) as tmp:
    root = Path(tmp)
    for rel in ("clips.csv", s.APPROVAL, s.REGISTRY):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes((ROOT / rel).read_bytes())
    rows = list(csv.DictReader((ROOT / "clips.csv").open(encoding="utf-8", newline="")))
    out["licence_full_receipt"] = {}
    for licence in ("CC-BY-NC-4.0", "CC-BY-ND-4.0", "pd-nc", "pd-not-public", "CC-BY-999.99", "CC-BY-.", "CC-BY-"):
        modified = copy.deepcopy(rows)
        next(r for r in modified if r["clip_id"] == "PJ03")["licence"] = licence
        with (root / "clips.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(modified[0]))
            w.writeheader()
            w.writerows(modified)
        out["licence_full_receipt"][licence] = rv.refusal(lambda: s.public_receipt("PJ03", rv.SHA["PJ03"], "projectile", root))
    (root / "clips.csv").write_bytes((ROOT / "clips.csv").read_bytes())
    approval = root / s.APPROVAL
    original = approval.read_text(encoding="utf-8")
    out["approval_parser"] = {}
    for label, text in {"negated_use": original.replace("**Use:** local", "**Use:** NOT approved for local"),
                        "unrelated_use_mention": "**Approved IDs:** PJ03.\n**Use:** DENIED.\nPrior request: local scene/tracking pipeline work\n"}.items():
        approval.write_text(text, encoding="utf-8")
        out["approval_parser"][label] = rv.refusal(lambda: s.public_receipt("PJ03", rv.SHA["PJ03"], "projectile", root))
    approval.write_text(original, encoding="utf-8")
    out["approval_parser"]["original_accepted"] = s.public_receipt("PJ03", rv.SHA["PJ03"], "projectile", root)["clip_id"]

labels = []
def walk(n):
    if isinstance(n, dict):
        for k, v in n.items():
            if k == "gate_m":
                assert v == "NOT_MET", v
                labels.append(v)
            walk(v)
    elif isinstance(n, list):
        for v in n:
            walk(v)
paths = sorted((ROOT / "evidence/S12").rglob("*.json"))
for path in paths:
    walk(json.loads(path.read_text(encoding="utf-8")))
actual = rv.read("evidence/S07/S07f/actual-gate-m.json")["gate"]
assert actual["status"] == "NOT_MET_INPUT_READINESS" and actual["physics_evaluation"] == "NOT_RUN"
out["gate_m"] = {"json_files": len(paths), "gate_m_fields": len(labels), "owning_gate": actual["status"]}
(HERE / "replay.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n", encoding="utf-8")
print("replay OK", out["gate_m"])

