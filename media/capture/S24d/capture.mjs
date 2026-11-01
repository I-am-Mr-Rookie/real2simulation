// S24d capture: real DEV product, Playwright Chromium. Run: node capture.mjs (env OWN05, RM04, OUT, HEADLESS=0). Videos stay out of Git.
import {createRequire} from 'module';
const require=createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright-core');
import fs from 'fs';
const base='https://web-dev-cd80.up.railway.app';
const OUT=process.env.OUT;fs.mkdirSync(OUT,{recursive:true});
const OWN=process.env.OWN05,RM04=process.env.RM04;
const marks={};
const b=await chromium.launch({headless:process.env.HEADLESS==='1'});
async function open(name,W,H){
  const ctx=await b.newContext({viewport:{width:W,height:H},recordVideo:{dir:OUT+'/_v',size:{width:W,height:H}}});
  // privacy: owner clips never visible; injected before any navigation
  await ctx.addInitScript(()=>{const s=document.createElement('style');s.textContent='video,[poster]{visibility:hidden!important}';(document.head||document.documentElement).appendChild(s)});
  const p=await ctx.newPage();const t0=Date.now();const m=marks[name]={};
  const mark=k=>{m[k]=+((Date.now()-t0)/1000).toFixed(1)};
  const shot=n=>p.screenshot({path:OUT+'/'+n+'.png'});
  const email='s24d-'+Date.now().toString(36)+'+clerk_test@example.com';
  await p.goto(base+'/sign-up');await p.locator('input[name=emailAddress]').fill(email);await p.locator('input[name=emailAddress]').press('Enter');
  await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({timeout:60000});await p.keyboard.type('424242');
  await p.waitForURL(u=>!/sign-up/.test(u.pathname),{timeout:60000});await p.waitForTimeout(2500);
  if(!/workspace/.test(p.url()))await p.goto(base+'/workspace');await p.waitForURL(/workspace\/.+/,{timeout:30000});await p.waitForTimeout(1500);
  const finish=async()=>{const v=p.video();await ctx.close();await v.saveAs(OUT+'/'+name+'.webm');};
  return {p,mark,shot,finish};
}
async function flow(name,W,H,pre){
  const {p,mark,shot,finish}=await open(name,W,H);
  await p.waitForTimeout(1500);mark('workspace_ready');await p.waitForTimeout(2500);await shot(pre+'a1-workspace');
  await p.setInputFiles('input[type=file]',OWN);mark('upload_started');
  await p.getByText(/Queued|Processing|Waiting|question/i).first().waitFor({timeout:60000}).catch(()=>{});await p.waitForTimeout(2500);await shot(pre+'a2-upload');
  await p.locator('textarea:visible').first().waitFor({timeout:60000});await p.waitForTimeout(3000);mark('agent_question');await shot(pre+'a3-agent-question');
  await p.locator('textarea:visible').first().pressSequentially('book cover horizontal edge 20.28 cm',{delay:70});await p.waitForTimeout(2000);mark('known_size_typed');await shot(pre+'a4-known-size');
  await p.getByRole('button',{name:/finish|send|submit/i}).first().click();mark('answer_sent');
  await p.getByText(/g = /).first().waitFor({timeout:40000});await p.waitForTimeout(3500);mark('fit_shown');await shot(pre+'b1-chart-fit-band');
  // reveal: held-out prediction (dashed) vs recorded suffix points (hollow)
  await p.evaluate(()=>window.scrollTo(0,0));await p.waitForTimeout(4000);mark('heldout_reveal');await shot(pre+'b2-heldout-reveal');
  await p.getByText('Show data table').first().click();await p.waitForTimeout(3000);mark('data_table');await shot(pre+'b3-data-table');
  await p.getByText('Show data table').first().click().catch(()=>{});
  await p.getByText(/^g = 8|g = \d/).first().scrollIntoViewIfNeeded();await p.waitForTimeout(3500);mark('g_headline');await shot(pre+'c1-g-headline');
  await p.getByText(/Held-out points \(3\)/).first().evaluate(e=>e.scrollIntoView({block:'start',behavior:'smooth'}));await p.waitForTimeout(3500);mark('caveats');await shot(pre+'c2-caveats');
  await p.getByRole('button',{name:/report/i}).first().click({timeout:8000});await p.waitForTimeout(3500);mark('report_body');await shot(pre+'c3-report');
  await p.mouse.wheel(0,500);await p.waitForTimeout(3000);mark('report_scrolled');await shot(pre+'c4-report-scrolled');
  fs.writeFileSync(OUT+'/'+pre+'body.txt',(await p.innerText('body')).replace(/\S+@\S+/g,'<email>'));
  await finish();
}
async function viewer(){
  const {p,mark,shot,finish}=await open('d-viewer',1920,1080);
  await p.waitForTimeout(2000);mark('workspace_ready');await p.setInputFiles('input[type=file]',RM04);mark('upload_started');
  await p.locator('canvas').first().waitFor({timeout:120000});await p.waitForTimeout(5000);mark('viewer_loaded');await shot('d1-viewer');
  const c=await p.locator('canvas').first().boundingBox();const cx=c.x+c.width/2,cy=c.y+c.height/2;
  await p.mouse.move(cx,cy);await p.mouse.down();await p.mouse.move(cx+160,cy+30,{steps:40});await p.mouse.up();await p.waitForTimeout(3000);mark('orbited');await shot('d2-viewer-orbit');
  fs.writeFileSync(OUT+'/d-body.txt',(await p.innerText('body')).replace(/\S+@\S+/g,'<email>'));
  await finish();
}
const only=process.env.ONLY||'aebcd';
try{
 if(only.includes('a'))await flow('abc-flow',1920,1080,'');
 if(only.includes('d'))await viewer();
 if(only.includes('e'))await flow('e-backup-1280',1280,720,'e-');
}catch(e){console.log('ERR',e.message.slice(0,400))}
fs.writeFileSync(OUT+'/marks.json',JSON.stringify(marks,null,1));console.log(JSON.stringify(marks));
await b.close();






