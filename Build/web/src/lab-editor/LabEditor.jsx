'use client';

// N10 lab editor: optional room + editable objects (lab-scene-v1 JSON) + Rapier play/pause/reset + per-object sensor traces.
import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls.js';
import { defaultScene, makeObject, validateScene, parseScene, sceneJson, fitterRequest, KINDS, MAX_OBJECTS } from './scene.mjs';
import { createPhysics, loadRapier, movingStart, upQuat } from './physics.mjs';
import AgentPanel from './AgentPanel.jsx';
import { decodePlyXyzRgb } from '../viewer/scene-model.mjs';
import { naturalPoint, trajectoryScene } from '../workspace/measure.mjs';
import { robustBounds, fitDistance } from './frame.mjs';
import './lab-editor.css';

const COLORS = { ball: 0xe4572e, block: 0x3b82f6, ramp: 0x9ca3af, pendulum: 0xf59e0b, spring: 0x10b981 };
const LABELS = { ball: 'Ball', block: 'Block', ramp: 'Ramp', pendulum: 'Pendulum', spring: 'Spring' };
const MAX_STEPS_PER_FRAME = 8;
// N24: compact icon toolbar (inline 24px stroke paths, same style as shell/icons.mjs).
const ICONS = {
  ball: 'M12 4a8 8 0 1 0 0 16a8 8 0 1 0 0-16z', block: 'M5 5h14v14H5z', ramp: 'M3 19h18L3 7z',
  pendulum: 'M4 4h16M12 4l4 11M16 15a2.5 2.5 0 1 0 0.01 0', spring: 'M12 2v3l-5 2 10 3-10 3 10 3-5 2v4',
  play: 'M7 4l13 8-13 8z', pause: 'M8 5v14M16 5v14', reset: 'M4 12a8 8 0 1 0 2.3-5.6M4 4v4h4',
  traces: 'M4 4v16h16M8 15l3-4 3 2 5-6', download: 'M12 4v11M7 10l5 5 5-5M4 20h16', upload: 'M12 15V4M7 9l5-5 5 5M4 20h16',
  panel: 'M4 5h16v14H4zM9 5v14', frame: 'M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5',
};
const Ico = ({ n }) => <svg className="le-ico" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false"><path d={ICONS[n]} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>;
const isDark = () => typeof document !== 'undefined' && document.documentElement.dataset.tone === 'dark';
function themeColor(name, fallback) {
  const v = typeof document === 'undefined' ? '' : getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  try { return new THREE.Color(v || fallback); } catch { return new THREE.Color(fallback); }
}

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

// N22: live sources. ?room=<job> = room.ply + scene.json from the room job; ?experiment=<id> = the measured track as a lab scene.
const WS = '/api/workspace';
const LIVE_ID = /^[A-Za-z0-9_-]{1,64}$/;
async function getJson(path, init) {
  const r = await fetch(WS + path, { cache: 'no-store', ...init, headers: init?.body ? { 'content-type': 'application/json' } : undefined });
  const b = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(b?.error?.message ?? b?.detail?.error?.message ?? b?.detail?.message ?? 'HTTP ' + r.status);
  return b;
}

