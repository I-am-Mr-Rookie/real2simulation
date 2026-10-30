// S15t: REAL RM04 what-if observations (S15r spec response -> browser simulator) -> the exact controller /fit request body.
import fs from 'node:fs';
import { runBrowserSimulation } from '../../Build/web/src/lab/browser-simulator.mjs';
import { browserSimulate, fitRequest } from '../../Build/web/src/workspace/controller.mjs';
const r = JSON.parse(fs.readFileSync('evidence/S15r/rm04-spec-response.json', 'utf8'));
const obs = await browserSimulate(runBrowserSimulation)(r.validated_setup);
fs.writeFileSync('evidence/S15t/rm04-fit-request.json', JSON.stringify({ spec: r.spec, what_if_label: r.what_if_label, fit: fitRequest(obs) }, null, 1));
console.log(obs.length, 'samples');
