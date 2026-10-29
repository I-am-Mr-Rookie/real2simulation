"""Rebuild derived traces from frozen bytes; accept only after S08 oracle checks."""
import hashlib
import importlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
FOLDER = ROOT / 'evidence/S10/browser-simulation'
OUT = Path(__file__).resolve().parent
TEMPLATES = ('free_fall', 'projectile', 'ramp', 'pendulum')
BASE = 'b37f7b8'


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


sources = ['Build/lab/simulate.mjs', 'Build/simulator/rk4.mjs',
           'Build/simulator/extended-templates.mjs', 'Build/simulator/trajectories.mjs',
           'Build/web/src/lab/browser-simulator.mjs', 'Build/lab/regression.py',
           'Build/simulator/export_validated_setup.py',
           'evidence/S10/browser-simulation/generate_fixtures.py',
           'evidence/S10/browser-simulation/generation.json',
           'tests/lab/browser-simulator.test.mjs', 'tests/simulator/r14-invariants.test.mjs',
           'evidence/S10/numerical-invariants/validated-cases.json',
           *[f'Build/templates/{t}.py' for t in TEMPLATES]]
artifacts = git('ls-files', '--', 'experiments', 'evidence/S10/browser-simulation/*.artifact.json').decode().splitlines()
frozen_evidence = git('ls-files', '--', 'evidence/S10/numerical-invariants',
                      'evidence/S10/extension-replay', 'evidence/S10/replay-invariants',
                      'evidence/S10/replay-recovery').decode().splitlines()
immutable_paths = sorted(set(sources + artifacts + frozen_evidence))
before = {p: sha((ROOT / p).read_bytes()) for p in immutable_paths}
assert all(before[p] == sha(git('cat-file', '--filters', f'{BASE}:{p}')) for p in immutable_paths)
origin = git('log', '-1', '--format=%H', BASE, '--',
             'evidence/S10/browser-simulation/*.server-trace.json').decode().strip()
source_hashes = {p: {'snapshot_origin_git_blob_sha256': sha(git('show', f'{origin}:{p}')),
                     'current_git_blob_sha256': sha(git('show', f'{BASE}:{p}')),
                     'current_checkout_sha256': before[p]} for p in sources
                 if p.startswith('Build/')}
