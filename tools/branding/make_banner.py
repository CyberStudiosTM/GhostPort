import random

from PIL import Image, ImageDraw

S = 4
LW, LH = 400, 150

NAVY = (0x20, 0x28, 0x42)
LILAC = (0xC6, 0xB6, 0xF3)
MINT = (0xA8, 0xE8, 0xDC)
BLUE = (0xAE, 0xD8, 0xF5)
BLUSH = (0xF4, 0xC8, 0xEA)
VIOLET = (0x3B, 0x2A, 0x6B)
WIN_BODY = (0x2B, 0x35, 0x5E)
WIN_BACK = (0x34, 0x40, 0x72)
CLOUD = (0x3A, 0x47, 0x7E)
CLOUD_HI = (0x46, 0x55, 0x90)

G = {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "C": "01110 10001 10000 10000 10000 10001 01110",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    ".": "00000 00000 00000 00000 00000 01100 01100",
    ">": "10000 01000 00100 00010 00100 01000 10000",
    "0": "01110 10001 10011 10101 11001 10001 01110",
    "2": "01110 10001 00001 00110 01000 10000 11111",
    "8": "01110 10001 10001 01110 10001 10001 01110",
}

img = Image.new("RGBA", (LW, LH), NAVY + (255,))
d = ImageDraw.Draw(img)
random.seed(7)

bands = [
    (0, NAVY),
    (36, (0x25, 0x2F, 0x4F)),
    (66, (0x2C, 0x37, 0x60)),
    (96, (0x35, 0x41, 0x74)),
    (122, (0x40, 0x4E, 0x88)),
]
for i, (y0, col) in enumerate(bands):
    y1 = bands[i + 1][0] if i + 1 < len(bands) else LH
    d.rectangle([0, y0, LW, y1], fill=col)
    if i + 1 < len(bands):
        nxt = bands[i + 1][1]
        for yy in range(y1 - 3, y1):
            for xx in range(LW):
                if (xx + yy) % 2 == 0:
                    d.point((xx, yy), fill=nxt)


