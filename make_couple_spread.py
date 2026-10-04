"""Ghép ảnh chú rể + cô dâu thành 1 trang ngang (2000x1400), kiểu "Chú rể & Cô dâu".

- Nền giấy ngà có hạt nhẹ
- 2 ảnh trong khung vòm (giống ảnh bìa thiệp) + viền vàng mảnh bao ngoài
- Nhãn CHÚ RỂ / CÔ DÂU phía trên, tên viết tay (Great Vibes) phía dưới
- Trái tim "ღ" ở giữa (cùng ký tự trái tim dùng trên thiệp), ngày cưới dưới cùng

Chạy: python make_couple_spread.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "assets", "img")
SCRIPT_FONT = os.path.join(ROOT, "tools", "fonts", "GreatVibes-Regular.ttf")
SERIF_FONT = r"C:\Windows\Fonts\cambria.ttc"
HEART_FONT = r"C:\Windows\Fonts\sylfaen.ttf"  # ღ trong Sylfaen giống trái tim trên thiệp
HEART = "ღ"

GROOM_PHOTO, BRIDE_PHOTO = "album-02.webp", "album-03.webp"
OUT = "pic-ngang.webp"
GROOM_LABEL, BRIDE_LABEL = "CHÚ RỂ", "CÔ DÂU"
GROOM_NAME, BRIDE_NAME = "Lê Đức Thành", "Huỳnh Thị Ly Ly"
DATE = "16 · 11 · 2026"

W, H = 2000, 1400
PAPER = (247, 242, 235)
RED = (128, 0, 32)
GOLD = (196, 164, 112)
GREY = (120, 112, 106)

ARCH_W, ARCH_H, ARCH_TOP = 690, 980, 150
LEFT_X, RIGHT_X = 175, W - 175 - ARCH_W


def paper():
    noise = Image.effect_noise((W, H), 14).filter(ImageFilter.GaussianBlur(0.7))
    base = Image.new("RGB", (W, H), PAPER)
    darker = Image.new("RGB", (W, H), tuple(c - 7 for c in PAPER))
    return Image.composite(darker, base, noise.point(lambda v: int(max(0, v - 128) * 0.7)))


def arch_mask(w, h, ss=4):
    """Vòm: đỉnh nửa hình tròn, đáy bo nhẹ."""
    m = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(m)
    r = w * ss // 2
    d.rounded_rectangle((0, r, w * ss - 1, h * ss - 1), radius=28 * ss, fill=255)
    d.rectangle((0, r, w * ss - 1, r + 60 * ss), fill=255)
    d.ellipse((0, 0, w * ss - 1, 2 * r), fill=255)
    return m.resize((w, h), Image.LANCZOS)


def arch_outline(page, x, y, w, h, pad, color, width):
    ss = 4
    W2, H2 = (w + 2 * pad) * ss, (h + 2 * pad) * ss
    m = Image.new("L", (W2, H2), 0)
    d = ImageDraw.Draw(m)
    r = W2 // 2
    d.arc((0, 0, W2 - 1, 2 * r), 180, 360, fill=255, width=width * ss)
    d.line((0, r, 0, H2), fill=255, width=width * ss)
    d.line((W2 - 1, r, W2 - 1, H2), fill=255, width=width * ss)
    m = m.resize((w + 2 * pad, h + 2 * pad), Image.LANCZOS)
    page.paste(Image.new("RGB", m.size, color), (x - pad, y - pad), m)


def cover(img, w, h, focus_y):
    s = max(w / img.width, h / img.height)
    r = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = (r.width - w) // 2
    y = round((r.height - h) * focus_y)
    return r.crop((x, y, x + w, y + h))


def spaced(d, cx, y, text, f, fill, sp):
    ws = [d.textlength(c, font=f) for c in text]
    x = cx - (sum(ws) + sp * (len(text) - 1)) / 2
    for c, w in zip(text, ws):
        d.text((x, y), c, font=f, fill=fill)
        x += w + sp


def centered(d, cx, y, text, f, fill):
    d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)


def main():
    page = paper()
    mask = arch_mask(ARCH_W, ARCH_H)

    for x, photo, focus in ((LEFT_X, GROOM_PHOTO, 0.35), (RIGHT_X, BRIDE_PHOTO, 0.25)):
        img = Image.open(os.path.join(IMG, photo)).convert("RGB")
        # bóng đổ mềm phía sau khung
        sh = Image.new("L", (W, H), 0)
        sh.paste(mask, (x + 6, ARCH_TOP + 14))
        sh = sh.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.22))
        page = Image.composite(Image.new("RGB", (W, H), (90, 70, 60)), page, sh)
        page.paste(cover(img, ARCH_W, ARCH_H, focus), (x, ARCH_TOP), mask)
        arch_outline(page, x, ARCH_TOP, ARCH_W, ARCH_H, 16, GOLD, 2)

    d = ImageDraw.Draw(page)
    label_f = ImageFont.truetype(SERIF_FONT, 26)
    name_f = ImageFont.truetype(SCRIPT_FONT, 84)
    heart_f = ImageFont.truetype(HEART_FONT, 120)
    date_f = ImageFont.truetype(SERIF_FONT, 30)

    for x, label, name in ((LEFT_X, GROOM_LABEL, GROOM_NAME), (RIGHT_X, BRIDE_LABEL, BRIDE_NAME)):
        cx = x + ARCH_W / 2
        spaced(d, cx, 78, label, label_f, GREY, 9)
        centered(d, cx, ARCH_TOP + ARCH_H + 38, name, name_f, RED)

    # Trái tim ở giữa + 2 gạch mảnh trên/dưới
    cx, cy = W / 2, ARCH_TOP + ARCH_H / 2
    d.text((cx, cy), HEART, font=heart_f, fill=RED, anchor="mm")
    d.line((cx, cy - 260, cx, cy - 120), fill=GOLD, width=2)
    d.line((cx, cy + 95, cx, cy + 235), fill=GOLD, width=2)

    spaced(d, W / 2, H - 70, DATE, date_f, GREY, 6)

    dst = os.path.join(IMG, OUT)
    page.save(dst, "WEBP", quality=86, method=6)
    print(OUT, page.size, os.path.getsize(dst) // 1024, "KB")


if __name__ == "__main__":
    main()
