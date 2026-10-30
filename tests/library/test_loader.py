"""Exercise the browser ESM against fresh, real guest projections, not copied fixtures."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

from Build.library.guest import load_guest
from Build.library.example import safe_defaults
from Build.library.playable import encode
from Build.library.validate import validate_file


class LoaderContractTests(unittest.TestCase):
    def test_browser_loader_contract(self):
        manifest, objects = load_guest()
        root = Path(__file__).resolve().parents[2]
        # Retain legacy metadata/scene rejection coverage even when current entries
        # are unavailable; these real descriptor bytes are never guest-published.
        setup = copy.deepcopy(next(d for d in manifest["demos"] if d["availability"] == "playable"))
        trace = json.loads(objects[setup["artifact"]["sha256"]])
        payload = encode({"source": "simulated", "template": trace["kind"].replace("-", "_"),
                          "duration_s": trace["samples"][-1]["time_s"], "time_step_s": trace["dt_s"],
                          "display_only": True, "availability": "metadata-only"})
        setup["availability"] = "metadata-only"
        catalogue = validate_file(root / "test-data/library-artifacts/scenes.json")
        raw_scene = catalogue["demos"][0]
        scene = {key: raw_scene[key] for key in
                 ("id", "title", "source", "scale_verified", "scale_label", "gates", "limitations")}
        defaults = safe_defaults(root, raw_scene)
        defaults.pop("fallback_evidence")
        scene.update(label="SCALE_UNVERIFIED", availability="metadata-only", display_only=True,
                     defaults=defaults)
        scene_data = (root / "test-data/library-artifacts" / raw_scene["artifact"]["path"]).read_bytes()
        for entry, data, kind in ((setup, payload, "simulation-setup"), (scene, scene_data, "scene-descriptor")):
            sha = hashlib.sha256(data).hexdigest()
            objects[sha] = data
            entry["artifact"] = {"kind": kind, "media_type": "application/json", "sha256": sha,
                                 "bytes": len(data), "href": f"/api/library/artifacts/{sha}"}
        fixture = {"manifest": manifest, "objects": {
            sha: base64.b64encode(data).decode("ascii") for sha, data in objects.items()},
            "legacy": {"setup": setup, "scene": scene}}
        result = subprocess.run(
            ["node", "--test-reporter=tap", str(root / "tests/library/loader.test.mjs")],
            input=json.dumps(fixture), text=True, capture_output=True, cwd=root, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("# fail 0", result.stdout)
        self.assertIn("# pass", result.stdout)


if __name__ == "__main__":
    unittest.main()
