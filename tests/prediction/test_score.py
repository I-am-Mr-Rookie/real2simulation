"""S12e: Gate RS scoring verifies seal + committed sha BEFORE reading suffix observations."""
import dataclasses
import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Build.real2sim import boundary as b
from Build.real2sim import overlay as o
from Build.real2sim import predict as pr
from Build.real2sim import score as s
from Build.real2sim.params import ROOT


def ids_only(clip="SYNTHETIC", shift=0, sha="a" * 64):
    # SYNTHETIC: y_px = 100 + 20 i + 3 i^2 on frames 0..9 (H=1000); suffix identities 10..14 only (untracked seal).
    frames = [{"frame_index": i, "pts_s": i / 30, "y_px": 100 + 20 * i + 3 * i * i + shift} for i in range(10)]
    boundary, sealed = b.split({"clip_id": clip, "source_sha256": sha, "last_training_frame": 9,
                                "height_px": 1000, "frames": frames}, [(i, i / 30) for i in range(10, 15)])
    return boundary, sealed, pr.projectile(boundary, sealed)


REAL = {"P1": "PJ03", "B1": "BN01", "D1": "PD02"}  # approved licensed public clips (clips.csv + APPROVAL.md)
SHA = {f["clip_id"]: f["sha256"] for f in json.loads((ROOT / s.REGISTRY).read_text(encoding="utf-8"))["files"]
       if f.get("clip_id")}


def eligible(kind, clip, rms=0.01):
    """Shape of a real image-derived clip score (values illustrative, used only for gate() arithmetic)."""
    clip = REAL[clip]
    return {"clip_id": clip, "source_sha256": SHA[clip], "kind": kind, "prediction_sha256": clip * 16,
            "prediction_commitment": "prediction/v2", "sealed_frames": 10, "scored_frames": 9, "coverage": 0.9,
            "normalized_rms": rms, "scored": True, "provenance": "image-derived",
            "input_receipt": s.public_receipt(clip, SHA[clip], kind)}


