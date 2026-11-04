'use client';
import { useEffect } from 'react';

// N90: mounts the unchanged scroll-craft engine (public/scrollcraft/scrollcraft.js) on the home page.
// A pinned act carries data-pin-min="minWidth minHeight"; below that, or with reduced motion, it becomes a flow act
// (no sticky stage, no extra scroll) and any [data-flow-stagger] list inside it gets a one-shot entry reveal instead.
// shortcut: the engine has no unmount and gating is read once per load, so a resize across a threshold keeps the first choice
// and a client-side return to / adds a second idle instance; add a destroy() to the engine if that ever matters.
export default function ScrollMount() {
  useEffect(() => {
    const root = document.querySelector('.home-motion');
    if (!root || root.dataset.scMounted) return;
    root.dataset.scMounted = '1';
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    for (const el of root.querySelectorAll('[data-pin-min]')) {
      const [w, h] = el.dataset.pinMin.split(' ').map(Number);
      if (!reduce && innerWidth >= w && innerHeight >= h) continue;
      el.setAttribute('data-sc-act', 'flow');
      for (const l of el.querySelectorAll('[data-flow-stagger]')) { l.setAttribute('data-sc-in', ''); l.setAttribute('data-sc-stagger', '70'); }
    }
    const go = () => window.ScrollCraft.mount(root);
    if (window.ScrollCraft) { go(); return; }
    const s = document.createElement('script');
    s.src = '/scrollcraft/scrollcraft.js';
    s.onload = go;
    document.head.appendChild(s);
  }, []);
  return null;
}
