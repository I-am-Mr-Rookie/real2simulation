"""Synthetic contract checks, not clip calibration or physics evidence."""
import unittest

from Build.measurement.inputs import validate_input


def synthetic_input():
    return {
        "clip_id": "SYNTHETIC", "source_sha256": "a" * 64,
        "licence": "CC0-1.0", "provenance": "synthetic test only",
        "approval": {"scope": "scene_tracking", "evidence": "synthetic approval"},
        "motion": "earth_free_fall", "width_px": 100, "height_px": 100,
        "continuous_segment_evidence": "synthetic uninterrupted segment",
        "scale": {"method": "independent_reference", "m_per_px": 0.01,
                  "uncertainty_m_per_px": 0.001, "plane_verified": True,
                  "evidence": "synthetic ruler, not actual media"},
        "timebase": {"capture_seconds_per_pts_second": 1.0,
                     "uncertainty_factor": 0.01, "verified": True,
                     "evidence": "synthetic capture clock"},
        "last_training_frame": 2,
        "frames": [{"frame_index": i, "pts_s": i * 0.1,
                    "x_px": 10.0, "y_px": 10.0 + i} for i in range(5)],
    }


class InputTests(unittest.TestCase):
    def test_scene_approval_never_authorizes_metric_fit(self):
        result = validate_input(synthetic_input())
        self.assertIn("metric_use_not_approved", result.blockers)
        self.assertFalse(result.metric_eligible)

    def test_qualified_synthetic_input_has_disjoint_immutable_prefix_suffix(self):
        data = synthetic_input()
        data["approval"]["scope"] = "metric_measurement"
        result = validate_input(data)
        self.assertTrue(result.metric_eligible)
        self.assertEqual([f.frame_index for f in result.training], [0, 1, 2])
        self.assertEqual([f.frame_index for f in result.held_out], [3, 4])
        data["frames"][0]["x_px"] = 99
        self.assertEqual(result.training[0].x_px, 10.0)
        with self.assertRaises(AttributeError):
            result.training[0].x_px = 5

    def test_unknown_scale_timebase_and_continuity_abstain(self):
        data = synthetic_input()
        data.update(scale=None, timebase=None, continuous_segment_evidence=None)
        self.assertEqual(set(validate_input(data).blockers), {
            "metric_use_not_approved", "scale_unverified", "capture_timebase_unverified",
            "continuous_segment_unverified"})

    def test_circular_scale_and_unverified_plane_abstain(self):
        for changes in ({"method": "fall_time"}, {"plane_verified": False}, {"evidence": ""}):
            data = synthetic_input()
            data["scale"].update(changes)
            self.assertIn("scale_unverified", validate_input(data).blockers)

    def test_container_rate_alone_cannot_establish_capture_clock(self):
        data = synthetic_input()
        data["timebase"] = {"file_fps": "25/1"}
        self.assertIn("capture_timebase_unverified", validate_input(data).blockers)

    def test_non_fall_motion_cannot_count_as_earth_trial(self):
        for motion in ("projectile", "bounce", "pendulum", "iss", "lunar_free_fall"):
            data = synthetic_input()
            data["motion"] = motion
            self.assertIn("not_earth_free_fall", validate_input(data).blockers)

    def test_bad_numbers_bounds_order_or_leaking_split_rejected(self):
        bad = []
        for field, value in (("pts_s", float("nan")), ("x_px", 100),
                             ("y_px", -1), ("frame_index", True)):
            data = synthetic_input()
            data["frames"][1][field] = value
            bad.append(data)
        for field in ("pts_s", "frame_index"):
            data = synthetic_input()
            data["frames"][1][field] = data["frames"][0][field]
            bad.append(data)
        for split in (0, 4, 99, True, 2.5):
            data = synthetic_input()
            data["last_training_frame"] = split
            bad.append(data)
        for data in bad:
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_input(data)

    def test_invalid_calibration_uncertainty_rejected(self):
        for section, key, value in (("scale", "m_per_px", 0),
                                    ("scale", "uncertainty_m_per_px", -1),
                                    ("timebase", "uncertainty_factor", float("inf")),
                                    ("timebase", "capture_seconds_per_pts_second", True)):
            data = synthetic_input()
            data[section][key] = value
            with self.subTest(section=section, key=key), self.assertRaises(ValueError):
                validate_input(data)

    def test_missing_provenance_or_approval_rejected(self):
        for key in ("source_sha256", "provenance", "licence", "approval", "frames"):
            data = synthetic_input()
            del data[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_input(data)

    def test_unrepresentable_timestamp_is_validation_error_not_crash(self):
        data = synthetic_input()
        data["frames"][-1]["pts_s"] = 10 ** 1000
        with self.assertRaises(ValueError):
            validate_input(data)


if __name__ == "__main__":
    unittest.main()
