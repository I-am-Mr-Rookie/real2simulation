"""Regenerate only this child's four synthetic validated exports and server traces."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Build.lab.regression import regression_case
from Build.simulator.export_validated_setup import export


def generate():
    folder = Path(__file__).resolve().parent
    summary = []
    for template in ('free_fall', 'projectile', 'ramp', 'pendulum'):
        with tempfile.TemporaryDirectory() as tmp:
            spec, scene, _ = regression_case(Path(tmp), template)
            artifact = export(spec, scene)
        encoded = json.dumps(artifact, allow_nan=False)
        process = subprocess.run(['node', str(ROOT / 'Build/lab/simulate.mjs')],
                                 input=encoded, capture_output=True, text=True,
                                 encoding='utf-8', check=True, timeout=30, cwd=ROOT)
        trace = json.loads(process.stdout)
        (folder / f'{template}.artifact.json').write_text(encoded + '\n', encoding='utf-8')
        (folder / f'{template}.server-trace.json').write_text(process.stdout + '\n', encoding='utf-8')
        summary.append({'template': template, 'samples': len(trace['samples']),
                        'producer': 'regression_case -> export(validate_setup) -> Build/lab/simulate.mjs'})
    (folder / 'generation.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    generate()
