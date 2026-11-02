"""Local-only launcher: load existing credentials without printing or copying them."""
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

if sys.argv[1:] != ['live']:
    raise SystemExit('Use launch.py live (one public sample job only)')

CANONICAL = Path('C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon')
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(CANONICAL / '.env', override=False)
os.environ['R2S_DATA_DIR'] = str(CANONICAL / 'data')
os.environ['PYTHONUTF8'] = '1'
base = ['uv', 'run', '--python', '3.12', '--with', 'modal==1.6.3']
command = base + ['--with', 'numpy==2.2.6', '--with', 'pillow==11.3.0', '--with', 'scipy',
                  '--with', 'fastapi==0.124.4', '--with', 'jsonschema==4.23.0', 'python', 'evidence/N63/live.py']
raise SystemExit(subprocess.call(command, cwd=ROOT, env=os.environ.copy()))
