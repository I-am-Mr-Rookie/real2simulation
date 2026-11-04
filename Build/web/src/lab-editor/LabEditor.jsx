'use client';

// N10 lab editor: optional room + editable objects (lab-scene-v1 JSON) + Rapier play/pause/reset + per-object sensor traces.
import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls.js';
import { defaultScene, makeObject, validateScene, parseScene, sceneJson, fitterRequest, keepAdded, MAX_OBJECTS, MASS_SET } from './scene.mjs';
import { createPhysics, loadRapier, movingStart, upQuat, roomProxy, kitParts } from './physics.mjs';
import { emptyHistory, record, undo, redo, removeObject, typing, tidyView } from './history.mjs';
import AgentPanel from './AgentPanel.jsx';
import { decodePlyXyzRgb } from '../viewer/scene-model.mjs';
import { naturalPoint, trajectoryScene, fmtPm, gravityCheck } from '../workspace/measure.mjs';
import { robustBounds, fitDistance, FRAME_Q } from './frame.mjs';
import { colliderGeometry, loadShapeGlb, SHAPE_LABEL } from './sf3d-shape.mjs';
import { lookMesh } from './furniture-shape.mjs';
import { mergeShapeUpdates } from './shape-upgrades.mjs';
import { TEMPLATES, templateScene, PHYSICS_LAB_CARDS, hasPhysicsStations } from './templates.mjs';
import './lab-editor.css';

const COLORS = { ball: 0xe4572e, block: 0x3b82f6, ramp: 0x9ca3af, pendulum: 0xf59e0b, spring: 0x10b981, flywheel: 0x8b5cf6, atwood: 0x0ea5e9,
  cart: 0xef4444, launcher: 0xe4572e, cradle: 0x94a3b8, mass: 0xb8860b, ruler: 0xfacc15, protractor: 0x22c55e, photogate: 0xf97316 };
const LABELS = { ball: 'Ball', block: 'Block', ramp: 'Ramp', pendulum: 'Pendulum', spring: 'Spring', flywheel: 'Flywheel', atwood: 'Atwood machine',
  cart: 'Cart and track', launcher: 'Projectile launcher', cradle: 'Collision balls', mass: 'Mass', ruler: 'Ruler', protractor: 'Protractor', photogate: 'Photogate timer' };
// N33: compact Add menu, grouped. Mass set entries carry grams.
const MENU = [['Basics', ['ball', 'block', 'ramp', 'pendulum', 'spring']], ['Apparatus', ['flywheel', 'atwood', 'cart', 'launcher', 'cradle']],
  ['Mass set', MASS_SET.map((g) => ['mass', g])], ['Probes', ['ruler', 'protractor', 'photogate']]];
const ADD_Y = { ramp: 0.35, atwood: 1.6, cart: 0.4, launcher: 0.1, cradle: 0.9, mass: 1, ruler: 0.5, photogate: 0.5, protractor: 1.3 };
const MAX_STEPS_PER_FRAME = 8;
// N24: compact icon toolbar (inline 24px stroke paths, same style as shell/icons.mjs).
const ICONS = {
  ball: 'M12 4a8 8 0 1 0 0 16a8 8 0 1 0 0-16z', block: 'M5 5h14v14H5z', ramp: 'M3 19h18L3 7z',
  pendulum: 'M4 4h16M12 4l4 11M16 15a2.5 2.5 0 1 0 0.01 0', spring: 'M12 2v3l-5 2 10 3-10 3 10 3-5 2v4',
  play: 'M7 4l13 8-13 8z', pause: 'M8 5v14M16 5v14', reset: 'M4 12a8 8 0 1 0 2.3-5.6M4 4v4h4',
  traces: 'M4 4v16h16M8 15l3-4 3 2 5-6', download: 'M12 4v11M7 10l5 5 5-5M4 20h16', upload: 'M12 15V4M7 9l5-5 5 5M4 20h16',
  panel: 'M4 5h16v14H4zM9 5v14', frame: 'M12 3v4M12 17v4M3 12h4M17 12h4M12 9a3 3 0 1 0 .01 0', // N85: target, so it no longer reads as a second fullscreen icon
  trials: 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z',
  flywheel: 'M12 4a8 8 0 1 0 0 16a8 8 0 1 0 0-16zM12 11v2M20 12v9', atwood: 'M12 3a3 3 0 1 0 0 6a3 3 0 1 0 0-6zM9 6v10M15 6v6M7 16h4v4H7zM13 12h4v4h-4z',
  cart: 'M3 19L21 11M8 15l7-3-1-2-7 3z', launcher: 'M4 20h8M7 20l3-5M10 15l8-8M15 6h4v4', cradle: 'M3 4h18M6 4v11M10 4v11M14 4v11M18 4v11M6 15h12',
  mass: 'M8 9h8l2 11H6zM10 9V5h4v4', ruler: 'M3 9h18v6H3zM7 9v3M11 9v3M15 9v3M19 9v3', protractor: 'M3 17a9 9 0 0 1 18 0zM12 17l5-6',
  photogate: 'M5 4v16M19 4v16M5 12h14', trash: 'M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13', add: 'M12 5v14M5 12h14', undo: 'M9 6l-5 5 5 5M4 11h11a5 5 0 0 1 0 10h-3', redo: 'M15 6l5 5-5 5M20 11H9a5 5 0 0 0 0 10h3',
  select: 'M5 3l14 8-6 2-2 6z', translate: 'M12 3v18M3 12h18M12 3l-3 3M12 3l3 3M21 12l-3-3M21 12l-3 3', rotate: 'M20 12a8 8 0 1 1-3-6.2M20 4v4h-4', scale: 'M4 14v6h6M20 10V4h-6M4 20L20 4',
  eye: 'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM12 9a3 3 0 1 0 0.01 0', eyeoff: 'M3 3l18 18M10.6 6.1A10 10 0 0 1 12 6c6 0 10 6 10 6a17 17 0 0 1-3.2 3.7M6.6 6.6C3.8 8.3 2 12 2 12s4 7 10 7a9 9 0 0 0 4.4-1.1',
  agent: 'M12 3l2 5 5 2-5 2-2 5-2-5-5-2 5-2z', expand: 'M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5', room: 'M3 11l9-7 9 7v9H3zM9 20v-6h6v6', list: 'M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01',
  save: 'M5 3h11l3 3v15H5zM8 3v5h7V3M8 21v-7h8v7', copy: 'M9 9h11v11H9zM5 15H4V4h11v1',
};
const Ico = ({ n }) => <svg className="le-ico" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false"><path d={ICONS[n]} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>;
const isDark = () => typeof document !== 'undefined' && document.documentElement.dataset.tone === 'dark';
function themeColor(name, fallback) {
  const v = typeof document === 'undefined' ? '' : getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  try { return new THREE.Color(v || fallback); } catch { return new THREE.Color(fallback); }
}

