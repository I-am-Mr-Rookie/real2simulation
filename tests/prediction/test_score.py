"""S12e: Gate RS scoring verifies seal + committed sha BEFORE reading suffix observations."""
import dataclasses
import json
import unittest

from Build.real2sim import boundary as b
from Build.real2sim import overlay as o
from Build.real2sim import predict as pr
from Build.real2sim import score as s
from Build.real2sim.params import ROOT


def ids_only(clip="SYNTHETIC", shift=0):
    # SYNTHETIC: y_px = 100 + 20 i + 3 i^2 on frames 0..9 (H=1000); suffix identities 10..14 only (untracked seal).
    frames = [{"frame_index": i, "pts_s": i / 30, "y_px": 100 + 20 * i + 3 * i * i + shift} for i in range(10)]
    boundary, sealed = b.split({"clip_id": clip, "source_sha256": "a" * 64, "last_training_frame": 9,
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
        obs, note = s.st03_observations(json.dumps(raw), o.st03_frame_map(ROOT), record["height_px"])
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


if __name__ == "__main__":
    unittest.main()
