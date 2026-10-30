"""Offline review probes; SYNTHETIC attacks never constitute measured scene evidence.

Run: python -B evidence/reviews/R-RS/recheck4/review.py
Writes only beside this file; no product monkeypatches or dependencies.
"""
import copy
import csv
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location("recheck3", HERE.parent / "recheck3/review.py")
r3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r3)
s, b, p, o, rv = r3.s, r3.b, r3.p, r3.o, r3.rv


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    return {path.relative_to(ROOT).as_posix(): digest(path)
            for folder in ("Build/real2sim", "Build/pipeline", "tests/prediction", "evidence/S12")
            for path in sorted((ROOT / folder).rglob("*"))
            if path.is_file() and "__pycache__" not in str(path)}


def main():
    before = fingerprint()
    out = {"base": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "warning": "Synthetic offline attacks, not physical or Gate RS success"}
    # Execute the historical script unchanged, redirecting ONLY its review-output directory.
    rerun = HERE / "rerun-recheck3"
    rerun.mkdir(exist_ok=True)
    r3.HERE = rerun
    try:
        r3.main()
    except AssertionError:
        trace = traceback.format_exc()
        assert 's._tracking_ok(forged[kind], ROOT)' in trace, trace
        (HERE / "recheck3-rerun.txt").write_text(trace, encoding="utf-8")
        out["recheck3_rerun"] = "Expected historical _tracking_ok assertion now fails at line 99: forged trackers no longer eligible"
    else:
        raise AssertionError("historical exploit unexpectedly succeeded")

    bd, ids, pred = rv.fixture()
    out["F1_before_suffix_read"] = {}
    for field, value in {"clip_id": "OTHER", "source_sha256": "b" * 64,
                         "training_sha256": "c" * 64, "suffix_identity_sha256": "d" * 64,
                         "suffix_count": 4, "kind": "bounce", "model": pred.model + " edit",
                         "trace": pred.trace[:-1], "commitment": p.LEGACY}.items():
        out["F1_before_suffix_read"][field] = rv.before_read(bd, ids, replace(pred, **{field: value}))
    subset = replace(pred, trace=pred.trace[:1])
    subset = replace(subset, sha256=p.commitment_sha256(subset))
    out["F1_before_suffix_read"]["self_consistent_subset"] = rv.before_read(bd, ids, subset)

    forged = {}
    for kind, clip in zip(s.CATEGORIES, ("PJ03", "BN01", "PD02")):
        kb, ki, kp = rv.fixture(clip, rv.SHA[clip])
        kp = rv.kind_prediction(kind, kb, ki, kp)
        artifact = rerun / (kind + "-SYNTHETIC-track.json")
        shutil.copyfile(HERE.parent / "recheck3" / artifact.name, artifact)
        assert json.loads(artifact.read_text()) == r3.tracker(kb, kp)
        pts = dict([(i, t) for i, t, _ in kb.training] + list(ki))
        loader = s.Tracked(kb, artifact.relative_to(ROOT).as_posix(), pts)
        result = s.score(kb, ki, kp, kp.sha256, loader, "image-derived")
        assert result["tracking_evidence"]["validate"] == "validate_segment OK"
        assert result["scored"] and "no accepted tracking custody" in result["ineligible_reason"]
        assert not s._eligible(kind, result)
        forged[kind] = result
    out["F2_R3_native_forgery"] = {"scores": forged, "gate": s.gate(forged)}
    assert s.gate(forged)["shortfall"] == list(s.CATEGORIES)

    record, suffix, _ = p.st03_record(ROOT)
    real_bd, real_ids = b.split(record, suffix)
    real_pred = p.projectile(real_bd, real_ids)
    real_map = o.st03_frame_map(ROOT)
    real = s.score(real_bd, real_ids, real_pred, real_pred.sha256,
                   s.Tracked(real_bd, s.ST03_TRACK, real_map), "image-derived")
    saved = rv.read("evidence/S12/gate-rs/gate-rs.json")
    assert all(saved["clips"]["projectile"][k] == v for k, v in real.items())
    assert s.gate({"projectile": real}) == saved["result"]
    assert (real["scored_frames"], real["sealed_frames"], saved["result"]["status"]) == (7, 466, "NOT_MET")
    assert s._tracking_ok(real, ROOT)
    out["actual_gate"] = {"result": saved["result"], "scored_frames": 7, "sealed_frames": 466,
                          "normalized_rms": real["normalized_rms"], "coverage": real["coverage"]}
    shifted = copy.deepcopy(record)
    for frame in shifted["frames"]:
        frame["y_px"] += shifted["height_px"] * .01
    sb, si = b.split(shifted, suffix)
    sp = p.projectile(sb, si)
    loader = s.Tracked(real_bd, s.ST03_TRACK, real_map)
    out["F2_C"] = rv.refusal(lambda: s.score(sb, si, sp, sp.sha256, loader, "image-derived"))
    assert "different boundary" in out["F2_C"] and loader.evidence is None
    transplanted = copy.deepcopy(real)
    transplanted["training_sha256"] = sb.training_sha256
    assert not s._tracking_ok(transplanted, ROOT)
    transplanted["tracking_evidence"]["seal"] = s.seal_identity(sb)
    assert not s._tracking_ok(transplanted, ROOT)

    # All registry tampering is confined to an owned scratch root, not evidence/S12.
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        root = Path(tmp)
        registry = rv.read(s.TRACKING_REGISTRY)
        entry = registry["accepted"][0]
        for rel in (s.TRACKING_REGISTRY, s.ST03_TRACK, entry["presentation_map"], entry["gpu"]["ledger"],
                    "clips.csv", s.APPROVAL, s.REGISTRY):
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, target)
        registry_path = root / s.TRACKING_REGISTRY
        ev = real["tracking_evidence"]

        def write_registry(value):
            registry_path.write_text(json.dumps(value), encoding="utf-8")

        def check_registry(value):
            write_registry(value)
            return s.accepted_tracking(ev["path"], ev["sha256"], ev["seal"], ev["frame_pts"], root)

        original_receipt = check_registry(registry)
        cases = {}
        for label, field, value in (("artifact_digest", "artifact_sha256", "0" * 64),
                                    ("artifact_path", "artifact", "other.json"),
                                    ("presentation_digest", "presentation_map_sha256", "0" * 64),
                                    ("range_start", "frame_range", [59, 83]),
                                    ("range_end", "frame_range", [58, 84]),
                                    ("reversed_range", "frame_range", [83, 58]),
                                    ("seal", "seal", s.seal_identity(sb))):
            changed = copy.deepcopy(registry)
            changed["accepted"][0][field] = value
            cases[label] = rv.refusal(lambda: check_registry(changed))
        duplicate = copy.deepcopy(registry)
        duplicate["accepted"].append(copy.deepcopy(entry))
        cases["duplicate"] = rv.refusal(lambda: check_registry(duplicate))
        cases["empty_registry"] = rv.refusal(lambda: check_registry({"accepted": []}))
        write_registry(registry)
        bad_pts = copy.deepcopy(ev["frame_pts"]); bad_pts[0][1] += .01
        cases["caller_pts"] = rv.refusal(lambda: s.accepted_tracking(ev["path"], ev["sha256"], ev["seal"], bad_pts, root))
        pmap = root / entry["presentation_map"]
        original_map = pmap.read_bytes()
        pmap.write_bytes(original_map + b"\n")
        cases["map_bytes"] = rv.refusal(lambda: check_registry(registry))
        pmap.write_bytes(original_map)

        # A changed registry invalidates carried receipts. Fresh readers trust its author.
        changed = copy.deepcopy(registry); changed["note"] = "review-only registry edit"
        write_registry(changed)
        assert not s._tracking_ok(real, root)
        fresh = copy.deepcopy(real)
        fresh["tracking_evidence"]["custody"] = check_registry(changed)
        assert s._tracking_ok(fresh, root)
        write_registry(registry)
        assert not s._tracking_ok(fresh, root)
        # Byte-identical historical registry replay is not prevented or required to be.
        raw = (ROOT / s.TRACKING_REGISTRY).read_bytes()
        registry_path.write_bytes(raw)
        assert s._tracking_ok(real, root)
        cases["registry_edit_old_receipt"] = "rejected"
        cases["registry_edit_fresh_receipt"] = "accepted: registry writer is trusted"
        cases["exact_registry_replay"] = "accepted: no monotonic revision/revocation store"

        # Runtime does not attest ledger/app/cost/run references: test and report explicitly.
        forged_meta = copy.deepcopy(registry)
        forged_meta["accepted"][0]["gpu"] = {"ledger": "missing.jsonl", "app_id": "ap-REVIEW-FAKE"}
        forged_meta["accepted"][0]["accepted_runs"] = ["missing-report.md"]
        check_registry(forged_meta)
        cases["invented_ledger_app_run_metadata"] = "accepted by custody reader; controller-only assertions"
        ledger = [json.loads(line) for line in (ROOT / entry["gpu"]["ledger"]).read_text().splitlines() if line.strip()]
        matching = [row for row in ledger if row.get("app_id") == entry["gpu"]["app_id"]]
        assert len(matching) == 1 and matching[0]["billed_usd"] == entry["gpu"]["billed_usd"]
        assert "26 frames" in matching[0]["result"]
        out["registry_trust"] = {"cases": cases, "actual_entry_ledger_match": matching,
            "ledger_binds_artifact_sha": any(entry["artifact_sha256"] in json.dumps(row) for row in matching),
            "authority": "Any repository/file writer can edit registry; controller review is the admission boundary, not JSON parser or git commit verification"}

        # Deliberately cross the TRUSTED registry-writer boundary in scratch only.
        # This proves admission is a controller responsibility, not an independent GPU attestation.
        injected = {"accepted": []}
        admitted = {}
        fixtures = {}
        for kind, clip in zip(s.CATEGORIES, ("PJ03", "BN01", "PD02")):
            kb, ki, kp = rv.fixture(clip, rv.SHA[clip])
            kp = rv.kind_prediction(kind, kb, ki, kp)
            rel = "attacker/" + kind + "-SYNTHETIC.json"
            path = root / rel; path.parent.mkdir(exist_ok=True)
            shutil.copyfile(rerun / (kind + "-SYNTHETIC-track.json"), path)
            pts = dict([(i, t) for i, t, _ in kb.training] + list(ki))
            map_rel = "attacker/" + kind + "-map.json"
            (root / map_rel).write_text(json.dumps({"frames": [
                {"source_frame_index": i, "pts_time": t} for i, t in pts.items()]}), encoding="utf-8")
            injected["accepted"].append({"id": "REVIEW-SYNTHETIC-" + kind,
                "artifact": rel, "artifact_sha256": digest(path), "seal": s.seal_identity(kb),
                "presentation_map": map_rel, "presentation_map_sha256": digest(root / map_rel),
                "frame_range": [0, 14], "gpu": {"app_id": "ap-FAKE", "ledger": "missing"}})
            fixtures[kind] = (kb, ki, kp, rel, pts)
        write_registry(injected)
        for kind, (kb, ki, kp, rel, pts) in fixtures.items():
            admitted[kind] = s.score(kb, ki, kp, kp.sha256, s.Tracked(kb, rel, pts, root), "image-derived")
        injected_gate = s.gate(admitted, root)
        assert injected_gate["status"] == "MET"
        out["registry_trust"]["trusted_registry_writer_can_admit_synthetic"] = {
            "gate": injected_gate, "committed": False, "media_gpu_used": False,
            "meaning": "Trusted registry modified in owned scratch; NOT a bypass available to an ordinary tracker caller"}

        original_approval = (root / s.APPROVAL).read_text(encoding="utf-8")
        out["F2_A"] = {}
        for denial in ("not approved", "denied", "revoked", "withdrawn", "never", "except"):
            text = original_approval.replace(s.APPROVED_USE + " ONLY", s.APPROVED_USE + " ONLY " + denial)
            (root / s.APPROVAL).write_text(text, encoding="utf-8")
            out["F2_A"][denial] = rv.refusal(lambda: s.public_receipt("PJ03", rv.SHA["PJ03"], "projectile", root))
        (root / s.APPROVAL).write_text(original_approval, encoding="utf-8")
        assert s.public_receipt("PJ03", rv.SHA["PJ03"], "projectile", root)
        rows = list(csv.DictReader((root / "clips.csv").open(encoding="utf-8", newline="")))
        out["F2_L"] = {}
        for licence in ("CC-BY-NC-4.0", "CC-BY-ND-4.0", "pd-nc", "pd-not-public", "CC-BY-999.99", "CC-BY-.", "CC-BY-", "CC-BY-SA-9.0"):
            edited = copy.deepcopy(rows)
            next(row for row in edited if row["clip_id"] == "PJ03")["licence"] = licence
            with (root / "clips.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(edited[0])); writer.writeheader(); writer.writerows(edited)
            out["F2_L"][licence] = rv.refusal(lambda: s.public_receipt("PJ03", rv.SHA["PJ03"], "projectile", root))

    assert fingerprint() == before, "Protected source/test/evidence changed"
    save("source-hashes.json", before)
    save("results.json", out)
    print("PASS: F2-R3/F2-C/F1/F2-A/F2-L; registry tamper/replay probes; actual RS NOT_MET 7/466; protected hashes unchanged")


if __name__ == "__main__":
    main()
