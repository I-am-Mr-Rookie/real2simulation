import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const web = fileURLToPath(new URL('../../', import.meta.url));
let count = 0;
async function walk(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) await walk(file);
    else if (/\.(js|map)$/.test(entry.name)) {
      const body = await readFile(file, 'utf8');
      assert.ok(!body.includes('sk_test_S04C_SYNTHETIC_SERVER_SENTINEL'), 'server sentinel in browser asset');
      assert.doesNotMatch(body, /(?:sk_(?:test|live)_[A-Za-z0-9_-]{16,}|GOOGLE_CLIENT_SECRET)/,
        'secret-shaped credential or custom Google secret in browser asset');
      count++;
    }
  }
}
await walk(path.join(web, '.next/static'));
assert.ok(count > 0, 'must inspect a real build');
const serverConfig = await readFile(new URL('./server-config.js', import.meta.url), 'utf8');
assert.ok(serverConfig.startsWith("import 'server-only';"));
console.log(`PASS ${count} emitted browser JS/map assets; server-only config boundary`);
