// R-P-native: contact-time convergence vs dt (same-state Rapier adapter). Run: node evidence/reviews/R-P-native/repro-contact-convergence.mjs
import { freeFallTrajectory } from '../../../Build/simulator/trajectories.mjs';
import { contactAwareTrajectory } from '../../../Build/simulator/contacts.mjs';
const physics={friction:0.4,restitution:0,density:1}, r=0.1, h=2, g=9.81;
const analytic=Math.sqrt(2*(h-r)/g);
for (const dt of [0.02,0.01,0.005,0.002,0.001,0.0005]) {
 const t=freeFallTrajectory({initialPosition:[0,h,0],initialVelocity:[0,0,0],gravity:g,dt,steps:Math.round(1/dt),source:'simulated',inputProvenance:'synthetic'});
 const o=await contactAwareTrajectory({trajectory:t,geometry:{floorY:0,floorHalfExtents:[5,0.1,5],sphereRadius:r},physics,gravity:g});
 const f=o.samples.find(s=>s.contact);
 console.log(JSON.stringify({dt,contact_t:f?.time_s??null,err_s:f?f.time_s-analytic:null,gap_m:f?f.position_m[1]-r:null}));
}
