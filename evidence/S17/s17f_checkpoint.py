"""python -m evidence.S17.s17f_checkpoint style run: python evidence/S17/s17f_checkpoint.py (from repo root).
Writes the RM02 checkpoint page. No fitter result exists for a real recorded scene (physics NOT_RUN), so the page is the honest fallback."""
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from Build.reports.checkpoint import load_gate, render_checkpoint, scene_provenance

out = Path("evidence/S17/checkpoint")
out.mkdir(exist_ok=True)
html, fb = render_checkpoint(None, None, scene_provenance("evidence/S14/S14g-fix7-offline.json", "RM02"), load_gate("evidence/S14/GATE_A.json"))
(out / "RM02-checkpoint.html").write_text(html, encoding="utf-8", newline="\n")
(out / "RM02-fallback.json").write_text(json.dumps(fb, indent=1, sort_keys=True) + "\n")
print(fb)
