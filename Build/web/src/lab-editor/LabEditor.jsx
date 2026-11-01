'use client';

// N10 lab editor: optional room + editable objects (lab-scene-v1 JSON) + Rapier play/pause/reset + per-object sensor traces.
import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls.js';
import { defaultScene, makeObject, validateScene, parseScene, sceneJson, fitterRequest, KINDS, MAX_OBJECTS } from './scene.mjs';
import { createPhysics, loadRapier, movingStart, upQuat } from './physics.mjs';
import { decodePlyXyzRgb } from '../viewer/scene-model.mjs';
import './lab-editor.css';

const COLORS = { ball: 0xe4572e, block: 0x3b82f6, ramp: 0x9ca3af, pendulum: 0xf59e0b, spring: 0x10b981 };
const LABELS = { ball: 'Ball', block: 'Block', ramp: 'Ramp', pendulum: 'Pendulum', spring: 'Spring' };
const MAX_STEPS_PER_FRAME = 8;

function download(name, text) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

function plyCount(bytes) {
  const m = /element vertex (\d+)/.exec(new TextDecoder().decode(bytes.subarray(0, 2048)));
  if (!m) throw new Error('PLY header has no vertex count');
  return Number(m[1]);
}

function objectMesh(o) {
  const g = new THREE.Group();
  g.userData.id = o.id;
  g.position.fromArray(o.position);
  g.quaternion.fromArray(o.rotation);
  const mat = new THREE.MeshStandardMaterial({ color: COLORS[o.kind], roughness: 0.6 });
  const geo = o.kind === 'ball' || o.kind === 'pendulum' ? new THREE.SphereGeometry(0.5, 24, 16) : new THREE.BoxGeometry(1, 1, 1);
  const body = new THREE.Mesh(geo, mat);
  body.scale.fromArray(o.kind === 'ball' || o.kind === 'pendulum' ? Array(3).fill(Math.max(...o.size)) : o.size);
  body.userData.id = o.id;
  g.add(body);
  if (o.kind === 'pendulum' || o.kind === 'spring') {
    g.updateMatrixWorld();
    body.position.copy(g.worldToLocal(new THREE.Vector3(...movingStart(o))));
    const anchor = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.06, 0.06), new THREE.MeshStandardMaterial({ color: 0x374151 }));
    anchor.userData.id = o.id;
    g.add(anchor);
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), body.position.clone()]), new THREE.LineBasicMaterial({ color: 0x111827 }));
    g.add(line);
    g.userData.line = line;
  }
  g.userData.body = body;
  return g;
}

