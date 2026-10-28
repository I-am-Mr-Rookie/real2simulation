"""Offline child for scheduler verification; no AI, credentials or product files."""
import argparse
import json
from pathlib import Path
import sys
import time

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", required=True)
    p.add_argument("--scenario", choices=["normal", "quota", "timeout"], default="normal")
    a = p.parse_args()
    target = Path(a.target)
    assert not target.is_absolute() and ".." not in target.parts
    assert target.parts[0] == "dry-run"
    if a.scenario == "quota":
        print(json.dumps({"type": "error", "error": {"code": "insufficient_quota"}}), flush=True)
        time.sleep(5)
        return 2
    if a.scenario == "timeout":
        time.sleep(120)
        return 3
    time.sleep(0.2)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("S03 harmless dispatcher verification\n", encoding="utf-8")
    print(json.dumps({"type": "result", "status": "ok"}), flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
