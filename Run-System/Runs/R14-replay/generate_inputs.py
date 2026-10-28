"""Reuse real S08 factories/validator; no analytic or numerical acceptance run."""
import json
import hashlib
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from Build.lab.regression import regression_case
from Build.simulator.export_validated_setup import export

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / 'evidence/S10/replay-invariants'
DEST.mkdir(parents=True, exist_ok=True)
results = []
for template in ('free_fall', 'projectile', 'ramp', 'pendulum'):
    with tempfile.TemporaryDirectory(prefix='r14-replay-') as tmp:
        spec, scene, _ = regression_case(Path(tmp), template)
        artifact = export(spec, scene)
        (DEST / f'{template}-validated.json').write_text(
            json.dumps(artifact, allow_nan=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        replay = subprocess.run(['node', str(ROOT / 'Build/lab/replay-check.mjs')],
                                input=json.dumps(artifact, allow_nan=False), text=True,
                                capture_output=True, encoding='utf-8', timeout=15, cwd=ROOT, check=True)
        results.append({'template': template, 'seed': artifact['spec']['simulation']['seed'],
                        'replay': json.loads(replay.stdout)})

sources = ['Build/simulator/replay.mjs', 'Build/lab/replay-check.mjs', 'Build/lab/regression.py']
(DEST / 'actual-record-hashes.json').write_text(json.dumps({
    'captured_at': datetime.now(timezone.utc).isoformat(),
    'scope': 'existing actual four-template replay transport; simulated synthetic only',
    'sources_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
    'cases': results,
}, indent=2, allow_nan=False) + '\n', encoding='utf-8')
