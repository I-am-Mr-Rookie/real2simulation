
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import fs from 'node:fs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';
await R.init();
const raw = JSON.parse(fs.readFileSync('evidence/N43/drop-scene.json'));
const s = validateScene(raw);
const t1 = s.objects.find(o=>o.id==='room-object-1');
const v=t1.shape.vertices, n=v.length/3, ol=t1.shape.support.outline;
let ys=[];for(let i=0;i<n;i++) ys.push(v[3*i+1]);
console.log('verts',n,'outline',ol,'ymax',Math.max(...ys),'count at .5', ys.filter(y=>y>0.4999).length);
const out=v.slice(-3*ol); let xs=[],zs=[];for(let k=0;k<out.length;k+=3){xs.push(out[k]);zs.push(out[k+2]);}
console.log('outline x',Math.min(...xs),Math.max(...xs),'z',Math.min(...zs),Math.max(...zs));
const run=(dx,dz)=>{const objs=s.objects.map(o=>o.id==='ball-1'?{...o,position:[o.position[0]+dx,o.position[1],o.position[2]+dz]}:o);
const sim=createPhysics(R,{...s,room:{kind:'plane',floor_y:0},objects:objs}); sim.step(4*120); const tr=sim.trace('ball-1').samples; sim.free(); return tr;};
const tr=run(0,0); for(const k of [40,50,52,55,60,80,120,240,479]) if(tr[k]) console.log(k, tr[k].t?.toFixed?.(3), tr[k].p.map(x=>x.toFixed(4)).join(','));

