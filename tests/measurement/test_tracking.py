"""Synthetic transport fixtures only: never evidence of live SAM inference."""
import copy
import dataclasses
import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from Build.measurement.inputs import validate_input
from test_inputs import synthetic_input


def response(index, ids=(7,), mask=None):
    if mask is None:
        mask = np.zeros((len(ids), 80, 100), dtype=bool)
        if len(ids):
            mask[:, 10:12, 20:24] = True
    return {"frame_index": index, "outputs": {
        "out_obj_ids": np.array(ids, dtype=np.int64), "out_binary_masks": mask}}


class FixturePredictor:
    """Implements documented request surface, NOT a SAM model."""
    def __init__(self, responses):
        self.responses = responses
        self.requests = []

    def handle_request(self, request):
        self.requests.append(copy.deepcopy(request))
        return {"session_id": "fixture-session"}

    def handle_stream_request(self, request):
        self.requests.append(copy.deepcopy(request))
        yield from self.responses


class TrackingTests(unittest.TestCase):
    def setUp(self):
        try:
            self.module = importlib.import_module("Build.measurement.tracking")
        except ModuleNotFoundError as error:
            self.fail(f"SAM 3.1 adapter is not implemented: {error}")
        self.metadata = synthetic_input()
        self.metadata["height_px"] = 80
        self.suffix = self.metadata.pop("frames")[3:]
        self.metadata["last_training_frame"] = 2
        self.mapping = ((0, 0.0), (1, 0.04), (2, 0.09))

    def sanitize(self, responses, **kwargs):
        return self.module.sanitize_responses(
            responses, self.metadata, self.mapping, object_id=7, **kwargs)

    def test_module_exists_without_loading_model_stack(self):
        self.assertNotIn("sam3", sys.modules)
        self.assertNotIn("torch", sys.modules)

    def test_centroid_source_pts_immutable_and_s07a_custody_integration(self):
        result = self.sanitize([response(i) for i in range(3)])
        self.assertEqual([(f.frame_index, f.pts_s, f.x_px, f.y_px)
                          for f in result.training],
                         [(i, t, 21.5, 10.5) for i, t in self.mapping])
        record = result.training_record()
        record["frames"].extend(self.suffix)
        record["approval"]["scope"] = "scene_tracking"
        record["scale"] = record["timebase"] = None
        checked = validate_input(record)
        self.assertIn("metric_use_not_approved", checked.blockers)
        self.assertIn("scale_unverified", checked.blockers)
        self.assertIn("capture_timebase_unverified", checked.blockers)
        self.metadata["clip_id"] = "mutated"
        self.assertNotEqual(result.training_record()["clip_id"], "mutated")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            result.training[0].x_px = 99

    def test_unknown_calibration_preserved_not_filled(self):
        self.metadata["scale"] = self.metadata["timebase"] = None
        result = self.sanitize([response(0)])
        self.assertIsNone(result.training_record()["scale"])
        self.assertIsNone(result.training_record()["timebase"])

    def test_local_indices_map_to_irregular_original_segment_not_frame_over_fps(self):
        self.metadata["last_training_frame"] = 41
        self.mapping = ((30, 1.2), (33, 1.24), (41, 1.31))
        result = self.sanitize([response(0), response(2)])
        self.assertEqual([(f.frame_index, f.pts_s) for f in result.training],
                         [(30, 1.2), (41, 1.31)])
        self.assertEqual(result.missing_frames, (33,))

    def test_missing_objects_frames_and_empty_masks_are_not_interpolated(self):
        empty = np.zeros((1, 80, 100), dtype=bool)
        result = self.sanitize([response(0, ids=()), response(2, mask=empty)])
        self.assertEqual(result.training, ())
        self.assertEqual(result.missing_frames, (0, 1, 2))

    def test_explicit_object_selection_no_largest_or_first_heuristic(self):
        masks = np.zeros((2, 80, 100), dtype=bool)
        masks[0, 1, 2] = True
        masks[1, 6, 8] = True
        result = self.sanitize([response(0, ids=(8, 7), mask=masks)])
        self.assertEqual((result.training[0].x_px, result.training[0].y_px), (8, 6))

    def test_malformed_responses_fail_closed(self):
        bad = [None, {}, response(True), response(-1), response(3),
               response(0, ids=(7, 7)), response(0, ids=(-1,)),
               response(0, mask=np.ones((1, 40, 50), dtype=bool)),
               response(0, mask=np.ones((1, 80, 100))),
               response(0, mask=np.full((1, 80, 100), np.nan)),
               response(0, mask=np.ones((2, 80, 100), dtype=bool))]
        for item in bad:
            with self.subTest(item=str(item)[:80]), self.assertRaises(ValueError):
                self.sanitize([item])
        for items in ([response(0), response(0)], [response(2), response(1)]):
            with self.assertRaises(ValueError):
                self.sanitize(items)
        with self.assertRaises(ValueError):
            self.sanitize(None)

    def test_mapping_cannot_cross_split_or_infer_clock(self):
        for mapping in (((0, 0.0), (1, float("nan")), (2, .1)),
                        ((0, 0.0), (1, .1), (3, .2)),
                        ((0, 0.0), (1, .1), (2, .1)),
                        ((True, 0.0), (1, .1), (2, .2)),
                        ((0, 0.0), (2, .1), (1, .2))):
            self.mapping = mapping
            with self.subTest(mapping=mapping), self.assertRaises(ValueError):
                self.sanitize([])

    def test_full_record_or_bad_provenance_rejected_before_predictor(self):
        for change in ({"frames": self.suffix}, {"approval": None},
                       {"source_sha256": "not-a-hash"}, {"width_px": True}):
            original = copy.deepcopy(self.metadata)
            self.metadata.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.sanitize([])
            self.metadata = original

    def test_execution_opt_in_and_local_checkpoint_required(self):
        with self.assertRaises(PermissionError):
            self.module.load_local_predictor("missing.pt")
        with self.assertRaises(ValueError):
            self.module.load_local_predictor("https://remote/weights", execute=True)
        self.assertNotIn("sam3", sys.modules)

    def test_remote_paths_rejected_without_filesystem_access(self):
        for path in ("https://remote/weights", "\\\\remote\\share\\weights", "//remote/share"):
            with self.subTest(path=path), patch.object(Path, "is_file", side_effect=AssertionError("network probe")):
                with self.assertRaises(ValueError):
                    self.module.load_local_predictor(path, execute=True)

    def test_factory_calls_actual_documented_builder_only_when_opted_in(self):
        calls = []
        builder = types.ModuleType("sam3.model_builder")
        def build(**kwargs):
            calls.append(kwargs)
            return "fixture-predictor-not-a-model"
        builder.build_sam3_multiplex_video_predictor = build
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory, "fixture.pt")
            checkpoint.write_bytes(b"abc")  # Integrity fixture only, never model bytes.
            with patch.dict(sys.modules, {"sam3": types.ModuleType("sam3"), "sam3.model_builder": builder}), \
                 patch.object(self.module, "_CHECKPOINT_BYTES", 3, create=True), \
                 patch.object(self.module, "_CHECKPOINT_SHA256",
                              "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", create=True):
                result = self.module.load_local_predictor(checkpoint, execute=True)
            self.assertEqual(result, "fixture-predictor-not-a-model")
            self.assertEqual(calls, [{"checkpoint_path": str(checkpoint.resolve()),
                                     "compile": False, "warm_up": False,
                                     "async_loading_frames": False}])

    def test_checkpoint_size_and_same_size_corruption_rejected_before_builder(self):
        builder = types.ModuleType("sam3.model_builder")
        def forbidden(**kwargs):
            self.fail("unverified checkpoint reached heavy model construction")
        builder.build_sam3_multiplex_video_predictor = forbidden
        with tempfile.TemporaryDirectory() as directory, \
             patch.dict(sys.modules, {"sam3": types.ModuleType("sam3"), "sam3.model_builder": builder}), \
             patch.object(self.module, "_CHECKPOINT_BYTES", 3, create=True), \
             patch.object(self.module, "_CHECKPOINT_SHA256",
                          "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", create=True):
            checkpoint = Path(directory, "fixture.pt")
            for data in (b"ab", b"abcd", b"abd"):
                checkpoint.write_bytes(data)
                with self.subTest(data=data), self.assertRaises(ValueError):
                    self.module.load_local_predictor(checkpoint, execute=True)

    def test_exact_documented_calls_prefix_only_and_close_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            for i in range(3):
                Path(directory, f"{i:05d}.jpg").write_bytes(b"transport fixture, not media")
            predictor = FixturePredictor([response(i) for i in range(3)])
            args = (predictor, directory, self.metadata, self.mapping)
            with self.assertRaises(PermissionError):
                self.module.track_training(*args, prompt="ball", object_id=7)
            result = self.module.track_training(*args, prompt="ball", object_id=7, execute=True)
            self.assertEqual(len(result.training), 3)
            self.assertEqual([r["type"] for r in predictor.requests],
                             ["start_session", "add_prompt", "propagate_in_video", "close_session"])
            stream = predictor.requests[2]
            self.assertEqual(stream["propagation_direction"], "forward")
            self.assertEqual(stream["start_frame_index"], 0)
            self.assertEqual(stream["max_frame_num_to_track"], 2)
            self.assertEqual(predictor.requests[1]["text"], "ball")
            predictor.responses = [response(3)]
            with self.assertRaises(ValueError):
                self.module.track_training(*args, prompt="ball", object_id=7, execute=True)
            self.assertEqual(predictor.requests[-1]["type"], "close_session")
            Path(directory, "00003.jpg").write_bytes(b"withheld")
            before = len(predictor.requests)
            with self.assertRaises(ValueError):
                self.module.track_training(*args, prompt="ball", object_id=7, execute=True)
            self.assertEqual(len(predictor.requests), before)


if __name__ == "__main__":
    unittest.main()
