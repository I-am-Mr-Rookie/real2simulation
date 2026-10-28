"""One bounded CPU-only installation/import check; no model or media loading."""
import json
from pathlib import Path
import sys

import modal

app = modal.App("s05b-recovery3-cpu-imports")


@app.function(
    image=modal.Image.debian_slim(python_version="3.11"),
    cpu=(1, 2), memory=(8192, 16384),
    timeout=520, startup_timeout=60, retries=0,
    min_containers=0, max_containers=1, buffer_containers=0,
    scaledown_window=2, single_use_containers=True,
    serialized=True, include_source=False,
)
def check_imports(requirements):
    import importlib.metadata
    import subprocess
    import sys
    import time
    from pathlib import Path

    started = time.monotonic()
    Path("/tmp/s05b-requirements.txt").write_text(requirements)
    subprocess.run([
        sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
        "--no-cache-dir",
        "-r", "/tmp/s05b-requirements.txt",
    ], check=True, timeout=450)
    # A separate interpreter proves installed imports, not pip metadata alone.
    result = subprocess.check_output([
        sys.executable, "-c",
        "import torch,torchvision,torchaudio,numpy; "
        "from mapanything.models import MapAnything; "
        "from mapanything.utils.image import load_images; "
        "print('CPU_IMPORTS_OK',torch.__version__,torchvision.__version__,"
        "torchaudio.__version__,numpy.__version__)",
    ], text=True, timeout=60)
    return {"imports": result.strip(), "elapsed_s": time.monotonic()-started,
            "python": sys.version, "gpu_requested": False,
            "versions": {p: importlib.metadata.version(p) for p in
                         ("torch", "torchvision", "torchaudio", "numpy", "mapanything")}}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parents[3]
    evidence = root / "evidence/S05/S05b/recovery3"
    lock = Path(__file__).with_name("requirements-linux-py311.txt").read_text()
    try:
        with modal.enable_output(), app.run():
            (evidence / "cpu-app.json").write_text(json.dumps({"app_id": app.app_id})+"\n")
            print("S05B_CPU_APP", app.app_id, flush=True)
            result = check_imports.remote(lock)
            (evidence / "cpu-import-result.json").write_text(json.dumps(result, indent=2)+"\n")
    finally:
        if app.app_id:
            app.stop()
            print("S05B_CPU_STOP_REQUESTED", app.app_id, flush=True)