// N44: walls the fit could not trust are named "not observed" instead of being counted (N43 RM02 partial view)
const wallText = (sh) => { const n = sh.walls.filter((w) => w.status === 'FIT').length; return n + ' walls' + (n < sh.walls.length ? ' (' + (sh.walls.length - n) + ' not observed, placed at the scan edge)' : ''); };
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
  const mat = new THREE.MeshStandardMaterial({ color: COLORS[o.kind], roughness: 0.6, ...(String(o.id).startsWith('wall-') && { transparent: true, opacity: 0.3 }) }); // N39: see through shell walls
  if (o.kind !== 'ball' && o.kind !== 'block' && o.kind !== 'ramp' && o.kind !== 'pendulum' && o.kind !== 'spring') return kitMesh(o, g, mat);
  const sf3d = o.shape?.type === 'mesh';
  if (o.look && !sf3d) return lookMesh(o, g); // N49: room shell class shape (wall, door, table, chair...)
  const geo = sf3d ? colliderGeometry(o.shape) : o.kind === 'ball' || o.kind === 'pendulum' ? new THREE.SphereGeometry(0.5, 24, 16) : new THREE.BoxGeometry(1, 1, 1);
  const body = new THREE.Mesh(geo, mat);
  body.scale.fromArray(o.kind === 'ball' || o.kind === 'pendulum' ? Array(3).fill(Math.max(...o.size)) : o.size);
  body.userData.id = o.id;
  g.add(body);
  if (sf3d) loadShapeGlb(o.shape, body, o.id);
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

// N33 kit meshes; moving parts follow physics poses (userData.parts), strings follow userData.links.
function kitMesh(o, g, mat) {
  const mesh = (geo, m = mat) => { const x = new THREE.Mesh(geo, m); g.add(x); return x; };
  const local = (p) => { g.updateMatrixWorld(); return g.worldToLocal(new THREE.Vector3(...p)); };
  const dark = new THREE.MeshStandardMaterial({ color: 0x374151 });
  const parts = kitParts(o), P = o.params;
  g.userData.parts = []; g.userData.links = [];
  const link = (from, i) => {
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([from, g.userData.parts[i].position.clone()]), new THREE.LineBasicMaterial({ color: 0x111827 }));
    g.add(line); g.userData.links.push([line, i]);
  };
  if (o.kind === 'flywheel' || o.kind === 'atwood') {
    const r = P.radius;
    const disc = mesh(new THREE.CylinderGeometry(r, r, o.kind === 'flywheel' ? o.size[2] : 0.02, 32).rotateX(Math.PI / 2), o.kind === 'flywheel' ? mat : dark);
    mesh(new THREE.BoxGeometry(0.02, 0.02, 0.12), dark);
    if (o.kind === 'flywheel') { g.userData.parts.push(disc); mesh(new THREE.BoxGeometry(0.02, 0.06, 0.02), dark).position.set(0.6 * r, 0, o.size[2] / 2 + 0.01); disc.add(g.children.at(-1)); }
    for (const pt of o.kind === 'flywheel' ? parts.slice(1) : parts) {
      const m = mesh(o.kind === 'flywheel' ? new THREE.SphereGeometry(pt.r, 16, 12) : new THREE.BoxGeometry(2 * pt.r, 2 * pt.r, 2 * pt.r));
      m.position.copy(local(pt.p)); g.userData.parts.push(m);
    }
    (o.kind === 'flywheel' ? [[new THREE.Vector3(r, 0, 0), 1]] : [[new THREE.Vector3(-r, 0, 0), 0], [new THREE.Vector3(r, 0, 0), 1]]).forEach(([f, i]) => link(f, i));
  } else if (o.kind === 'cart') {
    for (const pt of parts) {
      const m = mesh(new THREE.BoxGeometry(...pt.size), pt.role === 'track' ? new THREE.MeshStandardMaterial({ color: 0x9ca3af }) : mat);
      m.position.copy(local(pt.p)); m.quaternion.copy(g.quaternion.clone().invert().multiply(new THREE.Quaternion(...pt.q))); g.userData.parts.push(m);
    }
  } else if (o.kind === 'cradle') {
    const d = Math.max(...o.size);
    mesh(new THREE.BoxGeometry((P.count + 1) * d, 0.02, 0.04), dark);
    parts.forEach((pt, i) => { const m = mesh(new THREE.SphereGeometry(d / 2, 20, 14)); m.position.copy(local(pt.p)); g.userData.parts.push(m); link(local(pt.anchor), i); });
  } else if (o.kind === 'launcher') {
    const a = (P.angle_deg * Math.PI) / 180, barrel = mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.2, 16), dark);
    barrel.rotation.z = a - Math.PI / 2; barrel.position.set(-0.1 * Math.cos(a), -0.1 * Math.sin(a), 0);
    g.userData.body = mesh(new THREE.SphereGeometry(Math.max(...o.size) / 2, 20, 14));
  } else if (o.kind === 'mass') {
    mesh(new THREE.CylinderGeometry(0.5, 0.5, 1, 24)).scale.fromArray(o.size);
  } else if (o.kind === 'ruler') {
    mesh(new THREE.BoxGeometry(P.length, o.size[1], o.size[2]));
  } else if (o.kind === 'protractor') {
    mesh(new THREE.RingGeometry(0.08, 0.1, 32, 1, Math.PI, Math.PI), new THREE.MeshStandardMaterial({ color: COLORS.protractor, side: THREE.DoubleSide }));
  } else {
    for (const z of [-1, 1]) mesh(new THREE.BoxGeometry(0.02, 0.15, 0.02)).position.set(0, 0.075, (z * o.size[2]) / 2);
    mesh(new THREE.BoxGeometry(0.004, 0.004, o.size[2]), new THREE.MeshBasicMaterial({ color: 0xef4444 }));
  }
  g.traverse((m) => { m.userData.id = o.id; });
  return g;
}

// N22: live sources. ?room=<job> = room.ply + scene.json from the room job; ?experiment=<id> = the measured track as a lab scene.
const WS = '/api/workspace';
const LIVE_ID = /^[A-Za-z0-9_-]{1,64}$/;
async function getJson(path, init) {
  const r = await fetch(WS + path, { cache: 'no-store', ...init, headers: init?.body ? { 'content-type': 'application/json' } : undefined });
  const b = await r.json().catch(() => ({}));
  if (!r.ok) throw Object.assign(new Error(b?.error?.message ?? b?.detail?.error?.message ?? b?.detail?.message ?? 'HTTP ' + r.status), { status: r.status });
  return b;
}
const PENDING = 'r2s-template-edit'; // N89: template edits survive the sign-in round trip of Make a copy

