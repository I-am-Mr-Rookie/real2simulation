"""S18i: measure guest-library load times (in-process load_guest + local HTTP via loader.mjs).

python -B -m Build.library.load_times [--reps N] [--out evidence/S18/S18i-load-times.json]
Local machine only; no network beyond 127.0.0.1, no GPU, no deploy.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import socket
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
TARGET_MS = 3000.0
COLD = ("import json,time;t=time.perf_counter();from Build.library.guest import load_guest;"
        "i=time.perf_counter();load_guest();e=time.perf_counter();"
        "print(json.dumps({'import_ms':(i-t)*1e3,'first_load_guest_ms':(e-i)*1e3}))")
SERVER = ("import sys,uvicorn;from Build.library.guest import create_app;"
          "uvicorn.run(create_app(),host='127.0.0.1',port=int(sys.argv[1]),log_level='warning')")


def stats(values):
    ordered = sorted(values)
    return {"n": len(ordered), "median_ms": round(statistics.median(ordered), 2),
            "p95_ms": round(ordered[min(len(ordered) - 1, round(0.95 * (len(ordered) - 1)))], 2),
            "max_ms": round(ordered[-1], 2)}


def run_python(code, *args):
    out = subprocess.run([sys.executable, "-B", "-c", code, *args], cwd=ROOT, capture_output=True,
                         text=True, timeout=120, check=True)
    return {k: round(v, 2) for k, v in json.loads(out.stdout).items()}


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def http(reps):
    port = free_port()
    server = subprocess.Popen([sys.executable, "-B", "-c", SERVER, str(port)], cwd=ROOT,
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        start = time.perf_counter()
        while True:  # TCP probe only: no HTTP request may warm the server before the cold timing.
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
                break
            except OSError:
                if server.poll() is not None or time.perf_counter() - start > 60:
                    raise RuntimeError("guest server did not start: " + server.stderr.read().decode()[-400:])
                time.sleep(0.05)
        startup_ms = (time.perf_counter() - start) * 1e3
        out = subprocess.run(["node", str(ROOT / "Build/library/load_times.mjs"), f"http://127.0.0.1:{port}",
                              str(reps)], cwd=ROOT, capture_output=True, text=True, timeout=600, check=True)
        return startup_ms, json.loads(out.stdout)
    finally:
        server.terminate()
        server.wait(timeout=10)


def measure(reps=5, cold_runs=3):
    from Build.library.guest import load_guest
    cold = [run_python(COLD) for _ in range(cold_runs)]  # fresh processes, so this import does not warm them
    warm = []
    for _ in range(reps):
        t = time.perf_counter()
        load_guest()
        warm.append((time.perf_counter() - t) * 1e3)
    startup_ms, measured = http(reps)
    entries = {}
    for demo_id, row in measured["entries"].items():
        opened = row["availability"] != "unavailable"
        entries[demo_id] = {"availability": row["availability"], "can_mount": row["canMount"],
                            "opens_demo": opened, "open": stats(row["open_ms"]),
                            "entry_only": stats(row["entry_ms"]), "manifest_get": stats(row["manifest_ms"]),
                            "under_3s_p95": stats(row["open_ms"])["p95_ms"] < TARGET_MS}
    opening = [k for k, v in entries.items() if v["opens_demo"]]
    fast = [k for k in opening if entries[k]["under_3s_p95"]]
    return {
        "schema": "S18i-load-times/1",
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "label": "measured (local wall-clock timing; not deployed, browser-rendered or real-network latency)",
        "conditions": {
            "machine": {"platform": platform.platform(), "processor": platform.processor(),
                        "cpu_count": os.cpu_count(), "python": platform.python_version(),
                        "node": subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()},
            "transport": "in-process load_guest(); local HTTP uvicorn 127.0.0.1 + Node fetch + Build/library/loader.mjs",
            "open_definition": "deep-link open = that rep's GET /api/library/manifest + loadLibraryEntry "
                               "(artifact GET, bytes/sha256/schema/trace validation); unavailable entries do no GET",
            "cold": "fresh Python process (import + first load_guest); first HTTP request after server start. "
                    "OS file cache NOT flushed.",
            "warm_reps": reps, "cold_runs": cold_runs, "target_ms": TARGET_MS,
            "p95": "nearest-rank over n reps (small n: p95 is near the max sample)",
        },
        "in_process": {"cold": cold, "warm_load_guest": stats(warm)},
        "http": {"server_startup_ms": round(startup_ms, 2), "cold_manifest_ms": round(measured["cold_manifest_ms"], 2),
                 "entries": entries},
        "summary": {"entries_total": len(entries), "demos_openable": len(opening),
                    "demos_open_under_3s_p95": len(fast), "openable_ids": opening,
                    "unavailable_entries": len(entries) - len(opening),
                    "six_demo_target_met": len(fast) >= 6},
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--out", default=str(ROOT / "evidence/S18/S18i-load-times.json"))
    args = parser.parse_args(argv)
    result = measure(args.reps)
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"]))
    return result


if __name__ == "__main__":
    main()
