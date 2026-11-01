// S24f capture: beats 8-9. Playwright Chromium. Run: node capture.mjs (env OUT). Videos stay out of Git.
import {createRequire} from 'module';
const require=createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright-core');
import fs from 'fs';import {pathToFileURL} from 'url';
const OUT=process.env.OUT;fs.mkdirSync(OUT,{recursive:true});
const marks={};
const b=await chromium.launch({headless:true});
async function run(name,fn,H=1080){
  const ctx=await b.newContext({viewport:{width:1920,height:H},recordVideo:{dir:OUT+'/_v',size:{width:1920,height:H}}});
  await ctx.addInitScript(()=>{const s=document.createElement('style');s.textContent='video,[poster]{visibility:hidden!important}';(document.head||document.documentElement).appendChild(s)});
  const p=await ctx.newPage();const t0=Date.now();const m=marks[name]={};
  await fn(p,k=>{m[k]=+((Date.now()-t0)/1000).toFixed(1)},n=>p.screenshot({path:OUT+'/'+n+'.png'}));
  const v=p.video();await ctx.close();await v.saveAs(OUT+'/'+name+'.webm');
}
const smooth=(p,y,ms=2500)=>p.evaluate(([y,ms])=>new Promise(r=>{const s=scrollY,t=performance.now();const f=n=>{const k=Math.min(1,(n-t)/ms),e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;scrollTo(0,s+(y-s)*e);k<1?requestAnimationFrame(f):r()};requestAnimationFrame(f)}),[y,ms]);
await run('beat8-card',async(p,mark,shot)=>{await p.goto(pathToFileURL(process.cwd()+'/card.html').href);await p.waitForLoadState('networkidle');await p.waitForTimeout(500);mark('first_row');await p.waitForTimeout(4800);mark('all_rows_visible');await shot('8a-checklist-card');await p.waitForTimeout(2500);mark('end')});
await run('beat9-close',async(p,mark,shot)=>{
  await p.goto('https://github.com/I-am-Mr-Rookie/real2simulation');await p.waitForTimeout(2500);mark('repo_top');await shot('9a-repo-top');await smooth(p,500);await p.waitForTimeout(1500);mark('repo_readme');
  await p.goto('https://github.com/I-am-Mr-Rookie/real2simulation/blob/main/BENCHMARK.md');await p.waitForTimeout(2500);mark('benchmark_top');await shot('9b-benchmark-md');await smooth(p,700);await p.waitForTimeout(1500);mark('benchmark_gates');await shot('9c-benchmark-gates');
  await p.goto('https://web-dev-cd80.up.railway.app/');await p.waitForTimeout(3000);mark('dev_home_hero');await shot('9d-dev-home');await p.waitForTimeout(2000);mark('end');});
fs.writeFileSync(OUT+'/marks.json',JSON.stringify(marks,null,1));await b.close();

