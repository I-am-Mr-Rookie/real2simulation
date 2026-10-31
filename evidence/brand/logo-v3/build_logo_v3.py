"""S15at logo v3: pendulum mark redrawn from Koushik's pencil sketch (Oct31). Copied from logo-v2; only the drawing changed.
One primitive list per drawing feeds both SVG and Pillow raster."""
import math, pathlib
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[3]
BRAND = ROOT / "Build/web/public/brand"
EV = ROOT / "evidence/brand/logo-v3"
_SK = "evidence/owner/logo-sketches-2026-10-31/owner-pendulum-logo-sketch-1.jpeg"  # local-only owner input, never committed
SKETCH = next((p for p in (ROOT / _SK, ROOT.parents[1] / _SK) if p.exists()), ROOT / _SK)  # worktree falls back to canonical root
LIGHT = {"ink": "#1c1a16", "bob": "#b23a0e", "faint": "#1c1a1680"}   # paper rust; ink = paper text; faint = ink at 50% (16px ghost strings)
DARK = {"ink": "#f4f4f5", "bob": "#ff8a4c", "faint": "#f4f4f599"}    # dark-mode text + ember; faint = ink at 60%
MODES = [("paper", "#f3eee3", LIGHT), ("light", "#f7f7f8", LIGHT), ("contrast", "#ffffff", LIGHT),
         ("dark", "#111113", DARK), ("midnight", "#0b1020", DARK), ("graphite", "#1f2023", DARK)]

# Primitives: ("line", x1, y1, x2, y2, width, role) round caps; ("ring", cx, cy, r, width, role); ("dot", cx, cy, r, role)
def dashed(x1, y1, x2, y2, w, role, dash=4, gap=3, start=0.0):
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; out, s = [], start
    while s < L:
        e = min(s + dash, L); out.append(("line", round(x1 + ux * s, 2), round(y1 + uy * s, 2), round(x1 + ux * e, 2), round(y1 + uy * e, 2), w, role)); s = e + gap
    return out

def edge(px, py, cx, cy, r, w, sw):
    """Point on the pivot-to-ghost line that stops short of the ring so a round cap never enters it."""
    L = math.hypot(cx - px, cy - py); t = (L - r - w / 2 - sw / 2) / L
    return px + (cx - px) * t, py + (cy - py) * t

def hatch(x0, x1, n, y, h, lean, w):
    """Textbook fixed-support hatching: n parallel diagonal ticks rising from the support line."""
    step = (x1 - x0) / (n - 1)
    return [("line", round(x0 + i * step, 2), y, round(x0 + i * step + lean, 2), y - h, w, "ink") for i in range(n)]

def ghost_string(pv, g, r, rw, sw, dash, gap, start):
    ex, ey = edge(*pv, *g, r, rw, sw); return dashed(*pv, ex, ey, sw, "ink", dash, gap, start)

def faint_string(pv, g, r, rw, sw):
    ex, ey = edge(*pv, *g, r, rw, sw); return [("line", *pv, round(ex, 2), round(ey, 2), sw, "faint")]

# 64-unit grid, sketch structure: wide support line + hatch ticks above, one pivot at its middle,
# solid string to a solid centre bob, dashed strings to hollow ghost bobs roughly level with it.
PV, BOB, GL, GR = (32, 18), (32, 49), (15, 46), (49, 46)
# Dashes start 7u below the pivot (as in the sketch) so they never crowd the solid string into an arrowhead.
FINAL = ([("line", 7, 18, 57, 18, 3, "ink")] + hatch(9, 51, 7, 18, 7, 4, 2)
         + ghost_string(PV, GL, 5.5, 2, 2, 3.5, 4.5, 7) + ghost_string(PV, GR, 5.5, 2, 2, 3.5, 4.5, 7)
         + [("line", 32, 18, 32, 42, 2.5, "ink"), ("ring", *GL, 5.5, 2, "bob"), ("ring", *GR, 5.5, 2, "bob"), ("dot", *BOB, 7.5, "bob")])
# 16-unit small drawing (used for <=32px): 3 bold hatch ticks; dashes become faint solid strings (dashes are mush
# at 16px), drawn first so the solid bar/string paint over the shared pivot; ghosts spread so a 1px gap separates them from the bob.
SPV, SGL, SGR = (8, 5), (2.5, 10.5), (13.5, 10.5)
SMALL = (faint_string(SPV, SGL, 1.5, 1, 1) + faint_string(SPV, SGR, 1.5, 1, 1)
         + [("line", 1.5, 5, 14.5, 5, 1.25, "ink")] + hatch(3, 12, 3, 5, 3, 1.5, 1.25)
         + [("line", 8, 5, 8, 10, 1.25, "ink"), ("ring", *SGL, 1.5, 1, "bob"), ("ring", *SGR, 1.5, 1, "bob"), ("dot", 8, 12, 2.5, "bob")])

