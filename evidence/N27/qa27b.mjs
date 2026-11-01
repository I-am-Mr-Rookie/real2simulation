
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base='https://web-dev-cd80.up.railway.app'; const D=decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1)); const out=[];
const b=await chromium.launch({headless:false}); const p=await (await b.newContext({viewport:{width:1280,height:900}})).newPage();
const email='n27-b-'+Date.now().toString(36)+'+clerk_test@example.com';
await p.goto(base+'/sign-up'); await p.locator('input[name=emailAddress]').fill(email); await p.locator('input[name=emailAddress]').press('Enter');
await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({timeout:90000}); await p.keyboard.type('424242'); await p.waitForURL(u=>!/sign-up/.test(u.pathname),{timeout:90000});
await p.waitForTimeout(4000); out.push('contrib_card_first_load='+await p.getByRole('heading',{name:'Choose how the agent runs'}).count()); await p.screenshot({path:D+'b-01-first-load.png'});
await p.goto(base+'/workspace'); await p.waitForTimeout(3000); out.push('contrib_card_after_goto='+await p.getByRole('heading',{name:'Choose how the agent runs'}).count()); await p.screenshot({path:D+'b-02-after-goto.png'});
const cont=p.getByRole('button',{name:'Continue'}); if(await cont.count()) await cont.click();
await p.getByRole('link',{name:'Open lab'}).first().click(); await p.getByText(/Your room: \d+ points/).waitFor({timeout:90000}); await p.waitForTimeout(1500);
out.push('status0='+(await p.locator('.le-status').first().innerText()).replace(/\s+/g,' ')); await p.screenshot({path:D+'b-03-sample-lab.png'});
const img=p.locator('.le-view img'); await p.waitForTimeout(3000); out.push('img_visible='+await img.isVisible()); await p.screenshot({path:D+'b-03b.png',fullPage:true}); console.log(out.join('|')); 
const nat=await img.evaluate(e=>[e.naturalWidth,e.naturalHeight,e.clientWidth,e.clientHeight]); const at=(r,c)=>({x:c*nat[2]/nat[0],y:r*nat[3]/nat[1]});
await p.getByRole('button',{name:'Mark the A4 sheet'}).click(); await img.click({position:at(250,200),force:true}); await img.click({position:at(250,260),force:true});
await p.getByText(/A4 scale applied|Not applied|rejected/i).first().waitFor({timeout:60000}); await p.waitForTimeout(800);
out.push('a4_status='+(await p.locator('.le-status').first().innerText()).replace(/\s+/g,' ')); out.push('room_panel='+(await p.locator('text=Your room').first().locator('xpath=..').innerText()).replace(/\s+/g,' ').slice(0,500)); await p.screenshot({path:D+'b-04-a4-implausible.png',fullPage:true});
fs.writeFileSync(D+'accB.json',JSON.stringify(out,null,1)); console.log(out.join('\n')); await b.close();

