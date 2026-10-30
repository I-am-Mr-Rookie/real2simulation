"""S12d: pendulum continuation from the prefix only; overlay contract rejects misalignment and mutation."""
import copy
import json
import unittest
from pathlib import Path

from Build.real2sim import boundary as b
from Build.real2sim import overlay as ov
from Build.real2sim import predict as pr
from contracts.overlay.validate import OverlayError, frame_map_sha256, validate

ROOT = Path(__file__).resolve().parents[2]


def pendulum_case(suffix_shift=0.0):
    record, freq = ov.synthetic_pendulum()
    for f in record["frames"][record["last_training_frame"] + 1:]:
        f["y_px"] += suffix_shift  # held-out values only
    boundary, sealed = b.split(record)
    return record, boundary, pr.pendulum(boundary, sealed, freq)


class PendulumTest(unittest.TestCase):
    def test_continuation_tracks_synthetic_truth_without_reading_suffix(self):
        record, _, a = pendulum_case()
        _, _, c = pendulum_case(suffix_shift=50.0)
        self.assertEqual(a.sha256, c.sha256)  # held-out values cannot influence the prediction
        truth = {f["frame_index"]: f["y_px"] / 480 for f in record["frames"]}
        self.assertEqual([r[0] for r in a.trace], list(range(24, 90)))
        self.assertLess(max(abs(y - truth[i]) for i, _, y, _ in a.trace), 1e-9)  # SYNTHETIC noise-free
        self.assertEqual(a.kind, "pendulum")
        self.assertEqual(a.gate_m, "NOT_MET")

    def test_frequency_record_required(self):
        record, freq = ov.synthetic_pendulum()
        boundary, sealed = b.split(record)
        with self.assertRaises(ValueError):
            pr.pendulum(boundary, sealed, dict(freq, name="restitution"))


class OverlayTest(unittest.TestCase):
    def setUp(self):
        self.record, self.boundary, self.pred = pendulum_case()
        self.fmap = {f["frame_index"]: f["pts_s"] for f in self.record["frames"]}
        self.doc = json.loads(json.dumps(ov.build(self.boundary, [self.pred], self.fmap, "synthetic")))

    def ok(self, doc=None, clip="SYNTHETIC-pendulum-v1", src=None, fmap=None):
        return validate(doc or self.doc, clip, src or self.record["source_sha256"], fmap or self.fmap)

    def test_roundtrip_returns_immutable_traces(self):
        (trace,) = self.ok()
        self.assertEqual(trace.prediction_sha256, self.pred.sha256)
        self.assertEqual(trace.rows, self.pred.trace)
        with self.assertRaises((AttributeError, TypeError)):
            trace.rows[0][2] = 0.0
        with self.assertRaises(AttributeError):
            trace.rows = ()

    def test_rejects_other_clip_or_source(self):
        with self.assertRaisesRegex(OverlayError, "different clip"):
            self.ok(clip="ST03")
        with self.assertRaisesRegex(OverlayError, "different source"):
            self.ok(src="0" * 64)

    def test_rejects_misaligned_timebase(self):
        shifted = {i: p + 1 / 60 for i, p in self.fmap.items()}  # half-frame PTS shift
        with self.assertRaisesRegex(OverlayError, "timebase differs"):
            self.ok(fmap=shifted)
        doc = copy.deepcopy(self.doc)
        doc["timebase"]["frame_map_sha256"] = frame_map_sha256(shifted)
        with self.assertRaisesRegex(OverlayError, "not aligned"):
            self.ok(doc, fmap=shifted)  # map hash matches, rows still on the old PTS
        dropped = {i: p for i, p in self.fmap.items() if i != 30}
        doc["timebase"]["frame_map_sha256"] = frame_map_sha256(dropped)
        with self.assertRaisesRegex(OverlayError, "frame 30 not aligned"):
            self.ok(doc, fmap=dropped)

    def test_rejects_mutated_trace_and_gate_claim(self):
        doc = copy.deepcopy(self.doc)
        doc["traces"][0]["trace"][5][2] += 1e-6
        with self.assertRaisesRegex(OverlayError, "changed after commitment"):
            self.ok(doc)
        doc = copy.deepcopy(self.doc)
        doc["traces"][0]["trace"][5][1] += 1 / 30  # retimed row: rejected (hash first; alignment is the backstop)
        with self.assertRaises(OverlayError):
            self.ok(doc)
        for key, value in (("gate_m", "MET"), ("contract_version", "overlay/1.0.0"), ("contract_version", "overlay/9"),
                           ("units", "m")):
            doc = dict(copy.deepcopy(self.doc), **{key: value})
            with self.assertRaises(OverlayError):
                self.ok(doc)

    def test_build_refuses_prediction_from_other_boundary(self):
        record, _ = ov.synthetic_pendulum(last=30)
        other, _ = b.split(record)
        with self.assertRaisesRegex(ValueError, "different clip, source, training"):
            ov.build(other, [self.pred], self.fmap, "synthetic")


class CommittedEvidenceTest(unittest.TestCase):
    def test_committed_overlays_validate_against_sources(self):
        record, suffix, _ = pr.st03_record(ROOT)
        rec, _ = ov.synthetic_pendulum()
        fmap = {f["frame_index"]: f["pts_s"] for f in rec["frames"]}
        for tag, legacy in (("", True), ("-v2", False)):  # v1 files: legacy-audit only; v2: new evidence
            st03 = json.loads((ROOT / f"evidence/S12/overlay-ST03{tag}.json").read_text(encoding="utf-8"))
            if legacy:
                with self.assertRaisesRegex(OverlayError, "legacy-audit only"):
                    validate(st03, record["clip_id"], record["source_sha256"], ov.st03_frame_map(ROOT))
            (trace,) = validate(st03, record["clip_id"], record["source_sha256"], ov.st03_frame_map(ROOT), legacy)
            committed = json.loads((ROOT / f"evidence/S12/prediction-ST03{tag}.json").read_text(encoding="utf-8"))
            self.assertEqual(trace.prediction_sha256, committed["prediction"]["sha256"])
            self.assertEqual(trace.commitment, "prediction/v1" if legacy else "prediction/v2")
            self.assertEqual([r[:2] for r in trace.rows], [tuple(s) for s in suffix])
            synth = json.loads((ROOT / f"evidence/S12/overlay-pendulum-SYNTHETIC{tag}.json").read_text(encoding="utf-8"))
            validate(synth, rec["clip_id"], rec["source_sha256"], fmap, legacy)
            self.assertEqual(synth["provenance"], "synthetic")


if __name__ == "__main__":
    unittest.main()