// "Mark the A4 sheet" (two clicks on its long edge) and "Add a real object" (one click) on a model view PNG.
function RoomTools({ id, room, onReload }) {
  const [view, setView] = useState(0);
  const [tool, setTool] = useState(null); // 'a4' | 'object'
  const [clicks, setClicks] = useState([]);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState('');
  const [bust, setBust] = useState(0);
  const [imageReady, setImageReady] = useState(false);
  useEffect(() => { setImageReady(false); }, [id, view, bust]);
  const pickTool = (t) => { setTool(tool === t ? null : t); setClicks([]); setNote(tool === t ? '' : t === 'a4' ? 'Click both ends of the A4 sheet long edge (29.7 cm).' : 'Click a real object, for example a chair or table.'); };
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
    if (tool === 'object') send('/objects', { view, point: rc }, (r) => 'Added ' + r.object.id + ': ' + r.object.size.map((v) => v.toFixed(2)).join(' x ') + ' m, ' + r.object.labels.geometry + ', shape ' + (r.object.labels.shape ?? 'box') + (r.object.shape?.fallback_reason ? ' (' + r.object.shape.fallback_reason + ')' : '') + ', scale ' + r.object.labels.scale + '. ' + r.object.labels.caveat + '.');
    else if (next.length === 2) send('/scale', { reference: { view, p0: next[0].rc, p1: next[1].rc } }, (r) => (r.room.scale.reference_rejected ? 'A4 scale not applied: ' + r.room.scale.reference_rejected.reason : 'A4 scale applied: ' + r.room.scale.status + '.'));
  };
  const sc = room.scale ?? {};
  return <div className="le-panel le-room">
    <h3>Your room</h3>
    <p>Geometry {room.labels?.geometry ?? 'MODEL-ESTIMATED'}. Scale <strong>{sc.status}</strong>{sc.sd != null ? ': ' + sc.metres_per_model_unit.toFixed(3) + ' +/- ' + sc.sd.toFixed(3) + ' m per unit' : ''}. Gravity {room.gravity?.status}{room.gravity?.uncertainty_deg != null ? ' +/- ' + room.gravity.uncertainty_deg + ' deg' : ''}.</p>
    {sc.reference_rejected && <p className="le-rejected" role="status">A4 scale not applied: {sc.reference_rejected.reason}</p>}
    <div className="le-bar" role="group" aria-label="Room tools">
      <button type="button" aria-pressed={tool === 'a4'} disabled={busy || !imageReady} onClick={() => pickTool('a4')}>Mark the A4 sheet</button>
      <button type="button" aria-pressed={tool === 'object'} disabled={busy || !imageReady} onClick={() => pickTool('object')}>Add a real object</button>
      <button type="button" disabled={busy} onClick={() => { setNote('Finding walls, windows, doors and main furniture (hosted SAM 3.1, then Stable Fast 3D). This can take a few minutes.'); send('/shell', {}, (r) => 'Lab shell built: ' + wallText(r.shell) + ', ' + r.shell.openings.length + ' openings, ' + r.shell.kept.length + ' furniture kept, ' + r.shell.dropped + ' detections dropped. Geometry MODEL-ESTIMATED, scale ' + r.shell.labels.scale + '.'); }}>Build lab shell</button>
      <label>View <select value={view} onChange={(e) => { setView(Number(e.target.value)); setClicks([]); }}>{Array.from({ length: room.views || 1 }, (_, i) => <option key={i} value={i}>{i + 1}</option>)}</select></label>
    </div>
    {note && <p role="status">{busy ? 'Working: ' : ''}{note}</p>}
    <div className="le-view" data-tool={tool ?? undefined}>
      <img src={WS + '/rooms/' + id + '/views/' + view + '.png?v=' + bust} alt={'Room view ' + (view + 1) + (tool ? '. Click to ' + (tool === 'a4' ? 'mark the A4 sheet' : 'add an object') : '')} onClick={click}
        onError={(e) => { e.currentTarget.style.display = 'none'; setImageReady(false); setNote('No view image for this room, so A4 and object clicks are unavailable here.'); }} onLoad={(e) => { e.currentTarget.style.display = ''; setImageReady(true); }} />
      {clicks.map((c, i) => <span key={i} className="le-mark" style={{ left: c.left + '%', top: c.top + '%' }} aria-hidden="true" />)}
    </div>
  </div>;
}

