import test from 'node:test';
import assert from 'node:assert/strict';
import { guessProxy } from '../../Build/web/src/app/api/guess/proxy.mjs';

const TOKEN = 'a'.repeat(32);
const env = { WORKSPACE_API_URL: 'http://api:1/' };
const req = (body) => new Request('http://x/', { method: 'POST', body });

test('bad token never reaches the API', async () => {
  const f = () => assert.fail('fetched');
  for (const t of ['x', '../internal', TOKEN + 'a', undefined]) assert.equal((await guessProxy(req('{}'), t, false, env, f)).status, 404);
});

test('GET and reveal map to the public API paths only, no auth headers', async () => {
  const seen = [];
  const f = async (url, init) => { seen.push([url, init.method, init.headers]); return new Response('{"ok":1}', { status: 200 }); };
  assert.equal((await guessProxy(req(), TOKEN, false, env, f)).status, 200);
  const r = await guessProxy(req('{"guess":9.8}'), TOKEN, true, env, f);
  assert.equal(r.headers.get('cache-control'), 'no-store');
  assert.deepEqual(seen.map((s) => s.slice(0, 2)), [['http://api:1/public/guess/' + TOKEN, 'GET'], ['http://api:1/public/guess/' + TOKEN + '/reveal', 'POST']]);
  assert.ok(seen.every((s) => !('x-workspace-token' in s[2])));
});

test('oversized reveal body, missing config and upstream failure', async () => {
  assert.equal((await guessProxy(req('1'.repeat(1001)), TOKEN, true, env, () => assert.fail())).status, 413);
  assert.equal((await guessProxy(req(), TOKEN, false, {}, () => assert.fail())).status, 503);
  assert.equal((await guessProxy(req(), TOKEN, false, env, async () => { throw new Error('down'); })).status, 502);
});
