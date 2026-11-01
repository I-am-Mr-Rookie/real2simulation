// N31: Stable Fast 3D object shape in the editor. The textured GLB is turned by quarter_turns and fitted into the unit
// box, exactly like the collider vertices (scene.mjs shape.vertices), so the drawn mesh and the physics shape agree.
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

export const SHAPE_LABEL = 'MODEL-GENERATED shape', SHAPE_CREDIT = 'Powered by Stability AI';

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
    m.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(m), size = box.getSize(new THREE.Vector3()), c = box.getCenter(new THREE.Vector3());
    const fit = new THREE.Group();
    fit.scale.set(1 / size.x, 1 / size.y, 1 / size.z);
    fit.position.copy(c).multiply(fit.scale).negate();
    fit.add(m);
    m.traverse((n) => { n.userData.id = id; });
    body.material.visible = false; // the collider placeholder stays for picking, hidden under the texture
    body.add(fit);
  }, undefined, () => { body.userData.glbError = true; });
}

// Two-line caption drawn under the object (licence duty 3: next to the MODEL-GENERATED label).
export function captionSprite(lines) {
  const cv = document.createElement('canvas');
  cv.width = 512; cv.height = 96;
  const x = cv.getContext('2d');
  x.fillStyle = 'rgba(17,24,39,0.8)'; x.fillRect(0, 0, 512, 96);
  x.fillStyle = '#fff'; x.font = '28px system-ui, sans-serif'; x.textAlign = 'center';
  lines.forEach((l, i) => x.fillText(l, 256, 38 + i * 36));
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv), depthTest: false }));
  s.scale.set(0.6, 0.1125, 1);
  return s;
}

