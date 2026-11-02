"""N42 live run: reuse the N39 room job of the owner clip N06_room.mp4 (PRIVATE, no new reconstruction) -> refit floor
(live_room.finish) -> lab shell via build_shell_files (the function run_job now calls automatically) with the cached
hosted SAM 3.1 boxes (no repeat paid calls) and real SF3D (Modal, daily_cap ledgered) -> finish again (rescale path must
keep the shell). Private data stays in test-data/private/N42; evidence/N42/live/*.json keeps numbers only.

uv run --python 3.12 --with modal==1.6.3 --with numpy --with fastapi --with httpx --with python-multipart \
  --with jsonschema --with pillow --env-file <root>/.env python evidence/N42/live_run.py <N39 job dir> <data_dir> [budget_s]
"""
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
OUT = HERE / "live"
OUT.mkdir(exist_ok=True)

from Build.api.room.objects import build_shell_files  # noqa: E402
from Build.gpu import sf3d  # noqa: E402
from Build.reconstruction import live_room  # noqa: E402

src, data = Path(sys.argv[1]), Path(sys.argv[2])
budget = int(sys.argv[3]) if len(sys.argv) > 3 else 220
d = data / "rooms" / "user_n42live" / src.name
d.mkdir(parents=True, exist_ok=True)
for n in ("mapanything.npz", "room.json", "scene.json", "status.json", "cost-log.json"):
    shutil.copyfile(src / n, d / n)
cache = json.loads((src.parents[2] / "sam-boxes.json").read_text())
old_floor = json.loads((d / "room.json").read_text())["floor"]
t0 = time.time()
out = live_room.finish(d)
refit = {"seconds": round(time.time() - t0, 1), "floor_before": old_floor, "floor_after": out["room"]["floor"],
         "gravity_after": out["room"]["gravity"], "objects_dropped": out["room"].get("objects_dropped"),
         "camera_heights_m": [round(c[1], 3) for c in out["room"]["camera_positions_m"]]}
misses = []


def detect(png, noun, w, h):
    key = f"{hashlib.sha1(png).hexdigest()[:12]}-{noun}"
    if key not in cache:  # no paid SAM call in this run: the N39 boxes cover every keyframe x noun
        misses.append(key)
        return []
    return cache[key]


sf3d_calls = []


def generate(png):
    t = time.time()
    r = sf3d.generate_remote(png, timeout_s=budget)
    sf3d_calls.append({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seconds": round(time.time() - t, 1),
                       **{k: r.get(k) for k in ("gpu", "wall_s", "inference_s", "estimated_usd")}})
    return r


t0 = time.time()
shell, scene = build_shell_files(d, detect, generate)
shell_s = round(time.time() - t0, 1)
n_before = len(scene["objects"])
again = live_room.finish(d)  # rescale path (no new reference): the shell must survive
res = {"label": "N06_room.mp4 PRIVATE; numbers only; geometry MODEL-ESTIMATED, scale unverified", "refit": refit,
       "shell_seconds": shell_s, "sam_cache_misses": len(misses), "sf3d_calls": sf3d_calls,
       "kept": [{k: v for k, v in x.items() if k != "sf3d"} for x in shell["kept"]], "dropped": shell["dropped"],
       "dropped_reasons": shell["dropped_reasons"], "walls_fit": sum(w["status"] == "FIT" for w in shell["walls"]),
       "openings": len(shell["openings"]),
       "supports": {o["id"]: o["shape"].get("support") for o in scene["objects"] if (o.get("shape") or {}).get("support")},
       "finish_again": {"objects_before": n_before, "objects_after": len(again["scene"]["objects"]),
                        "shell_kept": "shell" in again["room"], "rescaled_by": again["room"].get("shell", {}).get("rescaled_by")}}
(OUT / "shell.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
print(json.dumps(res)[:4000])

