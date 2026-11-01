import {createRequire} from 'module';import fs from 'fs';
const require=createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright-core');
const base='https://web-dev-cd80.up.railway.app';
const OWN='C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/Videos for Meta AI Hackathon/05_repeat_a__035711.mp4';
const D=decodeURIComponent(new URL('.',import.meta.url).pathname.slice(1));
const mode=process.argv[2];// f1 f2 f3 neg guest
const red=s=>String(s).replace(/\S+@\S+/g,'<email>').replace(/\?[^\s]*/g,'');
const rec={mode,steps:{},alerts:{},notes:{}};const t0=performance.now();const iso=()=>new Date().toISOString();rec.start_utc=iso();
const lap=k=>{rec.steps[k]={utc:iso(),ms:Math.round(performance.now()-t0)};};
const b=await chromium.launch({headless:false});
const ctx=await b.newContext({viewport:{width:1280,height:900}});const p=await ctx.newPage();
const cons=[],fails=[];p.on('console',m=>{if(m.type()==='error')cons.push(red(m.text()).slice(0,120))});
p.on('response',r=>{if(r.status()>=400)fails.push({status:r.status(),path:new URL(r.url()).pathname.slice(0,60)})});
p.on('requestfailed',r=>fails.push({status:'failed',path:new URL(r.url()).pathname}));
rec.api=[];p.on('response',async r=>{try{const u=new URL(r.url());if(!u.pathname.startsWith('/api/workspace')||r.request().method()==='GET'&&!/answer|interview/.test(u.pathname))return;const t=await r.text();rec.api.push({m:r.request().method(),status:r.status(),path:u.pathname.replace(/[0-9a-f]{20,}|job_[0-9a-f]+/g,'<id>').slice(0,70),setup_validated:(t.match(/setup_validated\\W+(true|false)/)||[])[1]||null,excerpt:t.replace(/\\S+@\\S+/g,'<email>').slice(0,260)})}catch(e){}});
const probe=async()=>p.evaluate(()=>({title:document.title,alerts:[...document.querySelectorAll('[role=alert]')].map(e=>e.innerText.trim()),live:[...document.querySelectorAll('[aria-live]')].map(e=>e.getAttribute('aria-live')+': '+e.innerText.trim())}));
const shot=n=>p.screenshot({path:D+n+'.png'});
try{
if(mode==='guest'){
 await p.goto(base+'/library');lap('library');await p.waitForTimeout(2500);
 rec.notes.library_text=(await p.innerText('body')).slice(0,400);
 const card=p.getByRole('link',{name:/mystery|simulated|demo|g/i}).first();
 const c2=(await card.count())?card:p.getByRole('button').first();
 await c2.click({timeout:10000});await p.waitForTimeout(2500);lap('card_open');rec.notes.url=new URL(p.url()).pathname;
 const t=await p.innerText('body');rec.notes.simulated_label=/SIMULATED/.test(t);
 const snap=async()=>p.evaluate(()=>[...document.querySelectorAll('svg')].map(s=>s.innerHTML.length+':'+(s.querySelector('circle,ellipse')?.getAttribute('cy')||s.querySelector('circle,ellipse')?.getAttribute('transform')||'')).join('|'));
 const a=await snap();await shot('guest-before');
 const pb=p.getByRole('button',{name:/play|replay|start/i}).first();rec.notes.play_button=await pb.count();
 if(rec.notes.play_button){await pb.click();}
 await p.waitForTimeout(1500);const a2=await snap();await p.waitForTimeout(1500);const a3=await snap();await shot('guest-playing');
 rec.notes.frames_differ=(a!==a2)||(a2!==a3);rec.notes.snap=[a,a2,a3].map(x=>x.slice(0,120));
 rec.notes.body_excerpt=t.split('\n').filter(l=>/SIMULATED|simulator|measurement|side/i.test(l)).slice(0,6);
}else{
 const email='s22l-'+mode+'-'+Date.now().toString(36)+'+clerk_test@example.com';rec.account_alias='s22l-'+mode+'-***';
 await p.goto(base+'/');lap('home');rec.title_home=await p.title();await shot(mode+'-home');
 const su=p.getByRole('link',{name:/sign up|get started|try/i}).first();if(await su.count())await su.click().catch(()=>{});
 if(!/sign-up/.test(p.url()))await p.goto(base+'/sign-up');lap('signup_page');
 await p.locator('input[name=emailAddress]').fill(email);await p.locator('input[name=emailAddress]').press('Enter');
 await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({timeout:60000});await p.keyboard.type('424242');
 await p.waitForURL(u=>!/sign-up/.test(u.pathname),{timeout:60000});lap('signed_up');await p.waitForTimeout(2000);
 if(!/workspace/.test(p.url()))await p.goto(base+'/workspace');await p.waitForURL(/workspace\/.+/,{timeout:30000});lap('workspace');
 rec.workspace_path=new URL(p.url()).pathname.replace(/[0-9a-f-]{12,}/g,'<id>');
 await shot(mode+'-workspace');
 rec.version=await p.evaluate(async()=>{const o={};for(const u of ['/api/workspace/version','/api/version']){try{const r=await fetch(u);o[u]=r.status+' '+(await r.text()).slice(0,200)}catch(e){o[u]='err'}}return o});
 rec.web_build=await p.evaluate(()=>(document.documentElement.innerHTML.match(/buildId":"([^"]+)"/)||[])[1]||null);
 rec.probe_before=await probe();
 await p.addStyleTag({content:'video{visibility:hidden!important}'});
 await p.setInputFiles('input[type=file]',OWN);
 await p.getByText(/Queued|Processing|ready|question|Waiting/i).first().waitFor({timeout:60000}).catch(()=>{});lap('uploaded');
 const jm=p.url().match(/workspace\/([^/?#]+)/);rec.job_id=jm?jm[1]:null;
 await p.locator('textarea:visible').first().waitFor({timeout:60000}).catch(()=>{if(!(0))rec.notes.no_textarea=true});
 if(!(await p.locator('textarea:visible').count())){await p.getByRole('button',{name:/answer in agent panel|^agent/i}).first().click({timeout:8000}).catch(()=>{});await p.waitForTimeout(800);}
 lap('interview_ready');
 const panel=await p.evaluate(()=>{const ta=document.querySelector('textarea');let n=ta;for(let i=0;i<4&&n&&n.parentElement;i++)n=n.parentElement;return {q:(n?.innerText||'').slice(0,500),buttons:[...(n?.querySelectorAll('button')||[])].map(x=>x.innerText.trim()).filter(Boolean)}});
 rec.question_panel=panel;await shot(mode+'-question');
 const ans=async t=>{await p.locator('textarea:visible, input[type=text]:visible').first().fill(t);await p.getByRole('button',{name:/finish|send|submit/i}).first().click();};
 if(mode==='neg'){
  await ans('0 cm');await p.waitForTimeout(4000);lap('neg_answered');rec.neg_probe=await probe();rec.neg_text=(await p.innerText('body')).split('\n').filter(l=>/invalid|must|greater|positive|422|valid|size|cm/i.test(l)).slice(0,10);rec.neg_textarea_still=await p.locator('textarea:visible').count();await shot('neg-after-invalid');rec.neg_buttons=await p.evaluate(()=>[...document.querySelectorAll('button:not([disabled])')].map(x=>x.innerText.trim()).filter(Boolean).slice(0,20));rec.neg_reopen=[];for(const nm of ['Back','Retry']){if(await p.locator('textarea:visible').count())break;const bt=p.getByRole('button',{name:new RegExp('^'+nm+'$')}).first();if(await bt.count()){await bt.click().catch(()=>{});await p.waitForTimeout(2500);rec.neg_reopen.push(nm+' -> textarea '+await p.locator('textarea:visible').count());}}await shot('neg-reopened');
 }
 await ans('book cover horizontal edge 20.28 cm');
 await p.getByText(/g = /).first().waitFor({timeout:45000}).catch(()=>rec.notes.no_g=true);await p.waitForTimeout(2000);lap('fit_shown');
 const t=await p.innerText('body');fs.writeFileSync(D+mode+'-body.txt',t.replace(/\S+@\S+/g,'<email>'));
 rec.g_line=(t.match(/g = [^\n]*/)||[])[0]||null;
 rec.lines=t.split('\n').filter(l=>/setup_validated|user-declared|Held-out|dof =|Fit:|Track:|Uncertainty|Scale:|spec|Display only|no scene/i.test(l)).slice(0,20);
 rec.probe_after=await probe();await shot(mode+'-result');
 const rb=p.getByRole('button',{name:/report/i}).first();await rb.click({timeout:8000}).catch(()=>rec.notes.report_click_fail=true);await p.waitForTimeout(2500);lap('report');
 const t2=await p.innerText('body');fs.writeFileSync(D+mode+'-report.txt',t2.replace(/\S+@\S+/g,'<email>'));
 rec.report_lines=t2.split('\n').filter(l=>/fitter|Held-out|caveat|not a validated|Your known size|g = /i.test(l)).slice(0,10);
 rec.probe_report=await probe();await shot(mode+'-report');
}}catch(e){rec.error=e.message.slice(0,300)}
rec.end_utc=iso();rec.total_ms=Math.round(performance.now()-t0);rec.console_errors=cons.slice(0,10);rec.failed_requests=fails.slice(0,20);
fs.writeFileSync(D+mode+'.json',JSON.stringify(rec,null,1));await b.close();console.log(JSON.stringify(rec,null,1).slice(0,5000));

