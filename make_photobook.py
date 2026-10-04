"""Ghép 2 ảnh thành 1 trang photobook ngang (2000x1400).

Trái : nền trắng, tiêu đề chữ có chân, ảnh khung chữ nhật, gạch ngang + ngày cưới
Phải: nền giấy be, khung ảnh bo 2 góc chéo, chữ trắng giãn cách phía trên + câu chúc phía dưới

Chạy: python make_photobook.py
"""
import os
import random
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "assets", "img")
FONTS = r"C:\Windows\Fonts"

LEFT_PHOTO = "2W4A4725.webp"
RIGHT_PHOTO = "2W4A4802.webp"
OUT = "album-ngang-02.webp"

TITLE = ("Thành", "Ly")  # chữ viết tay, giữa là trái tim
LEFT_CAPTION = "16 · 11 · 2026"
RIGHT_TOP = ""  # để trống = không hiện chữ phía trên khung phải
RIGHT_QUOTE = ["“Hai trái tim, một lời hẹn ước —",
               "cùng nhau đi qua mọi mùa yêu thương.”"]

W, H = 2000, 1400
WHITE = (255, 255, 255)
GREY = (110, 110, 110)
INK = (70, 62, 54)
LINE = (190, 190, 190)
BEIGE = (217, 203, 190)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def spaced_text(draw, cx, y, text, f, fill, spacing):
    """Vẽ chữ giãn cách, căn giữa tại cx."""
    widths = [draw.textlength(ch, font=f) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += w + spacing
    return total


def heart(page, cx, cy, h, width, color, tilt=-8):
    """Trái tim nét viền mảnh, vẽ phóng 4x rồi thu nhỏ cho mượt."""
    k = 4
    sz = int(h * 1.6) * k
    m = Image.new("L", (sz, sz), 0)
    sc = h * k / 34.0
    pts = []
    for i in range(801):
        t = 2 * math.pi * i / 800
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((sz / 2 + x * sc, sz / 2 + (y + 1.5) * sc))
    ImageDraw.Draw(m).line(pts, fill=255, width=int(width * k), joint="curve")
    m = m.rotate(tilt, resample=Image.BICUBIC).resize((sz // k, sz // k), Image.LANCZOS)
    page.paste(Image.new("RGB", m.size, color), (int(cx - m.width / 2), int(cy - m.height / 2)), m)


def script_title(page, d, cx, cy, names, size):
    """'Thành ♡ Ly' bằng Great Vibes, căn giữa tại (cx, cy)."""
    f = ImageFont.truetype(os.path.join(ROOT, "tools", "fonts", "GreatVibes-Regular.ttf"), size)
    hh = size * 0.61
    gap = size * 0.17
    hw = hh * 1.05
    w1, w2 = d.textlength(names[0], font=f), d.textlength(names[1], font=f)
    x = cx - (w1 + gap + hw + gap + w2) / 2
    d.text((x, cy), names[0], font=f, fill=INK, anchor="lm")
    heart(page, x + w1 + gap + hw / 2, cy + size * 0.03, hh, size / 30, INK)
    d.text((x + w1 + gap + hw + gap, cy), names[1], font=f, fill=INK, anchor="lm")


def cover(img, w, h, focus_y=0.5):
    """Cắt ảnh phủ kín khung w x h (giữ tỉ lệ)."""
    s = max(w / img.width, h / img.height)
    r = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = (r.width - w) // 2
    y = round((r.height - h) * focus_y)
    return r.crop((x, y, x + w, y + h))


def paper(w, h, base):
    """Nền giấy be có hạt nhẹ."""
    random.seed(7)
    noise = Image.effect_noise((w, h), 18).filter(ImageFilter.GaussianBlur(0.6))
    tex = Image.new("RGB", (w, h), base)
    return Image.composite(Image.new("RGB", (w, h), tuple(c - 8 for c in base)), tex,
                           noise.point(lambda v: int(max(0, v - 128) * 0.6)))


def diagonal_round_mask(w, h, r):
    """Khung bo tròn góc trên-trái và dưới-phải (giống mẫu)."""
    m = Image.new("L", (w * 4, h * 4), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, w * 4 - 1, h * 4 - 1), radius=r * 4, fill=255)
    d.rectangle((w * 4 - r * 4, 0, w * 4, r * 4), fill=255)        # góc trên-phải vuông
    d.rectangle((0, h * 4 - r * 4, r * 4, h * 4), fill=255)        # góc dưới-trái vuông
    return m.resize((w, h), Image.LANCZOS)


def main():
    page = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(page)

    # ---------- Trang trái ----------
    ph_x0, ph_y0, ph_x1, ph_y1 = 148, 175, 860, 1228
    left = Image.open(os.path.join(IMG, LEFT_PHOTO)).convert("RGB")
    page.paste(cover(left, ph_x1 - ph_x0, ph_y1 - ph_y0, focus_y=0.55), (ph_x0, ph_y0))

    script_title(page, d, (ph_x0 + ph_x1) / 2, 86, TITLE, 118)

    cap_f = font("cambria.ttc", 30)
    cy = 1287
    tw = spaced_text(d, (ph_x0 + ph_x1) / 2, cy - 18, LEFT_CAPTION, cap_f, GREY, 5)
    mid = (ph_x0 + ph_x1) / 2
    d.line((ph_x0, cy, mid - tw / 2 - 30, cy), fill=LINE, width=2)
    d.line((mid + tw / 2 + 30, cy, ph_x1, cy), fill=LINE, width=2)

    # ---------- Trang phải ----------
    page.paste(paper(W - 1000, H, BEIGE), (1000, 0))
    fx0, fy0, fx1, fy1 = 1038, 36, 1964, 1364
    fw, fh = fx1 - fx0, fy1 - fy0
    right = Image.open(os.path.join(IMG, RIGHT_PHOTO)).convert("RGB")
    right = right.crop((0, 14, right.width, right.height))  # bỏ vệt tối sát mép trên ảnh gốc
    photo = cover(right, fw, fh, focus_y=0.45)
    page.paste(photo, (fx0, fy0), diagonal_round_mask(fw, fh, 70))

    small_f = font("segoeuisl.ttf", 22)
    d = ImageDraw.Draw(page)
    if RIGHT_TOP:
        spaced_text(d, (fx0 + fx1) / 2, 92, RIGHT_TOP, small_f, WHITE, 7)

    quote_f = font("segoeuil.ttf", 22)
    for i, line in enumerate(RIGHT_QUOTE):
        spaced_text(d, (fx0 + fx1) / 2, 1290 + i * 32, line, quote_f, WHITE, 3)

    dst = os.path.join(IMG, OUT)
    page.save(dst, "WEBP", quality=86, method=6)
    print(OUT, page.size, os.path.getsize(dst) // 1024, "KB")


if __name__ == "__main__":
    main()
