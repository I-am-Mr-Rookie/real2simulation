"""S07g: register the 12 owner-recorded trims in clips.csv (idempotent) + sha256/PTS receipt.
Run from repo root: python evidence/S07/S07g/register_clips.py"""
import csv, hashlib, json, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CANONICAL = Path("C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon")
FOLDER = "Videos for Meta AI Hackathon"
CLIPS = [  # (file, role, source window) verbatim from the owner's CLIPS.md
    ("01_demo_hero__035735.mp4", "demo video hero", "_raw/VID_20261031_035735 13.8-16.8 s"),
    ("02_live_check__035628.mp4", "live/app upload check", "035628 16.0-18.9 s"),
    ("03_test_clean__035601.mp4", "internal test", "035601 18.3-21.1 s"),
    ("04_test_shadow__035348.mp4", "internal test (arm shadow)", "035348 12.2-15.0 s"),
    ("05_repeat_a__035711.mp4", "repeatability", "035711 11.1-14.0 s"),
    ("05_repeat_b__035711.mp4", "repeatability (sheet partly down)", "035711 26.1-29.0 s"),
    ("05_repeat_c__035842.mp4", "repeatability", "035842 38.5-41.3 s"),
    ("05_repeat_d__035842.mp4", "repeatability", "035842 53.0-55.6 s"),
    ("06_robust_nosheet__035711.mp4", "robustness: cluttered background", "035711 18.9-20.9 s"),
    ("06_robust_clutter__032830.mp4", "robustness: cluttered background", "032830 17.0-19.9 s"),
    ("06_robust_lowres_messenger__032830.mp4", "robustness: 478x850 WhatsApp re-encode",
     "_raw/messenger_lowres_of_032830 17.0-19.9 s"),
    ("06_robust_frontcover__035842.mp4", "robustness: non-yellow cover (weak, landing at clip end)",
     "035842 13.8-15.95 s"),
]


def probe(path):
    s = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height,r_frame_rate,duration", "-of", "json", str(path)], text=True))["streams"][0]
    pts = [float(x) for x in subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "frame=pts_time", "-of", "csv=p=0", str(path)], text=True).replace(",", " ").split()]
    d = [b - a for a, b in zip(pts, pts[1:])]
    return s, {"frames": len(pts), "first_pts_s": pts[0], "dt_min_s": min(d), "dt_max_s": max(d),
               "monotonic": all(x > 0 for x in d)}


def main():
    csv_path = REPO / "clips.csv"
    raw = csv_path.read_bytes()
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    have = {r["clip_id"] for r in rows}
    receipt, new = {}, []
    for i, (name, role, window) in enumerate(CLIPS, 1):
        cid, path = f"OWN{i:02d}", CANONICAL / FOLDER / name
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        s, pts = probe(path)
        uniform = pts["monotonic"] and pts["dt_max_s"] - pts["dt_min_s"] < 1e-3
        receipt[cid] = {"file": f"{FOLDER}/{name}", "sha256": sha, "bytes": path.stat().st_size, **s, "pts": pts}
        if cid in have:
            continue
        new.append({
            "clip_id": cid, "experiment": "free_fall", "title": f"Owner book drop {name} ({role})",
            "source_url": "owner-recorded (local, not published)", "original_source_url": f"{FOLDER}/_raw ({window})",
            "download_url": "", "creator": "Koushik Sadhak Jeet",
            "licence": "owner-recorded; all rights reserved; public use pending owner go-ahead", "licence_url": "",
            "attribution": "Koushik Sadhak Jeet (owner-recorded, Realme C53)",
            "adaptation_notes": f"Face-free trim of {window}; videos stay gitignored, never committed",
            "status": "OWNER_RECORDED", "owner_approved": "PRIVATE_PROCESSING_ONLY (Oct31)",
            "local_path": f"{FOLDER}/{name}", "file_fps": s["r_frame_rate"],
            "file_duration_s": f"{float(s['duration']):.6f}", "source_duration_label": f"{float(s['duration']):.1f} s trim",
            "source_resolution": f"{s['width']}x{s['height']}",
            "scale_reference": "book cover horizontal edge in fall plane", "scale_value_m": "0.2028",
            "scale_status": "USER_DECLARED_OWNER_MEASURED|NOT_INDEPENDENTLY_VERIFIED",
            "timebase_status": ("CONTAINER_PTS_UNIFORM_1_30S|PHONE_CLOCK_NOT_EXTERNALLY_VERIFIED" if uniform
                                else "CONTAINER_PTS_NONUNIFORM|PHONE_CLOCK_NOT_EXTERNALLY_VERIFIED"),
            "suitability": role, "capture_group": "OWNER_20261031_REALME_C53",
            "evidence_path": "evidence/S07/S07g/clips-sha256.json",
        })
    (REPO / "evidence/S07/S07g/clips-sha256.json").write_text(json.dumps(receipt, indent=1), "utf-8")
    if new:
        term = "\r\n" if b"\r\n" in raw else "\n"
        sep = "" if raw.endswith(term.encode()) else term
        with csv_path.open("a", encoding="utf-8", newline="") as f:
            f.write(sep)
            csv.DictWriter(f, fieldnames=fields, lineterminator=term).writerows(new)
    print(json.dumps({"added": [r["clip_id"] for r in new], "total": len(receipt)}))


if __name__ == "__main__":
    main()

