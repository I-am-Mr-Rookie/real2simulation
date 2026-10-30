import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import { readFile, readdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const web = fileURLToPath(new URL('../../', import.meta.url));
const app = path.join(web, 'src/app');
// No real credentials, sessions, email or OAuth calls in either smoke mode.
const configured = process.argv.includes('--synthetic-clerk');
const bindHost = process.argv.includes('--container-bind') ? '0.0.0.0' : 'localhost';
const sentinel = 'sk_test_S04C_SYNTHETIC_SERVER_SENTINEL';
const syntheticPublicKey = 'pk_test_' + Buffer.from('example.clerk.accounts.dev$').toString('base64');
async function checkIsolation(folder) {
  for (const entry of await readdir(folder, { withFileTypes: true })) {
    const item = path.join(folder, entry.name);
    if (entry.isDirectory()) await checkIsolation(item);
    else if (/\.(jsx|js|mjs)$/.test(entry.name)) {
      const source = await readFile(item, 'utf8');
      assert.doesNotMatch(source.replace("import '../../workspace/workspace.css';", ''), /(?:from\s*|import\s*\()['"][^'"]*(?:\/viewer\/|\/workspace\/)/,
        'shell routes must not import viewer/workspace internals');
    }
  }
}
await checkIsolation(app);
const probe = createServer();
await new Promise(resolve => probe.listen(0, '127.0.0.1', resolve));
const port = probe.address().port;
await new Promise(resolve => probe.close(resolve));
const server = spawn(process.execPath, [path.join(web, 'node_modules/next/dist/bin/next'), 'start',
  '--hostname', bindHost, '--port', String(port)], {
  cwd: web, env: { ...process.env, NEXT_TELEMETRY_DISABLED: '1', CLERK_TELEMETRY_DISABLED: '1',
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: configured ? syntheticPublicKey : '',
    CLERK_SECRET_KEY: configured ? sentinel : '' }, stdio: ['ignore', 'pipe', 'pipe']
});
let logs = '';
server.stdout.on('data', chunk => { logs += chunk; });
server.stderr.on('data', chunk => { logs += chunk; });
let processError;
server.on('error', error => { processError = error; });
// Clerk resumes via a same-URL rewrite; use Next's canonical localhost origin, not a different loopback alias.
const base = `http://localhost:${port}`;
const get = (route) => fetch(base + route, { signal: AbortSignal.timeout(3000), redirect: 'manual' });
try {
  let ready = false;
  for (let i = 0; i < 100; i++) {
    if (processError) throw processError;
    if (server.exitCode !== null) throw new Error('Server exited: ' + logs);
    try { if ((await get('/')).status === 200) { ready = true; break; } } catch {}
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  assert.ok(ready, 'server must start within 20 seconds: ' + logs);
  for (const [route, status, content] of [
    ['/', 200, 'Real2Simulation'],
    ['/icon.svg', 200, '<svg'],
    ['/library', 200, 'No demos are published yet'],
    ['/sign-in', 200, configured ? 'Sign in to Real2Simulation' : 'Sign-in unavailable'],
    ['/sign-in/factor-one', 200, configured ? 'Sign in to Real2Simulation' : 'Sign-in unavailable'],
    ['/sign-up', 200, configured ? 'Join Real2Simulation' : 'Sign-up unavailable'],
    ['/workspace', 404, 'Private workspaces require sign-in'],
    ['/workspace/probe-private-id', 404, 'Private workspaces require sign-in'],
    ['/health/live', 404, 'Page unavailable'],
    ['/health/ready', 404, 'Page unavailable'],
    ['/library/not-an-approved-entry', 404, 'Page unavailable'],
    ['/not-a-route', 404, 'Page unavailable']
  ]) {
    const response = await get(route);
    const body = await response.text();
    assert.equal(response.status, status, route);
    assert.ok(body.includes(content), route + ' content');
    assert.ok(!body.includes(sentinel), 'server credential sentinel must not enter HTML/RSC');
    if (!configured) assert.ok(!body.includes(syntheticPublicKey),
      'missing runtime config must not reuse a build-time Clerk provider');
    assert.doesNotMatch(body, /data-private-content=/, 'private child must not be rendered');
    console.log(`PASS ${route} -> ${status}`);
  }
  const forged = await fetch(base + '/workspace/probe-private-id', {
    headers: { Cookie: '__session=not-a-verified-session', 'X-User-Id': 'demo-user' },
    signal: AbortSignal.timeout(3000), redirect: 'manual'
  });
  assert.equal(forged.status, 404, 'unverified client identity must not grant access');
  console.log('PASS forged client identity -> 404');
  for (const headers of [
    { RSC: '1' },
    { Authorization: 'Bearer not-a-verified-token', 'X-Owner-Id': 'demo-user' },
    { 'X-Clerk-Auth-Status': 'signed-in', 'X-Clerk-Auth-User-Id': 'demo-user' },
  ]) {
    const privateUrl = base + '/workspace/probe-private-id?access=public&ownerId=demo-user';
    let response = await fetch(privateUrl, {
      headers, signal: AbortSignal.timeout(3000), redirect: 'manual'
    });
    // Next16 canonicalizes an RSC request missing its cache-busting hash. Follow
    // only this same-resource redirect, never a login redirect or another host.
    if (headers.RSC && response.status === 307) {
      const canonical = new URL(response.headers.get('location'), base);
      const original = new URL(privateUrl);
      assert.equal(canonical.origin, original.origin);
      assert.equal(canonical.pathname, original.pathname);
      assert.ok(canonical.searchParams.has('_rsc'));
      canonical.searchParams.delete('_rsc');
      assert.equal(canonical.search, original.search);
      response = await fetch(new URL(response.headers.get('location'), base), {
        headers, signal: AbortSignal.timeout(3000), redirect: 'manual'
      });
    }
    const body = await response.text();
    if (headers.RSC) {
      // Flight streams carry notFound as an error digest after headers are sent.
      assert.equal(response.status, 200);
      assert.ok(body.includes('NEXT_HTTP_ERROR_FALLBACK;404'), 'RSC must carry denial, not a workspace');
    } else {
      assert.equal(response.status, 404, 'forged auth metadata must deny');
    }
    assert.ok(!body.includes(sentinel));
    assert.doesNotMatch(body, /data-private-content=/);
  }
  const guest = await fetch(base + '/library?sceneId=probe-private-id&access=private', {
    headers: { Cookie: '__session=invalid', Authorization: 'Bearer invalid' },
    signal: AbortSignal.timeout(3000), redirect: 'manual'
  });
  assert.equal(guest.status, 200, 'guest library must not depend on Clerk session validity');
  assert.ok((await guest.text()).includes('No demos are published yet'));
  for (const [route, status] of [['/library', 200], ['/workspace/probe-private-id', 404]]) {
    const response = await fetch(base + route, {
      method: 'HEAD', signal: AbortSignal.timeout(3000), redirect: 'manual'
    });
    assert.equal(response.status, status, 'HEAD ' + route);
  }
  console.log('PASS RSC404 digest, forged auth metadata, public query isolation and HEAD boundaries');
  console.log(`PASS source isolation; production HTTP smoke (${configured ? 'synthetic-config SSR only' : 'missing-config'})`);
} catch (error) {
  console.error('Smoke server diagnostics:', logs.replaceAll(sentinel, '[synthetic-server-key]').replaceAll(syntheticPublicKey, '[synthetic-public-key]'));
  throw error;
} finally {
  server.kill();
  if (server.exitCode === null) await new Promise(resolve => server.once('exit', resolve));
}
