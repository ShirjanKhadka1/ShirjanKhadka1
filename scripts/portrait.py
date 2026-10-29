#!/usr/bin/env python3
"""Portrait treatment: duotone navy/gold, soft rim, circular crop.

Source: the owner's black-and-white portrait (already approved for
GitHub profile use). Output: assets/portrait.jpg, 640px, quality 78 —
target under 300 KB. No other photo is used anywhere on the page.
"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageOps

SRC = sys.argv[1]
DST = sys.argv[2]

im = Image.open(SRC).convert("L")
w, h = im.size
side = min(w, h)
im = im.crop(((w - side) // 2, (h - side) // 2,
              (w + side) // 2, (h + side) // 2)).resize((640, 640), Image.LANCZOS)
# Duotone: shadows -> deep navy, midtones -> slate, highlights -> warm gold-white.
navy = (7, 10, 18)
gold = (230, 195, 92)
white = (232, 236, 244)
lut = []
for i in range(256):
    t = i / 255
    if t < 0.5:
        f = t / 0.5
        lut.append(tuple(int(navy[c] + (70 - navy[c]) * f) for c in range(3)))
    else:
        f = (t - 0.5) / 0.5
        lut.append(tuple(int((70 + (gold[c] - 70) * f * 0.4 + white[c] * f * 0.6)) for c in range(3)))
flat = [v for rgb in lut for v in rgb]
# ImageOps.colorize-style mapping via point on RGB: apply LUT per channel manually.
rgb = Image.merge("RGB", [im.point([lut[i][c] for i in range(256)]) for c in range(3)])
mask = Image.new("L", (640, 640), 0)
ImageDraw.Draw(mask).ellipse((0, 0, 640, 640), fill=255)
out = Image.new("RGB", (640, 640), navy)
out.paste(rgb, (0, 0), mask)
out.save(DST, "JPEG", quality=78, optimize=True)
print(DST)
