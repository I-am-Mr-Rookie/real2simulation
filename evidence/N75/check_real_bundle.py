"""Offline integration: legacy RM04 SAMPLE -> actual shared RM02 shell/meshes; no inference."""
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.api.storage import Store, sample


def main():
    bundle = Path(sys.argv[1])
    manifest = json.loads(sample.MANIFEST.read_text())
    with tempfile.TemporaryDirectory(prefix="n75-real-") as tmp:
        tmp = Path(tmp)
        legacy = tmp / "legacy.json"
        legacy.write_text(json.dumps({k: v for k, v in manifest.items() if k != "sample_shell"}))
        store = Store(tmp / "data")
        try:
            sample.seed(store, "user_n75_real_check", bundle, legacy)
            d = next((store.root / "rooms/user_n75_real_check").iterdir())
            before = json.loads((d / "scene.json").read_text())
            assert len(before["objects"]) == 0
            with patch("Build.api.room.objects.build_shell_files", side_effect=AssertionError("unexpected SAM")), \
                 patch("Build.gpu.sf3d.generate_remote", side_effect=AssertionError("unexpected GPU")):
                assert sample.seed(store, "user_n75_real_check", bundle) is None
                scene = json.loads((d / "scene.json").read_text())
                room = json.loads((d / "room.json").read_text())
                meshes = [o for o in scene["objects"] if o.get("shape", {}).get("type") == "mesh"]
                assert len(scene["objects"]) == 23 and len(meshes) == 4
                assert room["sample"] and room["scale"]["status"] == "scale unverified"
                for o in meshes:
                    assert o["shape"]["glb"] == f"/api/workspace/rooms/{d.name}/objects/{o['id']}.glb"
                    name = manifest["sample_shell"]["meshes"][o["id"]]
                    assert hashlib.sha256((d / "objects" / f"{o['id']}.glb").read_bytes()).hexdigest() == manifest["files"][name]["sha256"]
                snapshot = {p.name: p.read_bytes() for p in d.glob("*.json")}
                sample.seed(store, "user_n75_real_check", bundle)
                assert snapshot == {p.name: p.read_bytes() for p in d.glob("*.json")}
                sample.seed(store, "user_n75_second", bundle)
            result = {"status": "PASS", "source": "public RM02 cached MapAnything/SAM + four N75 SF3D outputs",
                      "before_objects": len(before["objects"]), "after_objects": len(scene["objects"]),
                      "meshes": len(meshes), "furniture": len(room["shell"]["kept"]),
                      "archive_sha256": hashlib.sha256((d / "mapanything.npz").read_bytes()).hexdigest(),
                      "scale": room["scale"], "labels": room["labels"],
                      "idempotent": True, "second_user_seeded": True, "new_inference_calls": 0}
            (ROOT / "evidence/N75/real-bundle-check.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps(result))
        finally:
            store.db.close()


if __name__ == "__main__":
    main()
