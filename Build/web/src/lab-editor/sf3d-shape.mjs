// SF3D is an estimated visual inside the proxy. Physics keeps its existing collider independently.
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

export const SHAPE_LABEL = 'MODEL-GENERATED shape';

export function fitShapeGlb(model, proxySize) {
  const axes = ['x', 'y', 'z'];
  if (!axes.every((a) => Number.isFinite(proxySize[a]) && proxySize[a] > 0)) throw new Error('Invalid proxy size');
  model.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(model), size = box.getSize(new THREE.Vector3()), c = box.getCenter(new THREE.Vector3());
  const scale = Math.min(...axes.map((a) => size[a] > 0 ? proxySize[a] / size[a] : Infinity));
  if (box.isEmpty() || !axes.every((a) => Number.isFinite(size[a])) || !Number.isFinite(scale) || scale <= 0) throw new Error('Invalid GLB bounds');
  const fit = new THREE.Group();
  // Cancel the parent's non-uniform proxy scale, leaving one uniform visual scale in room units.
  fit.scale.set(scale / proxySize.x, scale / proxySize.y, scale / proxySize.z);
  fit.position.set(-c.x * fit.scale.x, -0.5 - box.min.y * fit.scale.y, -c.z * fit.scale.z);
  fit.add(model);
  return fit;
}

// Untextured collider mesh: shown until the GLB loads, and if it fails.
export function colliderGeometry(shape) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(shape.vertices, 3));
  g.setIndex(shape.indices);
  g.computeVertexNormals();
  return g;
}

export function loadShapeGlb(shape, body, id) {
  new GLTFLoader().load(shape.glb, (gltf) => {
    const m = gltf.scene;
    m.rotation.y = (shape.quarter_turns * Math.PI) / 2;
    let fit;
    try { fit = fitShapeGlb(m, body.scale); }
    catch { body.userData.glbError = true; return; }
    m.traverse((n) => { n.userData.id = id; });
    body.material.visible = false; // the collider placeholder stays for picking, hidden under the texture
    body.add(fit);
  }, undefined, () => { body.userData.glbError = true; });
}