// "Mark the A4 sheet" (two clicks on its long edge) and "Add a real object" (one click) on a model view PNG.
function RoomTools({ id, room, onReload }) {
  const [view, setView] = useState(0);
  const [tool, setTool] = useState(null); // 'a4' | 'object'
  const [clicks, setClicks] = useState([]);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState('');
  const [bust, setBust] = useState(0);
  const pickTool = (t) => { setTool(tool === t ? null : t); setClicks([]); setNote(t === 'a4' ? 'Click both ends of the A4 sheet long edge (29.7 cm).' : 'Click a real object, for example a chair or table.'); };
  const send = async (path, body, done) => {
    setBusy(true);
    try { const r = await getJson('/rooms/' + id + path, { method: 'POST', body: JSON.stringify(body) }); setTool(null); setClicks([]); setBust((b) => b + 1); await onReload(done(r)); setNote(''); }
    catch (e) { setNote('Not applied: ' + e.message); setClicks([]); }
    setBusy(false);
  };
  const click = (e) => {
    if (!tool || busy) return;
    const el = e.currentTarget, p = naturalPoint(e.nativeEvent.offsetX, e.nativeEvent.offsetY, el.clientWidth, el.clientHeight, el.naturalWidth, el.naturalHeight);
    if (!p) return;
    const rc = [p.y, p.x], next = [...clicks, { rc, left: (100 * p.x) / el.naturalWidth, top: (100 * p.y) / el.naturalHeight }];
    setClicks(next);
    if (tool === 'object') send('/objects', { view, point: rc }, (r) => 'Added ' + r.object.id + ': ' + r.object.size.map((v) => v.toFixed(2)).join(' x ') + ' m box proxy, ' + r.object.labels.geometry + ', scale ' + r.object.labels.scale + '. ' + r.object.labels.caveat + '.');
    else if (next.length === 2) send('/scale', { reference: { view, p0: next[0].rc, p1: next[1].rc } }, (r) => (r.room.scale.reference_rejected ? 'A4 scale not applied: ' + r.room.scale.reference_rejected.reason : 'A4 scale applied: ' + r.room.scale.status + '.'));
  };
  const sc = room.scale ?? {};
  return <div className="le-panel le-room">
    <h3>Your room</h3>
    <p>Geometry {room.labels?.geometry ?? 'MODEL-ESTIMATED'}. Scale <strong>{sc.status}</strong>{sc.sd != null ? ': ' + sc.metres_per_model_unit.toFixed(3) + ' +/- ' + sc.sd.toFixed(3) + ' m per unit' : ''}. Gravity {room.gravity?.status}{room.gravity?.uncertainty_deg != null ? ' +/- ' + room.gravity.uncertainty_deg + ' deg' : ''}.</p>
    {sc.reference_rejected && <p className="le-rejected" role="status">A4 scale not applied: {sc.reference_rejected.reason}</p>}
    <div className="le-bar" role="group" aria-label="Room tools">
      <button type="button" aria-pressed={tool === 'a4'} disabled={busy} onClick={() => pickTool('a4')}>Mark the A4 sheet</button>
      <button type="button" aria-pressed={tool === 'object'} disabled={busy} onClick={() => pickTool('object')}>Add a real object</button>
      <label>View <select value={view} onChange={(e) => { setView(Number(e.target.value)); setClicks([]); }}>{Array.from({ length: room.views || 1 }, (_, i) => <option key={i} value={i}>{i + 1}</option>)}</select></label>
    </div>
    {note && <p role="status">{busy ? 'Working: ' : ''}{note}</p>}
    <div className="le-view" data-tool={tool ?? undefined}>
      <img src={WS + '/rooms/' + id + '/views/' + view + '.png?v=' + bust} alt={'Room view ' + (view + 1) + (tool ? '. Click to ' + (tool === 'a4' ? 'mark the A4 sheet' : 'add an object') : '')} onClick={click}
        onError={(e) => { e.currentTarget.style.display = 'none'; setNote('No view image for this room, so A4 and object clicks are unavailable here.'); }} onLoad={(e) => { e.currentTarget.style.display = ''; }} />
      {clicks.map((c, i) => <span key={i} className="le-mark" style={{ left: c.left + '%', top: c.top + '%' }} aria-hidden="true" />)}
    </div>
  </div>;
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
  const [src, setSrc] = useState(null); // N22 live source: { kind: 'room', id, room } | { kind: 'experiment', id }
  const [side, setSide] = useState(true); // N24: inspector + scene JSON panel (collapsible)
  const [tone, setTone] = useState('light');
  const sceneRef = useRef(scene);
  sceneRef.current = scene;

  // N24: follow the site theme (light, dark, colour modes); collapse the side panel by default on narrow screens.
  useEffect(() => {
    if (window.matchMedia?.('(max-width: 900px)').matches) setSide(false);
    const read = () => setTone((document.documentElement.dataset.theme || '') + (isDark() ? ':dark' : ''));
    read();
    const mo = new MutationObserver(read);
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'data-tone'] });
    return () => mo.disconnect();
  }, []);
  useEffect(() => { const a = api.current; if (a) a.three.background = themeColor('--r2s-bg', isDark() ? '#111113' : '#f3f4f6'); }, [tone]);

  useEffect(() => {
    const el = host.current;
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    el.appendChild(renderer.domElement);
    const three = new THREE.Scene();
    three.background = themeColor('--r2s-bg', isDark() ? '#111113' : '#f3f4f6');
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

  useEffect(() => {
    const p = new URLSearchParams(window.location.search), room = p.get('room'), exp = p.get('experiment');
    if (room && LIVE_ID.test(room)) loadRoom(room); else if (exp && LIVE_ID.test(exp)) loadExperiment(exp);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Rebuild room and object meshes from the scene JSON whenever it changes (not while a run is live).
  useEffect(() => {
    const a = api.current;
    if (!a || run === 'playing' || run === 'paused') return;
    a.gizmo.detach();
    for (const c of [...a.objects.children]) { a.objects.remove(c); c.traverse((m) => { m.geometry?.dispose(); m.material?.dispose(); }); }
    for (const c of [...a.room.children]) if (c !== a.state.points) a.room.remove(c);
    if (scene.room.kind !== 'none') {
      const size = a.state.gridSize ?? 10, dark = isDark();
      const grid = new THREE.GridHelper(size, 20, dark ? 0x52525b : 0x9ca3af, dark ? 0x2a2a2e : 0xd1d5db);
      grid.quaternion.fromArray(upQuat(scene.gravity));
      grid.position.set(a.state.gridAt?.[0] ?? 0, scene.room.floor_y, a.state.gridAt?.[2] ?? 0);
      a.room.add(grid);
    }
    if (a.state.points) a.state.points.visible = scene.room.kind === 'ply';
    for (const o of scene.objects) a.objects.add(objectMesh(o));
    const g = a.objects.children.find((c) => c.userData.id === selected);
    if (g) { a.gizmo.attach(g); a.gizmo.setMode(mode); }
    setJsonText(sceneJson(scene));
  }, [scene, selected, mode, run, tone]);

  // N24: fit the camera to the loaded room or track (robust bounding box, keeps the current viewing direction).
  const frameTo = (positions) => {
    const a = api.current, b = robustBounds(positions);
    if (!a || !b) return null;
    const c = new THREE.Vector3(...b.center), dir = a.camera.position.clone().sub(a.orbit.target);
    if (dir.lengthSq() < 1e-9) dir.set(0.6, 0.45, 0.8);
    const d = fitDistance(b.radius, a.camera.fov, a.camera.aspect);
    a.camera.position.copy(c).add(dir.normalize().multiplyScalar(d));
    a.camera.near = Math.max(1e-3, d / 200); a.camera.far = Math.max(500, d * 20);
    a.camera.updateProjectionMatrix();
    a.orbit.target.copy(c); a.orbit.update();
    a.state.view = { center: b.center, radius: b.radius };
    return b;
  };
  const reframe = () => {
    const a = api.current, pos = a?.state.points?.visible ? a.state.points.geometry.attributes.position.array : null;
    if (pos) { frameTo(pos); return; }
    const pts = scene.objects.flatMap((o) => o.position);
    frameTo(pts.length ? [...pts, 0, scene.room.floor_y ?? 0, 0] : [-1, 0, -1, 1, 1.5, 1]);
  };

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
  const showPly = (bytes) => {
    const { positions, colors } = decodePlyXyzRgb(bytes, plyCount(bytes));
    const a = api.current;
    if (a.state.points) { a.room.remove(a.state.points); a.state.points.geometry.dispose(); }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3, true));
    const b = frameTo(positions);
    // Point size and floor grid follow the room extent so any reconstruction scale fills the view.
    a.state.points = new THREE.Points(geo, new THREE.PointsMaterial({ size: b ? Math.max(0.004, b.radius / 70) : 0.02, vertexColors: true }));
    if (b) { a.state.gridSize = Math.max(4, Math.ceil(b.radius * 3)); a.state.gridAt = b.center; }
    a.room.add(a.state.points);
    return positions.length / 3;
  };
  const loadRoom = async (id, note) => {
    try {
      const r = await getJson('/rooms/' + id + '/result');
      const res = await fetch(WS + '/rooms/' + id + '/room.ply', { cache: 'no-store' });
      if (!res.ok) throw new Error('room.ply HTTP ' + res.status);
      const n = showPly(new Uint8Array(await res.arrayBuffer()));
      stop(); setSelected(null); setScene(validateScene(r.scene)); setPlyName('room.ply'); setSrc({ kind: 'room', id, room: r.room });
      setMessage(note ?? 'Your room: ' + n + ' points, ' + r.scene.objects.length + ' objects. Geometry MODEL-ESTIMATED; ' + r.room.scale.status + '.');
    } catch (e) { setMessage('Room not loaded: ' + e.message); }
  };
  const loadExperiment = async (id) => {
    try {
      const t = trajectoryScene((await getJson('/experiments/' + id)).experiment.result);
      if (!t) throw new Error('this experiment has no finished track yet');
      const a = api.current;
      if (a.state.track) a.three.remove(a.state.track);
      const geo = new THREE.BufferGeometry().setFromPoints(t.track.map((q) => new THREE.Vector3(...q)));
      a.state.track = new THREE.Group().add(new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0x111827 })), new THREE.Points(geo, new THREE.PointsMaterial({ size: 0.025, color: 0x4f46e5 })));
      a.three.add(a.state.track);
      frameTo(t.track.flat());
      stop(); setSelected(null); setScene(validateScene(t.scene)); setSrc({ kind: 'experiment', id });
      setMessage('Dots and line: your measured track. ' + t.note);
    } catch (e) { setMessage('Experiment not loaded: ' + e.message); }
  };
  const loadFile = async (e) => {
    const f = e.target.files?.[0];
    e.target.value = '';
    if (!f) return;
    if (f.size > 64 * 1024 * 1024) { setMessage('File over 64 MB.'); return; }
    if (/\.json$/i.test(f.name)) { applyJson(await f.text()); return; }
    try {
      const bytes = new Uint8Array(await f.arrayBuffer());
      const n = showPly(bytes);
      setPlyName(f.name);
      edit((s) => ({ ...s, room: { kind: 'ply', floor_y: s.room.floor_y ?? 0, source: f.name.slice(0, 200), scale_verified: false } }));
      setMessage('Room loaded: ' + n + ' points. Scale unverified.');
    } catch (err) { setMessage('Room rejected: ' + err.message); }
  };

  const sel = scene.objects.find((o) => o.id === selected);
  const live = run === 'playing' || run === 'paused';
  const selTrace = live && sel?.sensor ? api.current?.state.sim?.trace(sel.id) : null;
  const title = src?.kind === 'room' ? 'Your room lab' : src?.kind === 'experiment' ? 'Experiment replay' : 'Virtual lab';
  return <section className="lab-editor" aria-label="Lab editor" data-side={side ? 'open' : 'closed'}>
    <div className="le-top" role="toolbar" aria-label="Lab tools">
      <button type="button" className="le-icon-btn" aria-pressed={side} aria-label={(side ? 'Hide' : 'Show') + ' inspector and scene JSON'} title="Inspector and scene JSON" onClick={() => setSide((v) => !v)}><Ico n="panel" /></button>
      <strong className="le-title">{title}</strong>
      <div className="le-group" role="group" aria-label="Add objects">
        {KINDS.map((k) => <button key={k} type="button" title={'Add a ' + LABELS[k].toLowerCase()} aria-label={'Add ' + LABELS[k]} onClick={() => addObject(k)} disabled={live}><Ico n={k} /><span className="le-lbl">{LABELS[k]}</span></button>)}
      </div>
      <div className="le-group" role="group" aria-label="Simulation">
        {run !== 'playing' ? <button type="button" className="le-primary" onClick={play} disabled={run === 'loading' || !scene.objects.length}><Ico n="play" /><span>{run === 'paused' ? 'Resume' : 'Play'}</span></button> : <button type="button" className="le-primary" onClick={pause}><Ico n="pause" /><span>Pause</span></button>}
        <button type="button" onClick={stop} disabled={!live} title="Reset to the start"><Ico n="reset" /><span className="le-lbl">Reset</span></button>
      </div>
      <div className="le-group le-end" role="group" aria-label="View and files">
        <button type="button" className="le-icon-btn" onClick={reframe} aria-label="Fit view to the room" title="Fit view to the room"><Ico n="frame" /></button>
        <button type="button" className="le-icon-btn" onClick={exportTraces} disabled={!live} aria-label="Export traces" title="Export SIMULATED sensor traces"><Ico n="traces" /></button>
        <button type="button" className="le-icon-btn" onClick={() => download('lab-scene.json', sceneJson(scene))} aria-label="Export scene" title="Export scene JSON"><Ico n="download" /></button>
        <label className="le-file le-icon-btn" title="Import scene or room (.json, .ply)"><Ico n="upload" /><span className="le-sr">Import scene or room (.json, .ply)</span><input type="file" accept=".json,.ply" onChange={loadFile} /></label>
      </div>
    </div>
    <div className="le-work">
      {side && <aside className="le-side le-left" aria-label="Inspector">
      <div className="le-panel">
        <h3>Selected object</h3>
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
      <details className="le-panel le-json">
        <summary>Scene JSON (lab-scene-v1)</summary>
        <textarea aria-label="Scene JSON" value={jsonText} onChange={(e) => setJsonText(e.target.value)} spellCheck={false} rows={12} />
        <button type="button" onClick={() => applyJson(jsonText)}>Apply JSON</button>
      </details>
      </aside>}
      <div className="le-stage">
        <div ref={host} className="le-canvas" data-testid="lab-editor-canvas" />
        <div className="le-chips">
          <span className="le-chip">SIMULATED</span>
          {src?.kind === 'experiment' && <span className="le-chip le-warn">Track MEASURED, ball what-if</span>}
          {scene.room.kind === 'ply' && !scene.room.scale_verified && <span className="le-chip le-warn">Room scale unverified</span>}
        </div>
        <span className="le-time" aria-live="off">t = {time.toFixed(2)} s</span>
        <p className="le-status" role="status">{message} Gravity [{scene.gravity.join(', ')}] m/s^2{plyName ? ', room ' + plyName : ''}.</p>
      </div>
      <aside className="le-side le-right" aria-label="Room tools and agent">
        {src?.kind === 'room' && <RoomTools id={src.id} room={src.room} onReload={(note) => loadRoom(src.id, note)} />}
        <AgentPanel scene={scene} load={!src && !/[?&](room|experiment)=/.test(window.location.search)} onScene={(s, msg) => { stop(); setSelected(null); setScene(s); setMessage(msg); }} />
      </aside>
    </div>
  </section>;
}

