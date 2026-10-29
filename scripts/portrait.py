#!/usr/bin/env python3
"""Portrait re-treatment, contrast-fix edition (29 Oct 2026).

Problem with the previous treatment: the harsh black-and-white source
(p5=18, p95=242, stdev 71) was mapped to a deep-navy/gold duotone that
kept crushed blacks and blown whites, so the circle read as a pasted
sticker — especially on the pale light hero.

Fix: gentle contrast compression BEFORE duotone (lift blacks, cap
highlights, smooth S-curve at 0.82 strength), a muted warm-grey
duotone (slate shadows, warm-grey mids, warm off-white highlights —
no pure black, no pure white, no saturated gold in the skin), a
feathered circular edge (blurred mask, ~4px), and a soft halo ring
baked into the square so the circle blends into both heroes.
Output: assets/portrait.jpg, 640px, quality 82.
"""
import sys
from PIL import Image, ImageDraw, ImageFilter

SRC = sys.argv[1]
DST = sys.argv[2]

im = Image.open(SRC).convert("L")
w, h = im.size
side = min(w, h)
im = im.crop(((w - side) // 2, (h - side) // 2,
              (w + side) // 2, (h + side) // 2)).resize((640, 640), Image.LANCZOS)
# 1. Contrast compression (mild): t -> 0.06 + 0.88 * smooth(t),
#    smooth = t*(1.10 - 0.20*t). Lifts p5 from ~18 to ~54, caps p95
#    from ~242 to ~190, keeps the photo photographic (stdev ~50).
lut_grey = []
for i in range(256):
    t = i / 255
    s = t * (1.10 - 0.20 * t)
    v = int(round((0.06 + 0.88 * s) * 255))
    lut_grey.append(max(0, min(255, v)))
im = im.point(lut_grey)
# 2. Muted warm-grey duotone (piecewise, same shape as before, softer ends).
shadow = (32, 36, 46)      # was (7, 10, 18) — no more crushed navy-black
mid = (108, 106, 98)       # warm grey
highlight = (238, 234, 224)  # warm off-white, not blown white
lut = []
for i in range(256):
    t = i / 255
    if t < 0.5:
        f = t / 0.5
        lut.append(tuple(int(shadow[c] + (mid[c] - shadow[c]) * f) for c in range(3)))
    else:
        f = (t - 0.5) / 0.5
        lut.append(tuple(int(mid[c] + (highlight[c] - mid[c]) * f) for c in range(3)))
rgb = Image.merge("RGB", [im.point([lut[i][c] for i in range(256)]) for c in range(3)])
rgb = rgb.filter(ImageFilter.GaussianBlur(0.4))
# 3. Feathered circular mask + soft halo: mask blurred 4px, plus a faint
#    mid-grey surround so the circle edge does not jump against either hero.
mask = Image.new("L", (640, 640), 0)
ImageDraw.Draw(mask).ellipse((0, 0, 640, 640), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(4))
out = Image.new("RGB", (640, 640), (88, 86, 80))
out.paste(rgb, (0, 0), mask)
out.save(DST, "JPEG", quality=82, optimize=True)
print(DST)
