"""S15ap logo v2: hand-authored pendulum mark. One primitive list per drawing feeds both SVG and Pillow raster."""
import math, pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[3]
BRAND = ROOT / "Build/web/public/brand"
EV = ROOT / "evidence/brand/logo-v2"
LIGHT = {"ink": "#1c1a16", "bob": "#b23a0e"}   # paper rust; ink = paper text
DARK = {"ink": "#f4f4f5", "bob": "#ff8a4c"}    # dark-mode text + ember
MODES = [("paper", "#f3eee3", LIGHT), ("light", "#f7f7f8", LIGHT), ("contrast", "#ffffff", LIGHT),
         ("dark", "#111113", DARK), ("midnight", "#0b1020", DARK), ("graphite", "#1f2023", DARK)]

# Primitives: ("line", x1, y1, x2, y2, width, role) round caps; ("ring", cx, cy, r, width, role); ("dot", cx, cy, r, role)
def dashed(x1, y1, x2, y2, w, role, dash=4, gap=3):
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; out, s = [], 0.0
    while s < L:
        e = min(s + dash, L); out.append(("line", x1 + ux * s, y1 + uy * s, x1 + ux * e, y1 + uy * e, w, role)); s = e + gap
    return out

# 64-unit grid. Pivot (32,12); centre bob (32,48); ghosts at +-30 deg-ish, (14,43)/(50,43) -> integer coords.
CAND_A = ([("line", 18, 12, 46, 12, 3, "ink")] + dashed(32, 12, 14, 43, 2, "ink") + dashed(32, 12, 50, 43, 2, "ink")
          + [("line", 32, 12, 32, 48, 2.5, "ink"), ("ring", 14, 43, 6, 2.5, "bob"), ("ring", 50, 43, 6, 2.5, "bob"), ("dot", 32, 48, 8, "bob")])
CAND_B = [("line", 20, 12, 44, 12, 4, "ink"), ("line", 32, 12, 32, 46, 3.5, "ink"),
          ("ring", 13, 42, 6.5, 3.5, "bob"), ("ring", 51, 42, 6.5, 3.5, "bob"), ("dot", 32, 49, 9, "bob")]
CAND_C = [("dot", 32, 12, 3, "ink"), ("line", 32, 12, 32, 46, 3, "ink")] + dashed(14, 43, 32, 50.5, 2.5, "ink", 3, 3) + dashed(32, 50.5, 50, 43, 2.5, "ink", 3, 3) \
         + [("ring", 14, 43, 6, 3, "ink"), ("ring", 50, 43, 6, 3, "ink"), ("dot", 32, 49, 8.5, "bob")]
def to_edge(px, py, cx, cy, r, w, sw):
    """Solid ghost string from pivot to the ring's outer edge (stops short so the round cap does not enter the ring)."""
    L = math.hypot(cx - px, cy - py); t = (L - r - w / 2 - sw / 2) / L
    return ("line", px, py, round(px + (cx - px) * t, 2), round(py + (cy - py) * t, 2), sw, "ink")

# D (chosen): B plus thin solid ghost strings, so the three phases read as one swinging pendulum, not "oTo".
# Ghost centres (14,44)/(50,44) sit ~36.7u from pivot, equal to the 37u centre string: same arc.
CAND_D = [("line", 20, 12, 44, 12, 4, "ink"), to_edge(32, 12, 14, 44, 6, 3, 2), to_edge(32, 12, 50, 44, 6, 3, 2),
          ("line", 32, 12, 32, 46, 3.5, "ink"), ("ring", 14, 44, 6, 3, "bob"), ("ring", 50, 44, 6, 3, "bob"), ("dot", 32, 49, 9, "bob")]
FINAL = CAND_D
# 16-unit small drawing (used for <=32px): bolder bar/string/bob, ghost strings kept at 1u so phases still connect.
# Ghosts spread wider and higher than the 64u geometry so a 1px gap separates them from the bob at 16px.
SMALL = [("line", 5, 2.5, 11, 2.5, 1.5, "ink"), to_edge(8, 2.5, 2.5, 9.5, 1.5, 1, 1), to_edge(8, 2.5, 13.5, 9.5, 1.5, 1, 1),
         ("line", 8, 2.5, 8, 10, 1.5, "ink"), ("ring", 2.5, 9.5, 1.5, 1, "bob"), ("ring", 13.5, 9.5, 1.5, 1, "bob"), ("dot", 8, 12, 2.5, "bob")]

def svg(prims, vb, pal, title="Real2Simulation"):
    f = lambda v: f"{v:g}"; parts = []
    for p in prims:
        c = pal[p[-1]]
        if p[0] == "line": parts.append(f'<line x1="{f(p[1])}" y1="{f(p[2])}" x2="{f(p[3])}" y2="{f(p[4])}" stroke="{c}" stroke-width="{f(p[5])}" stroke-linecap="round"/>')
        elif p[0] == "ring": parts.append(f'<circle cx="{f(p[1])}" cy="{f(p[2])}" r="{f(p[3])}" fill="none" stroke="{c}" stroke-width="{f(p[4])}"/>')
        else: parts.append(f'<circle cx="{f(p[1])}" cy="{f(p[2])}" r="{f(p[3])}" fill="{c}"/>')
    body = "\n  ".join(parts)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb} {vb}" width="{vb}" height="{vb}" role="img" aria-label="{title}">\n  <title>{title}</title>\n  {body}\n</svg>\n'