def cloud(cx, cy, w, col, hi):
    for dx, dy, r in ((0, 0, 7), (-9, 3, 5), (9, 3, 6), (18, 5, 4), (-16, 5, 3)):
        d.ellipse([cx + dx - r * w // 7, cy + dy - r, cx + dx + r * w // 7, cy + dy + r], fill=col)
    d.rectangle([cx - 20, cy + 5, cx + 22, cy + 9], fill=col)
    d.rectangle([cx - 8, cy - 5, cx + 4, cy - 5], fill=hi)


cloud(60, 120, 7, CLOUD, CLOUD_HI)
cloud(180, 138, 8, CLOUD, CLOUD_HI)
cloud(120, 22, 5, CLOUD, CLOUD_HI)

for _ in range(34):
    x, y = random.randrange(LW), random.randrange(LH)
    d.point((x, y), fill=random.choice([LILAC, BLUE, (0x7C, 0x88, 0xC0)]))
for sx, sy in ((30, 14), (368, 52), (290, 8), (150, 112)):
    d.point((sx, sy), fill=BLUE)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        d.point((sx + dx, sy + dy), fill=(0x7C, 0x88, 0xC0))
for _ in range(14):
    x, y = random.randrange(LW), random.randrange(LH)
    if (10 <= x <= 200 and 34 <= y <= 98) or (x >= 284 and y <= 135):
        continue
    d.rectangle([x, y, x + random.choice([1, 2, 3]), y], fill=random.choice([MINT, BLUSH, BLUE]))


def text(x, y, s, col, sc=1, shadow=None):
    for ch in s:
        if ch != " ":
            rows = G[ch].split()
            for r, row in enumerate(rows):
                for c, bit in enumerate(row):
                    if bit == "1":
                        if shadow:
                            d.rectangle(
                                [
                                    x + c * sc + 2,
                                    y + r * sc + 2,
                                    x + c * sc + sc + 1,
                                    y + r * sc + sc + 1,
                                ],
                                fill=shadow,
                            )
        x += 6 * sc
    return x


def draw_text(x, y, s, col, sc=1, shadow=None):
    if shadow:
        text(x, y, s, col, sc, shadow)
    for ch in s:
        if ch != " ":
            for r, row in enumerate(G[ch].split()):
                for c, bit in enumerate(row):
                    if bit == "1":
                        d.rectangle(
                            [x + c * sc, y + r * sc, x + c * sc + sc - 1, y + r * sc + sc - 1],
                            fill=col,
                        )
        x += 6 * sc
    return x


def window(x0, y0, x1, y1, title_col, body=WIN_BODY):
    d.rectangle([x0 + 2, y0 + 2, x1 + 2, y1 + 2], fill=(0x18, 0x1E, 0x35))
    d.rectangle([x0, y0, x1, y1], fill=body, outline=title_col)
    d.rectangle([x0, y0, x1, y0 + 8], fill=title_col)
    for i, c in enumerate((BLUSH, MINT, BLUE)):
        d.rectangle(
            [x0 + 3 + i * 5, y0 + 3, x0 + 5 + i * 5, y0 + 5],
            fill=c if title_col != BLUSH else VIOLET,
        )
    d.line([x1 - 12, y0 + 4, x1 - 4, y0 + 4], fill=VIOLET)


end = draw_text(14, 40, "GHOSTPORT", LILAC, 3, VIOLET)
d.rectangle([end - 2, 40, end + 4, 60], fill=MINT)
d.rectangle([end - 2 + 2, 62, end + 6, 62], fill=VIOLET)
draw_text(16, 74, "YOUR FRIENDLY LOCALHOST", BLUE, 1)
draw_text(16, 84, "INVESTIGATOR.", BLUE, 1)
for i in range(0, 52, 2):
    d.point((16 + i, 96), fill=(0x7C, 0x88, 0xC0))

window(226, 8, 300, 44, (0x7C, 0x88, 0xC0), WIN_BACK)

window(196, 22, 292, 68, LILAC)
draw_text(202, 36, "> INSPECT 8080", MINT, 1)
draw_text(202, 46, "OPEN", BLUSH, 1)
draw_text(202, 56, "HTTP 200", BLUE, 1)
d.rectangle([250, 56, 252, 62], fill=MINT)

window(200, 74, 290, 132, BLUE)
nodes = {"a": (212, 98), "b": (240, 88), "c": (264, 112), "d": (230, 118)}
links = [("a", "b"), ("b", "c"), ("a", "d"), ("d", "c")]
for p, q in links:
    (x0, y0), (x1, y1) = nodes[p], nodes[q]
    steps = max(abs(x1 - x0), abs(y1 - y0))
    for i in range(0, steps, 3):
        d.point(
            (x0 + (x1 - x0) * i // steps + 3, y0 + (y1 - y0) * i // steps + 3),
            fill=(0x9F, 0xAE, 0xE0),
        )
for key, col in zip(nodes, (LILAC, BLUSH, MINT, BLUE)):
    x, y = nodes[key]
    d.rectangle([x, y, x + 6, y + 6], fill=col, outline=VIOLET)

window(300, 52, 392, 128, LILAC)
d.rectangle([302, 62, 390, 126], fill=(0x24, 0x2C, 0x4E))
d.rectangle([302, 62, 390, 64], fill=(0x2E, 0x38, 0x66))

d.rectangle([366, 88, 388, 106], fill=VIOLET, outline=LILAC)
d.rectangle([386, 94, 388, 100], fill=(0x24, 0x2C, 0x4E))

for x in range(268, 378, 2):
    d.point((x, 115), fill=MINT)
for y in range(107, 116, 2):
    d.point((377, y), fill=MINT)

sprite = Image.open("portgeist_master_32.png").convert("RGBA").resize((96, 96), Image.NEAREST)
img.alpha_composite(sprite, (290, 9))

for gx, gy in ((318, 36), (270, 130), (30, 130)):
    d.rectangle([gx, gy, gx + 1, gy + 5], fill=MINT)
    d.rectangle([gx + 3, gy + 2, gx + 4, gy + 6], fill=BLUSH)

img.convert("RGB").resize((LW * S, LH * S), Image.NEAREST).save(
    "banner_haunted_desktop_1600x600.png"
)
