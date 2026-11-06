"""Hand-built pixel-art Eierbaer (56x72): curly hair, bear ears, smiling face with beaver
nose + buck teeth, leather strap, egg held in the paws, beaver tail, sitting in a stick nest.

Shapes are placed as 'materials' on a grid; a shading pass then lights every material from
the top-left and a final pass draws a dark outline around the silhouette - the classic
pixel-art recipe, but reproducible. The face mustache is a separate layer (it twitches).
"""
from PIL import Image, ImageDraw

W, H = 56, 72
OUTLINE = (43, 22, 8, 255)

PAL = {  # material -> (highlight, mid, shadow)
    "fur": ((168, 104, 54), (126, 74, 37), (90, 51, 26)),
    "hair": ((146, 88, 44), (102, 58, 29), (68, 37, 18)),
    "skin": ((248, 200, 164), (228, 166, 126), (196, 132, 98)),
    "belly": ((198, 138, 86), (166, 110, 66), (134, 86, 50)),
    "paw": ((104, 64, 36), (80, 48, 25), (58, 34, 18)),
    "tail": ((98, 64, 56), (74, 47, 43), (52, 32, 30)),
    "egg": ((255, 251, 238), (241, 229, 201), (206, 189, 153)),
    "strap": ((96, 62, 36), (74, 46, 26), (52, 31, 17)),
    "buckle": ((222, 222, 210), (178, 178, 168), (130, 130, 122)),
    "nose": ((126, 94, 84), (54, 32, 24), (38, 22, 16)),
    "stick": ((166, 120, 74), (128, 88, 50), (92, 60, 32)),
    "nestegg": ((255, 251, 238), (236, 222, 192), (200, 182, 146)),
}
FLAT = {  # material -> single colour (no shading)
    "eye": (30, 20, 14), "glint": (255, 255, 255), "brow": (74, 42, 20),
    "blush": (238, 146, 124), "mouth": (110, 36, 34), "teeth": (255, 255, 248),
    "toothline": (196, 184, 160), "speckle": (150, 108, 66), "claw": (34, 22, 16),
    "stickdark": (70, 44, 22), "earin": (196, 120, 104),
}


class Grid:
    def __init__(self):
        self.m = [[None] * W for _ in range(H)]

    def put(self, x, y, mat):
        if 0 <= x < W and 0 <= y < H:
            self.m[y][x] = mat

    def get(self, x, y):
        if 0 <= x < W and 0 <= y < H:
            return self.m[y][x]
        return None

    def shape(self, draw_fn, mat):
        """Rasterise a PIL shape (no anti-aliasing) and assign it a material."""
        tmp = Image.new("1", (W, H), 0)
        draw_fn(ImageDraw.Draw(tmp))
        p = tmp.load()
        for y in range(H):
            for x in range(W):
                if p[x, y]:
                    self.m[y][x] = mat

    def ellipse(self, box, mat):
        self.shape(lambda d: d.ellipse(box, fill=1), mat)

    def rect(self, box, mat):
        self.shape(lambda d: d.rectangle(box, fill=1), mat)

    def line(self, pts, mat, width=1):
        self.shape(lambda d: d.line(pts, fill=1, width=width), mat)


def base(mat):
    return mat.split("#")[0] if mat else None


