'use client';
import { createElement as h, useEffect, useState } from 'react';
import { THEME_KEY, THEME_OPTIONS, choiceOf, applyTheme } from '../shell/theme.mjs';
import { icon } from '../shell/icons.mjs';

// S15ai: public-header System/Light/Dark switch; reuses the S15ah theme layer (pre-paint script already applied the stored choice).
export default function ThemeToggle() {
  const [choice, setChoice] = useState('system');
  useEffect(() => { try { setChoice(choiceOf(localStorage.getItem(THEME_KEY))); } catch { /* storage blocked: stay on system */ } }, []);
  return <div className="theme-toggle" role="group" aria-label="Colour theme">
    {THEME_OPTIONS.map((o) => <button key={o.id} type="button" title={o.label} aria-label={o.label + ' theme'} aria-pressed={choice === o.id} onClick={() => { applyTheme(o.id); setChoice(o.id); }}>{icon(h, o.icon, 16)}</button>)}
  </div>;
}