def raster(prims, vb, px, pal):
    ss = max(4, min(16, 4096 // px))  # cap supersample canvas near 4k px for speed/memory
    S = px * ss; k = S / vb; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for p in prims:
        c = pal[p[-1]]
        if p[0] == "line":
            x1, y1, x2, y2, w = (v * k for v in p[1:6]); d.line((x1, y1, x2, y2), fill=c, width=max(1, round(w)))
            for x, y in ((x1, y1), (x2, y2)): d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=c)
        elif p[0] == "ring":
            cx, cy, r, w = (v * k for v in p[1:5]); d.ellipse((cx - r - w / 2, cy - r - w / 2, cx + r + w / 2, cy + r + w / 2), outline=c, width=max(1, round(w)))
        else:
            cx, cy, r = (v * k for v in p[1:4]); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    return im.resize((px, px), Image.LANCZOS)

def mark(px, pal):
    return raster(SMALL, 16, px, pal) if px <= 32 else raster(FINAL, 64, px, pal)

def on(bg, im, pad=0):
    t = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), bg); t.alpha_composite(im, (pad, pad)); return t

def font(sz):
    p = pathlib.Path.home() / "AppData/Local/Microsoft/Windows/Fonts/InstrumentSans_wdth_wght_.ttf"
    f = ImageFont.truetype(str(p), sz)
    try: f.set_variation_by_name("SemiBold")
    except Exception: pass
    return f

def wordmark(pal):
    W, H = 924, 192; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); im.alpha_composite(mark(192, pal), (0, 0))
    f = font(92); d = ImageDraw.Draw(im); bb = d.textbbox((0, 0), "Real2Simulation", font=f)
    d.text((196 - bb[0], (H - (bb[3] - bb[1])) // 2 - bb[1]), "Real2Simulation", font=f, fill=pal["ink"])
    assert 196 + bb[2] - bb[0] <= W, "wordmark overflows"
    return im

def main():
    EV.mkdir(parents=True, exist_ok=True)
    # Concepts: each candidate at 192/32/16 on paper and dark.
    for name, prims in (("a-dashed-paths", CAND_A), ("b-bar-three-phase", CAND_B), ("c-pivot-dot-arc", CAND_C), ("d-final-solid-strings", CAND_D)):
        sheet = Image.new("RGBA", (2 * (192 + 32 + 16 + 64) + 40, 220), "#888888")
        x = 10
        for bg, pal in (("#f3eee3", LIGHT), ("#111113", DARK)):
            for px in (192, 32, 16):
                sheet.alpha_composite(on(bg, raster(prims, 64, px, pal), 4), (x, 10)); x += px + 8 + 12
            x += 20
        sheet.save(EV / f"concept-{name}.png")
        (EV / f"concept-{name}.svg").write_text(svg(prims, 64, LIGHT), encoding="utf-8")
    # Final SVGs
    (BRAND / "mark.svg").write_text(svg(FINAL, 64, LIGHT), encoding="utf-8")
    (BRAND / "mark-dark.svg").write_text(svg(FINAL, 64, DARK), encoding="utf-8")
    (BRAND / "mark-16.svg").write_text(svg(SMALL, 16, LIGHT), encoding="utf-8")
    for px in (1024, 512, 192, 32): mark(px, LIGHT).save(BRAND / f"mark-{px}.png")
    # Maskable: opaque paper tile, art inside central 80% safe circle (art box 300px of 512).
    m = Image.new("RGBA", (512, 512), "#f3eee3"); m.alpha_composite(raster(FINAL, 64, 320, LIGHT), (96, 96)); m.save(BRAND / "icon-maskable-512.png")
    ico = [mark(s, LIGHT) for s in (16, 32, 48)]
    ico[2].save(BRAND / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:2])
    wordmark(LIGHT).save(BRAND / "wordmark-light.png"); wordmark(DARK).save(BRAND / "wordmark-dark.png")
    # Contact sheet: final at 16/24/32/64/192/512 on all six modes (512 shown at true size).
    sizes = (16, 24, 32, 64, 192, 512); cell = 16; rowh = 512 + 2 * cell; colw = sum(sizes) + cell * (len(sizes) + 1) + 120
    cs = Image.new("RGBA", (colw, rowh * len(MODES)), "#ffffff"); d = ImageDraw.Draw(cs); lab = font(20)
    for i, (mode, bg, pal) in enumerate(MODES):
        y0 = i * rowh; d.rectangle((0, y0, colw, y0 + rowh), fill=bg); d.text((cell, y0 + cell), mode, font=lab, fill=pal["ink"]); x = 120
        for px in sizes:
            cs.alpha_composite(mark(px, pal), (x, y0 + (rowh - px) // 2)); x += px + cell
    cs.save(EV / "contact-sheet-final.png")
    # Wordmarks on their modes for review
    wm = Image.new("RGBA", (924 + 40, 2 * 192 + 60), "#f3eee3"); ImageDraw.Draw(wm).rectangle((0, 192 + 30, 964, 500), fill="#111113")
    wm.alpha_composite(wordmark(LIGHT), (20, 15)); wm.alpha_composite(wordmark(DARK), (20, 192 + 45)); wm.save(EV / "wordmarks-review.png")

if __name__ == "__main__":
    main()

