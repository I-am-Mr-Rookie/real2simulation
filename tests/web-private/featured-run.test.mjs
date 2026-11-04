import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile, access } from 'node:fs/promises';
import { chartGeom, gravityCheck } from '../../Build/web/src/workspace/measure.mjs';
import { trajectoryScene } from '../../Build/web/src/workspace/measure.mjs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';
import { simulate } from '../../Build/web/src/lab-editor/agent-run.mjs';

// N89: the public featured run must be the stored live result verbatim (no hand-typed numbers).
const read = async (p) => JSON.parse(await readFile(new URL('../../' + p, import.meta.url), 'utf8'));

test('featured run is a verbatim copy of the N07 live ST03 result and renders', async () => {
  const shown = await read('Build/web/src/app/(public)/home/featured-st03.json');
  assert.deepEqual(shown, await read('evidence/N07/live-st03.json'));
  assert.deepEqual(await read('Build/web/src/app/(public)/home/featured-agent.json'), await read('evidence/N28/run1-turns.json'));
  // N89: the measured Muse card is a field-for-field projection of the recorded DEV turn
  const ev = await read('evidence/N89/muse-measures-sample.json'), calls = ev.body.tool_calls, start = calls.find((c) => c.name === 'start_experiment_track');
  assert.deepEqual(await read('Build/web/src/app/(public)/home/featured-agent-measured.json'), {
    utc: ev.utc, model: ev.body.model, sent: ev.sent, tools: calls.map((c) => c.name), target: start.args.target,
    known_size: start.args.known_size, quantity: calls.at(-1).output.quantity, frames: calls.at(-1).output.segment.frames, reply: ev.body.reply });
  const r = shown.result;
  assert.equal(r.fit.x.model, 'constant_acceleration'); // the card says acceleration wins on both axes
  assert.equal(r.fit.y.model, 'constant_acceleration');
  assert.ok(chartGeom(r).curve);
  assert.match(gravityCheck(r).text, /^what-if: .* mm in the plane of the fall/);
  await access(new URL('../../Build/web/public/featured/st03-frames.webp', import.meta.url));
  const jsx = await readFile(new URL('../../Build/web/src/app/(public)/home/FeaturedRun.jsx', import.meta.url), 'utf8');
  assert.doesNotMatch(jsx, /\u2014/);
  assert.match(jsx, /Roman Odintsov, Pexels License/);
});

test('featured phone drop is a verbatim copy of the N89 OWN07 live result, near Earth g, with no clip published', async () => {
  const shown = await read('Build/web/src/app/(public)/home/featured-own07.json');
  assert.deepEqual(shown, await read('evidence/N89/live-own07-book-drop.json'));
  const r = shown.result;
  assert.equal(r.units, 'm');
  assert.equal(r.fit.y.model, 'constant_acceleration');
  assert.match(gravityCheck(r).text, /^Consistent with Earth g/);
  assert.ok(chartGeom(r).curve);
  await assert.rejects(access(new URL('../../Build/web/public/samples/own07-book-drop.mp4', import.meta.url))); // owner clip stays private
});

test('public OWN07 replay: at the fitted g the SIMULATED ball lands on the last MEASURED dot, at 9.81 it runs ahead', async () => {
  const sweep = await read('Build/web/src/app/(public)/home/featured-own-sweep.json');
  assert.deepEqual(sweep, await read('evidence/N89/own-sweep/summary.json'));
  assert.equal(sweep.rows.length, 12); // every owner clip, none dropped
  assert.deepEqual(sweep.rows.map((x) => x.clip), Array.from({ length: 12 }, (_, i) => 'OWN' + String(i + 1).padStart(2, '0')));
  const r = (await read('Build/web/src/app/(public)/home/featured-own07.json')).result, tEnd = r.trajectory.t_s.at(-1);
  const endY = async (g) => {
    const t = trajectoryScene(r);
    t.scene.gravity = [0, -g, 0];
    const s = (await simulate(validateScene(t.scene), tEnd)).traces[0].samples;
    return [s.reduce((b, x) => (Math.abs(x.t - tEnd) < Math.abs(b.t - tEnd) ? x : b)).p[1], t.track.at(-1)[1]];
  };
  const [fit, dot] = await endY(r.quantity.value), [earth] = await endY(9.81);
  assert.ok(Math.abs(fit - dot) < 0.03, 'fitted g: ball ' + fit + ' vs dot ' + dot);
  assert.ok(dot - earth > 0.015, 'Earth g: ball ' + earth + ' vs dot ' + dot);
});

test('public ST03 replay: at the fitted gravity (px read as mm) the SIMULATED ball lands on the last tracked dot', async () => {
  const r = (await read('Build/web/src/app/(public)/home/featured-st03.json')).result, t = trajectoryScene(r);
  t.scene.gravity = [0, -+(r.quantity.value / 1000).toFixed(3), 0]; // same as LabEditor loadSample
  const tEnd = r.trajectory.t_s.at(-1), out = await simulate(validateScene(t.scene), tEnd);
  const s = out.traces[0].samples, last = s.reduce((b, x) => (Math.abs(x.t - tEnd) < Math.abs(b.t - tEnd) ? x : b));
  assert.ok(Math.abs(last.p[1] - t.track.at(-1)[1]) < 0.03, 'ball y ' + last.p[1] + ' vs dot ' + t.track.at(-1)[1]);
});
