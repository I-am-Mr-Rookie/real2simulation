import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

with patch.dict(os.environ, RM02_WATCHDOG_RECEIPT=str(Path(tempfile.gettempdir()) / "s05c-worker.json")):
    import modal_scenes
from rm02_result import persist_result


def manifest(directory, clip_id="RM04", corrupt=False):
    (directory / "local").mkdir()
    frames = []
    for index in range(2):
        data = b"synthetic-frame-%d" % index
        (directory / f"local/{index}.png").write_bytes(data)
        frames.append({"path": f"local/{index}.png", "bytes": len(data),
                       "sha256": hashlib.sha256(b"x" if corrupt else data).hexdigest()})
    path = directory / "input.json"
    path.write_text(json.dumps({"scenes": [{"clip_id": clip_id, "frames": frames}]}))
    return path


class SceneBatchTest(unittest.TestCase):
    def test_accepts_hash_verified_approved_scene(self):
        with tempfile.TemporaryDirectory() as tmp:
            scenes = modal_scenes.load_scenes(manifest(Path(tmp)))
        self.assertEqual([clip for clip, _ in scenes], ["RM04"])
        self.assertEqual(len(scenes[0][1]), 2)

    def test_rejects_unapproved_scope_and_hash_mismatch(self):
        for kwargs in ({"clip_id": "PD02"}, {"corrupt": True}):
            with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
                modal_scenes.load_scenes(manifest(Path(tmp), **kwargs))

    def test_real_manifest_preserves_original_clip_ids_when_frames_present(self):
        if not (modal_scenes.MANIFEST.parent / "local").exists():
            self.skipTest("licensed frames are local-only")
        self.assertEqual([c for c, _ in modal_scenes.load_scenes()], ["RM04", "RM05"])

    def test_persist_result_custom_name(self):
        data = b"bundle"
        receipt = {"output_bytes": len(data), "output_sha256": hashlib.sha256(data).hexdigest()}
        with tempfile.TemporaryDirectory() as tmp:
            persist_result(tmp, (receipt, data), "S05c-scenes.zip")
            self.assertEqual((Path(tmp) / "local/S05c-scenes.zip").read_bytes(), data)

    def test_bounded_private_batch_options(self):
        source = Path(modal_scenes.__file__).read_text()
        for needle in ('gpu="A10G"', "retries=0", "max_containers=1", "single_use_containers=True",
                       '"facebook/map-anything-apache", revision=weight_rev', '"torch": str(torch.__version__)'):
            self.assertIn(needle, source)
        for banned in (".deploy(", "modal.Secret", "probe.remote("):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()

