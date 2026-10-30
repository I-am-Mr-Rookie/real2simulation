import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { artifactResponse, manifestResponse } from '../../Build/web/src/app/api/library/guest.mjs';
import { traceFromBody } from '../../Build/web/src/viewer/trajectory-replay.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const manifest = await (await manifestResponse(root)).json();
const byId = Object.fromEntries(manifest.demos.map((d) => [d.id, d]));

test('manifest labels: playable SIMULATED, unavailable with reason, mystery answer-free', () => {
  for (const id of ['simulated-projectile-baseline-short', 'simulated-pendulum-short-small-angle']) {
    assert.equal(byId[id].label, 'SIMULATED'); assert.equal(byId[id].availability, 'playable');
  }
  for (const d of manifest.demos.filter((d) => d.label === 'UNAVAILABLE')) {
    assert.equal(d.artifact, null); assert.ok(d.reason.length > 0);
  }
  const m = byId['simulated-mystery-g'];
  assert.equal(m.availability, 'metadata-only'); assert.equal(m.challenge.answer_visibility, 'withheld-until-fit');
  assert.doesNotMatch(JSON.stringify(m), /"answer"|true_g/);
});

test('artifact route: strict id, 404 unknown, immutable verified bytes replay', async () => {
  assert.equal((await artifactResponse('../manifest.json', root)).status, 400);
  assert.equal((await artifactResponse('A'.repeat(64), root)).status, 400);
  assert.equal((await artifactResponse('0'.repeat(64), root)).status, 404);
  for (const id of ['simulated-projectile-baseline-short', 'simulated-pendulum-short-small-angle']) {
    const { sha256, href } = byId[id].artifact;
    assert.equal(href, '/api/library/artifacts/' + sha256);
    const res = await artifactResponse(sha256, root);
    assert.equal(res.status, 200); assert.match(res.headers.get('cache-control'), /immutable/);
    const bytes = new Uint8Array(await res.arrayBuffer());
    assert.equal(createHash('sha256').update(bytes).digest('hex'), sha256);
    const trace = await traceFromBody(bytes, sha256);
    assert.equal(trace.label, 'SIMULATED'); assert.ok(trace.samples.length > 1);
  }
});

test('broken root fails closed with 503, no data', async () => {
  const res = await manifestResponse(path.join(root, 'no-such-dir'));
  assert.equal(res.status, 503);
});
