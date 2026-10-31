// S24c capture: node media/capture/S24c/capture.mjs (run from repo root; needs test-data/public clips, gitignored)
import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {pathToFileURL} from 'node:url';
const require=createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright-core');
const ROOT=process.cwd(),OUT=path.join(ROOT,'media/capture/S24c'),TMP=path.join(OUT,'_pages');
const CLIPS=process.env.CLIPS||path.join(ROOT,'test-data/public');
fs.mkdirSync(TMP,{recursive:true});
const J=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const SITE='https://web-dev-cd80.up.railway.app';
const sum=J('evidence/S07/S07-chunktrack-orch67/PD02-summary.json');
const pd02=J('evidence/S07/S07-chunktrack-orch67/PD02-f0-438/result.json').stream;
const st03=J('evidence/S12/gate-rs/ST03-f58-83/result.json').stream;
const s05=J('evidence/S05/S05d/RESULT.json').RM02;
const grs=J('evidence/S12/gate-rs/gate-rs.json').clips.projectile;
const bench=fs.readFileSync('BENCHMARK.md','utf8').split('\n').filter(l=>/^\| (st03_g_image_relative_uncertainty|rm02_gravity_direction_bootstrap_sd|rm02_gravity_vs_camera_down_prior|st03_heldout_normalized_rms) /.test(l));
const t=fs.readFileSync('evidence/S07/S07n/table.md','utf8').split('\n');
const tbl=[t[0],t[1],...t.filter(l=>/^\| (OWN07|OWN01) /.test(l))];
const CSS='body{margin:0;background:#0b0f14;color:#e8eef5;font:20px system-ui}.cap{position:fixed;left:0;right:0;bottom:48px;text-align:center;font-size:26px;background:#000a;padding:12px}.cred{position:fixed;left:12px;bottom:8px;font-size:15px;color:#cfd}.wrap{position:relative;width:1280px;height:720px}video,canvas{position:absolute;left:0;top:0;width:1280px;height:720px}table{border-collapse:collapse;font-size:15px;margin:20px}td,th{border:1px solid #556;padding:6px}pre{white-space:pre-wrap;margin:20px;font-size:18px}.b{margin:20px;padding:10px;background:#a22;display:inline-block;font-weight:700}';
const CRED={PD02:'Alexandre Henry Alves - Foucault Pendulum Swing in Grand Hall - Pexels (Pexels License)',RM02:'Andy Barbour - Tracking shot of empty classroom - Pexels (Pexels License)',ST03:'Roman Odintsov - Woman dropping apple on ground - Pexels (Pexels License)'};
const vid=(clip,stream,idx,caption,trail,badge,off=0)=>'<style>'+CSS+'.wrap{left:50%;transform:translateX(-50%)}video,canvas{width:100%!important;height:100%!important}</style><div class=wrap id=w><video id=v src="'+pathToFileURL(path.join(CLIPS,clip+'.mp4')).href+'" muted autoplay loop></video><canvas id=c width=1280 height=720></canvas></div><div class=cap>'+caption+'</div><div class=cred>'+CRED[clip]+'</div>'+(badge?'<div class=b style="position:fixed;top:0;right:0;margin:10px;background:#146">'+badge+'</div>':'')+'<script>const S='+JSON.stringify(stream)+';const v=document.getElementById("v"),c=document.getElementById("c").getContext("2d");const FPS=30,OFF='+off+';const W=document.getElementById("w");v.addEventListener("loadedmetadata",()=>{v.currentTime=OFF/FPS;W.style.width=(720*v.videoWidth/v.videoHeight)+"px"});(function d(){const Wd=W.clientWidth;c.canvas.width=Wd;c.clearRect(0,0,Wd,720);const f=Math.floor(v.currentTime*FPS)-OFF;if(f>=S.length)v.currentTime=OFF/FPS;const pt=k=>{const e=S[k];const i=e[1].indexOf('+idx+');if(i<0)return null;const b=e[2][i];return[(b[0]+b[2]/2)*Wd,(b[1]+b[3]/2)*720,b]};if(f>=0&&S[f]){if('+trail+'){c.fillStyle="#ff0";for(let k=0;k<=f;k+=2){const p=pt(k);if(p){c.beginPath();c.arc(p[0],p[1],2.5,0,7);c.fill()}}}const p=pt(f);if(p){c.strokeStyle="#0f0";c.lineWidth=3;c.beginPath();c.arc(p[0],p[1],8,0,7);c.stroke();if('+trail+'){c.strokeRect(p[2][0]*Wd,p[2][1]*720,p[2][2]*Wd,p[2][3]*720)}}}requestAnimationFrame(d)})()</script>';
const card=(h,body)=>'<style>'+CSS+'</style><h2 style="margin:20px">'+h+'</h2>'+body;
const rows=bench.map(l=>l.split('|').slice(1,5).map(s=>s.trim()).join(' | '));
const row=id=>rows.find(r=>r.startsWith(id));
const pages={
 b1:{html:vid('PD02',pd02,0,'Real video → measured track → simulation → honest error',false),ms:9000},
 b2:{html:vid('PD02',pd02,0,'SAM 3.1 · '+sum.frames_observed+'/'+sum.frames_total+' frames tracked · Modal '+sum.gpu.split(',')[0].replace('NVIDIA ','').replace(' ',''),true,'A10G'),ms:12000},
 b3:{html:card('RM02 classroom · MapAnything floor fit (S05d RESULT.json)','<video src="'+pathToFileURL(path.join(CLIPS,'RM02.mp4')).href+'" muted autoplay loop style="width:640px;position:fixed;left:auto;height:auto;right:20px;top:120px"></video><pre>Floor-normal spread '+s05.floor.normal_bootstrap_std_deg.toFixed(5)+'° (bootstrap 1 sd)\nAngle to camera-down prior '+s05.floor.angle_to_camera_down_prior_deg+'°\nfloor status: '+s05.floor.status+'\n</pre><div class=b>scale: '+s05.metric_scale.status+'ED (unverified)</div><pre>Metric scale: ABSTAINED (unverified)\n'+s05.metric_scale.reason+'</pre><div class=cred>'+CRED.RM02+'</div>'),ms:8000},
 b4:{html:vid('ST03',st03,2,row('st03_g_image_relative_uncertainty')+' (track points only, no fit drawn)',true,'',J('evidence/S12/gate-rs/ST03-f58-83/result.json').frame_map[0][0]),ms:9000},
 b5:{html:card('ST03 sealed prediction vs suffix (gate-rs.json)','<pre>Gate RS: '+J('evidence/S12/gate-rs/gate-rs.json').result.status+' — diagnostic RMS '+grs.normalized_rms.toFixed(4)+' image heights, '+grs.scored_frames+'/'+grs.sealed_frames+' frames scored\nprediction commitment: '+grs.prediction_commitment+'  sha256 '+grs.prediction_sha256.slice(0,16)+'…\nmax abs error '+grs.max_abs.toFixed(4)+' image heights; coverage '+grs.coverage.toFixed(4)+'\n'+row('st03_heldout_normalized_rms')+'</pre><div class=b>Gate RS: NOT_MET</div>'),ms:8000},
 b5b:{html:card('S07n fall time and drop height (table.md; plots/tables only, no owner-clip frames)','<pre>'+tbl.join('\n').replace(/</g,'&lt;')+'</pre>'),ms:8000},
};
const b=await chromium.launch();
const shot=async(name,url,ms,act)=>{
 const ctx=await b.newContext({viewport:{width:1280,height:720},recordVideo:{dir:OUT,size:{width:1280,height:720}}});
 const p=await ctx.newPage();await p.goto(url,{waitUntil:'load',timeout:45000});await p.waitForTimeout(1500);
 await p.screenshot({path:path.join(OUT,name+'.png')});
 if(act)await act(p);await p.waitForTimeout(ms);
 const v=p.video();await ctx.close();fs.renameSync(await v.path(),path.join(OUT,name+'.webm'));console.log('ok',name);
};
const ONLY=(process.env.ONLY||'').split(',').filter(Boolean),on=n=>!ONLY.length||ONLY.includes(n);
for(const [k,v] of Object.entries(pages)){if(!on(k))continue;const f=path.join(TMP,k+'.html');fs.writeFileSync(f,v.html);await shot('beat'+k.slice(1),pathToFileURL(f).href,v.ms)}
for(const r of ['library','lab'])if(on('site-'+r))try{await shot('site-'+r,SITE+'/'+r,5000,async p=>{if(r=='lab'){await p.getByText('Mystery-g mode').click();await p.getByText('Run trial').click();await p.waitForTimeout(3000);await p.getByText('Fit & reveal').click({timeout:8000}).catch(()=>console.log('fit button disabled'));await p.waitForTimeout(3000);await p.screenshot({path:path.join(OUT,'site-lab-fit.png'),fullPage:true})}await p.mouse.wheel(0,500);await p.waitForTimeout(2000);await p.mouse.wheel(0,-500)})}catch(e){console.log('FAIL',r,String(e).slice(0,200))}
await b.close();

