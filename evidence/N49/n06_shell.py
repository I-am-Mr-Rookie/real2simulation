"""N49: offline shell of the cached N06 room (owner clip PRIVATE: outputs only under test-data/private/N49). N39 SAM box
cache (8 views), no SF3D, no paid calls. Prints numbers only.  python evidence/N49/n06_shell.py <N42 job dir> <sam-boxes.json> <out dir>"""
import hashlib, json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.reconstruction import room_shell
src, cache, out = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text()), Path(sys.argv[3])
misses = []
def detect(png, noun, w, h):
    k = f"{hashlib.sha1(png).hexdigest()[:12]}-{noun}"
    if k not in cache:
        misses.append(k)
        return []
    return cache[k]
room, scene = json.loads((src / "room.json").read_text()), json.loads((src / "scene.json").read_text())
scene["objects"] = [o for o in scene["objects"] if not str(o.get("id", "")).startswith(("wall-", "room-object-"))]
s, sh, _ = room_shell.build((src / "mapanything.npz").read_bytes(), room, scene, detect)
out.mkdir(parents=True, exist_ok=True)
(out / "scene.json").write_text(json.dumps(s))
shutil.copyfile(src / "room.ply", out / "room.ply")
print(json.dumps({"cache_misses": len(misses), "walls": [(w["status"], w.get("reason")) for w in sh["walls"]],
                  "openings": [(o["noun"], o["views"]) for o in sh["openings"]], "kept": [(k["category"], k["size_m"]) for k in sh["kept"]],
                  "objects": len(s["objects"]), "looks": sorted({o["look"]["category"] for o in s["objects"] if "look" in o})}))

