#!/usr/bin/env python3
"""Generate all EggMint pixel-art assets from the Eierbaer poster.

Usage: python3 gen_assets.py poster.png <package-dir>
Writes PNGs into <package-dir>/plymouth/eggmint/ and <package-dir>/greeter/.
Needs only Pillow (python3-pil, preinstalled on Linux Mint).
"""
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite  # noqa: E402  (hand-made pixel Eierbaer)

POSTER, PKG = sys.argv[1], sys.argv[2]
PLY = os.path.join(PKG, "plymouth", "eggmint")
GRT = os.path.join(PKG, "greeter")
os.makedirs(PLY, exist_ok=True)
os.makedirs(GRT, exist_ok=True)

poster = Image.open(POSTER).convert("RGB")
PW, PH = poster.size
sx, sy = PW / 1024.0, PH / 1536.0  # coordinates below are for a 1024x1536 poster

# palette
OUTLINE = (43, 22, 8, 255)
SHELL = (250, 240, 214, 255)
SHELL_SHADE = (222, 205, 168, 255)
ST_HI = (150, 92, 48, 255)
ST_MID = (105, 60, 28, 255)
ST_LO = (70, 38, 16, 255)
GHOST = (30, 40, 60, 90)
GHOST_EDGE = (30, 40, 60, 150)
CREAM = (255, 246, 222, 255)
RED = (196, 30, 24, 255)


def up(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def pixelate(region, w, h, colors):
    small = region.resize((w, h), Image.BOX)
    q = small.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE)
    return q.convert("RGBA")


# ---------------------------------------------------------------- pixel font
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10011", "10101", "10101", "10101", "11001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000"] * 7,
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
}
FONT["Ä"] = ["01010", "00000", "01110", "10001", "11111", "10001", "10001"]


def text_img(text, scale, color, shadow=OUTLINE):
    text = text.upper()
    w = len(text) * 6 - 1 + 1
    img = Image.new("RGBA", (w, 8), (0, 0, 0, 0))
    px = img.load()
    for i, ch in enumerate(text):
        g = FONT.get(ch, FONT["?"])
        for y, row in enumerate(g):
            for x, bit in enumerate(row):
                if bit == "1":
                    X, Y = i * 6 + x, y
                    if shadow and px[X + 1, Y + 1][3] == 0:
                        px[X + 1, Y + 1] = shadow
                    px[X, Y] = color
    return up(img, scale)


# ---------------------------------------------------------------- egg portrait
EGG_W, EGG_H = 60, 74


def egg_inside(x, y, w, h):
    # egg: narrower at the top
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0 + h * 0.04
    a, b = w / 2.0, h / 2.0
    yy = (y - cy) / b
    aa = a * (1.0 + 0.13 * yy)
    xx = (x - cx) / aa
    return xx * xx + yy * yy <= 1.0


def make_egg_portrait():
    # face + ears + curls region of the poster
    box = (int(272 * sx), int(352 * sy), int(712 * sx), int(894 * sy))
    face = pixelate(poster.crop(box), EGG_W, EGG_H, 28)
    out = Image.new("RGBA", (EGG_W + 6, EGG_H + 6), (0, 0, 0, 0))
    po, pf = out.load(), face.load()
    W, H = out.size
    for y in range(H):
        for x in range(W):
            if not egg_inside(x, y, W, H):
                continue
            # distance to edge in pixels (cheap check of neighbours)
            ring = 0
            for d in (1, 2, 3):
                if not all(egg_inside(x + dx, y + dy, W, H)
                           for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d))):
                    ring = d
                    break
            if ring == 1:
                po[x, y] = OUTLINE
            elif ring in (2, 3):
                po[x, y] = SHELL_SHADE if (x > W * 0.6 and y > H * 0.5) else SHELL
            else:
                po[x, y] = pf[min(EGG_W - 1, max(0, x - 3)), min(EGG_H - 1, max(0, y - 3))]
    return out


# ---------------------------------------------------------------- mustache
# Left half of a handlebar mustache (tip on the left, centre on the right);
# mirrored to get the full shape. '#' = filled.
STACHE_HALF = [
    "........................",
    "...#####................",
    "..#######...............",
    ".####..###..............",
    ".###....##..............",
    ".###....................",
    ".####..........#######..",
    "..#####......###########",
    "..#######..#############",
    "...#####################",
    "....####################",
    ".....###################",
    "......##################",
    "........################",
    "..........#############.",
    ".............#########..",
    "........................",
]
ST_W, ST_H = len(STACHE_HALF[0]) * 2, len(STACHE_HALF)
TIP_COLS = 9  # columns (from each end) that move when the mustache twitches


def mustache_mask(wiggle=0):
    """Set of filled (x, y). wiggle: 0 / -1 (tips up) / +1 (tips down)."""
    pts = {}
    half = len(STACHE_HALF[0])
    for y, row in enumerate(STACHE_HALF):
        for x, ch in enumerate(row):
            if ch != "#":
                continue
            dy = wiggle if x < TIP_COLS else 0
            for xx in (x, ST_W - 1 - x):
                yy = y + dy
                if 0 <= yy < ST_H:
                    pts[(xx, yy)] = True
    _ = half
    return pts


