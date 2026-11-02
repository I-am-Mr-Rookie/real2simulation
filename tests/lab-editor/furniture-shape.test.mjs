// N49: room shell class shapes (block.look): validated, drawn inside the measured box, physics still the box.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../Build/web/node_modules/three/build/three.module.js';
import R from '../../Build/web/node_modules/@dimforge/rapier3d-compat/dist/rapier.mjs';
import { validateScene } from '../../Build/web/src/lab-editor/scene.mjs';
import { createPhysics } from '../../Build/web/src/lab-editor/physics.mjs';
import { lookParts, lookMesh } from '../../Build/web/src/lab-editor/furniture-shape.mjs';

await R.init();
const table = { id: 'room-object-1', kind: 'block', position: [0, 0.36, 0], size: [1.0, 0.72, 0.6], rotation: [0, 0, 0, 1], fixed: true, sensor: false, mass: 25, look: { category: 'table', color: '#8a6d4b' } };
const scene = (objects) => validateScene({ version: 'lab-scene-v1', room: { kind: 'plane', floor_y: 0 }, objects });

test('look validates on blocks only, with a #rrggbb colour', () => {
  assert.deepEqual(scene([table]).objects[0].look, { category: 'table', color: '#8a6d4b' });
  assert.throws(() => scene([{ ...table, look: { category: 'table', color: 'red' } }]), /color/);
  assert.throws(() => scene([{ ...table, look: { category: 'table', color: '#000000', x: 1 } }]), /category, color/);
  assert.throws(() => scene([{ id: 'b', kind: 'ball', look: { category: 'table', color: '#000000' } }]), /only for blocks/);
});

test('class shapes stay inside the measured box; table top is flush with the box top', () => {
  for (const c of ['table', 'chair', 'sofa', 'bed', 'shelf', 'door', 'window', 'wall', 'floor', 'other']) {
    const s = c === 'window' ? [0.04, 1.2, 1.0] : [1.0, 0.8, 0.6];
    for (const [cx, cy, cz, sx, sy, sz] of lookParts(c, s)) {
      [[cx, sx, s[0]], [cy, sy, s[1]], [cz, sz, s[2]]].forEach(([p, d, S]) => assert.ok(Math.abs(p) + d / 2 <= S / 2 + 1e-9, c + ' part outside the box'));
    }
  }
  const [top, ...legs] = lookParts('table', table.size);
  assert.ok(Math.abs(top[1] + top[4] / 2 - 0.36) < 1e-9);
  assert.equal(legs.length, 4);
  assert.ok(legs.every((l) => Math.abs(l[1] - l[4] / 2 + 0.36) < 1e-9), 'legs reach the floor');
  assert.equal(lookParts('chair', [0.5, 0.9, 0.5]).length, 6); // seat, back, 4 legs
  const g = lookMesh(table, new THREE.Group());
  assert.equal(g.children.length, 5);
  assert.ok(g.children.every((m) => m.userData.id === 'room-object-1'));
});

test('ball dropped on a parametric table rests on its top (box collider)', () => {
  const sim = createPhysics(R, scene([table, { id: 'b', kind: 'ball', position: [0.2, 1.2, 0.1], size: [0.05, 0.05, 0.05], restitution: 0.1 }]));
  sim.step(3 * 120);
  const y = sim.trace('b').samples.at(-1).p[1];
  sim.free();
  assert.ok(Math.abs(y - 0.745) < 0.01, 'rest y ' + y);
});

