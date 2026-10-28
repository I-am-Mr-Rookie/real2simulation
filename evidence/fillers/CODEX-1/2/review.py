"""Independent synthetic observations and existing-suite execution. No product changes.

Run from checkout root with python -B evidence/fillers/CODEX-1/2/review.py.
All persistent output is inside this file's evidence directory. Exit zero means
observations matched expectations and existing suites passed, not gate success.
"""
import ast
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
tempfile.tempdir = str(OUT)
sys.path[:0] = [str(ROOT), str(ROOT / 'tests/spec')]
from test_setup_validation import setup, BUNDLE
from test_experiment_validation import validator
from Build.templates.free_fall import analytic_free_fall
from Build.templates.projectile import analytic_projectile
from Build.templates.ramp import analytic_ramp
from Build.templates.pendulum import analytic_pendulum

records = []
apis = dict(free_fall=analytic_free_fall, projectile=analytic_projectile,
            ramp=analytic_ramp, pendulum=analytic_pendulum)

# Distinct from the previous probe: both signs plus each sibling's error path.
for name, api in apis.items():
    for sign in (-1, 1):
        spec, scene = setup(name)
        before = copy.deepcopy((spec, scene))
        try:
            api(spec, scene, BUNDLE, times=[sign * 10**1000])
        except Exception as error:
            got = type(error).__name__
            expected = 'OverflowError' if name == 'free_fall' else 'ValueError'
            assert got == expected, (name, got)
            assert (spec, scene) == before
            records.append(dict(case='P1', template=name, sign=sign,
                                status='reproduced', exception=got, message=str(error)))
        else:
            raise AssertionError('huge time accepted')

# Boundary controls: below half an ULP versus one ULP, two independent origins.
for origin_y in (2.0, 4.0):
    for fraction in (0.125, 1.0):
        spec, scene = setup()
        spec['placement']['origin']['value'][1] = origin_y
        height = math.ulp(origin_y) * fraction
        spec['parameters']['drop_height']['value'] = height
        validator.validate_setup(spec, scene, BUNDLE)
        result = analytic_free_fall(spec, scene, BUNDLE)
        t = result['impact_time']['value']
        result = analytic_free_fall(spec, scene, BUNDLE, times=[0, t])
        ys = [s['position']['value'][1] for s in result['samples']]
        collapsed = ys[0] == ys[1]
        assert collapsed == (fraction < 0.5)
        assert t > 0
        records.append(dict(case='P2', status='reproduced' if collapsed else 'boundary-control',
                            origin_y=origin_y, height=height, sample_y=ys,
                            positive_time=t, collapsed=collapsed))

# The intentional domain split must occur at factory as well as oracle entry.
from test_s08_acceptance import api as entries, make_args
for name, field, value in [('ramp', 'friction_coefficient', 10),
                            ('pendulum', 'release_angle', .2)]:
    spec, scene = setup(name)
    spec['parameters'][field]['value'] = value
    spec['simulation']['time_step']['value'] = .0001
    validator.validate_setup(spec, scene, BUNDLE)
    factory, oracle = entries(name)
    for boundary, call in [('factory', lambda: factory(**make_args(spec, scene))),
                           ('oracle', lambda: oracle(spec, scene, BUNDLE))]:
        try:
            call()
        except ValueError as error:
            records.append(dict(case='P3', status='reproduced-intentional-limit',
                                template=name, boundary=boundary, message=str(error)))
        else:
            raise AssertionError('unsupported analytic domain accepted')

# Different ID control isolates ID-only evidence binding from global constant.
spec, scene = setup()
a = analytic_free_fall(spec, scene, BUNDLE)
changed = copy.deepcopy(spec)
changed['parameters']['drop_height']['value'] = .25
b = analytic_free_fall(changed, scene, BUNDLE)
changed['experiment_id'] += '-revision2'
c = analytic_free_fall(changed, scene, BUNDLE)
evidence = lambda r: r['impact_time']['source']['evidence']
assert evidence(a) == evidence(b) != evidence(c)
assert a['impact_time']['value'] != b['impact_time']['value']
records.append(dict(case='P4', status='reproduced-integration-limit',
                    same_id_changed_input_same_evidence=evidence(a) == evidence(b),
                    new_id_changes_evidence=evidence(b) != evidence(c)))

targets = [ROOT / 'contracts/scene/validate_scene.py',
           ROOT / 'contracts/experiment/validate_experiment.py',
           *[ROOT / f'Build/templates/{name}.py' for name in apis]]
hits = {str(p.resolve()): set() for p in targets}
def trace(frame, event, arg):
    filename = frame.f_code.co_filename
    if filename in hits:
        if event == 'line':
            hits[filename].add(frame.f_lineno)
        return trace
    return None

results = []
inventory = []
sys.settrace(trace)
try:
    for directory in ('tests/spec', 'contracts/scene'):
        suite = unittest.TestLoader().discover(str(ROOT / directory), pattern='test_*.py')
        def names(group):
            for test in group:
                if isinstance(test, unittest.TestSuite):
                    yield from names(test)
                else:
                    yield test.id()
        inventory.extend(names(suite))
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
        log = directory.replace('/', '-') + '.txt'
        (OUT / log).write_text(stream.getvalue(), encoding='utf-8')
        results.append(dict(suite=directory, tests=result.testsRun,
                            failures=len(result.failures), errors=len(result.errors),
                            skipped=len(result.skipped), success=result.wasSuccessful(), log=log))
finally:
    sys.settrace(None)

line_map = {}
for path in targets:
    tree = ast.parse(path.read_text(encoding='utf-8'))
    statements = {n.lineno for n in ast.walk(tree) if isinstance(n, ast.stmt)}
    key = str(path.resolve())
    line_map[str(path.relative_to(ROOT))] = dict(
        executed_lines=sorted(hits[key]),
        statement_start_lines_not_seen=sorted(statements - hits[key]),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest())
receipt = dict(scope='offline synthetic observations only; not physics/simulator/gate evidence',
               observations=records, suites=results, tests=inventory,
               line_map=line_map,
               line_map_limits='In-process lines only; imports before tracing and subprocess CLI lines excluded. AST statement starts include definitions. Not branch coverage or a coverage percentage.')
(OUT / 'results.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps(dict(observations=len(records), suites=results), indent=2))
assert all(r['success'] for r in results)