def build():
    g = Grid()
    # --- behind everything: beaver tail
    g.ellipse((1, 40, 15, 62), "tail")
    # --- body
    g.ellipse((8, 33, 48, 74), "fur")
    g.ellipse((16, 42, 40, 72), "belly")
    # --- leather strap over the shoulder with a buckle
    g.line([(13, 36), (42, 66)], "strap", width=3)
    # --- the egg, held in front of the chest
    g.ellipse((19, 43, 37, 64), "egg")
    for sx, sy in ((25, 48), (31, 51), (27, 57), (23, 53), (33, 58), (29, 62)):
        g.put(sx, sy, "speckle")
    g.rect((14, 37, 16, 39), "buckle")
    g.put(15, 38, "strap")
    # --- paws holding the egg from both sides, with claws
    g.ellipse((12, 52, 19, 59), "paw")
    g.ellipse((37, 50, 44, 57), "paw#r")
    for cx, cy in ((19, 54), (19, 57)):
        g.put(cx, cy, "claw")
    for cx, cy in ((37, 52), (37, 55)):
        g.put(cx, cy, "claw")
    # --- ears
    g.ellipse((4, 3, 18, 17), "fur#el")
    g.ellipse((38, 3, 52, 17), "fur#er")
    g.ellipse((8, 7, 14, 13), "earin")
    g.ellipse((42, 7, 48, 13), "earin")
    # --- head (fur ring = cheeks / beard of the costume)
    g.ellipse((8, 7, 48, 41), "fur#h")
    # --- face
    g.ellipse((16, 15, 40, 41), "skin")
    # --- curly hair: every curl is its own blob so the shading pass gives it a rim
    # (only on the crown, so the round bear head + ears still read)
    curls = [(16, 11), (21, 8), (27, 7), (33, 8), (39, 11), (19, 14), (25, 12), (31, 12),
             (37, 14), (14, 16), (42, 16)]
    for i, (cx, cy) in enumerate(curls):
        r = 3 if i < 9 else 2
        g.ellipse((cx - r, cy - r, cx + r, cy + r), "hair#%d" % i)
    # --- face details
    for x, y in ((20, 23), (21, 22), (22, 22), (23, 22), (24, 23)):
        g.put(x, y, "brow")
    for x, y in ((32, 23), (33, 22), (34, 22), (35, 22), (36, 23)):
        g.put(x, y, "brow")
    for ex in (21, 33):          # smiling eyes: 3x2 with a glint
        g.rect((ex, 25, ex + 2, 26), "eye")
        g.put(ex, 25, "glint")
        g.put(ex - 1, 26, "eye")
        g.put(ex + 3, 26, "eye")
    for bx in (18, 19, 37, 38):
        g.put(bx, 30, "blush")
    g.ellipse((25, 27, 31, 31), "nose")          # beaver nose
    # smile + buck teeth
    for x, y in ((22, 34), (23, 35), (24, 35), (25, 36), (31, 36), (32, 35), (33, 35), (34, 34)):
        g.put(x, y, "mouth")
    g.rect((26, 35, 30, 39), "teeth")
    g.line([(28, 35), (28, 39)], "toothline")
    g.line([(26, 39), (30, 39)], "toothline")
    # --- the nest of sticks, with two more eggs
    g.ellipse((4, 56, 11, 67), "nestegg#a")
    g.ellipse((45, 57, 52, 68), "nestegg#b")
    g.ellipse((0, 64, 55, 80), "stick")
    for i in range(-2, 12):
        x = i * 5
        g.line([(x, 65), (x + 7, 72)], "stickdark")
        g.line([(x + 7, 65), (x, 72)], "stick#x")
    return g


def render(g):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p = img.load()
    for y in range(H):
        for x in range(W):
            mat = g.get(x, y)
            if mat is None:
                continue
            b = base(mat)
            if b in FLAT:
                p[x, y] = FLAT[b] + (255,)
                continue
            hi, mid, lo = PAL[b]
            ul, dr = g.get(x - 1, y - 1), g.get(x + 1, y + 1)
            up_, dn = g.get(x, y - 1), g.get(x, y + 1)
            if dr != mat or dn != mat:
                c = lo
            elif ul != mat or up_ != mat:
                c = hi
            else:
                c = mid
                if b in ("fur", "hair") and (x * 3 + y * 5) % 9 == 0:
                    c = lo  # fur texture
                if b == "tail" and ((x + y) % 4 == 0 or (x - y) % 4 == 0):
                    c = lo  # scaly beaver-tail cross-hatch
            p[x, y] = c + (255,)
    # ink line around the eggs so they pop against the fur / nest
    INKED = ("egg", "nestegg")
    for y in range(H):
        for x in range(W):
            mat = g.get(x, y)
            b = base(mat)
            if mat is None or b in INKED or b in ("speckle", "claw"):
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if base(g.get(x + dx, y + dy)) in INKED:
                    p[x, y] = OUTLINE
                    break
    # outline around the whole silhouette
    out = img.copy()
    po = out.load()
    for y in range(H):
        for x in range(W):
            if p[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H and p[xx, yy][3]:
                    po[x, y] = OUTLINE
                    break
    return out


# face mustache: 13x4 at (22, 31) inside the sprite, three twitch poses
FACE_POS = (22, 31)
FACE_STACHE = [
    ["#...........#", "##..#####..##", ".###########.", "..####.####.."],
    ["##.........##", ".#..#####..#.", ".###########.", "..####.####.."],
    [".............", "#...#####...#", "#############", ".####...####."],
]


def face_stache(pose):
    rows = FACE_STACHE[pose]
    img = Image.new("RGBA", (len(rows[0]), len(rows)), (0, 0, 0, 0))
    p = img.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == "#":
                p[x, y] = (58, 30, 12, 255)
    # 1px highlight on the upper edge
    for x in range(img.width):
        for y in range(img.height):
            if p[x, y][3] and (y == 0 or not p[x, y - 1][3]):
                p[x, y] = (96, 56, 28, 255)
                break
    return img


def eierbaer():
    return render(build())


def eierbaer_with_stache(pose=0):
    img = eierbaer()
    img.alpha_composite(face_stache(pose), FACE_POS)
    return img
