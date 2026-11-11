"""Step 3 assets: mascot states, social preview, terminal screenshot."""

import random
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
master = Image.open(HERE / "portgeist_master_32.png").convert("RGBA")

NAVY = (0x20, 0x28, 0x42)
LILAC = (0xC6, 0xB6, 0xF3)
MINT = (0xA8, 0xE8, 0xDC)
MINT_D = (0x6F, 0xC9, 0xB8)
BLUE = (0xAE, 0xD8, 0xF5)
BLUSH = (0xF4, 0xC8, 0xEA)
VIOLET = (0x3B, 0x2A, 0x6B)
BODY = (0xC6, 0xB6, 0xF3, 255)
HI = (0xF1, 0xEC, 0xFF, 255)
CLOSED = (0x7B, 0x6C, 0xC4, 255)
DIM = (0xB0, 0xA4, 0xE0, 255)
CLEAR = (0, 0, 0, 0)

EYES = [(x, y) for x in (11, 12, 17, 18) for y in range(11, 15)]


def px_set(im, pts, col):
    p = im.load()
    for x, y in pts:
        p[x, y] = col


def connected():
    im = master.copy()
    px_set(im, [(11, 11), (17, 11)], HI)
    for cx, cy, arm in ((27, 5, BLUSH), (29, 10, BLUE)):
        px_set(im, [(cx, cy)], MINT + (255,))
        px_set(im, [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)], arm + (255,))
    return im


def closed_eyes(im):
    px_set(im, EYES, BODY)
    px_set(im, [(11, 13), (12, 13), (17, 13), (18, 13)], CLOSED)
    px_set(im, [(11, 12), (18, 12)], CLOSED)
    return im


def sleeping():
    im = closed_eyes(master.copy())
    px_set(im, [(14, 19), (15, 19)], DIM)
    px_set(im, [(14, 18), (15, 18)], (0xDD, 0xBB, 0xD8, 255))
    z = [(25, 3), (26, 3), (27, 3), (27, 4), (26, 5), (25, 6), (25, 7), (26, 7), (27, 7)]
    px_set(im, z, BLUE + (255,))
    return im


def confused():
    im = master.copy()
    px_set(im, EYES, BODY)
    px_set(im, [(11, y) for y in range(11, 15)] + [(12, y) for y in range(11, 15)], MINT + (255,))
    px_set(im, [(11, 14), (12, 14)], MINT_D + (255,))
    px_set(im, [(17, 12), (18, 12), (19, 12), (17, 13), (18, 13), (19, 13)], MINT + (255,))
    px_set(im, [(17, 13), (18, 13), (19, 13)], MINT_D + (255,))
    px_set(im, [(14, 19), (15, 19)], BLUSH + (255,))
    px_set(im, [(14, 18), (15, 18)], MINT + (255,))
    out = Image.new("RGBA", (32, 32), CLEAR)
    out.alpha_composite(im.crop((0, 0, 32, 10)), (1, 0))
    out.alpha_composite(im.crop((0, 10, 32, 32)), (0, 10))
    q = [(26, 2), (27, 2), (28, 2), (28, 3), (27, 4), (28, 4), (27, 6)]
    px_set(out, q, MINT + (255,))
    return out


def up(im, scale):
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


states = {
    "portgeist_display_512.png": master,
    "portgeist_connected_512.png": connected(),
    "portgeist_sleeping_512.png": sleeping(),
    "portgeist_confused_512.png": confused(),
}
for name, im in states.items():
    up(im, 16).save(HERE / name)

frames = []
blink = closed_eyes(master.copy())
glint = master.copy()
px_set(glint, [(11, 11), (17, 11)], HI)
for dy, base in ((0, master), (-1, master), (-1, glint), (-1, blink), (-1, master), (0, glint)):
    f = Image.new("RGBA", (32, 32), CLEAR)
    f.alpha_composite(base, (0, dy))
    frames.append(f)

sheet = Image.new("RGBA", (32 * len(frames), 32), CLEAR)
for i, f in enumerate(frames):
    sheet.alpha_composite(f, (i * 32, 0))
