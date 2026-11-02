"""Local-only launcher: load existing credentials without printing or copying them."""
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

if len(sys.argv) != 2 or sys.argv[1] not in ('deploy', 'live', 'status'):
    raise SystemExit('Use launch.py deploy|live|status')

CANONICAL = Path('C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon')
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(CANONICAL / '.env', override=False)
os.environ['R2S_DATA_DIR'] = str(CANONICAL / 'data')
os.environ['PYTHONUTF8'] = '1'
base = ['uv', 'run', '--python', '3.12', '--with', 'modal==1.6.3']
if sys.argv[1:] == ['deploy']:
    command = base + ['modal', 'deploy', 'Build/gpu/sf3d.py']
else:
    command = base + ['--with', 'numpy', '--with', 'pillow', '--with', 'scipy', '--with', 'fastapi', '--with', 'jsonschema',
                      'python', 'evidence/N59/' + ('status.py' if sys.argv[1] == 'status' else 'live.py')]
raise SystemExit(subprocess.call(command, cwd=ROOT, env=os.environ.copy()))
