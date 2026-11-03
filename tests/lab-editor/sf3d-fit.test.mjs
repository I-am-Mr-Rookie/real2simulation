import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../Build/web/node_modules/three/build/three.module.js';
import { GLTFLoader } from '../../Build/web/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import { fitShapeGlb, loadShapeGlb } from '../../Build/web/src/lab-editor/sf3d-shape.mjs';

const near = (a, b) => assert.ok(Math.abs(a - b) < 1e-7, `${a} != ${b}`);

for (const turns of [0, 1, 2, 3]) {
  test(`non-cubic GLB fits uniformly, centred and bottom-aligned, yaw ${turns}`, () => {
    const model = new THREE.Mesh(new THREE.BoxGeometry(2, 1, 4));
    model.position.set(5, -2, 9);
    model.rotation.y = turns * Math.PI / 2;
    const original = new THREE.Box3().setFromObject(model).getSize(new THREE.Vector3());
    const target = new THREE.Vector3(1.2, 3, .8), saved = target.clone();
    const body = new THREE.Group();
    body.scale.copy(target);
    body.add(fitShapeGlb(model, target));
    body.updateMatrixWorld(true);
    const bounds = new THREE.Box3().setFromObject(body), size = bounds.getSize(new THREE.Vector3());
    const centre = bounds.getCenter(new THREE.Vector3());
    const uniform = Math.min(target.x / original.x, target.y / original.y, target.z / original.z);
    for (const a of ['x', 'y', 'z']) {
      assert.ok(size[a] <= target[a] + 1e-7);
      near(size[a] / original[a], uniform);
      near(model.getWorldScale(new THREE.Vector3())[a], uniform);
    }
    near(centre.x, 0); near(centre.z, 0); near(bounds.min.y, -target.y / 2);
    assert.deepEqual(target.toArray(), saved.toArray());
  });
}

test('flat GLB stays finite; empty bounds and invalid proxy dimensions fail safely', () => {
  const model = new THREE.Mesh(new THREE.BoxGeometry(2, 0, 4));
  const fit = fitShapeGlb(model, new THREE.Vector3(1, 2, 3));
  assert.ok(fit.scale.toArray().every(Number.isFinite));
  near(new THREE.Box3().setFromObject(fit).min.y, -.5);
  assert.throws(() => fitShapeGlb(new THREE.Group(), new THREE.Vector3(1, 1, 1)), /Invalid GLB/);
  for (const x of [0, -1, NaN, Infinity]) {
    assert.throws(() => fitShapeGlb(model, new THREE.Vector3(x, 1, 1)), /Invalid proxy/);
  }
});

test('invalid loaded GLB leaves the old collider placeholder visible', () => {
  const load = GLTFLoader.prototype.load;
  GLTFLoader.prototype.load = (_url, done) => done({ scene: new THREE.Group() });
  try {
    const body = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshBasicMaterial());
    loadShapeGlb({ glb: '/old.glb', quarter_turns: 0 }, body, 'old-object');
    assert.equal(body.userData.glbError, true);
    assert.equal(body.material.visible, true);
    assert.equal(body.children.length, 0);
  } finally { GLTFLoader.prototype.load = load; }
});