class ScoreTests(unittest.TestCase):
    def setUp(self):
        # receipt/arithmetic layer only; the tracking-evidence re-check is exercised unpatched in TrackingEvidenceTests.
        patcher = mock.patch.object(s, "_tracking_ok", return_value=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_exact_truth_scores_zero_and_loader_runs_after_checks(self):
        boundary, sealed, pred = ids_only()
        calls = []
        truth = {i: (t, (100 + 20 * i + 3 * i * i) / 1000) for i, t in sealed}
        r = s.score(boundary, sealed, pred, pred.sha256, lambda: calls.append(1) or truth)
        self.assertEqual(calls, [1])
        self.assertLess(r["normalized_rms"], 1e-9)
        self.assertEqual((r["coverage"], r["scored"], r["gate_m"]), (1.0, True, "NOT_MET"))

    def test_tampered_seal_or_uncommitted_prediction_never_reads_suffix(self):
        boundary, sealed, pred = ids_only()
        never = lambda: self.fail("suffix read before verification")  # noqa: E731
        with self.assertRaises(ValueError):
            s.score(boundary, sealed[:-1], pred, pred.sha256, never)
        with self.assertRaises(ValueError):
            s.score(boundary, sealed, pred, "0" * 64, never)
        with self.assertRaises(ValueError):  # trace edited after hashing
            s.score(boundary, sealed, dataclasses.replace(pred, trace=pred.trace[:-1]), pred.sha256, never)

    def test_pts_mismatch_low_coverage_and_rms(self):
        boundary, sealed, pred = ids_only()
        with self.assertRaises(ValueError):
            s.score(boundary, sealed, pred, pred.sha256, lambda: {10: (10 / 30 + 0.01, 0.0)})
        rows = {i: (t, y + 0.1) for i, t, y, _ in pred.trace}  # constant 0.1 H offset
        r = s.score(boundary, sealed, pred, pred.sha256, lambda: rows)
        self.assertAlmostEqual(r["normalized_rms"], 0.1)
        r = s.score(boundary, sealed, pred, pred.sha256, lambda: {10: rows[10], 11: rows[11]})
        self.assertEqual((r["coverage"], r["scored"]), (0.4, False))

    def test_gate_needs_every_category(self):
        ok = eligible("projectile", "P1")
        self.assertEqual(s.gate({"projectile": ok})["status"], "NOT_MET")
        self.assertEqual(s.gate({"projectile": ok})["shortfall"], ["bounce", "pendulum"])
        g = s.gate({"projectile": ok, "bounce": eligible("bounce", "B1"), "pendulum": eligible("pendulum", "D1", 0.5)})
        self.assertEqual((g["status"], g["median"]), ("MET", 0.01))

    # --- R-RS regressions (evidence/reviews/R-RS/reproductions.json) ---
    def test_f1_wrong_clip_wrong_training_and_precommitted_subset_refused_before_read(self):
        boundary, sealed, _ = ids_only()
        never = lambda: self.fail("suffix read before binding check")  # noqa: E731
        for other in (ids_only(clip="SYNTHETIC-other")[2], ids_only(shift=5)[2]):  # wrong clip / wrong training
            with self.assertRaisesRegex(ValueError, "different clip, source, training"):
                s.score(boundary, sealed, other, other.sha256, never)
        _, _, pred = ids_only()
        short = pr._seal(pred.kind, boundary, pred.model, pred.trace[:1])  # precommitted one-row trace
        with self.assertRaisesRegex(ValueError, "complete sealed suffix"):
            s.score(boundary, sealed, short, short.sha256, never)

    def test_f1_overlay_forged_suffix_hash_refused(self):
        boundary, sealed, pred = ids_only()
        forged = dataclasses.replace(pred, suffix_identity_sha256="0" * 64)
        with self.assertRaises(ValueError):
            o.build(boundary, [forged], dict(sealed), "synthetic")
        doc = o.build(boundary, [pred], dict(sealed), "synthetic")
        doc["traces"][0]["suffix_identity_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "after commitment"):  # seal hash is inside the v2 commitment
            o.validate(doc, boundary.clip_id, boundary.source_sha256, dict(sealed))

    # --- R-RS recheck regressions (evidence/reviews/R-RS/RECHECK.md F1-R, F2-R) ---
    def test_f1r_metadata_only_relabel_refused_before_read(self):
        boundary, sealed, target = ids_only(clip="TARGET")
        never = lambda: self.fail("suffix read before binding check")  # noqa: E731
        for foreign in (ids_only(clip="FOREIGN")[2], ids_only(clip="TARGET", shift=5)[2]):  # foreign clip / training
            relabel = dataclasses.replace(foreign, clip_id=target.clip_id, training_sha256=target.training_sha256)
            with self.assertRaisesRegex(ValueError, "changed after hashing"):
                pr.check(relabel)
            with self.assertRaisesRegex(ValueError, "changed after hashing"):
                s.score(boundary, sealed, relabel, relabel.sha256, never)
            with self.assertRaises(ValueError):
                o.build(boundary, [relabel], dict(sealed), "synthetic")
            fb, fs, _ = ids_only(clip=foreign.clip_id, shift=5 if foreign.clip_id == "TARGET" else 0)
            doc = o.build(fb, [foreign], dict(fs), "synthetic")
            doc["clip_id"] = doc["traces"][0]["clip_id"] = target.clip_id
            doc["traces"][0]["training_sha256"] = target.training_sha256
            with self.assertRaisesRegex(ValueError, "after commitment"):
                o.validate(doc, target.clip_id, boundary.source_sha256, dict(sealed))
        v1 = dataclasses.replace(target, commitment=pr.LEGACY)
        v1 = dataclasses.replace(v1, sha256=pr.commitment_sha256(v1))
        pr.check(v1)  # legacy stays audit-readable ...
        with self.assertRaisesRegex(ValueError, "legacy prediction/v1"):  # ... never newly eligible
            s.score(boundary, sealed, v1, v1.sha256, never)

    def test_f2r_nonpublic_synthetic_fixtures_labelled_image_derived_are_shortfall(self):
        results = {}
        for kind in s.CATEGORIES:
            boundary, sealed, base = ids_only(clip=f"REVIEW-NONPUBLIC-{kind}")
            pred = pr._seal(kind, boundary, f"{kind} fixture", base.trace)  # distinct genuine v2 commitments
            truth = {i: (t, y) for i, t, y, _ in pred.trace}
            r = s.score(boundary, sealed, pred, pred.sha256, lambda: truth, "image-derived")
            self.assertEqual((r["scored"], r["normalized_rms"], r["input_receipt"]), (True, 0.0, None))
            self.assertIn("clips.csv", r["ineligible_reason"])
            results[kind] = r
        g = s.gate(results)
        self.assertEqual((g["status"], g["shortfall"], g["median"]), ("NOT_MET", list(s.CATEGORIES), None))
        # approved clip id with a non-registry source sha also fails closed
        boundary, sealed, pred = ids_only(clip="PJ03")
        r = s.score(boundary, sealed, pred, pred.sha256, lambda: {i: (t, y) for i, t, y, _ in pred.trace})
        self.assertIn("source sha", r["ineligible_reason"])
        self.assertEqual(s.gate({"projectile": r})["shortfall"], list(s.CATEGORIES))
        legacy = eligible("projectile", "P1") | {"prediction_commitment": "prediction/v1"}
        self.assertIn("projectile", s.gate({"projectile": legacy})["shortfall"])

    def test_f2_one_synthetic_projectile_aliased_three_times_is_shortfall(self):
        boundary, sealed, pred = ids_only()
        truth = {i: (t, y) for i, t, y, _ in pred.trace}
        full = s.score(boundary, sealed, pred, pred.sha256, lambda: truth)
        g = s.gate({c: full for c in s.CATEGORIES})
        self.assertEqual((g["status"], g["shortfall"]), ("NOT_MET", list(s.CATEGORIES)))
        real = eligible("projectile", "P1")
        g = s.gate({"projectile": real, "bounce": real | {"kind": "bounce"}, "pendulum": real | {"kind": "pendulum"}})
        self.assertEqual(g["shortfall"], ["bounce", "pendulum"])  # same clip cannot stand in for other categories
        forged = eligible("bounce", "B1") | {"coverage": 0.9, "scored_frames": 1}  # coverage recomputed, not trusted
        self.assertIsNone(s.gate({"bounce": forged})["per_category_normalized_rms"]["bounce"])

    def test_f3_wrong_record_object_is_unscored_shortfall(self):
        record, suffix, _ = pr.st03_record(ROOT)
        boundary, sealed = b.split(record, suffix)
        pred = pr.projectile(boundary, sealed)
        raw = json.loads((ROOT / s.ST03_TRACK).read_text(encoding="utf-8"))
        raw["record"]["tracking"]["object_id"] = 999
        obs, note = s.st03_observations(json.dumps(raw), o.st03_frame_map(ROOT), "ST03", record["source_sha256"])
        self.assertEqual(obs, {})
        self.assertIn("rejected (unscored)", note)
        r = s.score(boundary, sealed, pred, pred.sha256, lambda: obs, "image-derived")
        self.assertEqual((r["scored_frames"], r["scored"], r["normalized_rms"]), (0, False, None))

    def test_f4_nonfinite_observations_and_metrics_rejected(self):
        boundary, sealed, pred = ids_only()
        for bad in (float("nan"), float("inf")):
            rows = {i: (bad, y) for i, t, y, _ in pred.trace}
            with self.assertRaisesRegex(ValueError, "finite"):
                s.score(boundary, sealed, pred, pred.sha256, lambda: rows)
            rows = {i: (t, bad) for i, t, y, _ in pred.trace}
            with self.assertRaisesRegex(ValueError, "finite"):
                s.score(boundary, sealed, pred, pred.sha256, lambda: rows)
            g = s.gate({"projectile": eligible("projectile", "P1", 0.0), "bounce": eligible("bounce", "B1", 0.0),
                        "pendulum": eligible("pendulum", "D1", bad)})
            self.assertEqual((g["status"], g["shortfall"]), ("NOT_MET", ["pendulum"]))
        g = s.gate({"projectile": eligible("projectile", "P1", -0.1)})
        self.assertIn("projectile", g["shortfall"])


def st03():
    record, suffix, _ = pr.st03_record(ROOT)
    boundary, sealed = b.split(record, suffix)
    return boundary, sealed, pr.projectile(boundary, sealed)


class TrackingEvidenceTests(unittest.TestCase):
    """R-RS F2-R2 / F2-A / F2-L regressions (no patching of the eligibility path)."""

    def test_f2r2_known_public_id_true_sha_synthetic_observations_are_shortfall(self):
        for prov in ("synthetic", "image-derived"):
            results = {}
            for kind, clip in (("projectile", "PJ03"), ("bounce", "BN01"), ("pendulum", "PD02")):
                boundary, sealed, base = ids_only(clip=clip, sha=SHA[clip])
                pred = pr._seal(kind, boundary, f"{kind} fixture", base.trace)
                truth = {i: (t, y) for i, t, y, _ in pred.trace}
                r = s.score(boundary, sealed, pred, pred.sha256, lambda: truth, prov)
                self.assertIsNotNone(r["input_receipt"])  # identity is genuinely public...
                self.assertIn("tracking-evidence", r["ineligible_reason"])  # ...but observations are not tracked
                self.assertEqual((r["scored"], r["normalized_rms"], r["tracking_evidence"]), (True, 0.0, None))
                results[kind] = r
            g = s.gate(results)
            self.assertEqual((g["status"], g["median"], g["shortfall"]), ("NOT_MET", None, list(s.CATEGORIES)))

    def test_f2r2_real_evidence_rechecked_and_not_transplantable(self):
        boundary, sealed, pred = st03()
        load = s.Tracked(boundary, s.ST03_TRACK, o.st03_frame_map(ROOT))
        real = s.score(boundary, sealed, pred, pred.sha256, load, "image-derived")
        self.assertEqual((real["scored_frames"], real["tracking_evidence"]["prefix_frames"]), (7, 19))
        self.assertTrue(s._tracking_ok(real, ROOT))
        self.assertFalse(s._tracking_ok(real | {"provenance": "synthetic"}, ROOT))  # explicit synthetic never eligible
        self.assertFalse(s._tracking_ok(real | {"observations_sha256": "0" * 64}, ROOT))  # scored obs bound to artifact
        self.assertFalse(s._tracking_ok(real | {"clip_id": "PJ03", "source_sha256": SHA["PJ03"]}, ROOT))
        bad = dict(real["tracking_evidence"], sha256="0" * 64)
        self.assertFalse(s._tracking_ok(real | {"tracking_evidence": bad}, ROOT))
        outside = dict(real["tracking_evidence"], path="../outside.json")
        self.assertFalse(s._eligible("projectile", real | {"tracking_evidence": outside}))
        shifted = tuple((i, p, y + 0.01) for i, p, y in boundary.training)  # prefix not from this artifact
        with self.assertRaisesRegex(ValueError, "prefix custody"):
            s.Tracked(dataclasses.replace(boundary, training=shifted), s.ST03_TRACK, o.st03_frame_map(ROOT))()
        self.assertEqual(real["tracking_evidence"]["custody"]["entry"], "ST03-f58-83-S12e-orch45")  # F2-R3 positive
        unregistered = dict(real["tracking_evidence"], custody=None)
        self.assertFalse(s._tracking_ok(real | {"tracking_evidence": unregistered}, ROOT))

    def test_f2r3_reviewer_forged_native_tracked_end_to_end_is_shortfall(self):
        """R-RS recheck3 F2-R3, unpatched: hand-authored tracker JSON via native Tracked never reaches MET."""
        here = ROOT / "evidence/reviews/R-RS/recheck3"
        spec = importlib.util.spec_from_file_location("rrs_recheck3", here / "review.py")
        rv3 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rv3)
        forged = {}
        for kind, clip in (("projectile", "PJ03"), ("bounce", "BN01"), ("pendulum", "PD02")):
            kb, ki, kp = rv3.rv.fixture(clip, rv3.rv.SHA[clip])
            kp = rv3.rv.kind_prediction(kind, kb, ki, kp)
            rel = (here / (kind + "-SYNTHETIC-track.json")).relative_to(ROOT).as_posix()
            self.assertEqual(json.loads((ROOT / rel).read_text(encoding="utf-8")), rv3.tracker(kb, kp))
            loader = s.Tracked(kb, rel, dict(list((i, t) for i, t, _ in kb.training) + list(ki)))
            forged[kind] = s.score(kb, ki, kp, kp.sha256, loader, "image-derived")
            self.assertTrue(forged[kind]["scored"] and forged[kind]["input_receipt"])  # internally consistent...
            self.assertEqual(forged[kind]["tracking_evidence"]["validate"], "validate_segment OK")
            self.assertIn("no accepted tracking custody", forged[kind]["ineligible_reason"])  # ...but unknown
            self.assertFalse(s._tracking_ok(forged[kind], ROOT))
        g = s.gate(forged)
        self.assertEqual((g["status"], g["median"], g["shortfall"]), ("NOT_MET", None, list(s.CATEGORIES)))

    def test_f2c_tracked_bound_to_other_boundary_refused_and_not_eligible(self):
        """R-RS recheck3 F2-C with the genuine ST03 artifact: loader/boundary mismatch refuses before any read."""
        record, suffix, _ = pr.st03_record(ROOT)
        real_bd, _ = b.split(record, suffix)
        shifted = copy.deepcopy(record)
        for frame in shifted["frames"]:
            frame["y_px"] += shifted["height_px"] * 0.01
        shifted_bd, shifted_seal = b.split(shifted, suffix)
        shifted_pred = pr.projectile(shifted_bd, shifted_seal)
        wrong = s.Tracked(real_bd, s.ST03_TRACK, o.st03_frame_map(ROOT))
        with self.assertRaisesRegex(ValueError, "different boundary"):
            s.score(shifted_bd, shifted_seal, shifted_pred, shifted_pred.sha256, wrong, "image-derived")
        self.assertIsNone(wrong.evidence)  # refused before the artifact/suffix was read
        boundary, sealed, pred = st03()
        real = s.score(boundary, sealed, pred, pred.sha256, s.Tracked(boundary, s.ST03_TRACK, o.st03_frame_map(ROOT)),
                       "image-derived")
        transplant = real | {"training_sha256": shifted_bd.training_sha256}  # carried seal != scored prediction's
        self.assertFalse(s._tracking_ok(transplant, ROOT))
        reseal = dict(real["tracking_evidence"], seal=s.seal_identity(shifted_bd))  # custody binds the accepted seal
        self.assertFalse(s._tracking_ok(transplant | {"tracking_evidence": reseal}, ROOT))

    def test_f2r2_wrong_source_tracker_payload_and_mutated_real_record_refused(self):
        boundary, sealed, pred = st03()
        raw = json.loads((ROOT / s.ST03_TRACK).read_text(encoding="utf-8"))
        fmap = o.st03_frame_map(ROOT)
        for field, value in (("clip_id", "PJ03"), ("source_sha256", SHA["PJ03"]), ("clip_id", None)):
            mutated = json.loads(json.dumps(raw))
            mutated["record"][field] = value
            with self.assertRaisesRegex(ValueError, "tracker identity"):
                s.st03_observations(json.dumps(mutated), fmap, "ST03", boundary.source_sha256)
            with tempfile.TemporaryDirectory() as tmp:
                Path(tmp, "track.json").write_text(json.dumps(mutated), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "tracker identity"):
                    s.score(boundary, sealed, pred, pred.sha256, s.Tracked(boundary, "track.json", fmap, Path(tmp)),
                            "image-derived")
        self.assertEqual(s.gate({})["shortfall"], list(s.CATEGORIES))  # refused score => no result => shortfall
        mutated = json.loads(json.dumps(raw))
        mutated["frame_sha256"] = mutated["frame_sha256"][:-1]
        with self.assertRaisesRegex(ValueError, "frame_sha256"):
            s.st03_observations(json.dumps(mutated), fmap, "ST03", boundary.source_sha256)

    def test_f2a_only_positive_scoped_grant_in_authoritative_block(self):
        text = (ROOT / s.APPROVAL).read_text(encoding="utf-8")
        self.assertTrue(s.approved("PJ03", text))
        self.assertFalse(s.approved("XX99", text))
        denied = {"negated_use": text.replace("**Use:** local", "**Use:** NOT approved for local"),
                  "unrelated_use_mention": "**Approved IDs:** PJ03.\n**Use:** DENIED.\n"
                                           "Prior request: local scene/tracking pipeline work\n",
                  "only_then_denied": text.replace("work ONLY", "work ONLY - DENIED"),
                  "two_blocks": text + "\n**Approved IDs:** PJ03.\n**Use:** local scene/tracking pipeline work ONLY\n",
                  "unrecognized": "**Approved IDs:** PJ03.\n**Use:** demo publication\n"}
        for name, doc in denied.items():
            self.assertFalse(s.approved("PJ03", doc), name)
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_inputs(Path(tmp))
            (root / s.APPROVAL).write_text(denied["negated_use"], encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "owner-approved"):
                s.public_receipt("PJ03", SHA["PJ03"], "projectile", root)

    def test_f2l_finite_licence_allowlist(self):
        for good in ("Pexels", "Pexels License", "PD-USGov-NASA", "CC-BY-SA-4.0", "CC-BY-3.0", "CC0"):
            self.assertIn(good.lower(), s.LICENCES)
        for bad in ("pd-nc", "pd-not-public", "CC-BY-999.99", "CC-BY-", "CC-BY-NC-4.0", "CC-BY-ND-4.0",
                    "CC-BY-NC-SA-4.0", "pd-", "cc-by-sa-4.0.1"):
            self.assertNotIn(bad.lower(), s.LICENCES, bad)
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_inputs(Path(tmp))
            csv_path = root / "clips.csv"
            original = csv_path.read_text(encoding="utf-8")
            row = next(line for line in original.splitlines() if line.startswith("PJ03,"))
            licence = next(x for x in row.split(",") if x.strip().lower() in s.LICENCES)
            for bad in ("pd-nc", "pd-not-public", "CC-BY-999.99", "CC-BY-"):
                csv_path.write_text(original.replace(row, row.replace(licence, bad, 1)), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "licence"):
                    s.public_receipt("PJ03", SHA["PJ03"], "projectile", root)


def copy_inputs(root):
    for rel in ("clips.csv", s.APPROVAL, s.REGISTRY):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, root / rel)
    return root


if __name__ == "__main__":
    unittest.main()