up(sheet, 8).save(HERE / "portgeist_idle_sheet.png")

big = [up(f, 8) for f in frames]
colors = sorted({c[:3] for f in big for c in f.getdata() if c[3] == 255})
index = {c: i + 1 for i, c in enumerate(colors)}
gif_frames = []
for f in big:
    p = Image.new("P", f.size, 0)
    p.putdata([index[c[:3]] if c[3] == 255 else 0 for c in f.getdata()])
    p.putpalette([0, 0, 0] + [v for c in colors for v in c])
    gif_frames.append(p)
gif_frames[0].save(
    HERE / "portgeist_idle.gif",
    save_all=True,
    append_images=gif_frames[1:],
    duration=[260, 260, 260, 140, 260, 260],
    loop=0,
    transparency=0,
    disposal=2,
)

# ---- social preview (1280x640, 4px grid) ----
S, LW, LH = 4, 320, 160
img = Image.new("RGBA", (LW, LH), NAVY + (255,))
d = ImageDraw.Draw(img)
random.seed(11)
bands = [
    (0, NAVY),
    (40, (0x25, 0x2F, 0x4F)),
    (76, (0x2C, 0x37, 0x60)),
    (108, (0x35, 0x41, 0x74)),
    (134, (0x40, 0x4E, 0x88)),
]
for i, (y0, col) in enumerate(bands):
    y1 = bands[i + 1][0] if i + 1 < len(bands) else LH
    d.rectangle([0, y0, LW, y1], fill=col)
    if i + 1 < len(bands):
        for yy in range(y1 - 3, y1):
            for xx in range(LW):
                if (xx + yy) % 2 == 0:
                    d.point((xx, yy), fill=bands[i + 1][1])


def cloud(cx, cy):
    c, hi = (0x3A, 0x47, 0x7E), (0x46, 0x55, 0x90)
    for dx, dy, r in ((0, 0, 7), (-9, 3, 5), (9, 3, 6), (18, 5, 4), (-16, 5, 3)):
        d.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=c)
    d.rectangle([cx - 20, cy + 5, cx + 22, cy + 9], fill=c)
    d.rectangle([cx - 8, cy - 5, cx + 4, cy - 5], fill=hi)


cloud(70, 136)
cloud(160, 20)
cloud(300, 142)
for _ in range(30):
    x, y = random.randrange(LW), random.randrange(LH)
    if 8 <= x <= 190 and 30 <= y <= 120:
        continue
    d.point((x, y), fill=random.choice([LILAC, BLUE, (0x7C, 0x88, 0xC0)]))

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
}


def draw_text(x, y, s, col, sc, shadow=None):
    for layer, off in ((shadow, 2), (col, 0)):
        if layer is None:
            continue
        cx = x
        for ch in s:
            if ch != " ":
                for r, row in enumerate(G[ch].split()):
                    for c, bit in enumerate(row):
                        if bit == "1":
                            px, py = cx + c * sc + off, y + r * sc + off
                            d.rectangle([px, py, px + sc - 1, py + sc - 1], fill=layer)
            cx += 6 * sc
    return x + 6 * len(s) * sc - sc


end = draw_text(14, 52, "GHOSTPORT", LILAC, 3, VIOLET)
d.rectangle([end + 3, 52, end + 9, 72], fill=MINT)
draw_text(16, 88, "LOCALHOST", BLUE, 2)
draw_text(16, 106, "INVESTIGATOR.", BLUE, 2)

d.rectangle([192, 74, 314, 156], fill=(0x18, 0x1E, 0x35))
d.rectangle([188, 70, 310, 152], fill=(0x24, 0x2C, 0x4E), outline=LILAC)
d.rectangle([188, 70, 310, 80], fill=LILAC)
for i, c in enumerate((BLUSH, MINT, BLUE)):
    d.rectangle([192 + i * 6, 73, 194 + i * 6, 75], fill=c)
