// UI-e-orch88 copy of UI-b-orch72 preview harness: + global styles.css tokens, + empty viewer state, + optional code root (for before shots).
// Usage: node evidence/ui/orch88/preview.mjs <out.html> [code-root]
// Original header: UI-b-orch72 preview harness (evidence only, not product code). Renders the REAL workspace view functions with the REAL
// test fixtures (validated interview responses, real fitter output on SYNTHETIC settings, synthetic job fixtures) to static HTML
// so the stylesheet can be screenshotted: the (private) route is fail-closed (notFound) on main, so no live page exists.
// UI-e-orch88 copy: + global styles.css tokens, + empty viewer state, + optional code root for before shots (main checkout).
// Usage: node evidence/ui/orch88/preview.mjs <out.html> [code-root]
import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
const [out, rootArg] = process.argv.slice(2);
const root = rootArg ? pathToFileURL(rootArg.replace(/[\\/]?$/, '/')) : new URL('../../../', import.meta.url);
const m = (p) => import(new URL(p, root));
const { initialState, reduce } = await m('Build/web/src/workspace/workflow.mjs');
const { deps, jobReady, jobFailed } = await m('Build/web/src/workspace/fixtures.mjs');
const { layoutOf } = await m('Build/web/src/workspace/layout.mjs');
const { renderWorkspace, renderInterview } = await m('Build/web/src/workspace/view.mjs');
const { initialInterview, reduceInterview, interviewView } = await m('Build/web/src/workspace/interview.mjs');
const { fitView, renderFit } = await m('Build/web/src/workspace/fit-view.mjs');
const css = ['Build/web/src/app/styles.css', 'Build/web/src/workspace/workspace.css'].map((p) => readFileSync(new URL(p, root), 'utf8')).join('\n');

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const VOID = new Set(['input', 'br', 'img', 'meta']);
const h = (type, props, ...kids) => {
  const p = props ?? {}; let a = '', inner = '';
  for (const [k, v] of Object.entries(p)) {
    if (k === 'key' || k === 'ref' || typeof v === 'function' || v === undefined || v === null || v === false) continue;
    if (type === 'textarea' && k === 'value') { inner = esc(v); continue; }
    const name = k === 'className' ? 'class' : k === 'htmlFor' ? 'for' : k === 'maxLength' ? 'maxlength' : k;
    a += v === true && !name.startsWith('aria-') && !name.startsWith('data-') ? ' ' + name : ' ' + name + '="' + esc(v) + '"';
  }
  const body = inner + kids.flat(Infinity).filter((k) => k !== null && k !== undefined && k !== false).map((k) => (typeof k === 'object' ? k.html : esc(k))).join('');
  return { html: '<' + type + a + '>' + (VOID.has(type) ? '' : body + '</' + type + '>') };
};
const run = (s, ...ev) => ev.reduce((x, e) => reduce(x, e, deps), s);
const ready = run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobReady(1) });
const failed = run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobFailed(1) });
const FX = JSON.parse(readFileSync(new URL('tests/workspace/fixtures/interview-responses.json', root), 'utf8'));
const load = (r) => reduceInterview(initialInterview(), { type: 'Q_LOADED', response: r, sceneId: FX.scene_id, toolOutputs: FX.tool_outputs });
let iv = Object.values(FX.responses).map(load).find((s) => interviewView(s).status === 'asking' && interviewView(s).chips?.length) ?? load(Object.values(FX.responses)[0]);
const chip = interviewView(iv).chips?.[0];
if (chip) iv = reduceInterview(iv, { type: 'Q_CHIP', chipId: chip.id });
const FIT = JSON.parse(readFileSync(new URL('tests/workspace/fixtures/fit-output.json', root), 'utf8'));
const noop = () => {};
const ws = (label, layout, status = 'ready') => renderWorkspace(h, layout, { status, error: null }, null, noop).html;
const card = (title, inner) => '<div class="ws" data-preview="' + esc(title) + '" style="display:block"><section class="ws-panel" style="max-width:40rem"><h2>' + esc(title) + '</h2>' + inner + '</section></div>';
const page = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>UI-e preview (fixtures)</title><style>' + css + '</style></head><body>'
  + '<p style="margin:0;padding:.5rem 1rem;font:600 13px system-ui;background:#1c1a16;color:#fff">PREVIEW HARNESS: real view functions + test fixtures (SYNTHETIC). Not a product route.</p>'
  + ws('ready', layoutOf(ready))
  + card('Interview (validated fixture response)', renderInterview(h, interviewView(iv), noop).html)
  + card('Fit (real fitter output, SYNTHETIC settings)', renderFit(h, fitView({ phase: 'fit.done' }, { times: FIT.request.times, output: FIT.output })).html)
  + ws('failed', layoutOf(failed))
  + ws('empty', layoutOf(initialState()), 'empty')
  + '</body></html>';
writeFileSync(out, page);
console.log('wrote', out, page.length);
