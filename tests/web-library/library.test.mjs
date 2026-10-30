import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtempSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { GUEST_SCRIPT, artifactResponse, manifestResponse } from '../../Build/web/src/app/api/library/guest.mjs';
import { traceFromBody } from '../../Build/web/src/viewer/trajectory-replay.mjs';
import { readFileSync } from 'node:fs';
import { MYSTERY_COPY, TAG, creditLine, groupDemos } from '../../Build/web/src/app/(public)/library/library-copy.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const dir = mkdtempSync(path.join(os.tmpdir(), 's04k-'));
// Same command stage.py runs at staging time: the real load_guest() projection.
const raw = execFileSync('python', ['-B', '-c', GUEST_SCRIPT], { cwd: root, maxBuffer: 4 << 20, windowsHide: true });
const write = (name, bytes) => { const f = path.join(dir, name); writeFileSync(f, bytes); return f; };
const snap = write('guest.json', raw);
const res = await manifestResponse(snap);
const manifest = await res.json();
const byId = Object.fromEntries(manifest.demos.map((d) => [d.id, d]));

test('manifest labels: playable SIMULATED, unavailable with reason, mystery answer-free', () => {
  assert.equal(res.status, 200); assert.match(res.headers.get('etag'), /^"[a-f0-9]{64}"$/);
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

test('snapshot is exactly the load_guest projection: objects = manifest artifacts, no answers', () => {
  const { objects } = JSON.parse(raw);
  const refs = manifest.demos.filter((d) => d.artifact).map((d) => d.artifact.sha256);
  assert.deepEqual(Object.keys(objects).sort(), [...new Set(refs)].sort());
  const decoded = Object.values(objects).map((b) => Buffer.from(b, 'base64').toString('utf8')).join('\n');
  assert.doesNotMatch(JSON.stringify(manifest) + decoded, /true_g|"answer"/);
});

test('artifact route: strict id, 404 unknown, immutable verified bytes replay', async () => {
  assert.equal((await artifactResponse('../manifest.json', snap)).status, 400);
  assert.equal((await artifactResponse('A'.repeat(64), snap)).status, 400);
  assert.equal((await artifactResponse('0'.repeat(64), snap)).status, 404);
  for (const id of ['simulated-projectile-baseline-short', 'simulated-pendulum-short-small-angle']) {
    const { sha256, href } = byId[id].artifact;
    assert.equal(href, '/api/library/artifacts/' + sha256);
    const res = await artifactResponse(sha256, snap);
    assert.equal(res.status, 200); assert.match(res.headers.get('cache-control'), /immutable/);
    assert.equal(res.headers.get('etag'), `"${sha256}"`);
    const bytes = new Uint8Array(await res.arrayBuffer());
    assert.equal(createHash('sha256').update(bytes).digest('hex'), sha256);
    const trace = await traceFromBody(bytes, sha256);
    assert.equal(trace.label, 'SIMULATED'); assert.ok(trace.samples.length > 1);
  }
});

test('corrupt or oversize snapshot fails closed with 503, no data', async () => {
  const parsed = JSON.parse(raw);
  const [id, b64] = Object.entries(parsed.objects)[0];
  const tampered = { ...parsed, objects: { ...parsed.objects, [id]: Buffer.from(Buffer.from(b64, 'base64') + ' ').toString('base64') } };
  const dropped = { ...parsed, objects: Object.fromEntries(Object.entries(parsed.objects).slice(1)) };
  const bad = { tampered: JSON.stringify(tampered), dropped: JSON.stringify(dropped), json: '{nope', big: ' '.repeat((4 << 20) + 1) };
  for (const [name, body] of Object.entries(bad)) {
    const file = write(name + '.json', body);
    assert.equal((await manifestResponse(file, root)).status, 503, name);
    assert.equal((await artifactResponse(id, file, root)).status, 503, name);
  }
});

test('missing snapshot: production 503; local dev falls back to live python, broken root 503', async () => {
  const missing = path.join(dir, 'absent.json');
  const env = process.env.NODE_ENV;
  process.env.NODE_ENV = 'production';
  try { assert.equal((await manifestResponse(missing, root)).status, 503); } finally { process.env.NODE_ENV = env ?? ''; if (env === undefined) delete process.env.NODE_ENV; }
  const dev = await manifestResponse(missing, root);
  assert.equal(dev.status, 200); assert.deepEqual(await dev.json(), manifest);
  assert.equal((await manifestResponse(missing, path.join(root, 'no-such-dir'))).status, 503);
});

test('S04l copy: honest Mystery-g wording, visible labels and credits on real manifest', () => {
  assert.match(MYSTERY_COPY, /not a blind test/); assert.match(MYSTERY_COPY, /hidden g/);
  const src = readFileSync(path.join(root, 'Build/web/src/app/(public)/library/LibraryClient.jsx'), 'utf8');
  assert.doesNotMatch(src + MYSTERY_COPY, /answer is withheld/i);
  for (const l of ['SIMULATED', 'SCALE_UNVERIFIED', 'UNAVAILABLE']) assert.match(src + JSON.stringify(TAG), new RegExp(l));
  const { ready, unavailable } = groupDemos(manifest.demos);
  assert.equal(ready.length + unavailable.length, manifest.demos.length);
  assert.ok(unavailable.every((d) => TAG[d.availability] === 'UNAVAILABLE' && d.reason));
  for (const d of ready) { assert.match(TAG[d.availability], /^SIMULATED/); assert.match(creditLine(d), /^Credit: SIMULATED/); }
  assert.match(creditLine({ source: { kind: 'footage', creator: 'A', licence: 'CC BY' } }), /A · CC BY/);
  assert.match(creditLine({}), /no media/);
});

