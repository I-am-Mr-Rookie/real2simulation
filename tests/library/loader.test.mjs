// Python feeds current guest.load_guest() output to stdin; no network or fixture copies.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { loadLibraryEntry, validateTrace } from '../../Build/library/loader.mjs';
import { checkViewerRequest } from '../../Build/web/src/viewer/adapter.mjs';
import { DEFAULT_LIMITS } from '../../Build/web/src/viewer/artifact-loader.mjs';
import { SCALE_UNVERIFIED_BANNER } from '../../Build/web/src/viewer/fixture.mjs';

const { manifest, objects, legacy } = JSON.parse(readFileSync(0, 'utf8'));
const entries = manifest.demos;
const example = legacy.setup;
const scene = legacy.scene;
const playable = entries.find((e) => e.artifact?.kind === 'simulation-trace');
const challenge = entries.find((e) => e.artifact?.kind === 'challenge-record');
const clone = (value) => structuredClone(value);
const fetchObject = async (href, options) => {
  assert.equal(options.redirect, 'error');
  assert.equal(options.credentials, 'omit');
  const sha = href.split('/').at(-1);
  assert.ok(Object.hasOwn(objects, sha));
  const data = Buffer.from(objects[sha], 'base64');
  return new Response(data, { headers: { 'Content-Length': String(data.length) } });
};
const invalid = (pattern) => (error) => {
  assert.equal(error.code, 'INVALID_ARTIFACT');
  assert.match(error.message, pattern);
  return true;
};
const replacePayload = (entry, payload) => {
  const copy = clone(entry);
  const bytes = Buffer.isBuffer(payload) ? payload : Buffer.from(JSON.stringify(payload));
  const sha = createHash('sha256').update(bytes).digest('hex');
  copy.artifact = { ...copy.artifact, sha256: sha, bytes: bytes.length, href: `/api/library/artifacts/${sha}` };
  return [copy, { fetch: async () => new Response(bytes) }];
};

test('all 18 current entries load with only verified traces mountable, no gate/source mutation', async () => {
  const before = JSON.stringify(manifest);
  assert.equal(entries.length, 18);
  for (const entry of entries) {
    let calls = 0;
    const result = await loadLibraryEntry(entry, { fetch: (...args) => { calls++; return fetchObject(...args); } });
    assert.equal(result.label, entry.label);
    assert.equal(result.availability, entry.availability);
    assert.equal(result.canMount, entry.artifact?.kind === 'simulation-trace');
    assert.ok(Object.isFrozen(result));
    if (entry.label === 'UNAVAILABLE') {
      assert.equal(calls, 0);
      assert.equal(result.viewerRequest, null);
      assert.equal(result.metadata, null);
      assert.equal(result.reason, entry.reason);
    } else {
      assert.equal(calls, 1);
      assert.equal(result.scaleLabel, 'SCALE_UNVERIFIED');
      assert.deepEqual(result.defaults, entry.defaults);
      assert.deepEqual(result.source, entry.source);
      assert.deepEqual(result.gates, entry.gates);
      assert.deepEqual(result.limitations, entry.limitations);
      assert.equal(result.displayOnly, true);
      if (entry.artifact.kind === 'scene-descriptor') {
        assert.equal(checkViewerRequest(result.viewerRequest), null);
        assert.equal(result.viewerRequest.scene.scene_id, result.metadata.id);
        assert.equal(result.viewerRequest.scene.evidence, 'reconstructed');
        assert.equal(result.banner, SCALE_UNVERIFIED_BANNER);
        assert.match(result.reason, /render assets are not exposed/);
      } else {
        assert.equal(result.viewerRequest, null);
        assert.match(result.banner, /SIMULATED.*SCALE_UNVERIFIED/);
        assert.ok(!Object.hasOwn(result.metadata, 'gravity_m_s2'));
        assert.ok(!Object.hasOwn(result.metadata, 'trajectory'));
      }
    }
  }
  assert.equal(JSON.stringify(manifest), before);
});

test('projectile trace and pendulum unavailable never substitute synthetic geometry', async () => {
  for (const template of ['projectile', 'pendulum']) {
    const matches = entries.filter((e) => e.id.includes(template));
    assert.ok(matches.length > 0);
    for (const entry of matches) {
      const result = await loadLibraryEntry(entry, { fetch: fetchObject });
      if (entry.availability === 'playable') {
        assert.equal(result.trace.kind, template);
        assert.equal(result.trace.sha256, entry.artifact.sha256);
        assert.equal(result.trace.inputProvenance, 'synthetic');
        assert.ok(Object.isFrozen(result.trace.samples[0].position_m));
      } else {
        assert.equal(result.label, 'UNAVAILABLE');
        assert.equal(result.canMount, false);
      }
      assert.equal(result.viewerRequest, null);
    }
  }
});

