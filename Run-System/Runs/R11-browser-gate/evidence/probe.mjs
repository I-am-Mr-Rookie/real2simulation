import { handleLab } from '../../../../Build/lab/session-service.mjs';
import { runBrowserSimulation } from '../../../../Build/web/src/lab/browser-simulator.mjs';
const out = [];
for (const t of ['free_fall','projectile','ramp','pendulum']) {
  const r = await handleLab({ action: 'start', template: t, mystery: false });
  const tr = runBrowserSimulation(r.browserSimulation);
  out.push({ t, mode: r.mode, status: r.status, dtoBytes: JSON.stringify(r.browserSimulation).length, producer: r.browserSimulation.validatedSetup.producer, samples: tr.samples.length, integrator: tr.integrator, source: tr.source, prov: tr.inputProvenance, keys: Object.keys(r).sort().join(',') });
}
for (const t of ['free_fall','projectile']) {
  const r = await handleLab({ action: 'start', template: t, mystery: true });
  const s = JSON.stringify(r);
  out.push({ t, mode: r.mode, keys: Object.keys(r).sort().join(','), leak: ['browserSimulation','validatedSetup','seed','gravity','private','setup','magnitude_m_s2'].filter((k) => s.includes(k)) });
  let threw = false; try { runBrowserSimulation({ mode: 'mystery-g', validatedSetup: {} }); } catch (e) { threw = String(e.message).startsWith('INVALID_BROWSER_SIMULATION'); }
  out.at(-1).browserRejectsMystery = threw;
}
const bad = await handleLab({ action: 'start', template: 'ramp', mystery: true });
out.push({ mysteryRamp: bad });
console.log(JSON.stringify(out, null, 1));
