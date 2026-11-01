// Static evidence still: text copied from evidence/S14/GATE_A.json /verdict and /label (read at run time).
import {createRequire} from 'module';import fs from 'fs';
const {chromium}=createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/')('playwright-core');
const g=JSON.parse(fs.readFileSync(process.env.GATE,'utf8'));
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.setContent('<body style="margin:0;background:#f7f7f7;font-family:sans-serif;display:grid;place-items:center;height:100vh"><div style="text-align:center"><div style="font:24px monospace;color:#555">GATE A (static evidence: evidence/S14/GATE_A.json)</div><div style="font-size:64px;font-weight:700;margin:24px">'+g.verdict+' — '+g.label+'</div></div></body>');
await p.screenshot({path:'l1-gate-a-static.png'});await b.close();
