"""S15aj colour modes: single source of truth. Run: python contrast.py  -> rewrites COLOR_MODES.md (HEAD + tables), exits 1 on any AA failure."""
import pathlib, sys

KEYS = ["bg", "surface", "elevated", "border", "border-strong", "text", "muted", "accent", "accent-contrast",
        "success", "warning", "danger", "recorded-bg", "recorded-fg", "simulated-bg", "simulated-fg",
        "whatif-bg", "whatif-fg", "shadow", "focus"]
MODES = {
  # paper = current DEV look, kept as the warm default light (owner: keep fonts + shadow character)
  "paper":    "#f3eee3 #fffcf5 #ffffff #d8cfbe #8a8174 #1c1a16 #5a554b #b23a0e #ffffff #1d6a3a #8a5300 #a3191b #dcebe0 #14532d #e4e3f6 #3730a3 #f6e3c6 #6f3800 #1c1a16 #1c1a16",
  "light":    "#f7f7f8 #ffffff #ffffff #e4e4e7 #84848d #18181b #52525b #b53d0b #ffffff #15703a #8f4e00 #b91c1c #dcf2e3 #14532d #e6e6fb #3730a3 #fbe8cc #713f00 #18181b #18181b",
  # dark modes: the hard offset slab is LIT (border-strong tone), because a black slab vanishes on dark surfaces
  "dark":     "#111113 #18181b #212126 #2e2e35 #71717c #f4f4f5 #a1a1aa #ff8a4c #1a0d05 #4ade80 #fbbf24 #f87171 #0f2e1c #86efac #1e1b4b #c7d2fe #3a2508 #fcd34d #71717c #ff8a4c",
  "midnight": "#0b1020 #111831 #18213f #26304f #5f6c95 #e8ecf8 #9aa6c7 #7dd3fc #062033 #5eead4 #fcd34d #fca5a5 #0c2e2a #99f6e4 #221d52 #c4b5fd #3a2a0a #fde68a #5f6c95 #7dd3fc",
  "graphite": "#1f2023 #26282c #2e3035 #3a3d43 #7a7e87 #ededee #b0b3ba #f08a5d #1f0d04 #7bd88f #e8c15a #ff8f8f #1d3324 #a7f3b9 #2b2a4a #cfd0ff #3d3014 #f5d98a #7a7e87 #f08a5d",
  "contrast": "#ffffff #ffffff #ffffff #000000 #000000 #000000 #262626 #8a1f00 #ffffff #0b5a26 #6b3d00 #8b0000 #ffffff #0b5a26 #ffffff #2a1f8f #ffffff #6b3d00 #000000 #000000",
}
TEXT_ON = ["bg", "surface", "elevated"]
TEXT = ["text", "muted", "accent", "success", "warning", "danger"]
PAIRS = [(t, s, 4.5) for t in TEXT for s in TEXT_ON] + [
  ("accent-contrast", "accent", 4.5), ("recorded-fg", "recorded-bg", 4.5), ("simulated-fg", "simulated-bg", 4.5),
  ("whatif-fg", "whatif-bg", 4.5), ("border-strong", "bg", 3.0), ("border-strong", "surface", 3.0),
  ("focus", "bg", 3.0), ("focus", "surface", 3.0), ("shadow", "surface", 3.0)]

def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

assert round(ratio("#000000", "#ffffff"), 1) == 21.0 and round(ratio("#777777", "#ffffff"), 2) == 4.48  # self-check vs WCAG reference values

HEAD = pathlib.Path(__file__).with_name("color_modes_head.md").read_text(encoding="utf-8")
out, fails = [HEAD.rstrip()], []
for name, vals in MODES.items():
    tok = dict(zip(KEYS, vals.split()))
    assert len(tok) == len(KEYS), name
    out += ["", f"### {name}", "", "```css", f':root[data-theme="{name}"] {{'] + [f"  --r2s-{k}: {v};" for k, v in tok.items()] + ["}", "```", "", "| fg | on | ratio | min | pass |", "|---|---|---|---|---|"]
    for fg, bg, mn in PAIRS:
        r = ratio(tok[fg], tok[bg]); ok = r >= mn
        if not ok:
            fails.append(f"{name}: {fg} {tok[fg]} on {bg} {tok[bg]} = {r:.2f} < {mn}")
        out.append(f"| {fg} | {bg} | {r:.2f} | {mn} | {'PASS' if ok else 'FAIL'} |")
pathlib.Path(__file__).with_name("COLOR_MODES.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"{len(MODES)} modes x {len(PAIRS)} pairs; failures: {len(fails)}")
print("\n".join(fails))
sys.exit(1 if fails else 0)