d.rectangle([276, 120, 304, 144], fill=VIOLET, outline=LILAC)
d.rectangle([302, 128, 304, 136], fill=(0x24, 0x2C, 0x4E))
img.alpha_composite(up(master, 4), (176, 16))
for gx, gy in ((318 - 6, 22), (140, 18), (24, 150)):
    d.rectangle([gx, gy, gx + 1, gy + 5], fill=MINT)
    d.rectangle([gx + 3, gy + 2, gx + 4, gy + 6], fill=BLUSH)
img.convert("RGB").resize((LW * S, LH * S), Image.NEAREST).save(
    HERE / "social_preview_1280x640.png"
)

# ---- terminal screenshot from the real captured output ----
ansi = (HERE / "terminal_capture.ansi").read_text(encoding="utf-8")
FONT = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 22)
FONTB = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 22)
CW = round(FONT.getlength("M"))
LHT = 30
DEFAULT = (0xE6, 0xE9, 0xF5)

cmd_line = [
    ("PS> ", (0x9A, 0xA5, 0xC4), False),
    ("ghostport", (0xC9, 0xB6, 0xFF), True),
    (" inspect 8765 --http --expect-json", (0xE6, 0xE9, 0xF5), False),
]
lines = [[(ch, col, b) for t, col, b in cmd_line for ch in t]]
sgr = re.compile(r"\x1b\[([0-9;]*)m")
for raw in ansi.rstrip("\n").split("\n"):
    fg, bold, pos, row = DEFAULT, False, 0, []
    for m in sgr.finditer(raw):
        row += [(ch, fg, bold) for ch in raw[pos : m.start()]]
        pos = m.end()
        p = [int(v) for v in m.group(1).split(";") if v] or [0]
        i = 0
        while i < len(p):
            if p[i] == 0:
                fg, bold = DEFAULT, False
            elif p[i] == 1:
                bold = True
            elif p[i] == 38 and p[i + 1] == 2:
                fg = tuple(p[i + 2 : i + 5])
                i += 4
            i += 1
    row += [(ch, fg, bold) for ch in raw[pos:]]
    lines.append(row)
lines.append([])
lines.append([("PS> ", (0x9A, 0xA5, 0xC4), False)])

cols = max(len(r) for r in lines)
PAD, TB, MARGIN = 28, 44, 36
win_w, win_h = cols * CW + PAD * 2, TB + len(lines) * LHT + PAD * 2
W, H = win_w + MARGIN * 2, win_h + MARGIN * 2
shot = Image.new("RGB", (W, H), (0x2C, 0x37, 0x60))
sd = ImageDraw.Draw(shot)
sd.rectangle(
    [MARGIN + 8, MARGIN + 8, MARGIN + win_w + 8, MARGIN + win_h + 8], fill=(0x18, 0x1E, 0x35)
)
sd.rectangle(
    [MARGIN, MARGIN, MARGIN + win_w, MARGIN + win_h],
    fill=(0x1A, 0x20, 0x38),
    outline=LILAC,
    width=2,
)
sd.rectangle([MARGIN, MARGIN, MARGIN + win_w, MARGIN + TB], fill=LILAC)
for i, c in enumerate((BLUSH, MINT, BLUE)):
    sd.rectangle(
        [MARGIN + 16 + i * 26, MARGIN + 14, MARGIN + 30 + i * 26, MARGIN + 28],
        fill=c,
        outline=VIOLET,
    )
sd.text((MARGIN + 110, MARGIN + 10), "ghostport", font=FONTB, fill=VIOLET)
for r, row in enumerate(lines):
    y = MARGIN + TB + PAD + r * LHT
    for c, (ch, col, b) in enumerate(row):
        if ch != " ":
            sd.text((MARGIN + PAD + c * CW, y), ch, font=FONTB if b else FONT, fill=col)
cx = MARGIN + PAD + 4 * CW
cy = MARGIN + TB + PAD + (len(lines) - 1) * LHT
sd.rectangle([cx, cy + 2, cx + CW - 2, cy + 24], fill=MINT)
shot.save(HERE / "terminal_screenshot.png")

for f in sorted(HERE.glob("*.png")) + [HERE / "portgeist_idle.gif"]:
    with Image.open(f) as im:
        print(f.name, im.size, im.mode)
