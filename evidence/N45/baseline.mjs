// Run the N45 UI regressions against the dispatch base without changing the checkout.
// Expected: four failures. node --import ./evidence/N45/baseline.mjs --test tests/workspace/consistency.test.mjs
import { registerHooks } from 'node:module';
import { execFileSync } from 'node:child_process';
const root = new URL('../../', import.meta.url);
const original = (path) => execFileSync('git', ['show', 'addc05f2f954116e93b1307513f691e738682c20:' + path], { encoding: 'utf8' });
const panel = new URL('Build/web/src/lab-editor/AgentPanel.jsx', root).href;
const live = new URL('Build/web/src/workspace/live-view.mjs', root).href;
const test = new URL('tests/workspace/consistency.test.mjs', root).href;
const panelSource = original('Build/web/src/lab-editor/AgentPanel.jsx');
const liveSource = original('Build/web/src/workspace/live-view.mjs');
registerHooks({
  resolve(s, ctx, next) {
    if (s === 'node:fs' && ctx.parentURL === test) return { shortCircuit: true, url: 'data:text/javascript,' + encodeURIComponent(
      `import {readFileSync as read} from 'node:fs'; export const readFileSync=(p,...a)=>String(p)===${JSON.stringify(panel)}?${JSON.stringify(panelSource)}:read(p,...a);`) };
    return next(s, ctx);
  },
  load(url, ctx, next) {
    return url === live ? { format: 'module', source: liveSource, shortCircuit: true } : next(url, ctx);
  },
});