test('trace DTO rejects unsafe labels, samples, timing and answer-bearing fields', async () => {
  const trace = JSON.parse(Buffer.from(objects[playable.artifact.sha256], 'base64'));
  for (const mutate of [
    (t) => { t.kind = 'mystery-g'; }, (t) => { t.source = 'measured'; },
    (t) => { t.inputProvenance = 'image-derived'; }, (t) => { t.label = 'MEASURED'; },
    (t) => { t.dt_s = 0; }, (t) => { t.samples = []; },
    (t) => { t.samples = Array(4097).fill(t.samples[0]); },
    (t) => { t.samples[1].step = 9; }, (t) => { t.samples[1].time_s += 1; },
    (t) => { t.samples[1].position_m = [0, 1]; },
    (t) => { t.samples[1].position_m[0] = null; },
    (t) => { t.seed = 42; }, (t) => { t.sha256 = 'self-hash'; },
  ]) {
    const copy = clone(trace); mutate(copy);
    await assert.rejects(loadLibraryEntry(...replacePayload(playable, copy)), invalid(/trace/));
  }
  const sparse = clone(trace); delete sparse.samples[1];
  assert.throws(() => validateTrace(sparse), invalid(/trace/));
  const nonfinite = clone(trace); nonfinite.samples[1].position_m[0] = Infinity;
  assert.throws(() => validateTrace(nonfinite), invalid(/trace/));
  for (const mutate of [
    (e) => { e.availability = 'metadata-only'; }, (e) => { e.label = 'SCALE_UNVERIFIED'; },
    (e) => { e.source.kind = 'clip'; }, (e) => { e.gates.M = 'MET'; },
    (e) => { e.challenge = { mode: 'mystery-g' }; },
  ]) {
    const entry = clone(playable); mutate(entry);
    await assert.rejects(loadLibraryEntry(entry, { fetch: () => assert.fail('must reject before fetch') }), invalid(/invalid/));
  }
});

test('Mystery-g keeps answer withheld and Apollo never fetches', async () => {
  const result = await loadLibraryEntry(challenge, { fetch: fetchObject });
  assert.equal(result.metadata.answer_visibility, 'withheld-until-fit');
  assert.match(result.reason, /not a blind test.*server draws a hidden g.*server-owned fit/);
  const apollo = await loadLibraryEntry(entries.find((e) => e.id === 'apollo'), {
    fetch: () => assert.fail('Apollo must not fetch'),
  });
  assert.match(apollo.reason, /Moon result not measured/);
});

test('malformed/unavailable entries refuse without transport', async () => {
  for (const value of [null, [], {}, { id: 'x' }]) {
    await assert.rejects(loadLibraryEntry(value), invalid(/entry/));
  }
  const apollo = entries.find((e) => e.id === 'apollo');
  for (const patch of [{ artifact: example.artifact }, { reason: null }, { availability: 'playable' }]) {
    await assert.rejects(loadLibraryEntry({ ...apollo, ...patch }, { fetch: () => assert.fail('must not fetch') }),
      invalid(/inconsistent/));
  }
});

test('unknown kind refuses before network', async () => {
  const copy = clone(example); copy.artifact.kind = 'executable';
  await assert.rejects(loadLibraryEntry(copy, { fetch: () => assert.fail('must not fetch') }),
    (e) => e.code === 'UNSUPPORTED' && /kind/.test(e.message));
});

test('URL is the exact hash endpoint, not arbitrary source/audit URLs', async () => {
  for (const href of ['https://example.com/private', '//example.com/a', '/api/library/artifacts/../x',
    example.artifact.href + '?token=x', example.artifact.href + '#x']) {
    const copy = clone(example); copy.artifact.href = href;
    await assert.rejects(loadLibraryEntry(copy, { fetch: () => assert.fail('must not fetch') }), invalid(/URL\/hash/));
  }
});

test('hash mismatch refuses readable error before JSON consumption', async () => {
  const bytes = Buffer.from(objects[example.artifact.sha256], 'base64'); bytes[0] ^= 1;
  await assert.rejects(loadLibraryEntry(example, { fetch: async () => new Response(bytes) }), invalid(/sha256 mismatch/));
});

test('declared oversize/invalid sizes refuse before fetch', async () => {
  for (const size of [0, -1, 1.1, '12', DEFAULT_LIMITS.manifestBytes + 1]) {
    const copy = clone(example); copy.artifact.bytes = size;
    await assert.rejects(loadLibraryEntry(copy, { fetch: () => assert.fail('must not fetch') }), invalid(/size limit/));
  }
});

test('short response, oversized Content-Length and streamed overflow refuse', async () => {
  await assert.rejects(loadLibraryEntry(example, { fetch: async () => new Response('x') }), invalid(/byte length/));
  await assert.rejects(loadLibraryEntry(example, { fetch: async () => new Response('x', {
    headers: { 'Content-Length': String(example.artifact.bytes + 1) },
  }) }), invalid(/size limit/));
  let cancelled = false;
  await assert.rejects(loadLibraryEntry(example, { fetch: async () => new Response(new ReadableStream({
    pull(controller) { controller.enqueue(new Uint8Array(example.artifact.bytes + 1)); },
    cancel() { cancelled = true; },
  })) }), invalid(/size limit/));
  assert.equal(cancelled, true);
});

