"""Hosted SAM 3.1 client: recorded N01 response fixture, no network."""
import copy
import json
from pathlib import Path
import unittest

from Build.measurement import hosted_sam
from Build.measurement.inputs import validate_input

FIXTURE = Path(__file__).parent / "fixtures/hosted_sam/resp-n01-call1-6f.json"
META = {"clip_id": "ST03", "licence": "Pexels License", "provenance": "pexels", "motion": "free_fall",
        "source_sha256": "0" * 64, "approval": {"scope": "scene_tracking", "evidence": "x"},
        "width_px": 720, "height_px": 1366, "last_training_frame": 60}


def resp(edit=None):
    r = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if edit:
        c = r["output"][0]["content"][0]
        lines = c["text"].splitlines()
        edit(lines)
        c["text"] = "\n".join(lines)
    return r


class HostedSamTest(unittest.TestCase):
    def test_parse_every_object_and_strip_masks(self):
        text = hosted_sam.output_text(resp())
        frames, size = hosted_sam.parse(text)
        self.assertEqual(size, (720, 1366))
        self.assertEqual(sorted(frames), list(range(6)))
        self.assertTrue(all(sorted(o) == [0, 1, 2] for o in frames.values()))  # N01 call 1 read only object 0
        self.assertEqual(frames[0][2], (115.0, 409.0, 178.0, 471.0))
        self.assertNotIn("mask", hosted_sam._MASK.sub("", text))
        self.assertEqual(hosted_sam.parse(hosted_sam._MASK.sub("", text)), (frames, size))

    def test_moving_object_selection_cost_and_record(self):
        def drop_object_1(lines):  # move object 1 down 300 px on the last frame: largest travel must win
            lines[-1] = lines[-1].replace("y1=1141;", "y1=1441;", 1).replace("y2=1197;", "y2=1497;", 1)
        moved = hosted_sam.result(resp(drop_object_1))
        self.assertEqual(moved["object_id"], 1)
        self.assertEqual((moved["frame_count"], moved["video_frames_processed"]), (6, 6))
        self.assertAlmostEqual(moved["cost_usd"], 6 * 0.0002)
        fixed = hosted_sam.result(resp(), object_id=2)
        self.assertEqual((fixed["object_id"], fixed["points"][0][1:3], fixed["missing"]), (2, (146.5, 440.0), []))
        fmap = [(58 + k, 1.9 + k / 30) for k in range(6)]
        data = validate_input(hosted_sam.to_record(fixed, META, fmap))  # fitter boundary accepts it unchanged
        self.assertEqual([f.frame_index for f in data.training], [58, 59, 60])
        self.assertIn("scale_unverified", data.blockers)
        with self.assertRaises(ValueError):
            hosted_sam.to_record(fixed, META, fmap[:5])

    def test_missing_object_stays_missing_and_bad_input_fails(self):
        def empty_frame_3(lines):
            lines[3] = "<3f>"
        out = hosted_sam.result(resp(empty_frame_3), object_id=2)
        self.assertEqual((out["missing"], [p[0] for p in out["points"]]), ([3], [0, 1, 2, 4, 5]))
        with self.assertRaises(ValueError):
            hosted_sam.result(resp(), object_id=9)
        bad = copy.deepcopy(resp())
        bad["status"] = "failed"
        with self.assertRaises(ValueError):
            hosted_sam.result(bad)

    def test_prompt_grammar(self):
        self.assertEqual(hosted_sam.box_prompt(1, (10, 20, 30, 40), 720, 1366),
                         "<0f>1<|box;x1=10;y1=20;x2=30;y2=40;w=720;h=1366|>")
        self.assertEqual(hosted_sam.point_prompt(2, [(5.7, 6, True), (1, 2, False)], 720, 1366, 4),
                         "<4f>2<|point;x=5;y=6;w=720;h=1366|>-<|point;x=1;y=2;w=720;h=1366|>")


if __name__ == "__main__":
    unittest.main()
