
"""N44: offline shell rebuild of the cached N06 room (owner clip PRIVATE; N39 SAM box cache, no SF3D, no paid calls). Numbers only."""
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.reconstruction import room_shell
d, cache = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text())
misses = []
def detect(png, noun, w, h):
    k = f"{hashlib.sha1(png).hexdigest()[:12]}-{noun}"
    if k not in cache:
        misses.append(k)
        return []
    return cache[k]
room, scene = json.loads((d / "room.json").read_text()), json.loads((d / "scene.json").read_text())
_, sh, _ = room_shell.build((d / "mapanything.npz").read_bytes(), room, scene, detect)
fit = [w for w in sh["walls"] if w["status"] == "FIT"]
print(json.dumps({"cache_misses": len(misses), "walls": [{k: w.get(k) for k in ("axis", "side", "plane", "support", "status", "reason", "span")} for w in sh["walls"]],
                  "openings": len(sh["openings"]), "opening_views": [o["views"] for o in sh["openings"]],
                  "openings_on_wall": sum(room_shell.on_wall(o, fit[o["wall"]]) for o in sh["openings"]),
                  "opening_detections_off_wall": sh["opening_detections_off_wall"], "kept": len(sh["kept"])}))

