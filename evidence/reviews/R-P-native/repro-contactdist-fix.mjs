// R-P-native: check proposed fix — count only manifold points with contactDist<=0. Read-only use of Rapier; no source edit.
import RAPIER from '../../../Build/simulator/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { freeFallTrajectory } from '../../../Build/simulator/trajectories.mjs';
await RAPIER.init();
const r=0.1,h=2,g=9.81, analytic=Math.sqrt(2*(h-r)/g);
for (const dt of [0.02,0.01,0.005,0.002,0.001,0.0005]) {
 const t=freeFallTrajectory({initialPosition:[0,h,0],initialVelocity:[0,0,0],gravity:g,dt,steps:Math.round(1/dt),source:'simulated',inputProvenance:'synthetic'});
 const w=new RAPIER.World({x:0,y:-g,z:0}); w.timestep=dt;
 const floor=w.createCollider(RAPIER.ColliderDesc.cuboid(5,0.1,5).setTranslation(0,-0.1,0));
 const b=w.createRigidBody(RAPIER.RigidBodyDesc.dynamic().setGravityScale(0,true)); const s=w.createCollider(RAPIER.ColliderDesc.ball(r),b);
 let spec=null, touch=null;
 for (const smp of t.samples) { b.setTranslation({x:smp.position_m[0],y:smp.position_m[1],z:smp.position_m[2]},true); b.setLinvel({x:0,y:0,z:0},true); w.step();
  w.narrowPhase.contactPair(s.handle,floor.handle,w.bodies,(m)=>{ const n=m.numContacts(); if(n&&spec===null) spec=smp.time_s; for(let i=0;i<n;i++) if(m.contactDist(i)<=0&&touch===null) touch=smp.time_s; });
  if(touch!==null) break; }
 console.log(JSON.stringify({dt,speculative_t:spec,touch_t:touch,touch_err_s:touch===null?null:touch-analytic}));
 w.free();
}