export default function LabEditor({ initialScene }) {
  const host = useRef(null);
  const api = useRef(null);
  const [scene, setScene] = useState(() => validateScene(initialScene ?? defaultScene()));
  const [selected, setSelected] = useState(null);
  const [mode, setMode] = useState('translate');
  const [run, setRun] = useState('stopped'); // stopped | loading | playing | paused
  const [time, setTime] = useState(0);
  const [jsonText, setJsonText] = useState('');
  const [message, setMessage] = useState('Add an object, then press Play. Everything here is SIMULATED.');
  const [plyName, setPlyName] = useState(null);
  const sceneRef = useRef(scene);
  sceneRef.current = scene;

  useEffect(() => {
    const el = host.current;
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    el.appendChild(renderer.domElement);
    const three = new THREE.Scene();
    three.background = new THREE.Color(0xf3f4f6);
    three.add(new THREE.HemisphereLight(0xffffff, 0x888888, 2.2));
    const sun = new THREE.DirectionalLight(0xffffff, 1.5);
    sun.position.set(3, 6, 4);
    three.add(sun);
    const camera = new THREE.PerspectiveCamera(50, 1, 0.01, 500);
    camera.position.set(2, 1.7, 2.6);
    const orbit = new OrbitControls(camera, renderer.domElement);
    orbit.target.set(0, 0.7, 0);
    orbit.update();
    const gizmo = new TransformControls(camera, renderer.domElement);
    three.add(gizmo.getHelper());
    const room = new THREE.Group();
    const objects = new THREE.Group();
    three.add(room, objects);
    const state = { sim: null, acc: 0, last: 0, playing: false, frame: 0, dragging: false, points: null };
    gizmo.addEventListener('dragging-changed', (e) => {
      orbit.enabled = !e.value;
      state.dragging = e.value;
      if (e.value) return;
      const g = gizmo.object;
      if (!g) return;
      const id = g.userData.id;
      // Commit the gizmo pose back into the scene JSON; resize bakes the gizmo scale into size.
      setScene((s) => validateScene({ ...s, objects: s.objects.map((o) => (o.id !== id ? o : {
        ...o, position: g.position.toArray(), rotation: g.quaternion.toArray(),
        size: o.size.map((v, i) => Math.min(50, Math.max(0.005, v * g.scale.getComponent(i)))) })) }));
    });
    const ray = new THREE.Raycaster();
    const onDown = (e) => {
      if (state.dragging || gizmo.axis) return;
      const r = renderer.domElement.getBoundingClientRect();
      ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera);
      const hit = ray.intersectObjects(objects.children, true).find((h) => h.object.userData.id);
      if (hit) setSelected(hit.object.userData.id);
    };
    renderer.domElement.addEventListener('pointerdown', onDown);
    const resize = () => {
      const w = el.clientWidth, h = el.clientHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / Math.max(1, h);
      camera.updateProjectionMatrix();
    };
    const ro = new ResizeObserver(resize);
    ro.observe(el);
    resize();
    const loop = (now) => {
      state.frame = requestAnimationFrame(loop);
      if (state.playing && state.sim) {
        state.acc += Math.min(0.1, (now - (state.last || now)) / 1000);
        let n = 0;
        while (state.acc >= 1 / 120 && n < MAX_STEPS_PER_FRAME) { state.sim.step(); state.acc -= 1 / 120; n += 1; }
        if (n === MAX_STEPS_PER_FRAME) state.acc = 0; // slow device: drop wall-clock sync, keep fixed physics steps
        const poses = state.sim.poses();
        for (const g of objects.children) {
          const p = poses[g.userData.id];
          if (!p) continue;
          const o = state.sim.scene.objects.find((x) => x.id === g.userData.id);
          if (o.kind === 'pendulum' || o.kind === 'spring') {
            g.updateMatrixWorld();
            g.userData.body.position.copy(g.worldToLocal(new THREE.Vector3(...p.p)));
            const pos = g.userData.line.geometry.attributes.position;
            pos.setXYZ(1, ...g.userData.body.position.toArray());
            pos.needsUpdate = true;
          } else {
            g.position.fromArray(p.p);
            g.quaternion.fromArray(p.q);
          }
        }
        setTime(state.sim.time);
      }
      state.last = now;
      renderer.render(three, camera);
    };
    state.frame = requestAnimationFrame(loop);
    api.current = { three, room, objects, gizmo, state, camera, orbit };
    return () => {
      cancelAnimationFrame(state.frame);
      ro.disconnect();
      renderer.domElement.removeEventListener('pointerdown', onDown);
      state.sim?.free();
      gizmo.dispose();
      orbit.dispose();
      renderer.dispose();
      el.removeChild(renderer.domElement);
      api.current = null;
    };
  }, []);

  // Rebuild room and object meshes from the scene JSON whenever it changes (not while a run is live).
  useEffect(() => {
    const a = api.current;
    if (!a || run === 'playing' || run === 'paused') return;
    a.gizmo.detach();
    for (const c of [...a.objects.children]) { a.objects.remove(c); c.traverse((m) => { m.geometry?.dispose(); m.material?.dispose(); }); }
    for (const c of [...a.room.children]) if (c !== a.state.points) a.room.remove(c);
    if (scene.room.kind !== 'none') {
      const grid = new THREE.GridHelper(10, 20, 0x9ca3af, 0xd1d5db);
      grid.quaternion.fromArray(upQuat(scene.gravity));
      grid.position.set(0, scene.room.floor_y, 0);
      a.room.add(grid);
    }
    if (a.state.points) a.state.points.visible = scene.room.kind === 'ply';
    for (const o of scene.objects) a.objects.add(objectMesh(o));
    const g = a.objects.children.find((c) => c.userData.id === selected);
    if (g) { a.gizmo.attach(g); a.gizmo.setMode(mode); }
    setJsonText(sceneJson(scene));
  }, [scene, selected, mode, run]);

  const edit = (fn) => {
    try { setScene((s) => validateScene(fn(structuredClone(s)))); } catch (e) { setMessage(e.message); }
  };
  const addObject = (kind) => {
    if (scene.objects.length >= MAX_OBJECTS) { setMessage('At most ' + MAX_OBJECTS + ' objects.'); return; }
    const o = makeObject(kind, scene, [((scene.objects.length % 5) - 2) * 0.6, kind === 'ramp' ? 0.35 : 1.2, 0]);
    edit((s) => ({ ...s, objects: [...s.objects, o] }));
    setSelected(o.id);
  };
  const stop = () => {
    const st = api.current?.state;
    if (st) { st.playing = false; st.sim?.free(); st.sim = null; }
    setRun('stopped'); setTime(0);
  };
  const play = async () => {
    const st = api.current.state;
    if (run === 'paused') { st.playing = true; setRun('playing'); return; }
    setRun('loading'); setMessage('Loading the physics engine...');
    try {
      const R = await loadRapier();
      api.current.gizmo.detach();
      st.sim = createPhysics(R, sceneRef.current);
      st.acc = 0; st.playing = true;
      setRun('playing'); setMessage('Running. SIMULATED physics, gravity from the scene vector.');
    } catch (e) { setRun('stopped'); setMessage('Physics could not start: ' + e.message); }
  };
  const pause = () => { api.current.state.playing = false; setRun('paused'); setMessage('Paused. Resume, reset, or export the SIMULATED sensor traces.'); };
  const traces = () => api.current?.state.sim?.traces() ?? [];
  const exportTraces = () => {
    const t = traces();
    if (!t.length) { setMessage('Play the scene with at least one sensor first.'); return; }
    download('lab-traces.json', JSON.stringify({ label: 'SIMULATED', traces: t, fitter_requests: Object.fromEntries(t.map((x) => [x.object_id, fitterRequest(x, 1)])) }));
  };
  const applyJson = (text) => {
    try { const s = parseScene(text); stop(); setSelected(null); setScene(s); setMessage('Scene loaded: ' + s.objects.length + ' objects.'); }
    catch (e) { setMessage('Scene rejected: ' + e.message); }
  };
  const loadFile = async (e) => {
    const f = e.target.files?.[0];
    e.target.value = '';
    if (!f) return;
    if (f.size > 64 * 1024 * 1024) { setMessage('File over 64 MB.'); return; }
    if (/\.json$/i.test(f.name)) { applyJson(await f.text()); return; }
    try {
      const bytes = new Uint8Array(await f.arrayBuffer());
      const { positions, colors } = decodePlyXyzRgb(bytes, plyCount(bytes));
      const a = api.current;
      if (a.state.points) { a.room.remove(a.state.points); a.state.points.geometry.dispose(); }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geo.setAttribute('color', new THREE.BufferAttribute(colors, 3, true));
      a.state.points = new THREE.Points(geo, new THREE.PointsMaterial({ size: 0.02, vertexColors: true }));
      a.room.add(a.state.points);
      setPlyName(f.name);
      edit((s) => ({ ...s, room: { kind: 'ply', floor_y: s.room.floor_y ?? 0, source: f.name.slice(0, 200), scale_verified: false } }));
      setMessage('Room loaded: ' + positions.length / 3 + ' points. Scale unverified.');
    } catch (err) { setMessage('Room rejected: ' + err.message); }
  };

  const sel = scene.objects.find((o) => o.id === selected);
  const live = run === 'playing' || run === 'paused';
  const selTrace = live && sel?.sensor ? api.current?.state.sim?.trace(sel.id) : null;
  return <section className="lab-editor" aria-label="Lab editor">
    <div className="le-bar" role="toolbar" aria-label="Add objects">
      {KINDS.map((k) => <button key={k} type="button" onClick={() => addObject(k)} disabled={live}>+ {LABELS[k]}</button>)}
    </div>
    <div className="le-stage">
      <div ref={host} className="le-canvas" data-testid="lab-editor-canvas" />
      <span className="le-chip">SIMULATED</span>
      {scene.room.kind === 'ply' && !scene.room.scale_verified && <span className="le-chip le-warn">Room scale unverified</span>}
      <span className="le-time" aria-live="off">t = {time.toFixed(2)} s</span>
    </div>
    <div className="le-bar" role="toolbar" aria-label="Simulation">
      {run !== 'playing' ? <button type="button" onClick={play} disabled={run === 'loading' || !scene.objects.length}>{run === 'paused' ? 'Resume' : 'Play'}</button> : <button type="button" onClick={pause}>Pause</button>}
      <button type="button" onClick={stop} disabled={!live}>Reset</button>
      <button type="button" onClick={exportTraces} disabled={!live}>Export traces</button>
      <button type="button" onClick={() => download('lab-scene.json', sceneJson(scene))}>Export scene</button>
      <label className="le-file">Import scene or room (.json, .ply)<input type="file" accept=".json,.ply" onChange={loadFile} /></label>
    </div>
    <p className="le-status" role="status">{message} Gravity [{scene.gravity.join(', ')}] m/s^2{plyName ? ', room ' + plyName : ''}.</p>
    <div className="le-panels">
      <div className="le-panel">
        <h3>Selected</h3>
        {!sel ? <p>Click an object to select it.</p> : <>
          <p><strong>{sel.id}</strong> ({LABELS[sel.kind]})</p>
          <div className="le-bar" role="group" aria-label="Transform mode">
            {[['translate', 'Move'], ['rotate', 'Rotate'], ['scale', 'Resize']].map(([m, l]) => <button key={m} type="button" aria-pressed={mode === m} onClick={() => setMode(m)} disabled={live}>{l}</button>)}
          </div>
          <label><input type="checkbox" checked={sel.sensor} disabled={live} onChange={(e) => edit((s) => ({ ...s, objects: s.objects.map((o) => (o.id === sel.id ? { ...o, sensor: e.target.checked } : o)) }))} /> Record trajectory sensor</label>
          {sel.kind !== 'pendulum' && sel.kind !== 'spring' && <label><input type="checkbox" checked={sel.fixed} disabled={live} onChange={(e) => edit((s) => ({ ...s, objects: s.objects.map((o) => (o.id === sel.id ? { ...o, fixed: e.target.checked } : o)) }))} /> Fixed in place</label>}
          <p>Size {sel.size.map((v) => v.toFixed(2)).join(' x ')} m, mass {sel.mass} kg</p>
          {selTrace && <p>Sensor: {selTrace.samples.length} samples{selTrace.truncated ? ' (cap reached)' : ''}</p>}
          <button type="button" className="le-danger" disabled={live} onClick={() => { edit((s) => ({ ...s, objects: s.objects.filter((o) => o.id !== sel.id) })); setSelected(null); }}>Delete</button>
        </>}
      </div>
      <div className="le-panel">
        <h3>Scene JSON (lab-scene-v1)</h3>
        <textarea aria-label="Scene JSON" value={jsonText} onChange={(e) => setJsonText(e.target.value)} spellCheck={false} rows={10} />
        <button type="button" onClick={() => applyJson(jsonText)}>Apply JSON</button>
      </div>
    </div>
  </section>;
}

