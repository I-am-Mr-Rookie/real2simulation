"""Image-build helper: install undeclared sam3 runtime imports until model_builder imports.

shortcut: unpinned --no-deps installs of missing modules, recorded via pip freeze; pin into the lock once stable.
"""
import importlib
import subprocess
import sys

PIP = {"cv2": "opencv-python-headless", "sklearn": "scikit-learn", "PIL": "pillow", "yaml": "pyyaml"}
for _ in range(10):
    try:
        importlib.import_module("sam3.model_builder")
        print("sam3.model_builder import OK")
        break
    except ModuleNotFoundError as error:
        name = error.name.split(".")[0]
        print("missing", name, flush=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--no-deps",
                        PIP.get(name, name)], check=True)
        for key in [k for k in sys.modules if k.startswith("sam3")]:
            del sys.modules[key]
else:
    sys.exit("sam3.model_builder still not importable")
