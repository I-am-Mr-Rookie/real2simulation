import fs from 'node:fs';
import { runBrowserSimulation } from '../../Build/web/src/lab/browser-simulator.mjs';
import { browserSimulate } from '../../Build/web/src/workspace/controller.mjs';
const r = JSON.parse(fs.readFileSync('evidence/S15r/rm04-spec-response.json', 'utf8'));
const obs = await browserSimulate(runBrowserSimulation)(r.validated_setup);
const out = { input: 'evidence/S15r/rm04-spec-response.json (RM04 Q16 path, web answer body tests/workspace/fixtures/rm04-spec-body.json)',
  mode: r.validated_setup.what_if ? 'what-if' : 'normal', label: r.validated_setup.label, scene: r.validated_setup.scene,
  samples: obs.length, first: obs[0], last: obs.at(-1) };
fs.writeFileSync('evidence/S15r/rm04-what-if-run.json', JSON.stringify(out, null, 1));
console.log(JSON.stringify(out));
