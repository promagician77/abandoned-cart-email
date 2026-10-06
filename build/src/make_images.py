"""Simple product shots for a fictional brand. Real flows pull Shopify image URLs instead."""
from PIL import Image, ImageDraw, ImageFilter
S = 480  # drawn at 2x, saved at 240
def shot(name, bg, draw_fn):
    im = Image.new("RGB", (S, S), bg); d = ImageDraw.Draw(im)
    sh = Image.new("L", (S, S), 0); ImageDraw.Draw(sh).ellipse([110, 380, 370, 420], fill=90)
    im.paste((0, 0, 0), mask=sh.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v // 3))
    draw_fn(d); im.resize((240, 240), Image.LANCZOS).save(f"site/img/{name}.jpg", quality=86)
def candle(d):
    d.rounded_rectangle([150, 170, 330, 400], 22, fill=(236, 226, 208)); d.rectangle([150, 250, 330, 330], fill=(120, 140, 112))
    d.line([240, 140, 240, 170], fill=(60, 50, 40), width=6); d.ellipse([226, 96, 254, 142], fill=(242, 170, 60))
def mug(d):
    d.rounded_rectangle([140, 180, 310, 400], 30, fill=(60, 86, 110)); d.ellipse([290, 230, 370, 330], outline=(60, 86, 110), width=22)
def tote(d):
    d.arc([180, 90, 300, 230], 180, 360, fill=(150, 120, 80), width=14); d.polygon([(130, 170), (350, 170), (370, 400), (110, 400)], fill=(214, 196, 160))
def planter(d):
    for i, c in enumerate([(70, 130, 80), (90, 150, 95), (60, 115, 70)]): d.ellipse([170 + i * 40, 90 + (i % 2) * 30, 260 + i * 40, 230], fill=c)
    d.polygon([(150, 220), (330, 220), (305, 400), (175, 400)], fill=(196, 110, 80))
def throw(d):
    d.rounded_rectangle([110, 200, 370, 400], 18, fill=(178, 92, 72))
    for y in range(215, 400, 26): d.line([110, y, 370, y], fill=(200, 120, 98), width=6)
def vase(d):
    d.ellipse([160, 200, 320, 400], fill=(232, 232, 226)); d.rectangle([205, 120, 275, 230], fill=(232, 232, 226)); d.ellipse([200, 108, 280, 132], fill=(210, 210, 204))
def soap(d):
    d.rounded_rectangle([130, 260, 350, 390], 40, fill=(238, 214, 196)); d.rounded_rectangle([170, 290, 310, 330], 12, fill=(222, 194, 172))
def notebook(d):
    d.rounded_rectangle([150, 120, 330, 400], 10, fill=(44, 62, 56)); d.rectangle([150, 120, 170, 400], fill=(30, 44, 40)); d.rectangle([200, 200, 300, 230], fill=(214, 190, 120))
def diffuser(d):
    for x in (210, 235, 260, 285): d.line([240, 230, x, 90], fill=(110, 80, 50), width=5)
    d.rounded_rectangle([180, 220, 300, 400], 26, fill=(176, 196, 206))
for n, bg, f in [("candle", (244, 239, 230), candle), ("mug", (236, 240, 242), mug), ("tote", (244, 240, 232), tote),
                 ("planter", (238, 242, 236), planter), ("throw", (246, 238, 234), throw), ("vase", (236, 236, 240), vase),
                 ("soap", (246, 242, 238), soap), ("notebook", (240, 240, 236), notebook), ("diffuser", (238, 242, 244), diffuser)]:
    shot(n, bg, f)
Image.new("RGB", (240, 240), (238, 238, 236)).save("site/img/placeholder.jpg", quality=80)
print("images done")
