#!/usr/bin/env python3
"""Render the Eierbaer sprite big (x8) next to the 3 mustache poses -> /tmp/sprite.png"""
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite  # noqa: E402

k = 8
sheet = Image.new("RGBA", (sprite.W * k * 3 + 40, sprite.H * k + 20), (92, 150, 216, 255))
for i in range(3):
    s = sprite.eierbaer_with_stache(i).resize((sprite.W * k, sprite.H * k), Image.NEAREST)
    sheet.alpha_composite(s, (10 + i * (sprite.W * k + 10), 10))
sheet.convert("RGB").save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/sprite.png")
print("ok")
