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
  const email='s24e-'+Date.now().toString(36)+'+clerk_test@example.com';
  await p.goto(base+'/sign-up');await p.locator('input[name=emailAddress]').fill(email);await p.locator('input[name=emailAddress]').press('Enter');
  await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({timeout:60000});await p.keyboard.type('424242');
  await p.waitForURL(u=>!/sign-up/.test(u.pathname),{timeout:60000});await p.waitForTimeout(2500);
  if(!/workspace/.test(p.url()))await p.goto(base+'/workspace');await p.waitForURL(/workspace\/.+/,{timeout:30000});await p.waitForTimeout(1500);
  const finish=async()=>{const v=p.video();await ctx.close();await v.saveAs(OUT+'/'+name+'.webm');};
  return {p,mark,shot,finish};
}



const OWNF=process.env.OWN05,RMF=process.env.RM04;
const dump=async(p,t)=>console.log('##',t,(await p.innerText('body')).replace(/\S+@\S+/g,'<email>').replace(/\s+/g,' ').slice(0,1800));
const T=(p,ms)=>p.waitForTimeout(ms);
const step=async(n,fn)=>{try{await fn()}catch(e){console.log('ERR',n,e.message.slice(0,200))}};
{const {p,mark,shot,finish}=await open('beat6-own05',1920,1080);
await T(p,2000);mark('workspace_ready');
await p.setInputFiles('input[type=file]',OWNF);mark('upload_started');
await p.locator('textarea:visible').first().waitFor({timeout:60000});await T(p,3000);mark('agent_question');await shot('a1-agent-question-chips');
await step('chip',async()=>{await p.getByText('the length recorded with this clip').first().click();await T(p,2500);mark('chip_selected');await shot('a2-chip-selected');
await p.getByRole('button',{name:/finish/i}).first().click();mark('answer_sent');
await p.getByText(/g = /).first().waitFor({timeout:40000});await T(p,3500);mark('result');await shot('a3-validated-result');await dump(p,'RESULT')});
await finish();}
{const {p,mark,shot,finish}=await open('beat6-rm04',1920,1080);
await T(p,2000);mark('workspace_ready');await p.setInputFiles('input[type=file]',RMF);mark('upload_started');
await step('rm04',async()=>{for(let i=1;i<=3;i++){await p.locator('textarea:visible').first().waitFor({timeout:120000});await T(p,3000);mark('q'+i);await shot('b'+i+'-rm04-question');await dump(p,'RM04 Q'+i);
 const chip=p.locator('button:visible',{hasText:/^1\n/}).first();
 if(await chip.count()){await chip.click();await T(p,1500);}
 await shot('b'+i+'x-rm04-answer');await p.getByRole('button',{name:/finish|next|send/i}).first().click();mark('a'+i);await T(p,4000);}
 await T(p,4000);mark('after');await shot('b4-rm04-after');await dump(p,'RM04 AFTER')});
await finish();}
{const {p,mark,shot,finish}=await open('beat7-sidebar',1920,1080);
await step('sidebar',async()=>{await T(p,2000);await dump(p,'WS');await p.getByText('Agent & tools').first().scrollIntoViewIfNeeded();await shot('c1-sidebar-tools');
 const s=p.getByPlaceholder(/search/i).first();if(await s.count()){await s.fill('free fall');await s.press('Enter');await T(p,4000);mark('search');await shot('c2-sidebar-search');await dump(p,'SEARCH')}else console.log('no search box')});
await finish();}
const ctx=await b.newContext({viewport:{width:1920,height:1080},recordVideo:{dir:OUT+'/_v',size:{width:1920,height:1080}}});
const p=await ctx.newPage();const m=marks.beat7={};const t0=Date.now();const mk=k=>m[k]=+((Date.now()-t0)/1000).toFixed(1);
await step('library',async()=>{await p.goto(base+'/library');await T(p,3500);mk('library');await p.screenshot({path:OUT+'/d1-library.png'});await dump(p,'LIB');await p.mouse.wheel(0,700);await T(p,2500);mk('library_scrolled');await p.screenshot({path:OUT+'/d2-library-scrolled.png'})});
await step('lab',async()=>{await p.goto(base+'/lab');await T(p,3500);mk('lab');await p.screenshot({path:OUT+'/e1-lab.png'});await dump(p,'LAB');await p.mouse.wheel(0,600);await T(p,2500);mk('lab_scrolled');await p.screenshot({path:OUT+'/e2-lab-scrolled.png'})});
await step('home',async()=>{await p.goto(base+'/');await T(p,2500);mk('home');await p.screenshot({path:OUT+'/f1-home.png'});for(let i=0;i<8;i++){await p.mouse.wheel(0,260);await T(p,700)}mk('home_end');await p.screenshot({path:OUT+'/f2-home-scrolled.png'})});
const v=p.video();await ctx.close();await v.saveAs(OUT+'/beat7-library-lab-home.webm');
fs.writeFileSync(OUT+'/marks.json',JSON.stringify(marks,null,1));console.log(JSON.stringify(marks));
await b.close();