rows, pending = [], {}
command = ['node', str(ROOT / 'Build/lab/simulate.mjs')]
for template in TEMPLATES:
    artifact_path = FOLDER / f'{template}.artifact.json'
    raw = artifact_path.read_bytes()
    artifact = json.loads(raw)
    # Same actual CLI as generate_fixtures.py; never recreate/write an artifact.
    run = subprocess.run(command, input=raw, cwd=ROOT, capture_output=True, check=True, timeout=30)
    repeat = subprocess.run(command, input=raw, cwd=ROOT, capture_output=True, check=True, timeout=30)
    assert run.stdout == repeat.stdout, f'{template}: nondeterministic CLI'
    trace = json.loads(run.stdout)
    samples = trace['samples']
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        shutil.copyfile(ROOT / 'test-data/synthetic/scene/room-v1/points.ply', folder / 'points.ply')
        # Accepted S08 oracle itself validates the unchanged spec/scene/assets.
        module = importlib.import_module(f'Build.templates.{template}')
        reference = getattr(module, f'analytic_{template}')(
            artifact['spec'], artifact['scene'], folder,
            times=[s['time_s'] for s in samples])
    assert len(samples) == len(reference['samples'])
    position_error = max(math.dist(s['position_m'], a['position']['value'])
                         for s, a in zip(samples, reference['samples']))
    if template == 'pendulum':
        scale = artifact['spec']['parameters']['length']['value'] * reference['amplitude']['value']
    elif template == 'ramp':
        scale = max(a['distance']['value'] for a in reference['samples'])
    else:
        start = artifact['spec']['placement']['origin']['value']
        scale = max(math.dist(start, a['position']['value']) for a in reference['samples'])
    assert math.isfinite(scale) and scale > 0
    relative_error = position_error / scale
    assert math.isfinite(relative_error) and relative_error <= 0.005, (template, relative_error)
    path = FOLDER / f'{template}.server-trace.json'
    snapshot_path = path.relative_to(ROOT).as_posix()
    old_blob = git('show', f'{BASE}:{snapshot_path}')
    old_bytes = git('cat-file', '--filters', f'{BASE}:{snapshot_path}')
    old = json.loads(old_bytes)
    assert {k: v for k, v in old.items() if k != 'samples'} == {
        k: v for k, v in trace.items() if k != 'samples'}
    assert len(old['samples']) == len(samples)
    assert [s['time_s'] for s in old['samples']] == [s['time_s'] for s in samples]
    # Preserve the existing checkout's newline convention, not an unrelated EOL edit.
    new_bytes = run.stdout + (b'\r\n' if old_bytes.endswith(b'\r\n') else b'\n')
    assert path.read_bytes() in (old_bytes, new_bytes), f'{template}: unexpected edited snapshot'
    pending[path] = new_bytes
    rows.append(dict(template=template, samples=len(samples), artifact_sha256=sha(raw),
                     old_snapshot_sha256=sha(old_bytes), new_snapshot_sha256=sha(new_bytes),
                     old_snapshot_git_blob_sha256=sha(old_blob),
                     new_snapshot_git_blob_sha256=sha(run.stdout + b'\n'),
                     changed=old_bytes != new_bytes, cli_stdout_sha256=sha(run.stdout),
                     oracle=reference['method'], max_position_error_m=position_error,
                     characteristic_scale_m=scale, relative_error=relative_error,
                     threshold=0.005, passed=True, deterministic=True, metadata_unchanged=True,
                     changed_sample_count=sum(a != b for a, b in zip(old['samples'], samples)),
                     max_old_new_scalar_delta={key: max(abs(a[key] - b[key])
                         for a, b in zip(old['samples'], samples))
                         for key, value in samples[0].items() if isinstance(value, (int, float))},
                     max_old_new_position_distance_m=max(math.dist(a['position_m'], b['position_m'])
                         for a, b in zip(old['samples'], samples)),
                     max_old_new_velocity_distance_m_s=max(math.dist(a['velocity_m_s'], b['velocity_m_s'])
                         for a, b in zip(old['samples'], samples))))

# All four independent checks succeed BEFORE any snapshot is accepted/written.
assert before == {p: sha((ROOT / p).read_bytes()) for p in immutable_paths}
for path, data in pending.items():
    if path.read_bytes() != data:
        path.write_bytes(data)
after = {p: sha((ROOT / p).read_bytes()) for p in immutable_paths}
assert before == after
receipt = dict(base_commit=git('rev-parse', BASE).decode().strip(),
               snapshot_origin_commit=origin,
               current_source_commit=git('rev-parse', 'HEAD').decode().strip(),
               source_hashes=source_hashes,
               immutable_before_sha256=before, immutable_after_sha256=after,
               immutable_byte_identical=True,
               checkout_note='Git core.autocrlf=true; raw checkout and canonical Git blob hashes are distinct',
               command=command, stdin='original *.artifact.json bytes (not re-exported)',
               generation_command='python -B evidence/S10/consumer-recovery/regenerate.py',
               original_generator='inspected, not executed: rewrites artifacts; CLI path reused',
               node_version=subprocess.check_output(['node', '--version'], text=True).strip(),
               python_version=sys.version, cases=rows,
               acceptance='four frozen synthetic inputs only; not broad Gate P or physical evidence')
(OUT / 'generation-verification.json').write_text(json.dumps(receipt, indent=2, allow_nan=False) + '\n', encoding='utf-8')
print(json.dumps({'immutable_byte_identical': True, 'cases': rows}, indent=2))
