#!/usr/bin/env python3
"""Compose a static preview of the boot splash (what Plymouth draws) -> preview-splash.png"""
import os
import sys
from PIL import Image

PKG = sys.argv[1]
step = int(sys.argv[2]) if len(sys.argv) > 2 else 15
wig = int(sys.argv[3]) if len(sys.argv) > 3 else 0
P = os.path.join(PKG, "plymouth", "eggmint")
W, H = 1280, 800
bg = Image.new("RGBA", (W, H))
top, bot = (84, 148, 219), (189, 222, 250)
for y in range(H):
    t = y / (H - 1)
    c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,)
    for x in range(W):
        bg.putpixel((x, y), c)
title = Image.open(os.path.join(P, "title.png"))
por = Image.open(os.path.join(P, "portrait.png"))
st = Image.open(os.path.join(P, "stache-%d-%d.png" % (step, wig)))
sub = Image.open(os.path.join(P, "subtitle-boot.png"))
block = title.height + 24 + por.height + 24 + st.height + 20 + sub.height
y = (H - block) // 2
fx, fy = map(int, open(os.path.join(P, "face-offset.txt")).read().split())
face = Image.open(os.path.join(P, "face-%d.png" % wig))
for img, gap in ((title, 24), (por, 24), (st, 20), (sub, 0)):
    x = (W - img.width) // 2
    bg.alpha_composite(img, (x, y))
    if img is por:
        bg.alpha_composite(face, (x + fx, y + fy))
    y += img.height + gap
bg.convert("RGB").save(os.path.join(PKG, "preview-splash.png"))
print("ok")
