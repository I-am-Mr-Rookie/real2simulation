import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';

const read = (p) => readFileSync(new URL('../../Build/web/src/' + p, import.meta.url), 'utf8');
const editor = read('lab-editor/LabEditor.jsx');
const css = read('lab-editor/lab-editor.css');

test('Reset clears running or paused status as well as physics, time and trace selection', () => {
  const body = editor.match(/const stop = \(\) => \{([\s\S]*?)\n  \};/)?.[1];
  assert.ok(body);
  for (const message of ['Running. SIMULATED physics, gravity from the scene vector.', 'Paused. Resume, reset, or export the SIMULATED sensor traces.']) {
    const state = { run: 'playing', time: 2, cursor: 1, traceFit: {}, message };
    let freed = 0;
    const api = { current: { state: { playing: true, sim: { free() { freed++; } } } } };
    const keys = ['run', 'time', 'cursor', 'traceFit', 'message'];
    const setters = keys.map((key) => (value) => { state[key] = value; });
    new Function('api', 'setRun', 'setTime', 'setCursor', 'setTraceFit', 'setMessage', body)(api, ...setters);
    assert.equal(state.run, 'stopped');
    assert.equal(state.time, 0);
    assert.equal(state.cursor, null);
    assert.equal(state.traceFit, null);
    assert.match(state.message, /Ready.*SIMULATED/);
    assert.equal(api.current.state.playing, false);
    assert.equal(api.current.state.sim, null);
    assert.equal(freed, 1);
  }
});

test('graph value, unit and honesty caption wrap on desktop and remain visible on phones', () => {
  const caption = css.match(/\.le-graph figcaption \{([^}]*white-space[^}]*)\}/)?.[1];
  assert.match(caption, /white-space: normal/);
  assert.match(caption, /overflow-wrap: anywhere/);
  for (const property of ['margin', 'padding', 'border']) assert.ok(caption.includes(property + ': 0;'), property);
  assert.doesNotMatch(caption, /overflow: hidden|text-overflow: ellipsis/);
  for (const rule of css.matchAll(/([^{}]+)\{([^{}]*display:\s*none[^{}]*)\}/g)) {
    assert.doesNotMatch(rule[1], /\.le-graph figcaption/);
  }
  const phone = css.slice(css.indexOf('@media (max-width: 900px)'));
  assert.match(phone, /\.le-graph \{[^}]*flex-wrap: wrap/);
  assert.match(phone, /\.le-graph figcaption \{[^}]*flex-basis: 100%;[^}]*max-width: none/);
});

test('N56 full-window app: site header and footer hidden, fixed grid of top bar, work area and timeline', () => {
  assert.match(css, /body:has\(\.lab-editor\) \.site-header, body:has\(\.lab-editor\) \.site-footer/);
  assert.match(css, /\.lab-editor \{[^}]*position: fixed; inset: 0;[^}]*grid-template-rows: auto minmax\(0, 1fr\) auto/);
  assert.match(css, /\.le-stage:fullscreen \{ width: 100%; height: 100%; min-height: 0; \}/);
  for (const x of ['className="le-top"', 'className="le-rail"', 'role="tablist"', 'className="le-float"', 'className="le-timeline"', 'className="le-honesty"', 'aria-label="Lab name"', 'aria-label="Fullscreen"']) assert.ok(editor.includes(x), x);
  // agent panel stays mounted (hidden) so its thread and project scene load survive toggling
  assert.match(editor, /<div hidden=\{!agentOpen\}>\s*<AgentPanel /);
});

test('SF3D credit is one conditional viewport chip, never a per-object sprite', () => {
  const fixture = validateScene(JSON.parse(readFileSync(new URL('../../evidence/N50/two-sf3d-scene.json', import.meta.url))));
  assert.equal(fixture.objects.filter((o) => o.shape?.type === 'mesh').length, 2);
  assert.doesNotMatch(read('lab-editor/sf3d-shape.mjs'), /Sprite|CanvasTexture|captionSprite/);
  assert.doesNotMatch(editor, /captionSprite/);
  assert.match(editor, /scene\.objects\.some\(\(o\) => o\.shape\?\.type === 'mesh'\) \? \[\['MODEL-GENERATED shapes · Powered by Stability AI'/);
  assert.equal(editor.match(/MODEL-GENERATED shapes · Powered by Stability AI/g)?.length, 1);
  for (const w of ['SIMULATED', 'Track MEASURED, ball what-if', 'Room scale unverified', 'MODEL-ESTIMATED collision proxy']) assert.ok(editor.includes("['" + w), w);
  assert.doesNotMatch(editor, /className="le-chip/);
  assert.match(editor, /SHAPE_LABEL \+ ' \(Stable Fast 3D\)/);
});

test('outside-canvas panels allow native scroll chaining and controls target only the canvas', () => {
  for (const selector of ['le-side', 'le-log']) {
    const rule = css.match(new RegExp('\\.' + selector + ' \\{([^}]+)\\}'))?.[1];
    assert.ok(rule, selector);
    assert.match(rule, /overflow-y: auto/);
    assert.doesNotMatch(rule, /overscroll-behavior(?:-y)?:\s*(?:contain|none)/);
  }
  assert.match(editor, /new OrbitControls\(camera, renderer\.domElement\)/);
  assert.match(editor, /new TransformControls\(camera, renderer\.domElement\)/);
  assert.doesNotMatch(editor, /(?:onWheel|onTouchMove)=|addEventListener\(['"](?:wheel|touchmove)['"]/);
  for (const rule of css.matchAll(/([^{}]+)\{([^{}]*touch-action:\s*none[^{}]*)\}/g)) {
    assert.equal(rule[1].trim(), '.le-canvas, .le-canvas canvas');
  }
});

test('Template trials is a Templates section of the Add menu, not a separate toolbar button', () => {
  const page = read('app/(public)/lab/page.jsx');
  assert.match(page, /!editor && <p className="lab-toggle"/);
  assert.match(page, /<LabEditor onTemplateTrials=\{\(\) => setEditor\(false\)\} \/>/);
  assert.match(css, /\.le-top button, \.le-file[^{]*\{[^}]*margin: 0;/);
  assert.match(editor, /aria-label="Templates"><span className="le-menu-h">Templates<\/span>\s*<button type="button" role="menuitem" onClick=\{onTemplateTrials\}>/);
  assert.equal(editor.match(/onClick=\{onTemplateTrials\}/g)?.length, 1);
});
