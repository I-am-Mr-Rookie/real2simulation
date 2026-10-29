const base=await import(process.argv[2]); const cur=await import('file:///C:/Users/HP/.codex/worktrees/swarm12-covariance-fix/2026-10-26%20-%20Meta%20Global%20AI%20Developer%20Hackathon/Build/simulator/replay.mjs');
const inp={seed:7,parameters:{g:9.81,list:[1,2,{a:null}]},trace:[[0,1.5],[0.1,-2e-300]]};
const a=await base.createReplayRecord(inp), b=await cur.createReplayRecord(inp);
console.log('hash identical', a.replayHash===b.replayHash && a.traceHash===b.traceHash);
const run=(p,s)=>inp.trace; console.log('replay ok', (await cur.replayRecord(JSON.parse(JSON.stringify(a)),run)).replayHash===a.replayHash);
for (const [n,x] of [['explicit undefined version',{...inp,version:undefined}],['extra key',{...inp,note:'x'}]]) { for (const [m,mod] of [['base',base],['cur',cur]]) { try{const r=await mod.createReplayRecord(x); console.log(n,m,'ok',r.replayHash===a.replayHash);}catch(e){console.log(n,m,'err',e.message)} } }
const rec={...a}; let reads=0; const t=rec.trace; Object.defineProperty(rec,'trace',{get(){reads++;return reads>2?[[9,9]]:t},enumerable:true});
try{await cur.replayRecord(rec,run);console.log('getter accepted')}catch(e){console.log('getter rejected',e.message)}

