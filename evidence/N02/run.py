"""N02 paid run: hosted SAM 3.1 on full ST03 (543 frames), text prompt then a point prompt. Key never printed.

Usage: python evidence/N02/run.py <ST03.mp4>  (local Pexels copy; video is never committed)
Writes evidence/N02/resp-<name>.json with mask payloads stripped (boxes, ids, usage kept).
"""
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.measurement import hosted_sam  # noqa: E402

SOURCE_SHA256 = "7239da801ff407cf5ff047fceb82351724ad35985be298ffcb0e4ba1a53df051"
OUT = ROOT / "evidence/N02"


def load_env():
    env = Path(os.environ.get("N02_ENV", ROOT / ".env"))
    for line in env.read_text(encoding="utf-8").splitlines():
        k, _, v = line.partition("=")
        if k.strip() in ("MODEL_API_KEY", "MODEL_API_BASE_URL") and v.strip():
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def call(name, file_id, prompt, ledger):
    t0 = time.time()
    resp = hosted_sam.track(file_id, prompt)
    secs = round(time.time() - t0, 1)
    for item in resp.get("output", []):
        for c in item.get("content", []):
            if "text" in c:
                c["text"] = hosted_sam._MASK.sub("", c["text"])
    (OUT / f"resp-{name}.json").write_text(json.dumps(resp) + "\n", encoding="utf-8")
    r = hosted_sam.result(resp)
    row = {"utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "model": "sam-3.1", "call": name,
           "prompt": prompt, "seconds": secs, "video_frames_processed": r["video_frames_processed"],
           "cost_usd": round(r["cost_usd"], 4), "frames": r["frame_count"], "travel_px": r["travel_px"],
           "moving_id": r["object_id"], "missing": len(r["missing"])}
    ledger.append(row)
    print(json.dumps(row))
    return r


def main(video):
    if hashlib.sha256(Path(video).read_bytes()).hexdigest() != SOURCE_SHA256:
        raise SystemExit("ST03 bytes differ from the accepted source hash")
    load_env()
    ledger = []
    file_id = hosted_sam.upload(video)
    text = call("apple", file_id, "apple", ledger)
    k, x, y, box = text["points"][0]
    # point prompt on the moving object at its first tracked frame, from the text-prompt box centre
    call("point", file_id, hosted_sam.point_prompt(1, [(x, y, True)], text["width"], text["height"], k), ledger)
    with (OUT / "ledger.jsonl").open("a", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in ledger)


if __name__ == "__main__":
    main(sys.argv[1])
