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
    const p = shape.support?.plane; // N42: the collider's flattened support plane is the box top; blobs above stick out
    if (p != null) { fit.scale.y /= p + 0.5; fit.position.y = (fit.position.y + 0.5) / (p + 0.5) - 0.5; }
    fit.add(m);
    m.traverse((n) => { n.userData.id = id; });
    body.material.visible = false; // the collider placeholder stays for picking, hidden under the texture
    body.add(fit);
  }, undefined, () => { body.userData.glbError = true; });
}

// Two-line caption drawn under the object (licence duty 3: next to the MODEL-GENERATED label). N44: fixed on-screen
// size (CAPTION_PX tall, about 15 px text) and slid sideways to stay inside the canvas (N43: unreadable and clipped at
// 375 px when the caption scaled with distance).
export const CAPTION_PX = 44;
const _v = new THREE.Vector3();
export function captionSprite(lines) {
  const cv = document.createElement('canvas');
  cv.width = 400; cv.height = 88;
  const x = cv.getContext('2d');
  x.fillStyle = 'rgba(17,24,39,0.85)'; x.fillRect(0, 0, 400, 88);
  x.fillStyle = '#fff'; x.font = '600 30px system-ui, sans-serif'; x.textAlign = 'center';
  lines.forEach((l, i) => x.fillText(l, 200, 36 + i * 38, 388));
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv), depthTest: false, sizeAttenuation: false }));
  s.scale.set(0.2, 0.044, 1);
  s.frustumCulled = false;
  s.onBeforeRender = (r, _scene, cam) => {
    const el = r.domElement, p11 = cam.projectionMatrix.elements[5], p00 = cam.projectionMatrix.elements[0];
    const h = (2 * CAPTION_PX) / ((el.clientHeight || 600) * p11), w = (h * cv.width) / cv.height, wN = w * p00;
    const v = s.getWorldPosition(_v).project(cam);
    s.scale.set(w, h, 1);
    // slide so the caption stays inside the canvas, also when its anchor is just off screen (not when behind the camera)
    s.center.x = v.z > 1 ? 0.5 : Math.min((v.x + 1) / wN, Math.max(1 - (1 - v.x) / wN, 0.5));
    s.updateMatrixWorld();
  };
  return s;
}

