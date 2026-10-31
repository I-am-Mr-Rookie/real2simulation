
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { initialInterview, reduceInterview } from '../../Build/web/src/workspace/interview.mjs';
import { renderQuestionCard, renderWaiting, pendingOf } from '../../Build/web/src/shell/agent-card.mjs';
import { renderShell, toolsOf } from '../../Build/web/src/shell/workspace-shell.mjs';
const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = require('react'); const { renderToStaticMarkup } = require('react-dom/server');
const h = React.createElement;
const FX = JSON.parse(readFileSync(new URL('../../tests/workspace/fixtures/interview-responses.json', import.meta.url), 'utf8'));
let s = reduceInterview(initialInterview(), { type: 'Q_LOADED', response: FX.responses['authored-three-kinds'], sceneId: FX.scene_id, toolOutputs: FX.tool_outputs });
s = [{ type: 'Q_CHIP', chipId: 'ball' }, { type: 'Q_SUBMIT' }, { type: 'Q_TEXT', text: 'book cover horizontal edge 20.28 cm' }, { type: 'Q_SUBMIT' }, { type: 'Q_CHIP', chipId: 'table' }].reduce(reduceInterview, s);
const pending = pendingOf(s);
const tools = toolsOf({ live: true, phase: 'interview.active', owner: true, jobId: 'synthetic-job', uploadStatus: null, hasReport: false, pending });
const page = (right) => renderToStaticMarkup(renderShell(h, { title: 'Static S15ac render (synthetic fixture, not a measurement)', left: right, right, tools, pending, agent: renderQuestionCard(h, s, () => {}) }, {}, {},
  h('p', { role: 'note' }, 'Owner clip: no scene (reconstruction not run); interview in progress (not a measurement)'), renderWaiting(h, s, () => {}),
  h('section', { className: 'ws-viewport', 'aria-label': 'Scene viewport', style: { margin: '1rem', height: '240px', border: '1px solid #1c1a16', display: 'grid', placeItems: 'center' } }, 'Scene / clip preview stays here')));
const css = readFileSync(new URL('../../Build/web/src/workspace/workspace.css', import.meta.url), 'utf8');
mkdirSync(new URL('./', import.meta.url), { recursive: true });
for (const r of [true, false]) writeFileSync(new URL('./static-' + (r ? 'open' : 'closed') + '.html', import.meta.url), '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>body{margin:0}' + css + '</style>' + page(r));

