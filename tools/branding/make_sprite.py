from PIL import Image

W = H = 32
OUT = (0x3B, 0x2A, 0x6B, 255)
BODY = (0xC6, 0xB6, 0xF3, 255)
SHADE = (0x9F, 0x8F, 0xDB, 255)
HI = (0xF1, 0xEC, 0xFF, 255)
MINT = (0xA8, 0xE8, 0xDC, 255)
MINT_D = (0x6F, 0xC9, 0xB8, 255)
BLUSH = (0xF4, 0xC8, 0xEA, 255)
CAB = (0xAE, 0xD8, 0xF5, 255)
CAB_D = (0x7F, 0xAE, 0xDB, 255)
CON = (0xE4, 0xE8, 0xF5, 255)
CON_D = (0xB4, 0xBC, 0xD8, 255)
GOLD = (0xE8, 0xC8, 0x6A, 255)

rows = {4: (11, 18), 5: (9, 20), 6: (8, 21), 7: (7, 22)}
for y in range(8, 23):
    rows[y] = (6, 23)

body = set()
for y, (a, b) in rows.items():
    for x in range(a, b + 1):
        body.add((x, y))
for a, b in ((6, 9), (11, 14), (16, 19), (21, 23)):
    for x in range(a, b + 1):
        body.add((x, 23))
for x in (7, 8, 12, 13, 17, 18):
    body.add((x, 24))

cable = set()
for x, y in [(21, 24), (21, 25), (22, 26), (23, 27), (24, 28)]:
    cable |= {(x, y), (x + 1, y)}

con = {(x, y) for x in range(26, 31) for y in range(27, 31)} | {(28, 26), (29, 26)}
pins = {(27, 27), (29, 27)}

solid = body | cable | con
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
px = img.load()

for x, y in solid:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (x + dx, y + dy)
        if n not in solid and 0 <= n[0] < W and 0 <= n[1] < H:
            px[n] = OUT

for x, y in body:
    shaded = x >= 19 or y >= 20 or (x >= 18 and y >= 17)
    px[x, y] = SHADE if shaded else BODY
for x, y in cable:
    px[x, y] = CAB_D if (x + y) % 2 == 0 and y > 25 else CAB
for x, y in con:
    px[x, y] = CON_D if y >= 30 or x == 30 else CON
for x, y in pins:
    px[x, y] = GOLD
for x, y in ((28, 27), (30, 27), (28, 26), (29, 26), (26, 27), (26, 28), (26, 29), (26, 30)):
    px[x, y] = CON_D
for x in (28, 29):
    px[x, 28] = HI if x == 28 else CON

px[9, 8] = HI
px[9, 9] = HI
px[10, 7] = HI

for ex in (11, 17):
    for ey in range(11, 15):
        for dx in (0, 1):
            px[ex + dx, ey] = MINT
    px[ex, 14] = MINT_D
    px[ex + 1, 14] = MINT_D

px[14, 18] = BLUSH
px[15, 18] = BLUSH
px[14, 19] = MINT
px[15, 19] = MINT

img.save("portgeist_master_32.png")
img.resize((512, 512), Image.NEAREST).save("portgeist_master_preview_512.png")
bg = Image.new("RGBA", (512, 512), (0x20, 0x28, 0x42, 255))
bg.alpha_composite(img.resize((512, 512), Image.NEAREST))
bg.save("portgeist_master_preview_512_navy.png")
