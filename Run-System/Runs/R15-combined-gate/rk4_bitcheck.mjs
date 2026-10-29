import { rk4Step } from 'file:///C:/Users/HP/.codex/worktrees/swarm12-covariance-fix/2026-10-26%20-%20Meta%20Global%20AI%20Developer%20Hackathon/Build/simulator/rk4.mjs';
const old=(state,dt,f)=>{const k1=f(state);const mid=k=>state.map((x,i)=>x+dt*k[i]/2);const k2=f(mid(k1)),k3=f(mid(k2)),k4=f(state.map((x,i)=>x+dt*k3[i]));return state.map((x,i)=>x+dt*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6);};
let diff=0,tot=0,maxrel=0;
const cases=[[s=>[s[1],-9.81],[10,0]],[s=>[s[1],-9.81*s[0]],[0.08,0]],[s=>[s[1],-(9.81/1.3)*Math.sin(s[0])],[1.2,0.3]],[s=>[s[1],9.81*(Math.sin(0.4)-0.2*Math.cos(0.4))],[0,0]]];
for(const [f,s0] of cases){let a=s0,b=s0;for(let n=0;n<2000;n++){a=old(a,1/240,f);b=rk4Step(b,1/240,f);tot++;if(a[0]!==b[0]||a[1]!==b[1])diff++;maxrel=Math.max(maxrel,Math.abs(a[0]-b[0])/Math.max(1e-300,Math.abs(a[0])));}}
console.log('steps',tot,'bitdiff',diff,'maxrel',maxrel);
try{console.log('overflow new',rk4Step([0,1e308],0.5,s=>[1e308,1e308]));}catch(e){console.log('overflow new err',e.message)}
console.log('overflow old',old([0,1e308],0.5,s=>[1e308,1e308]));
console.log('subnormal new',rk4Step([0],5e-324,s=>[1]),'old',old([0],5e-324,s=>[1]));