export default function LabEditor({ initialScene, onTemplateTrials }) {
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
  const [backdrop, setBackdrop] = useState(true); // N39: room point cloud is an optional backdrop (off for shell rooms)
  const [src, setSrc] = useState(null); // N22 live source: { kind: 'room', id, room } | { kind: 'experiment', id }
  const improving = src?.kind === 'room' ? (src.room.shell?.kept ?? []).filter((o) => o.upgrade?.state === 'pending').length : 0;
  useEffect(() => {
    if (src?.kind !== 'room' || !improving) return;
    let cancelled = false, timer;
    const poll = async () => {
      try {
        const r = await getJson('/rooms/' + src.id + '/result');
        if (cancelled) return;
        // A running simulation keeps its bodies and mesh until it is stopped.
        if (run === 'stopped') {
          const next = validateScene(r.scene);
          setScene((s) => mergeShapeUpdates(s, next));
          setSrc((s) => s?.id === src.id ? { ...s, room: r.room } : s);
        }
      } catch { /* optional improvement; keep the usable room and retry */ }
      if (!cancelled) timer = setTimeout(poll, 5000);
    };
    timer = setTimeout(poll, 1000);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [src?.id, src?.kind, improving, run]);
  const [side, setSide] = useState(true); // N24: inspector + scene JSON panel (collapsible)
  const [tone, setTone] = useState('light');
  // N56 full-window layout: left tab, agent drawer, view-only hidden objects, lab name, project for the preview snapshot.
  const [leftTab, setLeftTab] = useState('objects');
  const [agentOpen, setAgentOpen] = useState(false);
  const [hidden, setHidden] = useState([]);
  const [name, setName] = useState('');
  const [project, setProject] = useState(null);
  const [origin, setOrigin] = useState(null); // N89: { kind: 'template', id, title } | { kind: 'saved' }
  const [savedJson, setSavedJson] = useState(null);
  const [copying, setCopying] = useState(false);
  const [sourceResult, setSourceResult] = useState(null);
  const [traceFit, setTraceFit] = useState(null);
  const [fitting, setFitting] = useState(false);
  const [cursor, setCursor] = useState(null);
  const sceneRef = useRef(scene);
  sceneRef.current = scene;
  useEffect(() => { const p = new URLSearchParams(window.location.search).get('project'); if (p && LIVE_ID.test(p)) setProject(p); }, []);
  useEffect(() => {
    const outside = (e) => { if (!addMenu.current?.contains(e.target)) addMenu.current?.removeAttribute('open'); };
    const escape = (e) => { if (e.key === 'Escape' && addMenu.current?.open) { addMenu.current.removeAttribute('open'); addMenu.current.querySelector('summary')?.focus(); } };
    document.addEventListener('pointerdown', outside); document.addEventListener('keydown', escape);
    return () => { document.removeEventListener('pointerdown', outside); document.removeEventListener('keydown', escape); };
  }, []);
  // N56: small JPEG of the canvas for the N55 workspace card (owner-scoped PUT; no project, no snapshot).
  const snapshot = async (id = project) => {
    const a = api.current;
    if (!a || !id) return;
    try {
      a.renderer.render(a.three, a.camera); // same tick as the copy, so no preserveDrawingBuffer needed
      const src = a.renderer.domElement, w = Math.min(640, src.width), c = document.createElement('canvas');
      c.width = w; c.height = Math.round((src.height * w) / Math.max(1, src.width));
      c.getContext('2d').drawImage(src, 0, 0, c.width, c.height);
      const blob = await new Promise((ok) => c.toBlob(ok, 'image/jpeg', 0.75));
      if (blob) await fetch(WS + '/projects/' + id + '/snapshot', { method: 'PUT', headers: { 'content-type': 'image/jpeg' }, body: blob });
    } catch { /* preview only; the lab itself is unaffected */ }
  };
  const rename = async (title) => {
    if (!project || !title.trim()) return;
    try { await getJson('/projects/' + project, { method: 'PATCH', body: JSON.stringify({ title: title.trim().slice(0, 120) }) }); setMessage('Renamed to ' + title.trim() + '.'); }
    catch (e) { setMessage('Not renamed: ' + e.message); }
  };

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
    renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap; // N56: soft floor shadow
    el.appendChild(renderer.domElement);
    const three = new THREE.Scene();
    three.background = themeColor('--r2s-bg', isDark() ? '#111113' : '#f3f4f6');
    three.add(new THREE.HemisphereLight(0xf8fafc, 0x6b7280, 1.9));
    const sun = new THREE.DirectionalLight(0xffffff, 1.6);
    sun.position.set(3, 6, 4);
    sun.castShadow = true; sun.shadow.mapSize.set(1024, 1024); sun.shadow.radius = 4; sun.shadow.bias = -0.0005;
    Object.assign(sun.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 0.5, far: 30 });
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
          if (p.parts && g.userData.parts) {
            g.updateMatrixWorld();
            const gi = g.quaternion.clone().invert();
            g.userData.parts.forEach((m, i) => { m.position.copy(g.worldToLocal(new THREE.Vector3(...p.parts[i].p))); m.quaternion.copy(gi.clone().multiply(new THREE.Quaternion(...p.parts[i].q))); });
            for (const [line, i] of g.userData.links) { const pos = line.geometry.attributes.position; pos.setXYZ(1, ...g.userData.parts[i].position.toArray()); pos.needsUpdate = true; }
          } else if (o.kind === 'pendulum' || o.kind === 'spring' || o.kind === 'launcher') {
            g.updateMatrixWorld();
            g.userData.body.position.copy(g.worldToLocal(new THREE.Vector3(...p.p)));
            const pos = g.userData.line?.geometry.attributes.position;
            if (pos) { pos.setXYZ(1, ...g.userData.body.position.toArray()); pos.needsUpdate = true; }
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
    api.current = { three, room, objects, gizmo, state, camera, orbit, renderer };
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
    const p = new URLSearchParams(window.location.search), room = p.get('room'), exp = p.get('experiment'), tpl = p.get('template'), saved = p.get('project');
    if (room && LIVE_ID.test(room)) loadRoom(room); else if (exp && LIVE_ID.test(exp)) loadExperiment(exp);
    else if (tpl) loadTemplate(tpl); else if (saved && LIVE_ID.test(saved)) loadSaved(saved);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Rebuild room and object meshes from the scene JSON whenever it changes (not while a run is live).
  useEffect(() => {
    const a = api.current;
    if (!a || run === 'playing' || run === 'paused') return;
    a.gizmo.detach();
    for (const c of [...a.objects.children]) { a.objects.remove(c); c.traverse((m) => { m.geometry?.dispose(); m.material?.dispose(); }); }
    for (const c of [...a.room.children]) if (c !== a.state.points) { a.room.remove(c); c.traverse((m) => { m.geometry?.dispose(); m.material?.dispose(); }); }
    if (scene.room.kind !== 'none') {
      const size = a.state.gridSize ?? 10, dark = isDark();
      const grid = new THREE.GridHelper(size, 20, dark ? 0x3f3f46 : 0xc4c4c8, dark ? 0x26262a : 0xe4e4e7);
      grid.material.transparent = true; grid.material.opacity = 0.7;
      grid.quaternion.fromArray(upQuat(scene.gravity));
      grid.position.set(a.state.gridAt?.[0] ?? 0, scene.room.floor_y, a.state.gridAt?.[2] ?? 0);
      a.room.add(grid);
      const floor = new THREE.Mesh(new THREE.PlaneGeometry(size, size).rotateX(-Math.PI / 2), new THREE.ShadowMaterial({ opacity: dark ? 0.35 : 0.18 }));
      floor.quaternion.copy(grid.quaternion); floor.position.copy(grid.position); floor.position.y += 0.001; floor.receiveShadow = true;
      a.room.add(floor);
    }
    const proxy = scene.room.collision;
    if (proxy?.enabled) { // N29: show the MODEL-ESTIMATED collision boxes so contacts are visible
      const mat = new THREE.LineBasicMaterial({ color: 0xb45309, transparent: true, opacity: 0.45 });
      for (const [x, y, z, hx, hy, hz] of proxy.boxes) {
        const box = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(2 * hx, 2 * hy, 2 * hz)), mat);
        box.position.set(x, y, z); box.quaternion.fromArray(proxy.rotation);
        a.room.add(box);
      }
    }
    if (a.state.points) a.state.points.visible = scene.room.kind === 'ply' && backdrop;
    for (const o of scene.objects) {
      const m = objectMesh(o);
      m.visible = !hidden.includes(o.id);
      m.traverse((x) => { if (x.isMesh) { x.castShadow = true; if (x.material?.roughness != null) x.material.roughness = Math.max(x.material.roughness, 0.8); } });
      a.objects.add(m);
    }
    const g = a.objects.children.find((c) => c.userData.id === selected);
    if (g && mode !== 'select') { a.gizmo.attach(g); a.gizmo.setMode(mode); }
    setJsonText(sceneJson(scene));
  }, [scene, selected, mode, run, tone, backdrop, hidden]);

  // N24: fit the camera to the loaded room or track (robust bounding box, keeps the current viewing direction).
  const frameTo = (positions) => {
    const a = api.current, b = robustBounds(positions, FRAME_Q);
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
  const addObject = (kind, grams) => {
    if (scene.objects.length >= MAX_OBJECTS) { setMessage('At most ' + MAX_OBJECTS + ' objects.'); return; }
    const o = makeObject(kind, scene, [((scene.objects.length % 5) - 2) * 0.6, ADD_Y[kind] ?? 1.2, 0]);
    if (grams) o.params.grams = grams;
    edit((s) => ({ ...s, objects: [...s.objects, o] }));
    setSelected(o.id);
  };
  // N33 undo/redo: every scene change (toolbar, gizmo, inspector, keyboard, agent) is recorded unless it is an undo/redo.
  const hist = useRef(emptyHistory()), prevScene = useRef(scene), replaying = useRef(false), addMenu = useRef(null);
  const [, setHistTick] = useState(0);
  const [tidy, setTidy] = useState(null); // N86: { before, after } scenes of the last agent cleanup
  useEffect(() => {
    if (prevScene.current === scene) return;
    if (!replaying.current) hist.current = record(hist.current, prevScene.current);
    replaying.current = false; prevScene.current = scene; setHistTick((n) => n + 1);
  }, [scene]);
  const travel = (fn, verb) => {
    const r = fn(hist.current, scene);
    if (!r) return;
    stop(); replaying.current = true; hist.current = r.history; setScene(r.scene);
    setSelected((id) => (r.scene.objects.some((o) => o.id === id) ? id : null)); setMessage(verb + '. SIMULATED.');
  };
  const removeSelected = () => {
    if (!selected || run === 'playing' || run === 'paused') return;
    edit((s) => removeObject(s, selected)); setMessage('Deleted ' + selected + '. Ctrl+Z undoes it.'); setSelected(null);
  };
  useEffect(() => {
    const onKey = (e) => {
      if (typing(e.target)) return;
      const k = e.key.toLowerCase();
      if ((e.ctrlKey || e.metaKey) && (k === 'z' || k === 'y')) { e.preventDefault(); travel(k === 'y' || e.shiftKey ? redo : undo, k === 'y' || e.shiftKey ? 'Redone' : 'Undone'); }
      else if ((e.ctrlKey || e.metaKey) && k === 's' && origin?.kind === 'saved') { e.preventDefault(); saveLab(); }
      else if (e.key === 'Delete' || e.key === 'Backspace') { if (selected) { e.preventDefault(); removeSelected(); } }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });
  const stop = () => {
    const st = api.current?.state;
    if (st) { st.playing = false; st.sim?.free(); st.sim = null; }
    setRun('stopped'); setTime(0); setCursor(null); setTraceFit(null);
    setMessage('Ready. Press Play to start again. Everything here is SIMULATED.');
  };
  const play = async () => {
    const st = api.current.state;
    if (run === 'paused') { st.playing = true; setRun('playing'); setCursor(null); return; }
    setRun('loading'); setMessage('Loading the physics engine...');
    try {
      const R = await loadRapier();
      api.current.gizmo.detach();
      st.sim = createPhysics(R, sceneRef.current);
      st.acc = 0; st.playing = true;
      setRun('playing'); setMessage('Running. SIMULATED physics, gravity from the scene vector.');
    } catch (e) { setRun('stopped'); setMessage('Physics could not start: ' + e.message); }
  };
  const pause = () => { api.current.state.playing = false; setRun('paused'); setMessage('Paused. Resume, reset, or export the SIMULATED sensor traces.'); snapshot(); };
  const traces = () => api.current?.state.sim?.traces() ?? [];
  const fitTrace = async () => {
    if (!graphTrace?.samples?.[0]?.p || fitting) return;
    setFitting(true);
    try {
      const result = await getJson('/fit', { method: 'POST', body: JSON.stringify(fitterRequest(graphTrace)) });
      const q = result.gravity;
      setTraceFit(q ? { ...q, name: graphTrace.object_id + ': fitted vertical acceleration', label: 'SIMULATED', caveat: '1 sigma from the fitter covariance. A quadratic summary, not necessarily gravity or a valid model for collisions or oscillation.' } : null);
      if (!q) setMessage('No acceleration fit is available for this trace.');
    } catch (e) { setMessage('Trace not fitted: ' + e.message); }
    finally { setFitting(false); }
  };
  const exportTraces = () => {
    const t = traces();
    if (!t.length) { setMessage('Play the scene with at least one sensor first.'); return; }
    download('lab-traces.json', JSON.stringify({ label: 'SIMULATED', traces: t, fitter_requests: Object.fromEntries(t.map((x) => [x.object_id, fitterRequest(x, 1)])) }));
  };
  const applyJson = (text) => {
    try { const s = parseScene(text); stop(); setSelected(null); setScene(s); setMessage('Scene loaded: ' + s.objects.length + ' objects.'); }
    catch (e) { setMessage('Scene rejected: ' + e.message); }
  };
  const showPly = (bytes, gravity, floorY) => {
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
    return { n: positions.length / 3, collision: roomProxy(positions, gravity, floorY) };
  };
  const loadRoom = async (id, note) => {
    try {
      const r = await getJson('/rooms/' + id + '/result');
      getJson('/rooms/' + id).then((s) => setProject((p) => p ?? s.project_id ?? s.job?.project_id ?? null)).catch(() => {});
      const res = await fetch(WS + '/rooms/' + id + '/room.ply', { cache: 'no-store' });
      if (!res.ok) throw new Error('room.ply HTTP ' + res.status);
      const { n, collision } = showPly(new Uint8Array(await res.arrayBuffer()), r.scene.gravity, r.scene.room?.floor_y ?? 0);
      // A4 rescale reloads the same room: keep objects the user added, positions scaled with the room.
      const k = src?.id === id ? r.room.scale.metres_per_model_unit / src.room.scale.metres_per_model_unit : NaN;
      // N39: dense collision boxes are optional (off by default); the shell walls and furniture are the lab.
      const next = validateScene({ ...r.scene, room: { ...r.scene.room, ...(collision && { collision: { ...collision, enabled: false } }) }, objects: keepAdded(sceneRef.current.objects, r.scene.objects, k) });
      const sh = r.room.shell;
      stop(); setSourceResult(null); setSelected(null); setScene(next); setPlyName('room.ply'); setSrc({ kind: 'room', id, room: r.room }); setBackdrop(!sh);
      setMessage(note ?? (sh ? 'Your room as a lab shell: floor, ' + wallText(sh) + ', ' + sh.openings.length + ' openings, ' + sh.kept.length + ' furniture kept, ' + sh.dropped + ' detections dropped. Geometry MODEL-ESTIMATED; ' + r.room.scale.status + '.'
        : 'Your room: ' + n + ' points, ' + r.scene.objects.length + ' objects. Geometry MODEL-ESTIMATED; ' + r.room.scale.status + '.'));
    } catch (e) { setMessage('Room not loaded: ' + e.message); }
  };
  const loadExperiment = async (id) => {
    try {
      const ex = (await getJson('/experiments/' + id)).experiment;
      setProject((p) => p ?? ex.project_id ?? null);
      const t = trajectoryScene(ex.result);
      if (!t) throw new Error('this experiment has no finished track yet');
      const a = api.current;
      if (a.state.track) a.three.remove(a.state.track);
      const geo = new THREE.BufferGeometry().setFromPoints(t.track.map((q) => new THREE.Vector3(...q)));
      a.state.track = new THREE.Group().add(new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0x111827 })), new THREE.Points(geo, new THREE.PointsMaterial({ size: 0.025, color: 0x4f46e5 })));
      a.three.add(a.state.track);
      frameTo(t.track.flat());
      stop(); setSourceResult(ex.result); setSelected(null); setScene(validateScene(t.scene)); setSrc({ kind: 'experiment', id });
      setMessage('Dots and line: your measured track. ' + t.note);
    } catch (e) { setMessage('Experiment not loaded: ' + e.message); }
  };
  // N89: frame a whole lab from the open front side, with the grid sized to the room.
  const frameScene = (s) => {
    const a = api.current;
    if (!a || !s.objects.length) return;
    const lo = [0, 1, 2].map((i) => Math.min(...s.objects.map((o) => o.position[i] - o.size[i] / 2)));
    const hi = [0, 1, 2].map((i) => Math.max(...s.objects.map((o) => o.position[i] + o.size[i] / 2)));
    a.state.gridSize = Math.max(10, Math.ceil(Math.max(hi[0] - lo[0], hi[2] - lo[2])) + 2);
    a.state.gridAt = [(lo[0] + hi[0]) / 2, 0, (lo[2] + hi[2]) / 2];
    a.camera.position.copy(a.orbit.target).add(new THREE.Vector3(0.2, 0.5, 1));
    frameTo([...lo, ...hi]);
  };
  const loadTemplate = (id) => {
    const t = TEMPLATES.find((x) => x.id === id);
    if (!t) { setMessage('Unknown template ' + id + '. Pick Blank lab or Physics lab from the workspace.'); return; }
    let kept = null;
    try { kept = JSON.parse(sessionStorage.getItem(PENDING) || 'null'); sessionStorage.removeItem(PENDING); } catch { /* storage blocked */ }
    let s = templateScene(id);
    try { if (kept?.id === id) s = validateScene(kept.scene); } catch { kept = null; }
    frameScene(s); setScene(s); setOrigin({ kind: 'template', id, title: t.title }); setName(kept?.name || t.title);
    setMessage(kept?.id === id ? 'Your edits are back. Press Make my copy to save them to your workspace.'
      : t.title + ' template. ' + (id === 'physics-lab' ? 'Press Play: the graph follows ball-drop falling through photogate-1; press Fit trace for its acceleration, or click any apparatus to graph it. '
        : 'Press Add to place apparatus, then Play. ') + 'Make my copy saves your own version (uses your 1 GB storage). Everything here is SIMULATED.');
  };
  const loadSaved = async (id) => {
    try {
      const [b, pj] = await Promise.all([getJson('/agent/lab/scene?project=' + id), getJson('/projects/' + id)]);
      const s = validateScene(b.scene);
      frameScene(s); setScene(s); setSavedJson(sceneJson(s)); setOrigin({ kind: 'saved' }); setName(pj.project.title);
      setMessage('Your saved lab. Save keeps changes; Make a copy starts a new version. Everything here is SIMULATED.');
    } catch (e) { setMessage(e.status === 401 ? 'Sign in to open your saved lab.' : 'Saved lab not loaded: ' + e.message); }
  };
  const saveLab = async () => {
    if (origin?.kind !== 'saved' || !project) return;
    const text = sceneJson(scene);
    try { await getJson('/agent/lab/scene?project=' + project, { method: 'POST', body: text }); setSavedJson(text); setMessage('Saved to your workspace.'); snapshot(); }
    catch (e) { setMessage('Not saved: ' + e.message); }
  };
  // Any open lab (template, saved, room, experiment) becomes a new saved lab owned by this user; a scan backdrop is not copied.
  const copyLab = async () => {
    const s = validateScene(scene), base = (name || title).trim() || 'My lab';
    const copy = { ...s, room: s.room.kind === 'ply' ? { kind: 'plane', floor_y: s.room.floor_y ?? 0 } : s.room };
    setCopying(true);
    try {
      const b = await getJson('/projects', { method: 'POST', body: JSON.stringify({ mode: 'room', title: (origin?.kind === 'template' ? base : base.slice(0, 115) + ' copy').slice(0, 120), scene: copy }) });
      await snapshot(b.project.id);
      window.location.assign('/lab?editor=1&project=' + b.project.id);
    } catch (e) {
      setCopying(false);
      if (e.status !== 401) { setMessage('Not copied: ' + e.message); return; }
      if (origin?.kind === 'template') try { sessionStorage.setItem(PENDING, JSON.stringify({ id: origin.id, name, scene: s })); } catch { /* edits are lost, the template stays */ }
      window.location.assign('/sign-in?redirect_url=' + encodeURIComponent(window.location.pathname + window.location.search));
    }
  };
  const loadFile = async (e) => {
    const f = e.target.files?.[0];
    e.target.value = '';
    if (!f) return;
    if (f.size > 64 * 1024 * 1024) { setMessage('File over 64 MB.'); return; }
    if (/\.json$/i.test(f.name)) { applyJson(await f.text()); return; }
    try {
      const bytes = new Uint8Array(await f.arrayBuffer());
      const { n, collision } = showPly(bytes, scene.gravity, scene.room.floor_y ?? 0);
      setPlyName(f.name);
      edit((s) => ({ ...s, room: { kind: 'ply', floor_y: s.room.floor_y ?? 0, source: f.name.slice(0, 200), scale_verified: false, ...(collision && { collision }) } }));
      setMessage('Room loaded: ' + n + ' points. Scale unverified.');
    } catch (err) { setMessage('Room rejected: ' + err.message); }
  };

  const sel = scene.objects.find((o) => o.id === selected);
  const live = run === 'playing' || run === 'paused';
  const selTrace = live && sel?.sensor ? api.current?.state.sim?.trace(sel.id) : null;
  const recordedTrace = sourceResult?.trajectory;
  const graphTrace = selTrace ?? (live ? api.current?.state.sim?.traces()[0] : recordedTrace ? { object_id: 'Tracked object', label: 'MEASURED', units: { value: recordedTrace.unit }, samples: recordedTrace.t_s.map((t, i) => ({ t, value: recordedTrace.y[i] })) } : null);
  const samples = graphTrace?.samples ?? [], seek = Math.min(cursor ?? samples.length - 1, samples.length - 1);
  const fitResult = traceFit ?? (sourceResult?.quantity ? { ...sourceResult.quantity, label: (sourceResult.sample ? 'RECORDED sample / ' : '') + (sourceResult.track?.label ?? 'MEASURED'), caveat: sourceResult.quantity.label + '. 1 sigma uncertainty. ' + (sourceResult.clock ?? '') } : null);
  const title = src?.kind === 'room' ? 'Your room lab' : src?.kind === 'experiment' ? 'Experiment replay' : 'Virtual lab';
  // N56: one honesty chip; every label word and caveat stays in its expanded list (SF3D credit once, not per object).
  const scaleOpen = scene.room.kind === 'ply' && !scene.room.scale_verified;
  const labels = [['SIMULATED', 'Physics runs in your browser (Rapier). Not a measurement.'],
    ...(sourceResult?.sample ? [['RECORDED sample', sourceResult.sample.label]] : []),
    ...(scene.objects.some((o) => o.shape?.type === 'mesh') ? [['MODEL-GENERATED shapes · Powered by Stability AI', 'Stable Fast 3D shapes; mass and friction MODEL-ESTIMATED.']] : []),
    ...(src?.kind === 'experiment' ? [['Track MEASURED, ball what-if', 'Dots and line are your tracked video; the ball is a what-if replay.']] : []),
    ...(scaleOpen ? [['Room scale unverified', 'Mark the A4 sheet in the Room tab to set metres.']] : []),
    ...(scene.room.collision?.enabled ? [['MODEL-ESTIMATED collision proxy', 'Static boxes fitted to the raw scan.']] : [])];
  const extra = labels.length - 1 - (scaleOpen ? 1 : 0);
  const setObj = (fn) => edit((s) => ({ ...s, objects: s.objects.map((o) => (o.id === selected ? fn(o) : o)) }));
  const toggleHidden = (id) => setHidden((h) => (h.includes(id) ? h.filter((x) => x !== id) : [...h, id]));
  const deleteId = (id) => { if (live) return; edit((s) => removeObject(s, id)); if (selected === id) setSelected(null); setMessage('Deleted ' + id + '. Ctrl+Z undoes it.'); };
  const playBtn = run !== 'playing' ? <button type="button" className="le-primary" onClick={play} disabled={run === 'loading' || !scene.objects.length}><Ico n="play" /><span>{run === 'paused' ? 'Resume' : 'Play'}</span></button> : <button type="button" className="le-primary" onClick={pause}><Ico n="pause" /><span>Pause</span></button>;
  const openLeft = (t) => { setLeftTab(t); setSide(true); };
  const tv = tidyView(hist.current, scene, tidy);
  return <section className="lab-editor" aria-label="Lab editor" data-side={side ? 'open' : 'closed'} data-sheet={agentOpen || sel ? 'open' : 'closed'}>
    <header className="le-top" role="toolbar" aria-label="Lab tools">
      <a className="le-logo" href="/workspace" title="Back to workspace" aria-label="Back to workspace"><img className="art-light" src="/brand/mark.svg" width="32" height="32" alt="" /><img className="art-dark" src="/brand/mark-dark.svg" width="32" height="32" alt="" /></a>
      <input className="le-name" aria-label="Lab name" value={name || title} maxLength={120} onChange={(e) => setName(e.target.value)} onBlur={(e) => rename(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') e.currentTarget.blur(); }} />
      <div className="le-group" role="group" aria-label="Edit history">
        <button type="button" className="le-icon-btn" onClick={() => travel(undo, 'Undone')} disabled={!hist.current.past.length} aria-label="Undo" title="Undo (Ctrl+Z)"><Ico n="undo" /></button>
        <button type="button" className="le-icon-btn" onClick={() => travel(redo, 'Redone')} disabled={!hist.current.future.length} aria-label="Redo" title="Redo (Ctrl+Shift+Z)"><Ico n="redo" /></button>
      </div>
      <div className="le-group" role="group" aria-label="Simulation">
        {playBtn}
        <button type="button" onClick={stop} disabled={!live} title="Reset to the start"><Ico n="reset" /><span className="le-lbl">Reset</span></button>
      </div>
      <div className="le-group" role="group" aria-label="Save">
        {origin?.kind === 'saved' && <button type="button" onClick={saveLab} disabled={jsonText === savedJson} title="Save to your workspace (Ctrl+S)"><Ico n="save" /><span className="le-lbl">{jsonText === savedJson ? 'Saved' : 'Save'}</span></button>}
        <button type="button" onClick={copyLab} disabled={copying || live} title="Save a copy of this lab to your workspace (uses your 1 GB storage)"><Ico n="copy" /><span className="le-lbl">{origin?.kind === 'template' ? 'Make my copy' : 'Make a copy'}</span></button>
      </div>
      <div className="le-group le-end" role="group" aria-label="View and files">
        <button type="button" className="le-icon-btn" onClick={reframe} aria-label="Fit view to the room" title="Fit view to the room"><Ico n="frame" /></button>
        <button type="button" className="le-icon-btn" onClick={exportTraces} disabled={!live} aria-label="Export traces" title="Export SIMULATED sensor traces"><Ico n="traces" /></button>
        <button type="button" className="le-icon-btn" onClick={() => { download('lab-scene.json', sceneJson(scene)); snapshot(); }} aria-label="Export scene" title="Export scene JSON"><Ico n="download" /></button>
        <label className="le-file le-icon-btn" title="Import scene or room (.json, .ply)"><Ico n="upload" /><span className="le-sr">Import scene or room (.json, .ply)</span><input type="file" accept=".json,.ply" onChange={loadFile} /></label>
        <button type="button" className="le-icon-btn" aria-label="Fullscreen" title="Fullscreen" onClick={(e) => (document.fullscreenElement ? document.exitFullscreen() : e.currentTarget.closest('.lab-editor')?.requestFullscreen?.())}><Ico n="expand" /></button>
        <button type="button" className="le-agent-btn" aria-label="Agent" aria-pressed={agentOpen} onClick={() => setAgentOpen((v) => !v)}><Ico n="agent" /><span className="le-lbl">Agent</span></button>
      </div>
    </header>
    <div className="le-work">
      <nav className="le-rail" aria-label="Side panel">
        <button type="button" className="le-icon-btn" aria-pressed={side && leftTab === 'objects'} aria-label="Objects" title="Objects" onClick={() => (side && leftTab === 'objects' ? setSide(false) : openLeft('objects'))}><Ico n="list" /></button>
        <button type="button" className="le-icon-btn" aria-pressed={side && leftTab === 'room'} aria-label="Room" title="Room" onClick={() => (side && leftTab === 'room' ? setSide(false) : openLeft('room'))}><Ico n="room" /></button>
      </nav>
      <aside hidden={!side} className="le-side le-left" aria-label={leftTab === 'room' ? 'Room' : 'Objects'}>
        <div className="le-tabs" role="tablist" aria-label="Side panel">
          {[['objects', 'Objects'], ['room', 'Room']].map(([t, l]) => <button key={t} type="button" role="tab" aria-selected={leftTab === t} onClick={() => setLeftTab(t)}>{l}</button>)}
          <button type="button" className="le-mini" aria-label="Collapse side panel" title="Collapse" onClick={() => setSide(false)}><Ico n="panel" /></button>
        </div>
        <div hidden={leftTab !== 'objects'} className="le-panel">
          {!scene.objects.length && <p className="le-muted">No objects yet. Use Add above the canvas.</p>}
          <ul className="le-outline" aria-label="Scene objects">
            {scene.objects.map((o) => { const off = hidden.includes(o.id); return <li key={o.id} aria-current={o.id === selected ? 'true' : undefined} data-off={off || undefined}>
              <button type="button" className="le-row" onClick={() => setSelected(o.id)}><Ico n={ICONS[o.kind] ? o.kind : 'block'} /><span>{o.id}</span><small>{LABELS[o.kind]}</small></button>
              <button type="button" className="le-mini" aria-label={(off ? 'Show ' : 'Hide ') + o.id} title={off ? 'Show in view' : 'Hide in view (still simulated)'} onClick={() => toggleHidden(o.id)}><Ico n={off ? 'eyeoff' : 'eye'} /></button>
              <button type="button" className="le-mini" aria-label={'Delete ' + o.id} title="Delete" disabled={live} onClick={() => deleteId(o.id)}><Ico n="trash" /></button>
            </li>; })}
          </ul>
          <details className="le-json">
            <summary>Scene JSON (lab-scene-v1)</summary>
            <textarea aria-label="Scene JSON" value={jsonText} onChange={(e) => setJsonText(e.target.value)} spellCheck={false} rows={12} />
            <button type="button" onClick={() => applyJson(jsonText)}>Apply JSON</button>
          </details>
        </div><div hidden={leftTab !== 'room'}>
          {src?.kind === 'room' ? <RoomTools key={src.id} id={src.id} room={src.room} onReload={(note) => loadRoom(src.id, note)} />
            : <div className="le-panel"><h3>Room</h3><p className="le-muted">No room loaded. Open a room lab from your workspace, or import a .ply scan with the import button.</p></div>}
          {scene.room.collision && <div className="le-panel">
            <h3>Room collisions</h3>
            <label><input type="checkbox" checked={backdrop} onChange={(e) => setBackdrop(e.target.checked)} /> Show raw scan</label>
            <label><input type="checkbox" checked={scene.room.collision.enabled} disabled={live} onChange={(e) => edit((s) => ({ ...s, room: { ...s.room, collision: { ...s.room.collision, enabled: e.target.checked } } }))} /> Enable raw scan collisions</label>
            <p>Show raw scan changes visibility only. Collisions use {scene.room.collision.boxes.length} static boxes (MODEL-ESTIMATED), off by default for loaded rooms. The walls and furniture keep their own colliders.</p>
          </div>}
        </div>
      </aside>
      <div className="le-stage">
        <div ref={host} className="le-canvas" data-testid="lab-editor-canvas" />
        {tv && <div className="le-tidy" role="group" aria-label="Cleanup comparison">
          <span>Tidied by agent · SIMULATED</span>
          {[['before', 'Before', undo, 'Showing the lab before cleanup'], ['after', 'After', redo, 'Tidied by agent']].map(([v, l, fn, verb]) =>
            <button key={v} type="button" aria-pressed={tv === v} onClick={() => tv !== v && travel(fn, verb)}>{l}</button>)}
        </div>}
        <div className="le-float" role="toolbar" aria-label="Transform mode">
          {[['select', 'Select'], ['translate', 'Move'], ['rotate', 'Rotate'], ['scale', 'Resize']].map(([m, l]) => <button key={m} type="button" className="le-icon-btn" aria-pressed={mode === m} aria-label={l} title={l} onClick={() => setMode(m)} disabled={live}><Ico n={m} /></button>)}
          <span className="le-sep" aria-hidden="true" />
          <details className="le-add" ref={addMenu}>
            <summary className={live ? 'le-off' : ''} title="Add an object or probe" aria-label="Add an object or probe"><Ico n="add" /><span>Add</span></summary>
            <div className="le-menu" role="menu" aria-label="Lab kit">
              {MENU.map(([group, items]) => <div key={group} className="le-menu-g" role="group" aria-label={group}><span className="le-menu-h">{group}</span>
                {items.map((it) => { const [k, g] = Array.isArray(it) ? it : [it]; const label = g ? (g >= 1000 ? g / 1000 + ' kg' : g + ' g') + ' mass' : LABELS[k];
                  return <button key={label} type="button" role="menuitem" disabled={live} onClick={() => { addObject(k, g); addMenu.current.open = false; }}><Ico n={k} /><span>{label}</span></button>; })}
              </div>)}
              {onTemplateTrials && <div className="le-menu-g" role="group" aria-label="Templates"><span className="le-menu-h">Templates</span>
                <button type="button" role="menuitem" onClick={onTemplateTrials}><Ico n="trials" /><span>Template trials</span></button></div>}
            </div>
          </details>
        </div>
        <details className="le-honesty">
          <summary>{'SIMULATED' + (scaleOpen ? ' · scale unverified' : '') + (extra > 0 ? ' · +' + extra : '')}</summary>
          <ul>{labels.map(([l, why]) => <li key={l}><strong>{l}</strong> {why}</li>)}</ul>
        </details>
        <p className="le-status" role="status">{improving > 0 && 'Improving ' + improving + ' objects... '}{message} Gravity [{scene.gravity.join(', ')}] m/s^2{plyName ? ', room ' + plyName : ''}.</p>
      </div>
      <aside className="le-side le-right" aria-label={agentOpen ? 'Agent' : 'Properties'}>
        <button type="button" className="le-sheet-close" onClick={() => { setAgentOpen(false); setSelected(null); }}>Close</button>
        <div className="le-panel le-props" hidden={agentOpen}>
          {sel ? <>
            <h3>{sel.id} <small className="le-muted">{LABELS[sel.kind]}</small></h3>
            <fieldset disabled={live}><legend>Position (m)</legend><div className="le-xyz">{['x', 'y', 'z'].map((ax, i) => <Num key={ax} label={ax} value={sel.position[i]} onCommit={(v) => setObj((o) => ({ ...o, position: o.position.map((p, j) => (j === i ? v : p)) }))} />)}</div></fieldset>
            <fieldset disabled={live}><legend>Size (m)</legend><div className="le-xyz">{['x', 'y', 'z'].map((ax, i) => <Num key={ax} label={ax} value={sel.size[i]} onCommit={(v) => setObj((o) => ({ ...o, size: o.size.map((p, j) => (j === i ? Math.min(50, Math.max(0.005, v)) : p)) }))} />)}</div></fieldset>
            <fieldset disabled={live}><legend>Physics</legend>
              <Num label="Mass (kg)" value={sel.mass} onCommit={(v) => setObj((o) => ({ ...o, mass: v }))} />
              {sel.kind !== 'pendulum' && sel.kind !== 'spring' && <label className="le-check"><input type="checkbox" checked={sel.fixed} onChange={(e) => setObj((o) => ({ ...o, fixed: e.target.checked }))} /> Fixed in place</label>}
              <label className="le-check"><input type="checkbox" checked={sel.sensor} onChange={(e) => setObj((o) => ({ ...o, sensor: e.target.checked }))} /> Record trajectory sensor</label>
            </fieldset>
            {sel.shape && <p className="le-muted">{sel.shape.type === 'mesh' ? SHAPE_LABEL + ' (Stable Fast 3D). Collider: ' + (sel.shape.collider === 'box' ? 'measured box' : sel.fixed ? 'mesh' : 'convex hull') + '. Mass and friction MODEL-ESTIMATED (' + sel.shape.category + ').' : 'Measured box shape. ' + sel.shape.fallback_reason}</p>}
            {selTrace && <p>Sensor: {selTrace.samples.length} samples{selTrace.truncated ? ' (cap reached)' : ''}</p>}
            <button type="button" className="le-danger" disabled={live} onClick={removeSelected}>Delete</button>
          </> : <>
            <h3>Scene</h3>
            <fieldset disabled={live}><legend>Gravity (m/s^2)</legend><div className="le-xyz">{['x', 'y', 'z'].map((ax, i) => <Num key={ax} label={ax} value={scene.gravity[i]} onCommit={(v) => edit((s) => ({ ...s, gravity: s.gravity.map((g, j) => (j === i ? v : g)) }))} />)}</div></fieldset>
            <p className="le-muted">Time step {(1 / 120).toFixed(4)} s (fixed 120 Hz). {scene.objects.length} objects. Select an object in the canvas or the Objects list to edit it.</p>
          </>}
        </div>
        <div hidden={!agentOpen}>
          <AgentPanel scene={scene} cards={hasPhysicsStations(scene) ? PHYSICS_LAB_CARDS : undefined} load={!src && !/[?&](room|experiment|template|project)=/.test(window.location.search)} onScene={(s, msg, tidied) => { stop(); setSelected(null); if (tidied) setTidy({ before: prevScene.current, after: s }); setScene(s); setMessage(msg); }} />
        </div>
      </aside>
    </div>
    <footer className="le-timeline" aria-label="Timeline">
      {playBtn}
      <button type="button" className="le-icon-btn" onClick={stop} disabled={!live} aria-label="Reset" title="Reset to the start"><Ico n="reset" /></button>
      <span className="le-time" aria-live="off">t = {(samples[seek]?.t ?? time).toFixed(2)} s</span>
      <label className="le-seek">Recorded trace<input type="range" aria-label="Seek recorded sensor trace" min="0" max={Math.max(0, samples.length - 1)} value={Math.max(0, seek)} disabled={run === 'playing' || samples.length < 2} onChange={(e) => setCursor(Number(e.target.value))} aria-valuetext={samples[seek] ? samples[seek].t.toFixed(3) + ' s' : 'No trace'} /></label>
      <Graph trace={graphTrace} cursor={seek} />
      <button type="button" onClick={fitTrace} disabled={run === 'playing' || fitting || !samples[0]?.p || samples.length < 4}>{fitting ? 'Fitting...' : 'Fit trace'}</button>
      {fitResult && <section className="le-result" aria-label="Fit result"><strong>{fitResult.name}: {fitResult.uncertainty > 0 ? fmtPm(fitResult.value, fitResult.uncertainty) : fitResult.value + ' +/- ' + (fitResult.uncertainty ?? 'uncertainty unavailable')} {fitResult.unit}</strong><small>{fitResult.label}. {fitResult.caveat}</small>{!traceFit && gravityCheck(sourceResult) && <small>{gravityCheck(sourceResult).text}</small>}</section>}
    </footer>
  </section>;
}

// N56 compact numeric field: commits on blur or Enter so typing "0." is not rewritten mid-edit.
function Num({ label, value, onCommit }) {
  return <label className="le-field"><span>{label}</span>
    <input type="number" step="0.01" key={value} defaultValue={+Number(value).toFixed(4)}
      onBlur={(e) => { const v = Number(e.target.value); if (e.target.value !== '' && Number.isFinite(v) && v !== value) onCommit(v); }}
      onKeyDown={(e) => { if (e.key === 'Enter') e.currentTarget.blur(); }} /></label>;
}

// N56 live graph of the SIMULATED sensor trace (selected object, else the first sensor); values straight from the engine.
function Graph({ trace, cursor }) {
  const all = trace?.samples ?? [];
  if (all.length < 2) return <p className="le-graph le-muted">Turn on Record trajectory sensor for an object, then Play to see a live graph.</p>;
  const step = Math.ceil(all.length / 300), s = all.filter((_, i) => i % step === 0 || i === all.length - 1);
  const probe = s[0].value != null, ys = s.map((x) => (probe ? x.value : x.p[1])), t0 = s[0].t, t1 = s.at(-1).t;
  const lo = Math.min(...ys), span = Math.max(...ys) - lo || 1;
  const pts = s.map((x, i) => ((300 * (x.t - t0)) / (t1 - t0 || 1)).toFixed(1) + ',' + (56 - (52 * (ys[i] - lo)) / span).toFixed(1)).join(' ');
  const what = (probe ? 'reading' : 'y position') + ' (' + (probe ? trace.units.value : 'm') + ')';
  const current = all[Math.max(0, Math.min(cursor ?? all.length - 1, all.length - 1))], label = trace.label ?? 'SIMULATED';
  return <figure className="le-graph"><svg viewBox="0 0 300 60" preserveAspectRatio="none" role="img" aria-label={trace.object_id + ' ' + what + ' over time, ' + label}><polyline points={pts} /><line x1={300 * (current.t - t0) / (t1 - t0 || 1)} x2={300 * (current.t - t0) / (t1 - t0 || 1)} y1="0" y2="60" stroke="currentColor" /></svg>
    <figcaption>{trace.object_id} {what}: {(probe ? current.value : current.p[1]).toFixed(3)} at t = {current.t.toFixed(2)} s. {label}</figcaption></figure>;
}

