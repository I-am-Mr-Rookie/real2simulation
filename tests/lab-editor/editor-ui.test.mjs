import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';

const read = (p) => readFileSync(new URL('../../Build/web/src/' + p, import.meta.url), 'utf8');
const editor = read('lab-editor/LabEditor.jsx');
const css = read('lab-editor/lab-editor.css');

test('editor and side panels share a bounded width-based height, except fullscreen', () => {
  assert.match(css, /\.le-work \{ --le-stage-height: clamp\(420px, 38cqw, 640px\); container-type: inline-size/);
  assert.match(css, /\.le-side \{[^}]*max-height: var\(--le-stage-height\)/);
  assert.match(css, /\.le-stage \{[^}]*height: var\(--le-stage-height\)/);
  assert.match(css, /--le-stage-height: clamp\(320px, 80cqw, 480px\)/);
  assert.match(css, /\.le-stage:fullscreen \{ width: 100%; height: 100%; min-height: 0; \}/);
  assert.doesNotMatch(css, /height: (?:calc\(100vh|58vh)/);
});

test('SF3D credit is one conditional viewport chip, never a per-object sprite', () => {
  const fixture = validateScene(JSON.parse(readFileSync(new URL('../../evidence/N50/two-sf3d-scene.json', import.meta.url))));
  assert.equal(fixture.objects.filter((o) => o.shape?.type === 'mesh').length, 2);
  assert.doesNotMatch(read('lab-editor/sf3d-shape.mjs'), /Sprite|CanvasTexture|captionSprite/);
  assert.doesNotMatch(editor, /captionSprite/);
  assert.match(editor, /scene\.objects\.some\(\(o\) => o\.shape\?\.type === 'mesh'\) && <span className="le-chip">MODEL-GENERATED shapes · Powered by Stability AI<\/span>/);
  assert.equal(editor.match(/MODEL-GENERATED shapes · Powered by Stability AI/g)?.length, 1);
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

test('Template trials is in the toolbar right group before view/files, not in an editor toggle band', () => {
  const page = read('app/(public)/lab/page.jsx');
  assert.match(page, /!editor && <p className="lab-toggle"/);
  assert.match(page, /<LabEditor onTemplateTrials=\{\(\) => setEditor\(false\)\} \/>/);
  assert.match(css, /main:has\(\.lab-editor\) \{ padding-top: 0\.75rem; \}/);
  assert.match(css, /\.le-top button, \.le-file \{[^}]*margin: 0;/);
  assert.match(editor, /aria-label="View and files">\s*\{onTemplateTrials && <button[^>]*onClick=\{onTemplateTrials\}[^>]*><Ico n="trials" \/>Template trials<\/button>\}/);
});
