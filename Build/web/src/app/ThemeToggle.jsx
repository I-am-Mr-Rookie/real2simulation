'use client';
import { createElement as h, useEffect, useState } from 'react';
import { THEME_KEY, THEME_OPTIONS, DARK_QUERY, choiceOf, applyTheme } from '../shell/theme.mjs';
import { icon } from '../shell/icons.mjs';

// S15an: the ONE theme control on every page (public + workspace): palette button -> System + six COLOR_MODES with swatches.
// Pre-paint THEME_SCRIPT already applied the stored choice; here it is mirrored and System follows OS changes live.
export default function ThemeToggle() {
  const [choice, setChoice] = useState('system');
  useEffect(() => { try { setChoice(choiceOf(localStorage.getItem(THEME_KEY))); } catch { /* storage blocked: stay on system */ } }, []);
  useEffect(() => { const m = globalThis.matchMedia?.(DARK_QUERY); if (!m || choice !== 'system') return;
    const f = () => applyTheme('system'); m.addEventListener?.('change', f); return () => m.removeEventListener?.('change', f); }, [choice]);
  const pick = (e, id) => { applyTheme(id); setChoice(id); e.currentTarget.closest('details')?.removeAttribute('open'); };
  return <details className="theme-menu">
    <summary aria-label="Colour theme" title="Colour theme">{icon(h, 'palette', 18)}</summary>
    <div className="theme-menu-list" role="group" aria-label="Colour theme">
      {THEME_OPTIONS.map((t) => <button key={t.id} type="button" data-theme-option={t.id} aria-pressed={choice === t.id} onClick={(e) => pick(e, t.id)}>
        {t.tokens ? <span className="theme-swatch" aria-hidden="true" style={{ background: t.tokens.bg, borderColor: t.tokens['border-strong'], color: t.tokens.accent }} /> : icon(h, t.icon, 16)}
        {t.label}</button>)}
    </div>
  </details>;
}
