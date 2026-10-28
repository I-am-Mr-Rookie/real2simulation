// S09d overlay maths: collider edges, fixture alignment, camera-path sampling. Synthetic fixture only;
// alignment here is manifest consistency, not reconstruction, measured/simulated or Gate R evidence.
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadFixtureBundle } from './fixture-bundle.mjs';
import { buildSceneModel } from '../../Build/web/src/viewer/scene-model.mjs';
import { SYNTHETIC_FIXTURE } from '../../Build/web/src/viewer/fixture.mjs';
import { boxCorners, colliderEdgePositions, overlayAlignment, prepareCameraPath, sampleCameraPath, ndcToScreen, rotate } from '../../Build/web/src/viewer/scene-overlays.mjs';

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const fixtureModel = async () => buildSceneModel(await loadFixtureBundle(), SYNTHETIC_FIXTURE.request.scene);
const S = Math.SQRT1_2;

test('fixture geometry is aligned: collider faces touch surfaces, points lie on faces, labels in bounds', async () => {
  const m = await fixtureModel();
  const r = overlayAlignment(m);
  assert.deepEqual(r.issues, []); assert.equal(r.ok, true);
  assert.deepEqual(r.colliders.map((c) => [c.id, c.surfaceId, c.pointsOnFace]), [['floor-box', 'floor', 4], ['table-box', 'table', 4]]);
  for (const c of r.colliders) assert.ok(near(c.faceGapM, 0, 1e-12), c.id + ' face gap ' + c.faceGapM);
  assert.deepEqual(r.labels, [{ id: 'fixture-warning', ok: true }]);
});

test('misalignment is reported: offset, rotation footprint, bad quaternion, label outside bounds, missing surface', async () => {
  const m = structuredClone(await fixtureModel());
  const edit = (f) => { const x = structuredClone(m); f(x); return overlayAlignment(x); };
  const up = edit((x) => { x.colliders[1].pose.position_m[1] += 0.05; });
  assert.equal(up.ok, false); assert.match(up.issues.join(), /table-box: face is 0\.0500 m from surface table/);
  const rot = edit((x) => { x.colliders[1].pose.rotation_xyzw = [0, S, 0, S]; }); // 90 deg about +Y swaps footprint
  assert.equal(rot.colliders[1].pointsOnFace, 0, 'rotated footprint no longer matches table points');
  assert.ok(near(rot.colliders[1].faceGapM, 0, 1e-12), 'rotation about the normal keeps the face on the plane');
  const tilt = edit((x) => { x.colliders[1].pose.rotation_xyzw = [S, 0, 0, S]; }); // 90 deg about +X: y half-extent becomes 0.3
  assert.match(tilt.issues.join(), /table-box: face is/);
  assert.match(edit((x) => { x.colliders[0].pose.rotation_xyzw = [0, 0, 0, 2]; }).issues.join(), /floor-box: quaternion not unit/);
  assert.match(edit((x) => { x.colliders[0].pose.position_m = [0, NaN, 0]; }).issues.join(), /floor-box: collider invalid/);
  assert.match(edit((x) => { x.labels[0].position_m = [0, 5, 0]; }).issues.join(), /label fixture-warning: position invalid or outside bounds_m/);
  assert.match(edit((x) => { x.colliders[0].surface_id = 'nope'; }).issues.join(), /floor-box: surface nope missing/);
  assert.match(edit((x) => { x.colliders[0].pose.position_m[0] = 0.9; }).issues.join(), /floor-box: outside bounds_m/);
});

test('collider edges: 12 segments per box, each an axis edge between corners', async () => {
  const m = await fixtureModel();
  const e = colliderEdgePositions(m.colliders);
  assert.equal(e.length, 2 * 12 * 2 * 3);
  m.colliders.forEach((c, ci) => {
    const corners = boxCorners(c).map((p) => p.map((v) => +v.toFixed(6)).join());
    const lens = [];
    for (let s = 0; s < 12; s++) {
      const o = ci * 72 + s * 6;
      const a = [...e.slice(o, o + 3)], b = [...e.slice(o + 3, o + 6)];
      for (const p of [a, b]) assert.ok(corners.includes(p.map((v) => +v.toFixed(6)).join()), 'segment end is a corner');
      lens.push(+Math.hypot(...a.map((v, k) => v - b[k])).toFixed(5));
    }
    const h = c.half_extents_m.map((v) => +(2 * v).toFixed(5));
    assert.deepEqual(lens.sort(), [h[0], h[0], h[0], h[0], h[1], h[1], h[1], h[1], h[2], h[2], h[2], h[2]].sort());
  });
  assert.equal(colliderEdgePositions([]).length, 0);
  assert.deepEqual(rotate([0, S, 0, S], [1, 0, 0]).map((v) => +v.toFixed(12) + 0), [0, 0, -1]);
});

test('camera path: validation, lerp/slerp sampling, clamping', async () => {
  const keys = prepareCameraPath((await fixtureModel()).cameraPath);
  const mid = sampleCameraPath(keys, 0.5);
  assert.deepEqual(mid.position, [0.125, 1, 3]); assert.equal(mid.fov, 50);
  assert.deepEqual(sampleCameraPath(keys, -3).position, [0, 1, 3]);
  assert.deepEqual(sampleCameraPath(keys, 99).position, [0.25, 1, 3]);
  assert.equal(sampleCameraPath(keys, NaN).t, 0);
  const k = (t, q, fov = 50) => ({ time_s: t, pose: { position_m: [0, 0, 0], rotation_xyzw: q }, vertical_fov_deg: fov });
  const turn = prepareCameraPath([k(0, [0, 0, 0, 1], 40), k(2, [0, S, 0, S], 60)]);
  const h = sampleCameraPath(turn, 1);
  const s45 = Math.sin(Math.PI / 8), c45 = Math.cos(Math.PI / 8);
  h.quaternion.forEach((v, i) => assert.ok(near(v, [0, s45, 0, c45][i], 1e-12), 'slerp half-way = 45 deg'));
  assert.equal(h.fov, 50);
  const flip = prepareCameraPath([k(0, [0, 0, 0, 1]), k(1, [0, -S, 0, -S])]); // same rotation, opposite sign
  sampleCameraPath(flip, 0.5).quaternion.forEach((v, i) => assert.ok(near(v, [0, s45, 0, c45][i], 1e-12), 'shortest arc'));
  assert.throws(() => prepareCameraPath([]), /empty/);
  assert.throws(() => prepareCameraPath([k(1, [0, 0, 0, 1]), k(1, [0, 0, 0, 1])]), /strictly increasing/);
  assert.throws(() => prepareCameraPath([k(0, [0, 0, 0, 1], 180)]), /fov/);
  assert.throws(() => prepareCameraPath([k(0, [0, 0, 1, 1])]), /not unit/);
  assert.throws(() => prepareCameraPath([{ ...k(0, [0, 0, 0, 1]), pose: { position_m: [0, Infinity, 0], rotation_xyzw: [0, 0, 0, 1] } }]), /position/);
});

test('ndcToScreen maps the viewport and clips outside/behind', () => {
  assert.deepEqual(ndcToScreen([0, 0, 0.5], 640, 480), [320, 240]);
  assert.deepEqual(ndcToScreen([-1, 1, 0], 640, 480), [0, 0]);
  assert.equal(ndcToScreen([0, 0, 1.2], 640, 480), null);
  assert.equal(ndcToScreen([1.5, 0, 0], 640, 480), null);
  assert.equal(ndcToScreen([NaN, 0, 0], 640, 480), null);
});
