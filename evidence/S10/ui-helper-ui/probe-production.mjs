import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { once } from 'node:events';

const web = fileURLToPath(new URL('../../../Build/web/', import.meta.url));
const base = 'http://127.0.0.1:3102';
// Bind-test first: never stop an unrelated listener or reuse its responses.
const check = createServer();
await new Promise((resolve, reject) => { check.once('error', reject); check.listen(3102, '127.0.0.1', resolve); });
await new Promise(resolve => check.close(resolve));
const env = { ...process.env, NODE_ENV: 'production' };
assert.ok(!env.CLERK_SECRET_KEY && !env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, 'expected existing no-key environment');
const child = spawn(process.execPath, ['node_modules/next/dist/bin/next', 'start', '--hostname', '127.0.0.1', '--port', '3102'], {
  cwd: web, env, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'],
});
let output = ''; child.stdout.on('data', b => { output += b; }); child.stderr.on('data', b => { output += b; });
const exited = once(child, 'exit');
const results = { pid: child.pid, host: '127.0.0.1', port: 3102, nodeEnv: 'production', probes: [] };
async function probe(route, options = {}) {
  const response = await fetch(base + route, { ...options, redirect: 'manual', signal: AbortSignal.timeout(10000) });
  const body = await response.text();
  results.probes.push({ route, method: options.method || 'GET', status: response.status, cacheControl: response.headers.get('cache-control') });
  return { response, body };
}
try {
  let ready = false;
  for (let i = 0; i < 60; i++) {
    if (child.exitCode !== null) throw new Error('owned Next process exited before readiness');
    try { const r = await fetch(base + '/lab', { signal: AbortSignal.timeout(1000) }); if (r.status === 200) { ready = true; break; } }
    catch {}
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  assert.ok(ready, 'owned loopback production server readiness');
  const lab = await probe('/lab');
  assert.equal(lab.response.status, 200); assert.match(lab.body, /Test a motion model/);
  const scripts = [...lab.body.matchAll(/<script[^>]+src="([^"]+)"/g)].map(m => m[1]).filter(s => s.startsWith('/_next/static/'));
  assert.ok(scripts.length);
  const browserTexts = [];
  for (const script of scripts) { const r = await probe(script); assert.equal(r.response.status, 200); browserTexts.push(r.body); }
  assert.ok(browserTexts.some(t => t.includes('INVALID_BROWSER_SIMULATION')), 'production /lab actually serves the browser simulator chunk');
  for (const body of ['{"action":"start","template":"free_fall","mystery":false}', '{', '{"action":"fit","sessionId":"synthetic-no-session"}']) {
    const p = await probe('/api/lab', { method: 'POST', headers: { 'content-type': 'application/json', origin: base }, body });
    assert.equal(p.response.status, 403); assert.equal(p.response.headers.get('cache-control'), 'no-store');
    assert.deepEqual(JSON.parse(p.body), { status: 'error', error: { code: 'local_lab_disabled' } });
  }
  const library = await probe('/library'); assert.equal(library.response.status, 200);
  for (const route of ['/sign-in', '/sign-up']) {
    const p = await probe(route); assert.equal(p.response.status, 200); assert.match(p.body, /unavailable/); assert.match(p.body, /not configured/);
  }
  for (const headers of [{}, { 'X-Clerk-Auth-Status': 'signed-in', 'X-Clerk-Auth-User-Id': 'synthetic-probe', Authorization: 'Bearer invalid' }]) {
    const p = await probe('/workspace/synthetic-probe?access=public&ownerId=synthetic-probe', { headers });
    assert.equal(p.response.status, 404); assert.ok(!p.body.includes('data-private-content='));
  }
  results.status = 'PASS';
} finally {
  if (child.exitCode === null) child.kill();
  const [code, signal] = await exited;
  results.stoppedOwnedProcess = { code, signal };
  await writeFile(new URL('./production-server-output.txt', import.meta.url), output);
  await writeFile(new URL('./production-probes.json', import.meta.url), JSON.stringify(results, null, 2) + '\n');
}
console.log(`PASS ${results.probes.length} production HTTP probes; normal chunk served, API disabled, auth unavailable/private denied; owned server stopped`);