test('invalid JSON, UTF-8, scalar and array refuse after hash verification', async () => {
  for (const bytes of [Buffer.from('{'), Buffer.from([255]), Buffer.from('null'), Buffer.from('[]')]) {
    await assert.rejects(loadLibraryEntry(...replacePayload(example, bytes)), invalid(/JSON|object/));
  }
});

test('unsafe labels/defaults refuse before network', async () => {
  for (const mutate of [
    (e) => { e.label = 'MEASURED'; }, (e) => { e.scale_verified = true; },
    (e) => { e.defaults.autoplay = true; }, (e) => { e.defaults.physics_enabled = true; },
    (e) => { e.defaults.real_scene_prediction = 'ENABLED'; }, (e) => { e.defaults.parameters = [1]; },
    (e) => { e.availability = 'playable'; }, (e) => { e.artifact.media_type = 'text/javascript'; },
  ]) {
    const copy = clone(example); mutate(copy);
    await assert.rejects(loadLibraryEntry(copy, { fetch: () => assert.fail('must not fetch') }), invalid(/invalid/));
  }
});

test('challenge extra answer, unknown template and invalid timing refuse', async () => {
  const payload = JSON.parse(Buffer.from(objects[challenge.artifact.sha256], 'base64'));
  await assert.rejects(loadLibraryEntry(...replacePayload(challenge, { ...payload, gravity: 9 })), invalid(/setup/));
  const setup = JSON.parse(Buffer.from(objects[example.artifact.sha256], 'base64'));
  for (const patch of [{ template: 'unknown' }, { duration_s: 0 }, { time_step_s: -1 }, { time_step_s: 1e9 }]) {
    await assert.rejects(loadLibraryEntry(...replacePayload(example, { ...setup, ...patch })), invalid(/setup|template/));
  }
  const copy = clone(challenge); copy.challenge.target = 'https://example.com';
  await assert.rejects(loadLibraryEntry(copy, { fetch: fetchObject }), invalid(/answer boundary/));
});

test('scene request identity, scale/evidence, point and asset limits reuse viewer validation', async () => {
  const payload = JSON.parse(Buffer.from(objects[scene.artifact.sha256], 'base64'));
  for (const mutate of [
    (m) => { m.id = '../bad'; }, (m) => { m.synthetic = true; },
    (m) => { m.scale.status = 'measured'; }, (m) => { m.render.point_count = DEFAULT_LIMITS.points + 1; },
    (m) => { m.assets[0].bytes = DEFAULT_LIMITS.assetBytes + 1; },
    (m) => { m.assets[0].path = '../points.ply'; },
  ]) {
    const copy = clone(payload); mutate(copy);
    await assert.rejects(loadLibraryEntry(...replacePayload(scene, copy)), (e) => e.code === 'INVALID_ARTIFACT');
  }
});

test('HTTP failure/network error authored; no upstream secret text', async () => {
  for (const fetch of [async () => new Response('secret upstream', { status: 503 }),
    async () => { throw new Error('secret upstream'); },
    async () => new Response(new ReadableStream({ start(c) { c.error(new Error('secret upstream')); } }))]) {
    await assert.rejects(loadLibraryEntry(example, { fetch }),
      (e) => e.code === 'LOAD_FAILED' && !e.message.includes('secret'));
  }
});

test('selection mutation during transport cannot change checked safety defaults', async () => {
  const copy = clone(example);
  const result = await loadLibraryEntry(copy, { fetch: async (...args) => {
    copy.defaults.physics_enabled = true; copy.label = 'MEASURED'; copy.artifact.sha256 = 'bad';
    return fetchObject(...args);
  } });
  assert.equal(result.defaults.physics_enabled, false);
  assert.equal(result.label, 'SIMULATED');
});

test('aborts refuse before fetch and in-flight signal is forwarded', async () => {
  const c = new AbortController(); c.abort();
  await assert.rejects(loadLibraryEntry(example, { signal: c.signal, fetch: () => assert.fail('aborted') }),
    (e) => e.name === 'AbortError');
  const live = new AbortController();
  await assert.rejects(loadLibraryEntry(example, { signal: live.signal, fetch: async (_href, opts) => {
    assert.equal(opts.signal, live.signal); live.abort(); throw new DOMException('Aborted', 'AbortError');
  } }), (e) => e.name === 'AbortError');
  const duringRead = new AbortController();
  await assert.rejects(loadLibraryEntry(example, { signal: duringRead.signal, fetch: async () => ({
    ok: true, arrayBuffer: async () => {
      duringRead.abort(); return Buffer.from(objects[example.artifact.sha256], 'base64');
    },
  }) }), (e) => e.name === 'AbortError');
});
