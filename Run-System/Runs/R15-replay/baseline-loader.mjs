// Run the unchanged frozen tests against committed pre-fix code without replacing working edits.
import { execFileSync } from 'node:child_process';
import { registerHooks } from 'node:module';
import { fileURLToPath } from 'node:url';

const root = new URL('../../../', import.meta.url);
const target = new URL('Build/simulator/replay.mjs', root).href;
const source = execFileSync('git', ['show', 'f62b095734791798f2fe62149ddcc6d60b8ab7c4:Build/simulator/replay.mjs'], { cwd: fileURLToPath(root) });
const baseline = `data:text/javascript;base64,${source.toString('base64')}`;
registerHooks({ resolve(specifier, context, nextResolve) {
  const resolved = nextResolve(specifier, context);
  return resolved.url === target ? { ...resolved, url: baseline } : resolved;
} });
