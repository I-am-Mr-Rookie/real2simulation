// N31 headed Playwright Chromium: public /lab editor, import a scene with the live SF3D table (owner room: PRIVATE, so the
// scene, GLB and screenshots stay in OUT, a gitignored dir) and a ball above it, Play, screenshot desktop and 375 px.
// The GLB URL is served from the local file by a Playwright route (no API/BFF needed). No paid calls.
// OUT=<private dir> SCENE=<room scene.json> OBJ=room-object-3 GLB=<file.glb> node evidence/N31/shoot.mjs
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = process.env.BASE || 'http://localhost:3029', OUT = process.env.OUT;
const obj = JSON.parse(fs.readFileSync(process.env.SCENE, 'utf8')).objects.find((o) => o.id === process.env.OBJ);
const scene = { version: 'lab-scene-v1', room: { kind: 'plane', floor_y: 0 }, objects: [obj,
  { id: 'ball-1', kind: 'ball', position: [obj.position[0], obj.position[1] + 0.4, obj.position[2]], size: [0.04, 0.04, 0.04], restitution: 0.5 }] };
fs.writeFileSync(OUT + '/n31-scene.json', JSON.stringify(scene));
const rec = { start_utc: new Date().toISOString(), steps: [], console_errors: [], glb_requests: 0 };
const step = (k, v = true) => { rec.steps.push({ k, v }); console.log(k, typeof v === 'string' ? v.slice(0, 300) : JSON.stringify(v)); };
const b = await chromium.launch({ headless: false });
const p = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
p.on('console', (m) => { if (m.type() === 'error') rec.console_errors.push(m.text().slice(0, 200)); });
await p.route('**/api/workspace/rooms/**/objects/*.glb', (r) => { rec.glb_requests += 1; r.fulfill({ body: fs.readFileSync(process.env.GLB), contentType: 'model/gltf-binary' }); });
try {
  await p.goto(base + '/lab?editor=1');
  await p.locator('[data-testid=lab-editor-canvas] canvas').waitFor({ timeout: 60000 });
  await p.locator('input[type=file][accept=".json,.ply"]').setInputFiles(OUT + '/n31-scene.json');
  await p.getByText(/Scene loaded: 2 objects/).waitFor({ timeout: 15000 });
  await p.waitForTimeout(1500);
  await p.getByRole('button', { name: /Fit view to the room/ }).click();
  await p.getByRole('button', { name: 'Play' }).click();
  await p.waitForFunction(() => parseFloat(document.querySelector('.le-time')?.textContent.replace('t = ', '')) > 0.45, null, { timeout: 30000 });
  await p.getByRole('button', { name: 'Pause' }).click();
  step('time', await p.locator('.le-time').innerText());
  await p.screenshot({ path: OUT + '/n31-table-ball-desktop.png' });
  await p.setViewportSize({ width: 375, height: 812 }); await p.waitForTimeout(800);
  await p.getByRole('button', { name: /Fit view to the room/ }).click(); await p.waitForTimeout(500);
  step('scrollWidth_375', await p.evaluate(() => document.documentElement.scrollWidth));
  await p.screenshot({ path: OUT + '/n31-table-ball-375.png' });
  step('status', await p.locator('.le-status').innerText());
} catch (e) { step('error', String(e).slice(0, 400)); process.exitCode = 1; }
finally { rec.end_utc = new Date().toISOString(); fs.writeFileSync(new URL('./live/screenshots.json', import.meta.url), JSON.stringify(rec, null, 2)); await b.close(); }

