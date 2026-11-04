// N89: the two starter labs validate, the physics lab is open at the front, and its apparatus behaves in the agent's Rapier world.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { TEMPLATES, templateScene, hasPhysicsStations } from '../../Build/web/src/lab-editor/templates.mjs';
import { MAX_OBJECTS, KINDS } from '../../Build/web/src/lab-editor/scene.mjs';
import { simulate } from '../../Build/web/src/lab-editor/agent-run.mjs';
import { fitSimTrace } from '../../Build/web/src/workspace/measure.mjs';

test('blank is an empty grid floor; unknown ids give null', () => {
  assert.deepEqual(TEMPLATES.map((t) => t.id), ['blank', 'physics-lab']);
  const s = templateScene('blank');
  assert.deepEqual([s.room, s.objects], [{ kind: 'plane', floor_y: 0 }, []]);
  assert.equal(templateScene('nope'), null);
});

test('physics lab: three walls, open front, every apparatus kind, room left to add more', () => {
  const s = templateScene('physics-lab');
  const walls = s.objects.filter((o) => o.look?.category === 'wall');
  assert.deepEqual(walls.map((o) => o.id).sort(), ['wall-back', 'wall-left', 'wall-right']);
  const front = Math.max(...walls.map((o) => o.position[2] + o.size[2] / 2));
  assert.ok(s.objects.every((o) => o.position[2] < front), 'nothing sits in front of the open side');
  assert.deepEqual(new Set(s.objects.map((o) => o.kind)), new Set(KINDS));
  assert.ok(MAX_OBJECTS - s.objects.length >= 10);
  assert.ok(templateScene('physics-lab') !== s, 'each call returns a fresh scene');
  assert.ok(hasPhysicsStations(s) && !hasPhysicsStations(templateScene('blank')), 'lab agent suggestions follow the stations');
});

test('physics lab runs: free fall time through the photogate and nothing sinks through floor or benches', async () => {
  const out = await simulate(templateScene('physics-lab'), 1.5);
  const gate = out.traces.find((t) => t.object_id === 'photogate-1').samples[0].value;
  assert.ok(Math.abs(gate - Math.sqrt(2 / 9.81)) < 0.01, 'ball dropped 1 m reaches the gate in ' + gate + ' s');
  for (const t of out.traces) for (const p of t.samples) assert.ok(p.p.every(Number.isFinite) && p.p[1] > 0, t.object_id);
  for (const t of out.traces.filter((x) => x.object_id.startsWith('mass-'))) assert.ok(t.samples.at(-1).p[1] > 0.8, t.object_id + ' stays on the table');
  // Guest Fit trace: fitted only up to the first impact (the browser keeps recording the ball at rest), so it recovers scene g.
  const drop = out.traces.find((t) => t.object_id === 'ball-drop').samples, end = drop.at(-1);
  const rest = Array.from({ length: 40 }, (_, i) => ({ t: end.t + 0.02 * (i + 1), p: [end.p[0], 0.03, end.p[2]] }));
  const q = fitSimTrace({ samples: [...drop, ...rest] });
  assert.ok(q.n <= drop.length && q.n > drop.length - 3 && Math.abs(q.value + 9.81) < 0.2, 'fitted ' + q.value + ' from ' + q.n + '/' + q.total + ' samples');
  assert.equal(fitSimTrace({ samples: drop.slice(0, 3) }), null);
});
