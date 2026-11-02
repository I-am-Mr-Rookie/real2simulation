
"""N44: wall/opening/furniture check on a cached room (private data stays local; prints numbers only)."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.reconstruction import live_room, room_shell

d = Path(sys.argv[1])
npz = (d / "mapanything.npz").read_bytes()
scene = json.loads((d / "scene.json").read_text())
aligned, _, _, _ = live_room.analyse(npz)
centres = [(o["position"][0], o["position"][2]) for o in scene["objects"] if str(o.get("id", "")).startswith("room-object-")] + [(c[0], c[2]) for c in json.loads((d / "room.json").read_text())["camera_positions_m"]]
try:
    yaw, ws = room_shell.walls(aligned, centres)
except TypeError:
    yaw, ws = room_shell.walls(aligned)
ex, ez = room_shell._axes(yaw)
uv = [(float(np.dot(c, ex)), float(np.dot(c, ez))) for c in centres]
print(json.dumps({"yaw_deg": round(float(np.degrees(yaw)), 2), "walls": ws, "furniture_uv": [[round(a, 3), round(b, 3)] for a, b in uv]}))


