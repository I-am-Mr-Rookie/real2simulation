// N42 headed Playwright Chromium: public /lab editor, import the live room shell scene (walls with openings + kept
// furniture; owner room PRIVATE, so scene, GLBs and screenshots stay in OUT, a gitignored dir) with a ball above the
// detected table, Play, screenshot desktop and 375 px. GLBs are served from the job's objects dir by a Playwright route.
// OUT=<private dir> JOB=<room job dir> OBJ=<table id> node evidence/N42/shoot.mjs
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = process.env.BASE || 'http://localhost:3039', OUT = process.env.OUT, JOB = process.env.JOB;
const full = JSON.parse(fs.readFileSync(JOB + '/scene.json', 'utf8'));
const obj = full.objects.find((o) => o.id === process.env.OBJ);
const scene = { version: 'lab-scene-v1', room: { kind: 'plane', floor_y: 0 }, objects: [...full.objects,
  { id: 'ball-1', kind: 'ball', position: [obj.position[0], obj.position[1] + obj.size[1] / 2 + 0.3, obj.position[2]], size: [0.12, 0.12, 0.12], restitution: 0.3 }] };
fs.writeFileSync(OUT + '/n42-scene.json', JSON.stringify(scene));
const rec = { start_utc: new Date().toISOString(), objects: scene.objects.length, steps: [], console_errors: [], glb_requests: 0 };
const step = (k, v = true) => { rec.steps.push({ k, v }); console.log(k, typeof v === 'string' ? v.slice(0, 300) : JSON.stringify(v)); };
const b = await chromium.launch({ headless: false });
const p = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
p.on('console', (m) => { if (m.type() === 'error') rec.console_errors.push(m.text().slice(0, 200)); });
await p.route('**/api/workspace/rooms/**/objects/*.glb', (r) => { rec.glb_requests += 1; const id = r.request().url().split('/').pop(); r.fulfill({ body: fs.readFileSync(JOB + '/objects/' + id), contentType: 'model/gltf-binary' }); });
try {
  await p.goto(base + '/lab?editor=1');
  await p.locator('[data-testid=lab-editor-canvas] canvas').waitFor({ timeout: 60000 });
  await p.locator('input[type=file][accept=".json,.ply"]').setInputFiles(OUT + '/n42-scene.json');
  await p.getByText(/Scene loaded/).waitFor({ timeout: 15000 });
  await p.waitForTimeout(2000);
  await p.getByRole('button', { name: /Fit view to the room/ }).click();
  await p.getByRole('button', { name: 'Play' }).click();
  await p.waitForFunction(() => parseFloat(document.querySelector('.le-time')?.textContent.replace('t = ', '')) > 1.5, null, { timeout: 30000 });
  await p.getByRole('button', { name: 'Pause' }).click();
  step('time', await p.locator('.le-time').innerText());
  await p.screenshot({ path: OUT + '/n42-shell-ball-desktop.png' });
  await p.setViewportSize({ width: 375, height: 812 }); await p.waitForTimeout(800);
  await p.getByRole('button', { name: /Fit view to the room/ }).click(); await p.waitForTimeout(500);
  step('scrollWidth_375', await p.evaluate(() => document.documentElement.scrollWidth));
  await p.screenshot({ path: OUT + '/n42-shell-ball-375.png' });
  step('status', await p.locator('.le-status').innerText());
} catch (e) { step('error', String(e).slice(0, 400)); process.exitCode = 1; }
finally { rec.end_utc = new Date().toISOString(); fs.writeFileSync(new URL('./live/screenshots.json', import.meta.url), JSON.stringify(rec, null, 2)); await b.close(); }


