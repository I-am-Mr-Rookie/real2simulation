"""N49: time one live_room.load_views call on a room npz (structural bottleneck check). python time_views.py <npz>"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Build.reconstruction import live_room
b = Path(sys.argv[1]).read_bytes()
t = time.time(); live_room.load_views(b); t1 = time.time() - t
t = time.time(); live_room.load_views(b); print({"MB": round(len(b) / 1e6, 1), "first_s": round(t1, 3), "second_s": round(time.time() - t, 3)})
