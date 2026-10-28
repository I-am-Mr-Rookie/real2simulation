import { freeFallTrajectory } from '../../../Build/simulator/trajectories.mjs';
import { contactAwareTrajectory } from '../../../Build/simulator/contacts.mjs';
const physics={friction:0.4,restitution:0,density:1};
for (const [dt,thick] of [[0.05,0.01],[0.02,0.01],[0.05,0.1],[0.1,0.1]]) {
 const t=freeFallTrajectory({initialPosition:[0,2,0],initialVelocity:[0,0,0],gravity:9.81,dt,steps:Math.round(2/dt),source:'simulated',inputProvenance:'synthetic'});
 const out=await contactAwareTrajectory({trajectory:t,geometry:{floorY:0,floorHalfExtents:[5,thick,5],sphereRadius:0.1},physics,gravity:9.81});
 const last=out.samples.at(-1); const c=out.samples.findIndex(s=>s.contact);
 console.log(JSON.stringify({dt,thick,n:out.samples.length,firstContact:c,lastY:last.position_m[1],minY:Math.min(...out.samples.map(s=>s.position_m[1]))}));
}
// speculative gap at first contact
const t=freeFallTrajectory({initialPosition:[0,2,0],initialVelocity:[0,0,0],gravity:9.81,dt:0.01,steps:200,source:'simulated',inputProvenance:'synthetic'});
const o=await contactAwareTrajectory({trajectory:t,geometry:{floorY:0,floorHalfExtents:[5,0.1,5],sphereRadius:0.1},physics,gravity:9.81});
const f=o.samples.find(s=>s.contact); console.log('gap_at_first_contact_m', f.position_m[1]-0.1, 'time', f.time_s);