# tiny mustache that sits on the portrait's face (3 twitch poses)
FACE_STACHE = [
    [".............", "#...........#", "##..#####..##", ".###########.", "..####.####.."],
    ["#...........#", "#...........#", ".#..#####..#.", ".###########.", "..####.####.."],
    [".............", ".............", "....#####....", "#############", "##.###.###.##"],
]


def face_stache(pose):
    rows = FACE_STACHE[pose]
    w = max(len(r) for r in rows)
    img = Image.new("RGBA", (w, len(rows)), (0, 0, 0, 0))
    p = img.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == "#":
                p[x, y] = (58, 30, 10, 255)
    return img


def mustache_layers(wiggle):
    pts = mustache_mask(wiggle)
    full = Image.new("RGBA", (ST_W, ST_H), (0, 0, 0, 0))
    ghost = Image.new("RGBA", (ST_W, ST_H), (0, 0, 0, 0))
    pf, pg = full.load(), ghost.load()
    for (x, y) in pts:
        n_up = (x, y - 1) in pts
        n_dn = (x, y + 1) in pts
        edge = not all(((x + dx, y + dy) in pts) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge:
            pf[x, y] = OUTLINE
            pg[x, y] = GHOST_EDGE
        else:
            if not (x, y - 2) in pts:
                pf[x, y] = ST_HI
            elif not (x, y + 2) in pts:
                pf[x, y] = ST_LO
            else:
                pf[x, y] = ST_MID
            pg[x, y] = GHOST
        _ = n_up, n_dn
    # a few hair strands for texture
    for (x, y) in pts:
        if pf[x, y] == ST_MID and (x * 7 + y * 3) % 11 == 0:
            pf[x, y] = ST_LO
    return full, ghost


STEPS = 24
ST_SCALE = 7


def make_mustache_frames():
    for w_i, wig in enumerate((0, -1, 1)):  # pose index 0=rest 1=tips up 2=tips down
        full, ghost = mustache_layers(wig)
        for s in range(STEPS + 1):
            cut = round(ST_W * s / STEPS)
            frame = ghost.copy()
            if cut > 0:
                frame.paste(full.crop((0, 0, cut, ST_H)), (0, 0))
            up(frame, ST_SCALE).save(os.path.join(PLY, "stache-%d-%d.png" % (s, w_i)))
    full, _ = mustache_layers(0)
    return full


# ---------------------------------------------------------------- small extras
def egg_bullet():
    img = Image.new("RGBA", (7, 9), (0, 0, 0, 0))
    p = img.load()
    for y in range(9):
        for x in range(7):
            if egg_inside(x, y, 7, 9):
                edge = not all(egg_inside(x + dx, y + dy, 7, 9) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                p[x, y] = OUTLINE if edge else SHELL
    return up(img, 3)


def entry_box(w, h):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w - 1, h - 1), fill=OUTLINE)
    d.rectangle((1, 1, w - 2, h - 2), fill=(105, 60, 28, 235))
    d.rectangle((2, 2, w - 3, h - 3), fill=(70, 38, 16, 235))
    return up(img, 3)


# ---------------------------------------------------------------- build
# the hand-made pixel Eierbaer (tools/sprite.py) is the star of every screen
portrait = sprite.eierbaer()
stache_full = make_mustache_frames()

# its face mustache is a separate sprite so Plymouth can twitch it in sync with the bar
P_SCALE = 6
for pose in range(3):
    up(sprite.face_stache(pose), P_SCALE).save(os.path.join(PLY, "face-%d.png" % pose))
with open(os.path.join(PLY, "face-offset.txt"), "w") as f:
    # top-left corner of face-N.png inside portrait.png (= FACE_OX/FACE_OY in eggmint.script)
    f.write("%d %d\n" % (sprite.FACE_POS[0] * P_SCALE, sprite.FACE_POS[1] * P_SCALE))
up(portrait, P_SCALE).save(os.path.join(PLY, "portrait.png"))
portrait_with_stache = sprite.eierbaer_with_stache(0)

text_img("EGGMINT", 5, CREAM).save(os.path.join(PLY, "title.png"))
text_img("LOADING MUSTACHE...", 3, CREAM).save(os.path.join(PLY, "subtitle-boot.png"))
text_img("BYE BYE!", 3, CREAM).save(os.path.join(PLY, "subtitle-shutdown.png"))
text_img("SEE YOU IN A SEC!", 3, CREAM).save(os.path.join(PLY, "subtitle-reboot.png"))
text_img("UPDATING EGGS...", 3, CREAM).save(os.path.join(PLY, "subtitle-updates.png"))
text_img("PASSWORD:", 3, CREAM).save(os.path.join(PLY, "password.png"))
egg_bullet().save(os.path.join(PLY, "bullet.png"))
entry_box(120, 13).save(os.path.join(PLY, "entry.png"))

