
"""N44: walls on a saved room.ply (= live_room.analyse aligned points) + result.json; numbers only."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.reconstruction import room_shell

d = Path(sys.argv[1])
lines = (d / "room.ply").read_text().splitlines()
n = next(int(l.split()[-1]) for l in lines if l.startswith("element vertex"))
start = lines.index("end_header") + 1
pts = np.array([[float(x) for x in l.split()[:3]] for l in lines[start:start + n]])
res = json.loads((d / "result.json").read_text())
objs = [o for o in res["scene"]["objects"] if str(o.get("id", "")).startswith("room-object-")]
centres = [(o["position"][0], o["position"][2]) for o in objs] + [(c[0], c[2]) for c in res["room"]["camera_positions_m"]]
print("points", len(pts), "y98", round(float(np.percentile(pts[:, 1], 98)), 4))
old = res["room"]["shell"]["walls"]
print("old", [(w["plane"], w["status"]) for w in old])
yaw, ws = room_shell.walls(pts, centres)
print("yaw", round(float(np.degrees(yaw)), 2), "old yaw", res["room"]["shell"]["yaw_deg"])
for w in ws: print(w)


