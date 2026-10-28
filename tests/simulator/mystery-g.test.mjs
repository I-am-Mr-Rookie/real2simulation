import assert from 'node:assert/strict';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { createMysteryGSession, createTrustedFitterHandoff, publicMysteryGPayload } from '../../Build/simulator/mystery-g.mjs';
import { spawnSync } from 'node:child_process';
const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const base = { seed: 42, gravity_m_s2: 9.81, privateSetup: { chamber: 'sealed' }, observations: [0, 1, 2, 3].map((time_s) => ({ time_s, position_m: 4.905 * time_s * time_s })) };
const python = (code) => spawnSync('python', ['-c', code], { encoding: 'utf8', cwd: repoRoot });

test('allowlisted public projection cannot leak arbitrary observation metadata', async () => { const s = await createMysteryGSession(base); const p = publicMysteryGPayload(s); assert.deepEqual(Object.keys(p.observations[0]).sort(), ['position_m', 'time_s']); assert.doesNotMatch(JSON.stringify(p), /gravity|seed|setup|secret|"g"/); await assert.rejects(() => createMysteryGSession({ ...base, observations: [{ time_s: 0, position_m: 1, g: 9.81 }] })); });

test('actual Python S11 response binds to same observations and preserves source', async () => { const code = "import json; from Build.fitter.api import handle; q=lambda v,u:{'value':v,'unit':u,'uncertainty':0.001,'source':{'label':'simulated','evidence':'x'}}; print(json.dumps(handle({'times':[q(0,'s'),q(1,'s'),q(2,'s'),q(3,'s')],'positions':[q(0,'m'),q(4.905,'m'),q(19.62,'m'),q(44.145,'m')],'degree':2})))"; const out = python(code); assert.equal(out.status, 0, out.stderr); assert.equal(out.stderr, ''); assert.ok(out.stdout.trim(), 'Python fitter returned empty JSON'); const handoff = await createTrustedFitterHandoff(JSON.parse(out.stdout), base.observations); const s = await createMysteryGSession(base); const revealed = s.revealFit(handoff); assert.equal(revealed.reveal.source, 'simulated'); assert.throws(() => s.revealFit(handoff)); });

test('version, mutation, and cross-session binding are enforced', async () => { await assert.rejects(() => createMysteryGSession({ ...base, version: { secret: 9.81 } })); const out = python("import json; print(json.dumps({'status':'ok','gravity':{'value':9.81,'unit':'m/s^2','uncertainty':.1,'source':{'label':'simulated','evidence':'x'}},'covariance':{'status':'available'},'uncertainty':{'model':'iid_fixed_clock_scale'}}))"); assert.equal(out.status, 0, out.stderr); assert.ok(out.stdout.trim()); const result = JSON.parse(out.stdout); const handoff = await createTrustedFitterHandoff(result, base.observations); const other = await createMysteryGSession({ ...base, observations: [{ time_s: 0, position_m: 3 }] }); result.gravity.value = NaN; assert.throws(() => other.revealFit(handoff)); });
