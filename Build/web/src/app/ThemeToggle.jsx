'use client';
import { createElement as h, useEffect, useState } from 'react';
import { THEME_KEY, THEME_OPTIONS, choiceOf, applyTheme } from '../shell/theme.mjs';
import { icon } from '../shell/icons.mjs';

// S15ai: public-header System/Light/Dark switch; reuses the S15ah theme layer (pre-paint script already applied the stored choice).
export default function ThemeToggle() {
  const [choice, setChoice] = useState('system');
  useEffect(() => { try { setChoice(choiceOf(localStorage.getItem(THEME_KEY))); } catch { /* storage blocked: stay on system */ } }, []);
  // S15am grew THEME_OPTIONS to 7 modes (not all have icons): a native select stays compact at 375px and lists every mode.
  return <label className="theme-toggle">{icon(h, 'sun', 16)}<select aria-label="Colour theme" value={choice} onChange={(e) => { applyTheme(e.target.value); setChoice(e.target.value); }}>
    {THEME_OPTIONS.map((o) => <option key={o.id} value={o.id}>{o.label}</option>)}
  </select></label>;
}