def svg(prims, vb, pal, title="Real2Simulation"):
    f = lambda v: f"{v:g}"; parts = []
    for p in prims:
        c = pal[p[-1]]
        op = f' stroke-opacity="{int(c[7:], 16) / 255:.2f}"' if len(c) == 9 else ""; c = c[:7]
        if p[0] == "line": parts.append(f'<line x1="{f(p[1])}" y1="{f(p[2])}" x2="{f(p[3])}" y2="{f(p[4])}" stroke="{c}"{op} stroke-width="{f(p[5])}" stroke-linecap="round"/>')
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
    # v3 art spans y 11..57.5 of 64 (hatch top to bob bottom), centre 34.25u: lift 7px so it balances the text.
    W, H = 924, 192; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); im.alpha_composite(mark(192, pal), (0, -7))
    f = font(92); d = ImageDraw.Draw(im); bb = d.textbbox((0, 0), "Real2Simulation", font=f)
    d.text((196 - bb[0], (H - (bb[3] - bb[1])) // 2 - bb[1]), "Real2Simulation", font=f, fill=pal["ink"])
    assert 196 + bb[2] - bb[0] <= W, "wordmark overflows"
    return im

def main():
    EV.mkdir(parents=True, exist_ok=True)
    (BRAND / "mark.svg").write_text(svg(FINAL, 64, LIGHT), encoding="utf-8")
    (BRAND / "mark-dark.svg").write_text(svg(FINAL, 64, DARK), encoding="utf-8")
    (BRAND / "mark-16.svg").write_text(svg(SMALL, 16, LIGHT), encoding="utf-8")
    for px in (1024, 512, 192, 32): mark(px, LIGHT).save(BRAND / f"mark-{px}.png")
    # Maskable: opaque paper tile, art inside central 80% safe circle.
    m = Image.new("RGBA", (512, 512), "#f3eee3"); m.alpha_composite(raster(FINAL, 64, 320, LIGHT), (96, 96)); m.save(BRAND / "icon-maskable-512.png")
    ico = [mark(s, LIGHT) for s in (16, 32, 48)]
    ico[2].save(BRAND / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:2])
    wordmark(LIGHT).save(BRAND / "wordmark-light.png"); wordmark(DARK).save(BRAND / "wordmark-dark.png")
    # Contact sheet: final at 16/24/32/64/192/512 on all six modes (512 shown at true size).
    sizes = (16, 24, 32, 64, 192, 512); cell = 16; rowh = 512 + 2 * cell; colw = sum(sizes) + cell * (len(sizes) + 1) + 120
    wmh = 192 + cell  # lockup row per mode under the marks, wordmark at true size
    cs = Image.new("RGBA", (colw, (rowh + wmh) * len(MODES)), "#ffffff"); d = ImageDraw.Draw(cs); lab = font(20)
    for i, (mode, bg, pal) in enumerate(MODES):
        y0 = i * (rowh + wmh); d.rectangle((0, y0, colw, y0 + rowh + wmh), fill=bg); d.text((cell, y0 + cell), mode, font=lab, fill=pal["ink"]); x = 120
        for px in sizes:
            cs.alpha_composite(mark(px, pal), (x, y0 + (rowh - px) // 2)); x += px + cell
        cs.alpha_composite(wordmark(pal), (120, y0 + rowh - cell))
    cs.save(EV / "contact-sheet-final.png")
    # Favicon frames at 6x nearest-neighbour: ICO 16/32/48 then mark-32.png, on paper and dark.
    ic = Image.open(BRAND / "favicon.ico"); frames = [ic.ico.getimage((s, s)).convert("RGBA") for s in (16, 32, 48)] + [Image.open(BRAND / "mark-32.png")]
    fw = sum(f.width * 6 + 24 for f in frames) + 24; fs = Image.new("RGBA", (fw, 2 * (48 * 6 + 24) + 24), "#888888"); y = 24
    for bg, pal in (("#f3eee3", LIGHT), ("#111113", DARK)):
        x = 24
        for i, f in enumerate(frames):
            src = f if pal is LIGHT else mark(f.width, DARK)
            fs.alpha_composite(on(bg, src).resize((f.width * 6, f.height * 6), Image.NEAREST), (x, y)); x += f.width * 6 + 24
        y += 48 * 6 + 24
    fs.save(EV / "favicon-frames-6x.png")
    # Real-size 16/32 strip on all modes (1x, for honest small-size viewing) plus 6x of the same.
    st = Image.new("RGBA", (len(MODES) * 64, 40), "#ffffff")
    for i, (_, bg, pal) in enumerate(MODES):
        t = on(bg, Image.new("RGBA", (56, 32), (0, 0, 0, 0))); t.alpha_composite(mark(16, pal), (4, 8)); t.alpha_composite(mark(32, pal), (22, 0)); st.alpha_composite(t, (i * 64 + 4, 4))
    st.save(EV / "small-real-size.png"); st.resize((st.width * 6, st.height * 6), Image.NEAREST).save(EV / "small-real-size-6x.png")
    # Side by side: tight grayscale crop of the owner sketch (drawing only) next to the new mark.
    if SKETCH.exists():
        sk = ImageOps.grayscale(Image.open(SKETCH).crop((500, 80, 910, 420))).convert("RGBA").resize((600, 497))
        sb = Image.new("RGBA", (600 + 512 + 72, 560), "#f3eee3"); sb.alpha_composite(sk, (24, 40)); sb.alpha_composite(mark(512, LIGHT), (600 + 48, 24))
        dd = ImageDraw.Draw(sb); lab = font(22)
        dd.text((24, 8), "Owner pencil sketch (Oct31, crop)", font=lab, fill="#1c1a16"); dd.text((648, 536), "Logo v3 mark.svg render, 512 px", font=lab, fill="#1c1a16")
        sb.save(EV / "sketch-vs-mark.png")
    wm = Image.new("RGBA", (924 + 40, 2 * 192 + 60), "#f3eee3"); ImageDraw.Draw(wm).rectangle((0, 192 + 30, 964, 500), fill="#111113")
    wm.alpha_composite(wordmark(LIGHT), (20, 15)); wm.alpha_composite(wordmark(DARK), (20, 192 + 45)); wm.save(EV / "wordmarks-review.png")

if __name__ == "__main__":
    main()

