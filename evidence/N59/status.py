"""Read-only proof of the SF3D pool and canonical GPU-dot state, never starts a GPU call."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import modal
from Build.api import gpu
from Build.reconstruction import live_room

stats = modal.Function.from_name('r2s-sf3d', 'generate').get_current_stats()
result = {'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
          'sf3d': {'runners': stats.num_total_runners, 'backlog': stats.backlog},
          'gpu_dot': gpu.status('n59_public_rm04', gpu.modal_stats())}
name = 'idle-asleep.json' if stats.num_total_runners == 0 else 'idle-warm.json'
live_room._write(ROOT / 'evidence/N59' / name, result)
print(json.dumps(result))
