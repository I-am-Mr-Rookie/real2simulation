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


{const {p,mark,shot,finish}=await open('beat6-rm04-run',1920,1080);
await T(p,2000);await p.setInputFiles('input[type=file]',RMF);mark('upload_started');
await step('rm04',async()=>{
 await p.locator('textarea:visible').first().waitFor({timeout:120000});await T(p,2500);mark('q1');
 await p.locator('textarea:visible').first().pressSequentially('1.5',{delay:90});await T(p,1200);mark('typed1');await shot('k1-rm04-q1-typed');
 await p.getByRole('button',{name:/continue/i}).first().click();await T(p,3500);mark('q2');await shot('k2-rm04-q2-chip');
 await p.locator('button:visible',{hasText:/Starts at rest/}).first().click();await T(p,1500);mark('chip2');
 await p.getByRole('button',{name:/continue/i}).first().click();await T(p,3500);mark('q3');
 await p.locator('button:visible',{hasText:/A four paper/}).first().click();await T(p,1500);mark('chip3');await shot('k3-rm04-q3-chip');
 await p.getByRole('button',{name:/finish/i}).first().click();mark('sent3');
 await T(p,12000);mark('result');await shot('k4-rm04-result');await dump(p,'RM04 RESULT');
 await p.getByRole('button',{name:/^run/i}).first().click();mark('run_clicked');await T(p,15000);mark('run_done');await shot('j1-rm04-run');await dump(p,'RM04 RUN');await p.mouse.wheel(0,700);await T(p,3000);mark('run_scrolled');await shot('j2-rm04-run-scrolled')});
await finish();}
fs.writeFileSync(OUT+'/marks4.json',JSON.stringify(marks,null,1));console.log(JSON.stringify(marks));await b.close();


