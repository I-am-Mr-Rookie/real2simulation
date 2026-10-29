import assert from 'node:assert/strict';
import { parseFitReveal, plotPoints } from '../../../Build/web/src/lab/fit-contract.mjs';
const A=["iid residual noise","clock fixed"];
const mk=(u)=>({status:'ok',sessionId:'s',fit:{status:'ok',gravity:{value:9.8,uncertainty:0.1,unit:'m/s^2',source:{label:'simulated',evidence:'e'}},uncertainty:u}});
const Q='standard uncertainty (one sigma), not a 95% interval';
let n=0; const ok=(c,m)=>{assert.ok(c,m);n++;};
// DTO
ok(parseFitReveal(mk({model:'m',assumptions:A}),'s'),'minimal DTO w/o quantity_uncertainty accepted');
ok(parseFitReveal(mk({model:'m',assumptions:A,quantity_uncertainty:Q,residual_degrees_of_freedom:3}),'s'),'real producer shape accepted');
ok(parseFitReveal(mk({model:'m',assumptions:[]}),'s'),'empty assumptions accepted');
for (const bad of ['95% interval',null,undefined,'', Q+' ']) ok(parseFitReveal(mk({model:'m',assumptions:A,quantity_uncertainty:bad}),'s')===null,'contradictory '+String(bad));
const sp=['a']; sp[2]='c'; ok(parseFitReveal(mk({model:'m',assumptions:sp}),'s')===null,'sparse rejected');
const big=['a']; big.length=2**32-1; let t=Date.now(); ok(parseFitReveal(mk({model:'m',assumptions:big}),'s')===null && Date.now()-t<100,'huge sparse fast reject');
ok(parseFitReveal(mk({model:'m',assumptions:['a',1]}),'s')===null,'non-string');
const r=parseFitReveal(mk({model:'m',assumptions:A}),'s'); ok(r.assumptions===undefined||r.assumptions.join(' ')==='iid residual noise clock fixed','assumptions intact');
// plot
const num=(s)=>s.points.split(' ').flatMap(p=>p.split(',').map(Number));
const P=(xs,ys)=>plotPoints(xs.map((x,i)=>({time_s:x,position_m:ys[i]})));
const M=Number.MAX_VALUE, T=Number.MIN_VALUE;
const cases=[[[-M,0,M],[0,1,2]],[[-M,M],[-M,M]],[[0,1,2],[-M,0,M]],[[-T,0,T],[T,2*T,3*T]],[[5],[5]],[[-0,0],[1,1]],[[1e308,-1e308,0],[3,-3,0]],[[1,2,3],[4,5,6]]];
for (const [x,y] of cases){const p=P(x,y); const v=num(p); ok(v.length===2*x.length && v.every(Number.isFinite),'finite '+JSON.stringify([x,y])); ok(Math.min(...v.filter((_,i)=>i%2==0))>=24 && Math.max(...v.filter((_,i)=>i%2==0))<=616,'x bounds'); ok(Math.min(...v.filter((_,i)=>i%2))>=30 && Math.max(...v.filter((_,i)=>i%2))<=190,'y bounds');}
let p=P([-M,0,M],[0,1,2]); ok(p.points.startsWith('24,190 320,110 616,30'),'overflow endpoints/mid exact: '+p.points);
p=P([-T,0,T],[0,1,2]); ok(p.points==='24,190 320,110 616,30','subnormal exact: '+p.points);
p=P([0,0.1,0.3],[0,1,3]); ok(p.points===`24,190 ${24+(0.1/0.3)*592},${190-(1/3)*160} 616,30`,'ordinary arithmetic unchanged');
p=P([5],[5]); ok(p.points==='320,110','degenerate centred');
const N=300000; const rows=Array.from({length:N},(_,i)=>({time_s:i,position_m:-i}));
p=plotPoints(rows); ok(p.time[0]===0&&p.time[1]===N-1&&p.points.split(' ').length===N,'large array no truncation/overflow');
ok(plotPoints([{time_s:NaN,position_m:1},{time_s:1,position_m:Infinity}]).points==='','nonfinite filtered (pre-existing)');
console.log('ALL '+n+' checks pass');
