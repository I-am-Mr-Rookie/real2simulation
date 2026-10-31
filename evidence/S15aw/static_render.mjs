// S15aw static SSR evidence (adapted from evidence/S15an/static_render.mjs): owner-clip result stage with the new result chart.
// FIXTURE responses = jobs.owner_measurement('OWN05'/'OWN01') dumped to FIXTURE-*-measurement.json (python, see REPORT); not a live run.
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { renderShell, toolsOf } from '../../Build/web/src/shell/workspace-shell.mjs';
import { renderWorkspace } from '../../Build/web/src/workspace/view.mjs';
import { THEME_CSS, THEME_OPTIONS, toneOf } from '../../Build/web/src/shell/theme.mjs';
const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = require('react'); const { renderToStaticMarkup } = require('react-dom/server');
const h = React.createElement;
const pub = new URL('../../Build/web/public/', import.meta.url).href;
const css = ['app/styles.css', 'workspace/workspace.css'].map((f) => readFileSync(new URL('../../Build/web/src/' + f, import.meta.url), 'utf8')).join('\n').replaceAll('url("/images/', 'url("' + pub + 'images/').replaceAll('url("/brand/', 'url("' + pub + 'brand/') + '\n' + THEME_CSS;
const stages = [['upload', 'Upload', 'done'], ['interview', 'Interview', 'done'], ['run', 'Run (not run)', 'skipped'], ['fit', 'Fit (not run)', 'skipped'], ['report', 'Report', 'current']].map(([id, label, status]) => ({ id, label, status, failed: false }));
const layout = { phase: 'report.owner', stages, viewport: { banner: null }, jobStatus: { label: 'Clip result (owner clip; no scene, run or fit)', jobId: 'job_FIXTURE', surface: null, error: null } };
const tools = toolsOf({ live: true, phase: 'report.owner', owner: true, jobId: 'job_FIXTURE', uploadStatus: null, hasReport: true, pending: 0 });
for (const clip of ['OWN05', 'OWN01']) {
  const measurement = JSON.parse(readFileSync(new URL('./FIXTURE-' + clip + '-measurement.json', import.meta.url), 'utf8'));
  for (const t of THEME_OPTIONS.filter((o) => o.id !== 'system')) { // system = OS-follow alias of light/dark
    const theme = t.id;
    const ws = renderWorkspace(h, layout, { status: 'empty' }, null, null, undefined, undefined, undefined, undefined, undefined, undefined, undefined, { label: 'RECORDED FIXTURE', measurement });
    const page = renderToStaticMarkup(h('main', { id: 'main' }, h('section', { 'data-private-content': 'live', 'aria-label': 'Private workspace' },
      renderShell(h, { title: 'FIXTURE static S15aw render of the owner-clip result stage (' + clip + ')', rail: { pane: 'navigate', open: false, preview: null }, right: false, tools, pending: 0, agent: null }, {}, {}, null, null, ws))));
    writeFileSync(new URL('./FIXTURE-' + clip + '-' + theme + '.html', import.meta.url), '<!doctype html><html data-theme="' + theme + '" data-tone="' + toneOf(theme) + '"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>' + css + '</style><body style="margin:0">' + page + '</body></html>');
  }
}
console.log(THEME_OPTIONS.map((o) => o.id).join(','));