# ---- greeter background: 16:9 pixel scene. Left: sky, clouds, mountains, pines
# (the login box sits there). Right: the pixelated Eierbaer, dithered into the scene.
BG_W, BG_H = 240, 135
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


bg = Image.new("RGBA", (BG_W, BG_H))
bp = bg.load()
sky_top, sky_bot = (66, 128, 212, 255), (190, 222, 248, 255)
BANDS = 7
for y in range(BG_H):
    for x in range(BG_W):
        t = y / (BG_H - 1) * (BANDS - 1)
        band = int(t)
        frac = t - band
        if frac * 16 > BAYER[y % 4][x % 4] + 0.5:
            band += 1
        bp[x, y] = lerp(sky_top, sky_bot, min(band, BANDS - 1) / (BANDS - 1))

d = ImageDraw.Draw(bg)
# clouds
for cx, cy, s in ((20, 18, 1.0), (70, 30, 0.7), (128, 12, 0.85), (40, 52, 0.55)):
    for dx, dy, r in ((0, 0, 7), (8, -3, 6), (15, 0, 6), (-7, 2, 5), (5, 3, 6)):
        rr = max(2, int(r * s))
        X, Y = cx + int(dx * s), cy + int(dy * s)
        d.ellipse((X - rr, Y - rr // 1.6, X + rr, Y + rr // 1.6), fill=(250, 250, 255, 255))
    d.line((cx - int(9 * s), cy + int(4 * s), cx + int(20 * s), cy + int(4 * s)), fill=(214, 228, 245, 255))
# mountains
for mx, mh, mw, col in ((30, 62, 60, (124, 146, 186, 255)), (82, 74, 70, (108, 130, 172, 255)),
                        (140, 58, 56, (124, 146, 186, 255)), (204, 70, 66, (108, 130, 172, 255))):
    base = 104
    d.polygon([(mx - mw // 2, base), (mx, base - mh), (mx + mw // 2, base)], fill=col)
    cap = mh // 3
    d.polygon([(mx - mw * cap // (2 * mh), base - mh + cap), (mx, base - mh),
               (mx + mw * cap // (2 * mh), base - mh + cap)], fill=(244, 248, 255, 255))
    for k in range(0, mw * cap // (2 * mh), 3):  # jagged snow line
        d.point((mx - mw * cap // (2 * mh) + k * 2, base - mh + cap + 1), fill=(244, 248, 255, 255))
# meadow + pines
d.rectangle((0, 108, BG_W, BG_H), fill=(52, 96, 70, 255))
d.rectangle((0, 104, BG_W, 108), fill=(70, 120, 84, 255))
for i, px_ in enumerate(range(-4, 170, 9)):
    h = 18 + (i * 7) % 11
    base = 112 + (i * 5) % 6
    for row in range(h):
        half = 1 + row * 5 // h
        y = base - h + row
        d.line((px_ - half, y, px_ + half, y), fill=(30, 66, 50, 255) if row % 4 else (24, 54, 42, 255))
    d.line((px_, base, px_, base + 3), fill=(70, 44, 24, 255))

# right half: more pines, a little lake, and the Eierbaer sitting in its nest
for i, px_ in enumerate(range(172, BG_W + 8, 11)):
    h = 16 + (i * 5) % 9
    base = 110 + (i * 3) % 5
    for row in range(h):
        half = 1 + row * 5 // h
        y = base - h + row
        d.line((px_ - half, y, px_ + half, y), fill=(30, 66, 50, 255) if row % 4 else (24, 54, 42, 255))
    d.line((px_, base, px_, base + 3), fill=(70, 44, 24, 255))
d.ellipse((128, 118, 214, 134), fill=(70, 130, 196, 255))         # lake
d.line((138, 124, 154, 124), fill=(150, 196, 236, 255))
d.line((176, 128, 198, 128), fill=(150, 196, 236, 255))
# x=144..200 stays visible even when a 4:3 screen crops the 16:9 picture at the sides
bear = sprite.eierbaer_with_stache(0)
bg.alpha_composite(bear, (144, BG_H - bear.height - 6))
up(bg, 8).convert("RGB").save(os.path.join(GRT, "background.png"))

# ---- greeter logo (bottom-left): Eierbaer head + text
head = portrait_with_stache.crop((0, 0, sprite.W, 43))
logo_txt = text_img("EGGMINT", 2, CREAM)
small = Image.new("RGBA", (head.width + 6 + logo_txt.width, head.height), (0, 0, 0, 0))
small.alpha_composite(head, (0, 0))
small.alpha_composite(logo_txt, (head.width + 6, (small.height - logo_txt.height) // 2))
small.save(os.path.join(GRT, "logo.png"))

# ---- user avatar 256x256: head + egg on sky
av = Image.new("RGBA", (64, 64), (92, 150, 216, 255))
av.alpha_composite(portrait_with_stache.crop((0, 0, sprite.W, 60)), (4, 4))
up(av, 4).save(os.path.join(GRT, "avatar.png"))

print("assets written to", PKG)
